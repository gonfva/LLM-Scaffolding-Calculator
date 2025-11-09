# LLM-Scaffolding Calculator

A proof-of-concept calculator built with Claude AI as the architect, dynamically generating the UI through tool calls. Explores a new paradigm where LLMs design and maintain interfaces rather than just responding to text queries.

"LLM-Scaffolded Interaction" Emphasizes that the LLM builds the structure/scaffold, then the client executes it.

## Development Setup

### Prerequisites
- Python 3.11+
- pip

### Initial Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

Start the FastAPI backend server:
```bash
python -m uvicorn src.app.main:app --reload
```

The app will be available at `http://127.0.0.1:8000/`
- Main UI: `http://127.0.0.1:8000/` (connects via WebSocket)
- Health check: `http://127.0.0.1:8000/health`

### Testing & Code Quality

**Run tests:**
```bash
pytest                    # Run all tests
pytest -v               # Verbose output
pytest tests/test_agent.py  # Run specific test file
```

**Format code:**
```bash
black src/ tests/
```

**Lint code:**
```bash
ruff check src/ tests/
```

**Type check:**
```bash
mypy src/
```

**Run all checks (format, lint, type check):**
```bash
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Project Structure

```
.
├── src/
│   ├── agent/                    # Agent and UI state management
│   │   ├── claude_agent.py       # Claude agent with tool use
│   │   ├── tool_executor.py      # Tool execution engine
│   │   ├── ui_state.py           # UI state management
│   │   └── tools.py              # Tool definitions
│   ├── app/
│   │   └── main.py               # FastAPI app & WebSocket endpoint
│   ├── config.py                 # Configuration (API key loading)
│   └── static/                   # Frontend assets
│       ├── index.html            # Main UI with CSS
│       └── client.js             # WebSocket client & UI renderer
├── tests/                        # Test suite (72 tests)
│   ├── test_*.py                 # Various test modules
│   └── conftest.py               # Pytest configuration
├── LICENSE                       # MIT License
├── README.md                     # This file
├── CLAUDE.md                     # Design vision document
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Linting/formatting config
└── .env                          # Environment variables (git-ignored)
```

## Architecture Overview

The application implements an **agentic UI pattern** where Claude AI dynamically builds and maintains the user interface:

```
┌─────────────────────┐
│  Claude (LLM)       │ ← Architect: Designs UI and interactions
├─────────────────────┤
│  Backend (FastAPI)  │ ← Mediator: Routes messages, executes tools
├─────────────────────┤
│  Client (JS)        │ ← Executor: Renders UI, handles interactions
└─────────────────────┘
```

**Key Features:**
- **Decoupled Concerns:** WebSocket connection → background LLM init → message processing
- **Tool-Based UI:** Claude uses tools (`display_text`, `create_button`, `create_container`, `update_element`) to build UI dynamically
- **Grid & Flexbox Layouts:** CSS Grid for structured layouts (calculators), Flexbox for responsive design
- **Message Queueing:** Button clicks during LLM processing are queued and processed in order
- **Processing Feedback:** Visual indicator (yellow "Processing..." status) shows when backend is busy
- **Real-Time Sync:** WebSocket keeps client and server state synchronized

See `CLAUDE.md` for the design philosophy and vision.
