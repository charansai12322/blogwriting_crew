"""
Blog Writing Crew - Core Agent Definitions and Execution Logic

Preserved directly from blog_crew.ipynb:
- Agents: content_strategist, blog_writer, editor
- Tasks: task_plan, task_write, task_edit
- Process: sequential execution
- Model: gemini/gemini-3.5-flash (configurable via GEMINI_MODEL env var)
- Key resolution: Google Colab userdata ('sec1') or GEMINI_API_KEY/SEC1 environment variable
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Ensure both repository root and backend directory are in sys.path
_current_dir = Path(__file__).resolve().parent
_repo_root = _current_dir.parent
for _p in [str(_repo_root), str(_current_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Load local environment variables from backend/.env or repo root .env
_backend_env = _current_dir / ".env"
_root_env = _repo_root / ".env"
if _backend_env.exists():
    load_dotenv(dotenv_path=_backend_env)
if _root_env.exists():
    load_dotenv(dotenv_path=_root_env)
load_dotenv()


def get_gemini_api_key() -> str:
    """
    Retrieve Gemini API key.
    Checks Google Colab userdata ('sec1') first to preserve notebook compatibility,
    then falls back to environment variables (GEMINI_API_KEY, SEC1, GOOGLE_API_KEY).
    """
    # 1. Check Google Colab Secrets (userdata) if in Colab environment
    try:
        from google.colab import userdata  # type: ignore
        key = userdata.get("sec1")
        if key:
            return key
    except (ImportError, Exception):
        pass

    # 2. Check environment variables
    key = os.getenv("GEMINI_API_KEY") or os.getenv("SEC1") or os.getenv("GOOGLE_API_KEY")
    if key and key.strip():
        return key.strip()

    raise ValueError(
        "Gemini API key not configured. Please set the GEMINI_API_KEY environment variable "
        "in your backend .env file or server environment (or secret 'sec1' in Google Colab)."
    )


def get_model_name() -> str:
    """
    Get the configured Gemini model name.
    Preserves default from notebook: 'gemini/gemini-3.5-flash'.
    Can be overridden via GEMINI_MODEL.
    """
    return os.getenv("GEMINI_MODEL", "gemini/gemini-3.5-flash").strip()


def build_blog_crew():
    """
    Factory function to construct fresh Agent, Task, and Crew instances
    per execution request, preventing concurrency race conditions or state pollution.
    All prompts, backstories, and roles are strictly preserved from the notebook.
    """
    from crewai import Agent, LLM, Task, Crew, Process

    api_key = get_gemini_api_key()
    model = get_model_name()

    llm = LLM(
        model=model,
        api_key=api_key
    )

    # Agent 1: content_strategist
    content_strategist = Agent(
        role="content_strategist",
        goal="Come up with engaging, well-structured blog post ideas and outlines based on user topic",
        backstory=(
            "You are an experienced content strategist."
            "You excel at turning vague topics into clear, compelling blog post plans including:"
            "- catchy title, hook, and key sections"
            "- target audience and tone"
            "- SEO-friendly structure"
            "Keep it focused enough to write as a single, complete blog post."
        ),
        verbose=True,
        llm=llm,
    )

    # Agent 2: blog_writer
    blog_writer = Agent(
        role="blog_writer",
        goal="Write a complete, engaging, and well-formatted blog post based on the content plan",
        backstory=(
            "You are a senior content writer specialized in creating engaging blog posts."
            "You write structured, readable content with:"
            "- Compelling introduction with a hook"
            "- Well-organized sections with subheadings"
            "- Examples, analogies, and actionable takeaways"
            "You always produce a complete, publish-ready blog post."
        ),
        verbose=True,
        llm=llm,
    )

    # Agent 3: editor
    editor = Agent(
        role="editor",
        goal="Review, edit, and polish the blog post for grammar, clarity, and engagement",
        backstory=(
            "You are a meticulous editor and proofreader."
            "You carefully check:"
            "- Grammar, spelling, and punctuation errors"
            "- Does the content match the planned outline?"
            "- Is the tone consistent and engaging throughout?"
            "- Flow, readability, and transitions between sections"
            "Suggest improvements and output the FINAL polished blog post."
        ),
        verbose=True,
        llm=llm,
    )

    # Task 1: task_plan
    task_plan = Task(
        description=(
            "Take the user's blog topic: {blog_topic}"
            "1. Clarify and expand it into an engaging blog post plan"
            "2. Describe: title, target audience, tone, key sections"
            "3. Keep scope focused (one main idea, 5-7 sections)"
            "Output format:"
            "## Blog Post Plan"
            "- Title: ..."
            "- Target Audience: ..."
            "- Tone: ..."
            "- Hook: ..."
            "- Sections: ..."
            "- Key Takeaways: ..."
        ),
        expected_output="A clear markdown Blog post plan ",
        agent=content_strategist
    )

    # Task 2: task_write
    task_write = Task(
        description=(
            "Using the blog post plan from the previous task"
            "Write a COMPLETE, publish-ready blog post."
            "- Include a compelling title and introduction"
            "- Use subheadings for each section"
            "- Add examples, analogies, or data points where relevant"
            "- End with a strong conclusion and call-to-action"
            "- Final answer MUST be ONLY the complete blog post in markdown format"
        ),
        expected_output="A complete, well-formatted blog post in markdown",
        agent=blog_writer
    )

    # Task 3: task_edit
    task_edit = Task(
        description=(
            "Review the blog post from the previous task."
            "1. Check for grammar, spelling, and punctuation errors"
            "2. Verify it matches the content plan"
            "3. Check flow, readability, and tone consistency"
            "4. Suggest fixes/improvements if needed"
            "5. Output the FINAL, polished, publish-ready blog post"
            "Your final answer MUST be ONLY the complete blog post in markdown format"
        ),
        expected_output="Final polished, publish-ready blog post in markdown",
        agent=editor
    )

    blog_crew = Crew(
        agents=[content_strategist, blog_writer, editor],
        tasks=[task_plan, task_write, task_edit],
        process=Process.sequential,
        verbose=True
    )

    return blog_crew


async def run_blog_crew(topic: str) -> Dict[str, Any]:
    """
    Executes the crew asynchronously with the given blog topic.
    Returns the resulting blog content and metadata.
    """
    crew = build_blog_crew()
    result = await crew.kickoff_async(
        inputs={"blog_topic": topic}
    )

    # Extract raw output string
    raw_output = str(result.raw if hasattr(result, "raw") else result)

    # Calculate word and character count
    word_count = len(raw_output.split())
    char_count = len(raw_output)

    return {
        "blog_markdown": raw_output,
        "model": get_model_name(),
        "stats": {
            "word_count": word_count,
            "char_count": char_count
        }
    }
