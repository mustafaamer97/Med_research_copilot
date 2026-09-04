from dataclasses import dataclass, field
from typing import List

============================================================

STEP 1 — RESEARCH CONTEXT

============================================================

@dataclass
class ResearchContext:

# --------------------------------------------------------
# Step 1
# --------------------------------------------------------
research_type: str = ""
research_topic: str = ""
population: str = ""
intervention_exposure: str = ""
comparator: str = ""
outcome: str = ""
research_goal: str = ""
data_source: str = ""
location: str = ""
study_period: str = ""
study_design: str = ""
# --------------------------------------------------------
# Step 2
# --------------------------------------------------------
final_research_idea: str = ""
final_research_rationale: str = ""
# --------------------------------------------------------
# Step 3
# --------------------------------------------------------
research_question: str = ""
primary_objective: str = ""
research_hypothesis: str = ""
framework: dict = field(
    default_factory=dict
)
search_query: str = ""
step3_completed: bool = False

============================================================

VALIDATION MESSAGE

============================================================

@dataclass
class ValidationMessage:
level: str
field: str
message: str

============================================================

STEP 2 — RESEARCH IDEA

============================================================

@dataclass
class ResearchIdea:
“””
Represents one research idea generated from the
structured research context.
“””

title: str
rationale: str
study_design: str
research_goal: str
strengths: List[str] = field(
    default_factory=list
)
limitations: List[str] = field(
    default_factory=list
)
warnings: List[str] = field(
    default_factory=list
)

============================================================

RESEARCH PROJECT

============================================================

@dataclass
class ResearchProject:

# --------------------------------------------------------
# Step 1
# --------------------------------------------------------
context: ResearchContext = field(
    default_factory=ResearchContext
)
# --------------------------------------------------------
# Validation
# --------------------------------------------------------
validation_messages: List[
    ValidationMessage
] = field(
    default_factory=list
)
# --------------------------------------------------------
# Step 2
# --------------------------------------------------------
generated_ideas: List[
    ResearchIdea
] = field(
    default_factory=list
)
selected_idea: ResearchIdea | None = None
# --------------------------------------------------------
# Future package
# --------------------------------------------------------
research_package: dict = field(
    default_factory=dict
)
# --------------------------------------------------------
# Validation helpers
# --------------------------------------------------------
def clear_validation(self) -> None:
    self.validation_messages.clear()
@property
def has_errors(self) -> bool:
    return any(
        message.level == "ERROR"
        for message in self.validation_messages
    )
@property
def has_warnings(self) -> bool:
    return any(
        message.level == "WARNING"
        for message in self.validation_messages
    )
# --------------------------------------------------------
# Step 2 helpers
# --------------------------------------------------------
def clear_ideas(self) -> None:
    self.generated_ideas.clear()
    self.selected_idea = None
def select_idea(
    self,
    index: int,
) -> None:
    """
    Select an idea by its zero-based index.
    """
    if 0 <= index < len(
        self.generated_ideas
    ):
        self.selected_idea = (
            self.generated_ideas[index]
        )
        # ------------------------------------
        # Save final idea into Context
        # ------------------------------------
        self.context.final_research_idea = (
            self.selected_idea.title
        )
        self.context.final_research_rationale = (
            self.selected_idea.rationale
        )

“””
