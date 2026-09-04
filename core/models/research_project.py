from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# STEP 1 — RESEARCH CONTEXT
# ============================================================

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
    final_research: str = ""
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

    # --------------------------------------------------------
    # Step 4 (future)
    # --------------------------------------------------------
    retrieved_articles: list = field(
        default_factory=list
    )

    research_gap_summary: str = ""

    literature_search_completed: bool = False


# ============================================================
# VALIDATION MESSAGE
# ============================================================

@dataclass
class ValidationMessage:
    level: str
    field: str
    message: str


# ============================================================
# STEP 2 — RESEARCH CANDIDATE
# ============================================================

@dataclass
class ResearchCandidate:
    """
    Represents one candidate research project
    generated from the structured research context.
    """

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


# ============================================================
# RESEARCH PROJECT
# ============================================================

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
    generated_candidates: List[
        ResearchCandidate
    ] = field(
        default_factory=list
    )

    selected_candidate: Optional[
        ResearchCandidate
    ] = None

    # --------------------------------------------------------
    # Future Package
    # --------------------------------------------------------
    research_package: dict = field(
        default_factory=dict
    )

    # ========================================================
    # Validation Helpers
    # ========================================================

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

    # ========================================================
    # Step 2 Helpers
    # ========================================================

    def clear_candidates(self) -> None:

        self.generated_candidates.clear()

        self.selected_candidate = None

        self.context.final_research = ""
        self.context.final_research_rationale = ""

    def select_candidate(
        self,
        index: int,
    ) -> None:
        """
        Select a candidate by index
        and save it into the project context.
        """

        if not (
            0 <= index < len(
                self.generated_candidates
            )
        ):
            return

        self.selected_candidate = (
            self.generated_candidates[index]
        )

        self.context.final_research = (
            self.selected_candidate.title
        )

        self.context.final_research_rationale = (
            self.selected_candidate.rationale
        )

    # ========================================================
    # Convenience Helpers
    # ========================================================

    @property
    def has_selected_candidate(self) -> bool:
        return (
            self.selected_candidate is not None
        )

    @property
    def step3_ready(self) -> bool:
        return bool(
            self.context.final_research
        )
