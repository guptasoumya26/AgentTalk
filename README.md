# 🤖 AgentTalk - Multi-Agent Collaboration Platform

A real-time AI collaboration platform where multiple AI agents work together to build applications and discuss complex topics. Watch agents think, code, and collaborate in real-time with stunning visualizations!

## 🎯 Project Overview

AgentTalk uses a **Hub-and-Spoke** architecture with **real-time streaming** where an orchestrator coordinates communication between different AI models. Experience true multi-agent collaboration with:

- **ChatGPT** (gpt-3.5-turbo) - Product Manager & Architect
- **Gemini** (gemini-2.5-flash) - Full-Stack Developer
- **Groq** (llama-3.3-70b-versatile) - QA Engineer & Tester

## ✨ Key Features

### 🔴 Real-Time Streaming
- **Live updates** as agents think and respond
- **Animated "Thinking..." indicators** for each agent
- No waiting - see responses as they're generated
- Smooth, ChatGPT-like experience

### 🎨 Interactive Visualizations
- **Animated agent panel** showing which agent is active
- **Bouncing animations** when agents are thinking
- **Pulsing rings** around active agents
- **Data packets** flowing between agents
- **Real-time status updates**

### 💬 Smart Message Display
- **Auto-collapse** for long messages (>10 lines or >800 chars)
- **"Show more/less"** buttons for better readability
- **Collapsible code blocks** with syntax highlighting
- **Gradient fades** for collapsed content
- **Completion confirmations** when workflows finish

### 🚀 Two Collaboration Modes

**1. Sequential Workflow** - Agents build together:
- ChatGPT creates technical specifications
- Gemini writes actual code (HTML, JS, Python)
- Groq reviews code and suggests test cases
- System confirms completion

**2. Round-Robin Discussion** - Agents debate:
- Multiple rounds of back-and-forth
- Each agent adds their perspective
- Perfect for exploring different approaches

### 🎯 Smart UI Features
- **Responsive design** (mobile-friendly)
- **No layout breaking** with long responses
- **Word wrapping** and proper overflow handling
- **Smooth scrolling** and animations
- **Clean, modern interface**

## 🚀 Quick Start

### 1. Activate Virtual Environment

```bash
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Edit `config.properties` and add your API keys:

```properties
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
```

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys ($5 free credits)
- **Google Gemini**: https://ai.google.dev/ (**100% FREE!**)
- **Groq**: https://console.groq.com/ (**100% FREE & SUPER FAST!**)

> **Note**: You need at least ONE API key. The system works with whatever you configure!

### 4. Run the Application

```bash
python app.py
```

Open browser to: **http://localhost:5000**

## 📁 Project Structure

```
AgentTalk/
├── backend/
│   ├── agents.py           # ChatGPT, Gemini & Groq implementations
│   ├── orchestrator.py     # Streaming hub-and-spoke coordinator
│   └── config_loader.py    # API key management
├── frontend/
│   ├── templates/
│   │   └── index.html      # Main UI with animation panel
│   └── static/
│       ├── style.css       # Modern styling + animations
│       └── app.js          # Streaming logic + visualizations
├── app.py                  # Flask server with SSE endpoints
├── requirements.txt        # Python dependencies
├── config.properties       # Your API keys go here
└── venv/                   # Virtual environment (pre-created)
```

## 🎮 How to Use

### Sequential Workflow (Code Generation)

1. Click **"Sequential Workflow"** tab
2. Enter: `"Build a calculator app with dark mode"`
3. Click **"Start Workflow"**
4. Watch the magic:
   - Left panel shows active agent with animations
   - ChatGPT creates technical spec
   - Gemini writes actual code
   - Groq reviews and suggests tests
   - System confirms completion
5. Long responses auto-collapse with "Show more" buttons

### Round-Robin Discussion

1. Click **"Round-Robin Discussion"** tab
2. Enter: `"Best practices for REST API design"`
3. Select rounds (1-3)
4. Click **"Start Discussion"**
5. Watch agents debate and build on each other's ideas

## 🏗️ Architecture: Streaming Hub-and-Spoke

```
┌──────────────────────────────────────────────┐
│      ORCHESTRATOR (Flask + SSE)              │
│  - Real-time streaming responses             │
│  - Maintains conversation history            │
│  - Controls agent execution order            │
│  - Passes full context to each agent         │
└───────┬──────────────┬─────────────┬─────────┘
        │              │             │
        ▼              ▼             ▼
   ┌────────┐     ┌─────────┐   ┌──────┐
   │ChatGPT │     │ Gemini  │   │ Groq │
   │   PM   │     │Full-Stack│  │  QA  │
   └────────┘     └─────────┘   └──────┘
```

### Key Design Principles

1. **Real-Time Streaming**: Server-Sent Events (SSE) for live updates
2. **Single Source of Truth**: Orchestrator maintains all state
3. **No Direct Communication**: Agents only interact through orchestrator
4. **Full Context**: Each agent gets complete conversation history
5. **Sequential Execution**: One agent at a time (prevents overwrites)
6. **Visual Feedback**: Animated UI shows exactly what's happening

### What Makes This Special

✅ **Real multi-agent collaboration** (not just sequential API calls)
✅ **Live streaming updates** (like ChatGPT, not batch responses)
✅ **Visual animations** (see which agent is working)
✅ **Actual code generation** (not just descriptions)
✅ **Smart UI** (auto-collapsing, proper formatting)
✅ **Cost-effective** (works with free tiers)

## 🔧 Customization

### Add More Agents

Edit `backend/orchestrator.py` to include more models:

```python
# Add in _initialize_agents method
if self.config.get('MISTRAL_API_KEY'):
    self.agents['mistral'] = MistralAgent(...)
```

### Change Agent Roles

In `backend/agents.py`:

```python
# Change Gemini's role
super().__init__("Gemini", "DevOps Engineer", model)
```

### Adjust Message Length

In `backend/agents.py`:

```python
max_tokens=1000  # Change from 1000 to whatever you need
```

### Modify Collapse Threshold

In `frontend/static/app.js`:

```javascript
const shouldCollapse = lineCount > 10 || message.length > 800;
// Change these numbers to adjust collapse behavior
```

## 📝 License

MIT License
