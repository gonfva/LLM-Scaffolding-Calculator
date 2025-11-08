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
  uiContainer: document.getElementById("ui-container"),
};

// Container for dynamically rendered UI elements
let uiElements = {};

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
    try {
      const msg = JSON.parse(event.data);
      handleServerMessage(msg);
    } catch (e) {
      console.error("Failed to parse message:", e);
      addMessage("Error", "Invalid message format", "error");
    }
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
 * Handle server messages (init, response, error)
 */
function handleServerMessage(msg) {
  if (msg.type === "init") {
    // Initial connection message
    addMessage("Assistant", msg.message, "received");
    renderUIState(msg.ui_state);
  } else if (msg.type === "response") {
    // Response to user message
    addMessage("Assistant", msg.message, "received");
    renderUIState(msg.ui_state);
  } else if (msg.type === "error") {
    // Error message
    addMessage("Error", msg.message, "error");
  }
}

/**
 * Apply theme to the UI
 */
function applyTheme(themeData) {
  if (!themeData || !themeData.variables) {
    console.log("No theme data to apply");
    return;
  }

  console.log("Applying theme:", themeData.name);

  // Apply CSS variables to the document root
  const root = document.documentElement;
  for (const [key, value] of Object.entries(themeData.variables)) {
    // Convert camelCase to kebab-case for CSS variables
    const cssVarName = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
    root.style.setProperty(cssVarName, value);
  }
}

/**
 * Render UI elements from state
 */
function renderUIState(uiState) {
  if (!uiState) {
    return;
  }

  // Apply theme if provided
  if (uiState.theme) {
    applyTheme(uiState.theme);
  }

  // Render elements if provided
  if (!uiState.elements) {
    return;
  }

  // Clear previous UI elements
  if (elements.uiContainer) {
    elements.uiContainer.innerHTML = "";
    uiElements = {};
  }

  // Render each element
  uiState.elements.forEach((elem) => {
    if (elem.type === "text") {
      renderTextElement(elem);
    } else if (elem.type === "button") {
      renderButtonElement(elem);
    } else if (elem.type === "container") {
      renderContainerElement(elem);
    }
  });
}

/**
 * Render a text element
 */
function renderTextElement(elem) {
  const textDiv = document.createElement("div");
  textDiv.className = "ui-element ui-text";
  textDiv.id = `elem-${elem.id}`;
  textDiv.textContent = elem.properties.content;

  // Apply layout properties
  if (elem.layout) {
    if (elem.layout.flex_grow !== undefined) {
      textDiv.style.flexGrow = elem.layout.flex_grow;
    }
    if (elem.layout.width) {
      textDiv.style.width = elem.layout.width;
    }
  }

  elements.uiContainer.appendChild(textDiv);
  uiElements[elem.id] = textDiv;
}

/**
 * Render a button element
 */
function renderButtonElement(elem) {
  const button = document.createElement("button");
  button.className = "ui-element ui-button";
  button.id = `elem-${elem.id}`;
  button.textContent = elem.properties.label;
  const callbackId = elem.properties.callback_id;

  // Apply layout properties
  if (elem.layout) {
    if (elem.layout.flex_grow !== undefined) {
      button.style.flexGrow = elem.layout.flex_grow;
    }
    if (elem.layout.width) {
      button.style.width = elem.layout.width;
    }
  }

  button.addEventListener("click", () => {
    console.log("Button clicked:", elem.id, "callback_id:", callbackId);
    sendButtonCallback(callbackId);
  });
  elements.uiContainer.appendChild(button);
  uiElements[elem.id] = button;
}

/**
 * Render a container element with flex layout
 */
function renderContainerElement(elem) {
  const container = document.createElement("div");
  container.className = "ui-element ui-container";
  container.id = `elem-${elem.id}`;

  // Apply flex layout properties
  if (elem.layout) {
    container.style.display = "flex";
    if (elem.layout.flex_direction) {
      container.style.flexDirection = elem.layout.flex_direction;
    }
    if (elem.layout.justify_content) {
      container.style.justifyContent = elem.layout.justify_content;
    }
    if (elem.layout.gap) {
      container.style.gap = elem.layout.gap;
    }
  }

  elements.uiContainer.appendChild(container);
  uiElements[elem.id] = container;
}

/**
 * Send button callback to server
 */
function sendButtonCallback(callbackId) {
  if (!callbackId || !ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }

  console.log("Sending button callback:", callbackId);
  addMessage("Client", `Button: ${callbackId}`, "sent");
  ws.send(
    JSON.stringify({
      type: "button_click",
      callback_id: callbackId,
    })
  );
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
