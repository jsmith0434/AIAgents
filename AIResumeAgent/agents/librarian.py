from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from typing import List
from state import AgentState


class SelectedBullets(BaseModel):
    """The structured output for bullet selection"""
    InstructureBullets: List[str] = Field(description="Top 4-5 relevant bullets for Instructure")
    CensusBullets: List[str] = Field(description="Top 4-5 relevant bullets for Census Bureau")
    AmazonBullets: List[str] = Field(description="Top 3-4 relevant bullets for Amazon")
    UnifyBullets: List[str] = Field(description="Top 2 relevant bullets for Unify")


def LibrarianNode(state: AgentState) -> dict:
    # 1. Check for previous feedback to guide the retry
    feedback = state.get("Feedback", "No previous feedback provided.")
    is_retry = state.get("RetryCount", 0) > 0

    if is_retry:
        print(f"--- LIBRARIAN AGENT: Retrying based on Feedback: {feedback} ---")
    else:
        print("--- LIBRARIAN AGENT: Selecting Best Evidence (First Pass) ---")

    # 2. Initialize with Caching Beta Headers
    model = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0.1 if is_retry else 0,  # Slight jitter on retry to explore new bullets
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    structured_model = model.with_structured_output(SelectedBullets)

    # 3. Construct the Cached Message
    retry_instruction = f"\n\nPREVIOUS FEEDBACK TO ADDRESS: {feedback}" if is_retry else ""

    message_content = [
        {
            "type": "text",
            "text": f"MASTER RESUME DATA:\n{state['MasterResumeMarkdown']}",
            "cache_control": {"type": "ephemeral"}
        },
        {
            "type": "text",
            "text": (
                f"JOB REQUIREMENTS:\n{state['ExtractedRequirements']}\n\n"
                "TASK: Select the most relevant bullets from the Master Resume above. "
                "Prioritize bullets with #Tags matching the requirements. "
                f"Ensure technical accuracy.{retry_instruction}"
            )
        }
    ]

    # 4. Invoke and update retry count
    selections = structured_model.invoke(message_content)
    new_retry_count = state.get("RetryCount", 0) + 1

    return {
        "SelectedBullets": selections.dict(),
        "RetryCount": new_retry_count
    }