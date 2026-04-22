import os
import json
from typing import List, Dict, Any, Callable
from .models import Message, UserMemory
from sqlmodel import Session, select

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

registry = ToolRegistry()

# Example Tool: Calculator
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
        # Warning: eval is used for demo, use a safer math parser in production
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error: {str(e)}"

class AIAgent:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = os.getenv("OPENAI_API_KEY")

    def get_history(self, session_id: str, limit: int = 15) -> List[Dict[str, str]]:
        statement = select(Message).where(Message.session_id == session_id).order_by(Message.created_at).limit(limit)
        messages = self.db.exec(statement).all()
        return [{"role": m.role, "content": m.content} for m in messages]

    def get_memory(self) -> str:
        statement = select(UserMemory)
        memories = self.db.exec(statement).all()
        return "\n".join([f"{m.key}: {m.value}" for m in memories])

    async def generate_response(self, session_id: str, prompt: str):
        history = self.get_history(session_id)
        memory = self.get_memory()
        
        system_prompt = f"You are a helpful assistant. User Preferences:\n{memory}"
        
        # In a real implementation, you'd call OpenAI/Anthropic SDK here
        # For this demo, we'll yield a mock stream
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": prompt}]
        
        # Save User Message
        user_msg = Message(session_id=session_id, role="user", content=prompt)
        self.db.add(user_msg)
        self.db.commit()

        # Mock Streaming Result
        yield "data: [START]\n\n"
        for word in ["Thinking", "...", " This", " is", " a", " response", " to", f" '{prompt}'"]:
            yield f"data: {word}\n\n"
        yield "data: [DONE]\n\n"
        
        # Save Assistant Message (Final)
        full_content = f"Response to '{prompt}'"
        assistant_msg = Message(session_id=session_id, role="assistant", content=full_content)
        self.db.add(assistant_msg)
        self.db.commit()
