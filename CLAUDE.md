+ I want to build a calculator using a new paradigm of UI interaction mode.
+ The usual way is a frontend built upfront interacting with a backend (or sometimes even no backends)
+ The new paradigm is based on a running backend server. The backend server contains a loop with a claude agent that interacts on one side with Claude (LLM) itself, and on the other with whatever the user acts upon the existing UI.
+ To avoid constant reloading of the page, we want to leverage Websockets
+ When the user visits the page for the first time, there is not yet anything on the UI. So either directly, or maybe the agent would need send the Websockets scaffold to keep sending and receiving things from/to the backend.
+ I imagine that on the agent we would come with some primitives (like window, button and text) that would be offered to Claude (LLM) as tools. Claude(LLM) would use those tools to send/interact with the UI.
+ I envision the interaction in the following way

```
┌─────────────────────────────────────────────────┐
│ LLM (Architect)                                 │
│ - Understands user intent                       │
│ - Designs UI structure                          │
│ - Defines interaction rules                     │
└────────────┬────────────────────────────────────┘
             │
             │ Tool Calls (JSON)
             ▼
┌─────────────────────────────────────────────────┐
│ Backend (Mediator)                              │
│ - Validates tool calls                          │
│ - Manages session state                         │
│ - Routes significant events back to LLM         │
└────────────┬────────────────────────────────────┘
             │
             │ Rendering Instructions
             ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│ Client (Executor)                                                                  │
│ - Renders UI from tool calls                                                       │
│ - Maybe executes behaviors locally (fast loop, not initially, optimization later)  │
│ - Notifies backend only for significant events                                     │
└────────────────────────────────────────────────────────────────────────────────────┘
```


+ Although the main objective is to focus in the new UI interaction model, the code for the backend needs to be properly tested, linted and formatted.
+ For the backend we will use python and FastAPI.
+ When there is ambiguity building the backend code, feel free to ask me.
+ Similarly, when I'm asking something that doesn't quite make sense, or you think there is a different approach, please challenge me
+ Please don't implement things in one go. Even if we both know the destination (what we want to achieve), I don't want to have a bunch of code in one go.
