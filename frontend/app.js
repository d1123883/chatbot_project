const API_BASE = "http://localhost:8000";
let currentSessionId = null;
let abortController = null;

const sessionList = document.getElementById('session-list');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const abortBtn = document.getElementById('abort-btn');

// Initial Load
window.addEventListener('DOMContentLoaded', loadSessions);

async function loadSessions() {
    const res = await fetch(`${API_BASE}/sessions`);
    const sessions = await res.json();
    sessionList.innerHTML = '';
    sessions.forEach(session => {
        const div = document.createElement('div');
        div.className = 'session-item';
        div.innerText = session.title;
        div.onclick = () => selectSession(session.id, session.title);
        sessionList.appendChild(div);
    });
}

newChatBtn.onclick = async () => {
    const title = prompt("Enter Chat Title:", "New Chat");
    if (!title) return;
    const res = await fetch(`${API_BASE}/sessions?title=${encodeURIComponent(title)}`, { method: 'POST' });
    const session = await res.json();
    loadSessions();
    selectSession(session.id, session.title);
};

async function selectSession(id, title) {
    currentSessionId = id;
    document.getElementById('current-chat-title').innerText = title;
    chatMessages.innerHTML = '';
    
    const res = await fetch(`${API_BASE}/sessions/${id}/messages`);
    const messages = await res.json();
    messages.forEach(msg => appendMessage(msg.role, msg.content));
}

function appendMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerText = content;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

sendBtn.onclick = async () => {
    const text = userInput.value.trim();
    if (!text || !currentSessionId) return;

    userInput.value = '';
    appendMessage('user', text);

    const aiMsgDiv = appendMessage('assistant', '...');
    let aiContent = "";

    abortController = new AbortController();
    abortBtn.disabled = false;

    try {
        const response = await fetch(`${API_BASE}/chat/stream?session_id=${currentSessionId}&prompt=${encodeURIComponent(text)}`, {
            method: 'POST',
            signal: abortController.signal
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split("\n\n");
            
            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const data = line.replace("data: ", "");
                    if (data === "[START]") {
                        aiContent = "";
                    } else if (data === "[DONE]") {
                        // Finished
                    } else {
                        aiContent += data;
                        aiMsgDiv.innerText = aiContent;
                    }
                }
            }
        }
    } catch (err) {
        if (err.name === 'AbortError') {
            aiMsgDiv.innerText += " (Stopped)";
        } else {
            console.error(err);
        }
    } finally {
        abortBtn.disabled = true;
        abortController = null;
    }
};

abortBtn.onclick = () => {
    if (abortController) {
        abortController.abort();
    }
};

// Auto-expand textarea
userInput.oninput = () => {
    userInput.style.height = 'auto';
    userInput.style.height = (userInput.scrollHeight) + 'px';
};
