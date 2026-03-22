import jinja2
import os
from state import AgentState
from utils import escape_for_latex


def CompilerNode(state: AgentState) -> dict:
    """
    Final Node: Renders the LaTeX template using Jinja2 with
    custom delimiters ((* and (((.
    """
    print("--- COMPILER NODE: Generating Final .tex File ---")

    # 1. Initialize Jinja2 with your custom delimiters
    env = jinja2.Environment(
        block_start_string='((*',
        block_end_string='*))',
        variable_start_string='(((',
        variable_end_string=')))',
        loader=jinja2.FileSystemLoader(searchpath="./data")
    )

    # Load your skeleton template
    template = env.get_template("AgentTemplate.tex")

    # 2. Sanitize the summary and skills
    safe_summary = escape_for_latex(state.get("ProfessionalSummary", ""))
    safe_skills = escape_for_latex(state.get("TailoredSkills", ""))

    # 3. Sanitize the selected bullets
    # We iterate through the dictionary and escape every bullet string
    raw_bullets = state.get("SelectedBullets", {})
    safe_bullets = {
        key: [escape_for_latex(bullet) for bullet in bullet_list]
        for key, bullet_list in raw_bullets.items()
    }

    # 4. Map state data to the CamelCase variables in your .tex file
    render_data = {
        "ProfessionalSummary": safe_summary,
        "TailoredSkills": safe_skills,
        "InstructureBullets": safe_bullets.get("InstructureBullets", []),
        "CensusBullets": safe_bullets.get("CensusBullets", []),
        "AmazonBullets": safe_bullets.get("AmazonBullets", []),
        "UnifyBullets": safe_bullets.get("UnifyBullets", [])
    }

    # 5. Render and save to the output folder
    output_content = template.render(**render_data)

    os.makedirs("output", exist_ok=True)
    output_path = "output/tailored_resume.tex"

    with open(output_path, "w") as f:
        f.write(output_content)

    print(f"Successfully saved tailored resume to: {output_path}")

    # Return IsSatisfactory=True to end the LangGraph workflow
    return {"IsSatisfactory": True}
