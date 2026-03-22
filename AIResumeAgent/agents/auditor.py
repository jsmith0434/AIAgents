from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from state import AgentState


class Evaluation(BaseModel):
    """The final assessment of the resume quality"""
    ProfessionalSummary: str = Field(description="A 3-line punchy summary tailored to the JD")
    TailoredSkills: str = Field(description="A comma-separated string of the 15 most relevant skills")
    AtsScore: int = Field(description="Score from 0-100 based on keyword match and relevance")
    IsSatisfactory: bool = Field(description="True if Score > 85, else False")
    Feedback: str = Field(description="Specific advice if IsSatisfactory is False")


def AuditorNode(state: AgentState) -> dict:
    print("--- AUDITOR AGENT: Final Review & Synthesis (Anthropic + Caching) ---")

    # 1. Initialize with Caching Beta Headers
    model = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0.3,
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    structured_model = model.with_structured_output(Evaluation)

    # 2. Construct Content Blocks
    message_content = [
        {
            "type": "text",
            "text": (
                "You are an expert Resume Editor. Evaluate if the selected bullets "
                "meet the Job Requirements. If the score is below 85, provide "
                "CRITICAL feedback on what skills or experiences are missing.\n\n"
                f"JOB REQUIREMENTS:\n{state['ExtractedRequirements']}"
            ),
            "cache_control": {"type": "ephemeral"}
        },
        {
            "type": "text",
            "text": f"SELECTED BULLETS FOR REVIEW:\n{state['SelectedBullets']}"
        }
    ]

    # 3. Invoke
    review = structured_model.invoke(message_content)

    # CRITICAL: We now return "Feedback" so it's stored in the state for the Librarian to read
    return {
        "ProfessionalSummary": review.ProfessionalSummary,
        "TailoredSkills": review.TailoredSkills,
        "IsSatisfactory": review.IsSatisfactory,
        "AtsEvaluationScore": review.AtsScore,
        "Feedback": review.Feedback  # This is the key addition
    }