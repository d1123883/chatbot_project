import os
import json
import asyncio
import uuid
from typing import List, Dict, Any, Callable, Optional
import google.generativeai as genai
from .models import Message, UserMemory
from sqlmodel import Session, select

# Initialize Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any]):
        def decorator(func: Callable):
            self.tools[name] = {
                "description": description,
                "parameters": parameters,
                "func": func
            }
            return func
        return decorator

    def get_gemini_tools(self):
        return [{"function_declarations": [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            } for name, info in self.tools.items()
        ]}]

registry = ToolRegistry()

@registry.register(
    name="calculate",
    description="Perform basic arithmetic calculations.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "The math expression, e.g., '2 + 2'"}
        },
        "required": ["expression"]
    }
)
def calculate(expression: str) -> str:
    try:
        # Use a simpler/safer way in production
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error: {str(e)}"

class AIAgent:
    def __init__(self, db: Session):
        self.db = db
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=registry.get_gemini_tools()
        )

    def get_history(self, session_id: uuid.UUID, limit: int = 15) -> List[Dict[str, Any]]:
        statement = select(Message).where(Message.session_id == session_id).order_by(Message.created_at).limit(limit)
        messages = self.db.exec(statement).all()
        history = []
        for m in messages:
            role = "user" if m.role == "user" else "model"
            history.append({"role": role, "parts": [m.content]})
        return history

    def get_memory(self) -> str:
        statement = select(UserMemory)
        memories = self.db.exec(statement).all()
        return "\n".join([f"{m.key}: {m.value}" for m in memories])

    async def generate_response(self, session_id: uuid.UUID, prompt: str, file_data: Optional[Dict[str, Any]] = None):
        history = self.get_history(session_id)
        memory = self.get_memory()
        
        system_instruction = f"You are a helpful assistant powered by Gemini 2.5 Flash. User Preferences:\n{memory}"
        
        # Start chat with history
        chat = self.model.start_chat(history=history or [])
        
        # Save User Message
        user_msg = Message(session_id=session_id, role="user", content=prompt)
        self.db.add(user_msg)
        self.db.commit()

        yield "data: [START]\n\n"
        
        full_response = ""
        try:
            # Prepare parts for multimodal input
            content_parts = [prompt]
            if file_data:
                content_parts.append({
                    "mime_type": file_data["mime_type"],
                    "data": file_data["data"]
                })

            # First generation call
            response = chat.send_message(content_parts, stream=True)
            
            for chunk in response:
                # 1. Check if there are any candidates
                if not chunk.candidates:
                    continue
                
                # 2. Check if the content part exists
                candidate = chunk.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    continue

                # Handle Tool Calls
                part = candidate.content.parts[0]
                if part.function_call:
                    fn_call = part.function_call
                    tool_name = fn_call.name
                    tool_args = fn_call.args
                    
                    yield f"data: [TOOL_USE: {tool_name}]\n\n"
                    
                    # Execute Tool
                    tool_func = registry.tools[tool_name]["func"]
                    result = tool_func(**tool_args)
                    
                    # Send tool result back to Gemini
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": result}
                                )
                            )]
                        ),
                        stream=True
                    )
                    # Continue reading from the new stream
                    for tool_chunk in response:
                        if tool_chunk.candidates and tool_chunk.candidates[0].content.parts:
                            text = tool_chunk.text
                            full_response += text
                            yield f"data: {text}\n\n"
                else:
                    text = chunk.text
                    full_response += text
                    yield f"data: {text}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
        
        yield "data: [DONE]\n\n"
        
        # Save Assistant Message
        assistant_msg = Message(session_id=session_id, role="assistant", content=full_response)
        self.db.add(assistant_msg)
        self.db.commit()
