/**
 * WebSocket client for Agentic Calculator
 * Handles connection, messaging, and UI updates
 */

let ws = null;
const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const wsUrl = `${protocol}//${window.location.host}/ws`;

const elements = {
  status: document.getElementById("status"),
  statusText: document.getElementById("status-text"),
  messages: document.getElementById("messages"),
  input: document.getElementById("input"),
  sendBtn: document.getElementById("send-btn"),
};

/**
 * Initialize WebSocket connection
 */
function connectWebSocket() {
  console.log("Connecting to WebSocket...", wsUrl);

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WebSocket connected");
    updateStatus(true);
    elements.input.disabled = false;
    elements.sendBtn.disabled = false;
    addMessage("System", "Connected to backend");
  };

  ws.onmessage = (event) => {
    console.log("Message received:", event.data);
    addMessage("Server", event.data, "received");
  };

  ws.onerror = (event) => {
    console.error("WebSocket error:", event);
    addMessage("System", "WebSocket error occurred", "error");
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected");
    updateStatus(false);
    elements.input.disabled = true;
    elements.sendBtn.disabled = true;
    addMessage("System", "Disconnected from backend");
  };
}

/**
 * Update connection status display
 */
function updateStatus(connected) {
  if (connected) {
    elements.status.classList.remove("disconnected");
    elements.status.classList.add("connected");
    elements.statusText.textContent = "Connected";
  } else {
    elements.status.classList.remove("connected");
    elements.status.classList.add("disconnected");
    elements.statusText.textContent = "Disconnected";
  }
}

/**
 * Add message to message log
 */
function addMessage(source, text, type = "info") {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${type}`;
  const timestamp = new Date().toLocaleTimeString();
  messageDiv.textContent = `[${timestamp}] ${source}: ${text}`;
  elements.messages.appendChild(messageDiv);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

/**
 * Send message to server
 */
function sendMessage() {
  const text = elements.input.value.trim();
  if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }

  console.log("Sending message:", text);
  addMessage("Client", text, "sent");
  ws.send(text);
  elements.input.value = "";
  elements.input.focus();
}

/**
 * Handle Enter key in input field
 */
elements.input.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

/**
 * Initialize on page load
 */
document.addEventListener("DOMContentLoaded", () => {
  console.log("Page loaded, connecting to WebSocket");
  connectWebSocket();
});
