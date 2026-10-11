# Blog Writing Crew

A multi-agent AI blog generation application powered by **CrewAI**, **Google Gemini**, **FastAPI**, and **React + TypeScript (Vite)**.

Originally prototyped in Google Colab (`blog_crew.ipynb`), this repository now features a production-ready, clean full-stack architecture connecting a modern web frontend to the three-agent editorial crew.

---

## 🏛 Architecture & Workflow

The core multi-agent system uses a sequential CrewAI pipeline with three specialized agents:

```
[ User Topic Input ]
         │
         ▼
[ 1. Content Strategist ] ──► Formulates outline, hook, target audience, and 5-7 key sections
         │
         ▼
[ 2. Blog Writer ]        ──► Drafts complete, publish-ready long-form blog post in Markdown
         │
         ▼
[ 3. Editor ]             ──► Proofreads, refines grammar, tone, flow, and outputs final Markdown
         │
         ▼
[ FastAPI Backend ]       ──► Returns structured JSON with blog Markdown & metadata
         │
         ▼
[ React Frontend ]        ──► Formats blog article, allows copying, downloading (.md), and resets
```

---

## 📁 Project Directory Structure

```
blogwriting_crew-1/
├── .gitignore               # Excludes secrets (.env), virtualenvs (.venv), and build artifacts
├── README.md                # Full setup and architecture documentation
├── blog_crew.ipynb          # Original Google Colab notebook (strictly preserved)
│
├── backend/
│   ├── __init__.py
│   ├── agent.py             # Preserved CrewAI agents, tasks, and Colab/local key adapter
│   ├── main.py              # FastAPI application (endpoints: /health, /api/generate)
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Template for backend environment variables
│
└── frontend/
    ├── index.html           # HTML5 entry with Inter font & SEO meta tags
    ├── package.json         # React 19, Vite, Lucide icons, React Markdown
    ├── .env.example         # Template for VITE_API_BASE_URL
    ├── src/
    │   ├── App.tsx          # Main interactive interface & state management
    │   ├── App.css          # Modern dark-mode styling & article typography
    │   ├── index.css        # Theme variables & base layout
    │   ├── api.ts           # Type-safe API client
    │   └── types.ts         # TypeScript data contracts
    └── dist/                # Production build output
```

---

## 🔑 API Key & Secret Management

In the original Google Colab notebook, credentials were read from Colab Secrets:
```python
from google.colab import userdata
gemini_api_key = userdata.get('sec1')
```

### Local Windows & Deployment Adaptation:
1. `backend/agent.py` automatically checks for `google.colab` userdata first (preserving notebook behavior).
2. When executed locally or on an external server outside Colab, it falls back to the `GEMINI_API_KEY` (or `SEC1` / `GOOGLE_API_KEY`) environment variable.
3. **Never hardcode or commit API keys**. Configure your key in `backend/.env`.

---

## 🚀 Running the Application on Windows

### Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** & npm

---

### Step 1: Configure Backend Environment

1. In `backend/`, copy `.env.example` to `.env`:
   ```powershell
   Copy-Item backend\.env.example backend\.env
   ```
2. Open `backend\.env` and paste your Google Gemini API key:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_gemini_api_key...
   GEMINI_MODEL=gemini/gemini-3.5-flash
   PORT=8000
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```
   *(Note: You can get a free API key at [Google AI Studio](https://aistudio.google.com/)).*

---

### Step 2: Set Up & Run the Backend

Open a PowerShell terminal in the repository root:

1. **Activate virtual environment** (or create one if needed):
   ```powershell
   # If .venv is already present:
   .\.venv\Scripts\Activate.ps1

   # Or if installing freshly:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend/requirements.txt
   ```

2. **Start the FastAPI backend server**:
   ```powershell
   .\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
   ```
   The backend will start at: `http://localhost:8000`

3. **Verify the Health Endpoint**:
   Open a browser or run in PowerShell:
   ```powershell
   curl http://localhost:8000/health
   ```
   Expected response:
   ```json
   {
     "status": "ok",
     "message": "Blog Writing Crew backend is running and ready.",
     "model": "gemini/gemini-3.5-flash",
     "agents": ["content_strategist", "blog_writer", "editor"]
   }
   ```

---

### Step 3: Run the Frontend

Open a second PowerShell terminal in `frontend/`:

1. **Navigate to the frontend directory**:
   ```powershell
   cd frontend
   ```

2. **Start the Vite development server**:
   ```powershell
   npm run dev
   ```

3. **Open the App**:
   Visit **`http://localhost:5173`** in your browser.

---

## 🧪 Testing Blog Generation

1. On the frontend (`http://localhost:5173`), confirm the backend indicator displays **Online**.
2. Type a topic (e.g., `How AI agents are transforming software development`) or click one of the suggested sample chips.
3. Click **Generate Blog**.
4. The 3-agent pipeline runs sequentially:
   - Content Strategist outlines key takeaways.
   - Blog Writer generates full Markdown body.
   - Editor reviews grammar, coherence, and flow.
5. The final blog will render in the article reader. Use **Copy Blog** or **Download .md** to save your post.

---

## 🔒 Security & Concurrency Guarantees

- **No Secret Leaks**: The frontend never receives or handles API keys.
- **Sanitized Errors**: Backend catches failures and returns clean HTTP error messages without leaking secrets or server filepaths.
- **Concurrency Safety**: An `asyncio.Lock` guards crew kickoff to prevent overlapping requests from corrupting agent memory or exceeding LLM rate limits.
- **Type Safety**: Pydantic schemas enforce payload integrity, and TypeScript ensures strict API contract compliance.