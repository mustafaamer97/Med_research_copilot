from dataclasses import dataclass, field
from typing import List


# ============================================================
# STEP 1 — RESEARCH CONTEXT
# ============================================================

@dataclass
class ResearchContext:
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


# ============================================================
# VALIDATION MESSAGE
# ============================================================

@dataclass
class ValidationMessage:
    level: str
    field: str
    message: str


# ============================================================
# STEP 2 — RESEARCH IDEA
# ============================================================

@dataclass
class ResearchIdea:
    """
    Represents one research idea generated from the
    structured research context.
    """

    title: str
    rationale: str
    study_design: str
    research_goal: str

    # Optional quality information
    strengths: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ============================================================
# RESEARCH PROJECT
# ============================================================

@dataclass
class ResearchProject:

    # Step 1
    context: ResearchContext = field(
        default_factory=ResearchContext
    )

    # General validation messages
    validation_messages: List[ValidationMessage] = field(
        default_factory=list
    )

    # Step 2
    generated_ideas: List[ResearchIdea] = field(
        default_factory=list
    )

    selected_idea: ResearchIdea | None = None

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

    def select_idea(self, index: int) -> None:
        """
        Select an idea by its zero-based index.
        """

        if 0 <= index < len(self.generated_ideas):
            self.selected_idea = self.generated_ideas[index]
