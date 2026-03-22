from langchain_anthropic import ChatAnthropic
from state import JobAnalysis, AgentState

def AnalystNode(state: AgentState) -> dict:
    # 1. Initialize the model with the Beta Header for Caching
    model = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0,
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )

    # 2. Bind the Pydantic tool
    structured_model = model.with_structured_output(JobAnalysis)

    print("--- ANALYST AGENT: Extracting JD Requirements (Anthropic + Caching) ---")

    # 3. Use a list of blocks to apply the cache breakpoint
    # We cache the instructions so subsequent JD analyses are cheaper
    message_content = [
        {
            "type": "text",
            "text": "You are an expert Technical Recruiter. Analyze the following Job Description and extract the core requirements into the specified schema.",
            "cache_control": {"type": "ephemeral"} # This saves the instruction in cache
        },
        {
            "type": "text",
            "text": f"Job Description: {state['RawJobDescription']}"
        }
    ]

    extracted_data = structured_model.invoke(message_content)

    return {"ExtractedRequirements": extracted_data}