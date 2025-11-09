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
    addMessage("System", "Connected to backend. LLM initializing...");
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
 * Handle server messages (init, response, error)
 */
function handleServerMessage(msg) {
  if (msg.type === "init") {
    // Initial auto-initialization message
    addMessage("You", "Create a calculator", "sent");
    addMessage("Assistant", msg.message, "received");
    renderUIState(msg.ui_state);
  } else if (msg.type === "response") {
    // Response to button clicks
    addMessage("Assistant", msg.message, "received");
    renderUIState(msg.ui_state);
  } else if (msg.type === "error") {
    // Error message
    addMessage("Error", msg.message, "error");
  }
}


/**
 * Render UI elements from state
 */
function renderUIState(uiState) {
  if (!uiState) {
    return;
  }

  // Render elements if provided
  if (!uiState.elements) {
    return;
  }

  // Create a map of all elements for quick lookup
  const elementMap = {};
  uiState.elements.forEach((elem) => {
    elementMap[elem.id] = elem;
  });

  // Clear previous UI elements
  if (elements.uiContainer) {
    elements.uiContainer.innerHTML = "";
    uiElements = {};
  }

  // Find and render root-level elements (those with no parent_id)
  uiState.elements.forEach((elem) => {
    if (!elem.parent_id) {
      renderElementAndChildren(elem, elements.uiContainer, elementMap);
    }
  });
}

/**
 * Render an element and its children recursively
 */
function renderElementAndChildren(elem, parentContainer, elementMap) {
  let domElement;

  if (elem.type === "text") {
    domElement = createTextElement(elem);
  } else if (elem.type === "button") {
    domElement = createButtonElement(elem);
  } else if (elem.type === "container") {
    domElement = createContainerElement(elem);
  }

  if (!domElement) {
    return;
  }

  // Add to parent container
  parentContainer.appendChild(domElement);
  uiElements[elem.id] = domElement;

  // If this is a container, render its children
  if (elem.type === "container") {
    Object.values(elementMap)
      .filter((child) => child.parent_id === elem.id)
      .forEach((child) => {
        renderElementAndChildren(child, domElement, elementMap);
      });
  }
}

/**
 * Create a text element (returns DOM element without adding to container)
 */
function createTextElement(elem) {
  const textDiv = document.createElement("div");
  textDiv.className = "ui-element ui-text";
  textDiv.id = `elem-${elem.id}`;
  textDiv.textContent = elem.properties.content;
  return textDiv;
}

/**
 * Create a button element (returns DOM element without adding to container)
 */
function createButtonElement(elem) {
  const button = document.createElement("button");
  button.className = "ui-element ui-button";
  button.id = `elem-${elem.id}`;
  button.textContent = elem.properties.label;
  const callbackId = elem.properties.callback_id;

  button.addEventListener("click", () => {
    console.log("Button clicked:", elem.id, "callback_id:", callbackId);
    sendButtonCallback(callbackId);
  });

  return button;
}

/**
 * Create a container element with flex layout (returns DOM element without adding to container)
 */
function createContainerElement(elem) {
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

  return container;
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
 * Initialize on page load
 */
document.addEventListener("DOMContentLoaded", () => {
  console.log("Page loaded, connecting to WebSocket");
  connectWebSocket();
});
