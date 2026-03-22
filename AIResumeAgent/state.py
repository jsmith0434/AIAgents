from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

class JobAnalysis(BaseModel):
    """The structured output from the Analyst Agent"""
    CoreTechStack: List[str]
    PrimaryFocus: str
    RequiredSoftSkills: List[str]
    TargetIndustryKeywords: List[str]

class AgentState(TypedDict):
    """The 'Clipboard' passed between nodes in LangGraph"""
    RawJobDescription: str
    MasterResumeMarkdown: str
    ExtractedRequirements: Optional[JobAnalysis] # Populated by Analyst
    SelectedBullets: dict[str, List[str]]        # Populated by Librarian
    ProfessionalSummary: str                     # Populated by Auditor
    TailoredSkills: str                          # Populated by Auditor
    IsSatisfactory: bool                         # Set by Auditor to trigger loops
    RetryCount: int  # Tracking how many times we've looped