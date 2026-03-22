
# 📝 AI agents to customize your resume

An automated, multi-agent pipeline designed to analyze job descriptions and perfectly tailor a LaTeX resume. This system uses **Claude 3.5 Sonnet** with **Prompt Caching** to minimize costs during iterative refinement loops.

## 🚀 The Multi-Agent Workflow

The system follows a "State Machine" logic where data is passed between specialized AI agents:

1.  **Analyst Agent**: Extracts core tech stacks and soft skills from a raw Job Description.
2.  **Librarian Agent**: Searches the `master_resume.md` and selects the most relevant "evidence" (bullets) for each previous role.
3.  **Auditor Agent**: Grades the selection (0-100). If the score is **< 85**, it provides critical feedback and triggers a **Retry Loop**.
4.  **Compiler Agent**: Sanitizes data for LaTeX compatibility and renders the final `.tex` file using Jinja2 templates.



---

## 🛠️ Project Structure

```text
AIResumeAgent/
├── agents/
│   ├── analyst.py    # JD analysis & requirement extraction
│   ├── librarian.py  # Evidence selection from master resume
│   ├── auditor.py    # Scoring, summary generation, and feedback
│   └── compiler.py   # LaTeX rendering engine
├── data/
│   ├── master_resume.md   # Your full career history (Markdown)
│   └── AgentTemplate.tex  # LaTeX skeleton with Jinja2 delimiters
├── output/
│   └── tailored_resume.tex # The final generated resume
├── main.py           # LangGraph orchestration & entry point
├── state.py          # Pydantic & TypedDict state definitions
├── utils.py          # LaTeX escaping & sanitization logic
└── .env              # Anthropic API Key
```

---

## ⚙️ Setup & Installation

1.  **Clone the Repository** and navigate to the folder.
2.  **Install Dependencies**:
    ```bash
    pip install langgraph langchain-anthropic jinja2 python-dotenv
    ```
3.  **Configure Environment**: Create a `.env` file in the root directory:
    ```text
    ANTHROPIC_API_KEY=your_api_key_here
    ```
4.  **Prepare Data**: 
    * Ensure your `data/master_resume.md` is populated.
    * Ensure `data/AgentTemplate.tex` is present.

---

## 🏃 Usage

1.  Open `main.py`.
2.  Paste the Job Description you are targeting into the `sample_jd` variable.
3.  Run the pipeline:
    ```bash
    python main.py
    ```
4.  The system will print the progress of each agent to the console. Once a score of **85%+** is reached, your tailored resume will be available in `output/tailored_resume.tex`.

---

## 💡 Key Features

* **Prompt Caching**: Uses Anthropic’s ephemeral caching to store the Master Resume and JD Requirements, reducing token costs by up to 90% during retries.
* **Automatic Sanitization**: `utils.py` automatically converts common copy-paste "breakers" (like smart quotes, em-dashes, and `#` symbols) into LaTeX-safe code.
* **Self-Correction**: The Auditor agent acts as a quality gate, forcing the Librarian to reconsider its choices if they don't align with the JD requirements.
