import os
import sys
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from state import AgentState

# Import your nodes
from agents.analyst import AnalystNode
from agents.librarian import LibrarianNode
from agents.auditor import AuditorNode
from agents.compiler import CompilerNode


# 1. PRE-FLIGHT VALIDATION
def pre_flight_check(master_resume: str):
    """Ensures the environment and data are ready for the pipeline."""
    print("--- PRE-FLIGHT CHECK: Validating Inputs ---")

    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY not found in .env file.")
        sys.exit(1)

    if len(master_resume.strip()) < 100:
        print("ERROR: Master Resume is too short or empty. Check data/master_resume.md.")
        sys.exit(1)

    if not os.path.exists("data/AgentTemplate.tex"):
        # Note: I updated this to match your folder structure image
        print("ERROR: AgentTemplate.tex missing from /data folder.")
        sys.exit(1)

    print("Check passed. Initializing Graph...\n")


# 2. ROUTING LOGIC (The Traffic Cop)
def grade_retry_router(state: AgentState):
    """
    Determines if we go to the Compiler or loop back to the Librarian.
    """
    # If the Auditor is happy (Score >= 85), we go to the Compiler
    if state.get("IsSatisfactory"):
        print(f"--- SUCCESS: Score {state.get('AtsEvaluationScore')}% reached. ---")
        return "continue_to_compiler"

    # If not happy, check if we've already tried 3 times
    retries = state.get("RetryCount", 0)
    if retries >= 3:
        print(f"--- MAX RETRIES REACHED ({retries}). Compiling best effort. ---")
        return "continue_to_compiler"

    # Otherwise, loop back to the Librarian for another attempt
    print(f"--- RETRYING: Score {state.get('AtsEvaluationScore')}% is below threshold. ---")
    return "loop_back_to_librarian"


# 3. BUILD THE GRAPH (The Blueprint)
workflow = StateGraph(AgentState)

# Add all the "Brains" and "Hands"
workflow.add_node("Analyst", AnalystNode)
workflow.add_node("Librarian", LibrarianNode)
workflow.add_node("Auditor", AuditorNode)
workflow.add_node("Compiler", CompilerNode)

# Define the Connections (Edges)
workflow.set_entry_point("Analyst")
workflow.add_edge("Analyst", "Librarian")
workflow.add_edge("Librarian", "Auditor")

# Add the Conditional Loop after the Auditor
workflow.add_conditional_edges(
    "Auditor",
    grade_retry_router,
    {
        "loop_back_to_librarian": "Librarian",
        "continue_to_compiler": "Compiler"
    }
)

# The Compiler is the final step
workflow.add_edge("Compiler", END)

# 4. COMPILE THE APP (The Engine)
# This 'app' variable is what you use to run the entire process.
app = workflow.compile()

# 5. EXECUTION BLOCK
if __name__ == "__main__":
    # Load Environment Variables
    load_dotenv()

    # Load your actual data files
    try:
        with open("data/master_resume.md", "r") as f:
            master_resume_content = f.read()

        # Run Validation
        pre_flight_check(master_resume_content)

        # Paste a Job Description here for testing
        sample_jd = """
        [PASTE YOUR JOB DESCRIPTION HERE]
        """

        # Initialize the "Clipboard" (State)
        initial_input = {
            "RawJobDescription": sample_jd,
            "MasterResumeMarkdown": master_resume_content,
            "RetryCount": 0,
            "IsSatisfactory": False  # Initialized as False
        }

        # Run the Agent!
        print("Starting Resume Generation Pipeline...")
        # We call .invoke() on the compiled 'app'
        final_state = app.invoke(initial_input)

        print("\n--- FINAL SUMMARY ---")
        print(f"Final Score: {final_state.get('AtsEvaluationScore', 'N/A')}%")
        print("Result saved to output/tailored_resume.tex")

    except FileNotFoundError as e:
        print(f"ERROR: Could not find required file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")