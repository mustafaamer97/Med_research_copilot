from typing import List

from core.models.research_project import (
    ResearchContext,
    ResearchIdea,
)


# ============================================================
# HELPERS
# ============================================================

def _clean(value: str) -> str:
    """
    Safely clean user-provided text.
    """
    return " ".join((value or "").strip().split())


def _has(value: str) -> bool:
    return bool(_clean(value))


def _unique_ideas(
    ideas: List[ResearchIdea],
) -> List[ResearchIdea]:
    """
    Remove duplicate ideas while preserving order.
    """

    seen = set()
    unique = []

    for idea in ideas:

        key = idea.title.strip().lower()

        if key not in seen:
            seen.add(key)
            unique.append(idea)

    return unique


# ============================================================
# CONTEXT QUALITY
# ============================================================

def assess_idea_context(
    context: ResearchContext,
) -> List[str]:
    """
    Identify missing information that may limit idea generation.

    These are context/design gaps, NOT literature gaps.
    """

    gaps = []

    if not _has(context.research_topic):
        gaps.append("Research topic is missing.")

    if not _has(context.population):
        gaps.append("Population is missing.")

    if not _has(context.outcome):
        gaps.append("Primary outcome is missing.")

    if not _has(context.research_goal):
        gaps.append("Research goal is missing.")

    if not _has(context.data_source):
        gaps.append("Data source is missing.")

    if not _has(context.location):
        gaps.append(
            "Study location is not specified."
        )

    if not _has(context.study_period):
        gaps.append(
            "Study period is not specified."
        )

    return gaps


# ============================================================
# IDEA QUALITY CHECK
# ============================================================

def validate_generated_idea(
    idea: ResearchIdea,
    context: ResearchContext,
) -> ResearchIdea:
    """
    Validate that the generated idea remains grounded
    in the supplied research context.
    """

    idea.strengths = []
    idea.limitations = []
    idea.warnings = []

    # --------------------------------------------------------
    # Required components
    # --------------------------------------------------------

    if _has(context.research_topic):
        idea.strengths.append(
            "Research topic is clearly defined."
        )

    if _has(context.population):
        idea.strengths.append(
            "Target population is specified."
        )

    if _has(context.outcome):
        idea.strengths.append(
            "Primary outcome is specified."
        )

    if _has(context.research_goal):
        idea.strengths.append(
            "Research goal is defined."
        )

    # --------------------------------------------------------
    # Intervention / Exposure
    # --------------------------------------------------------

    if _has(context.intervention_exposure):

        idea.strengths.append(
            "An intervention or exposure is available."
        )

    else:

        idea.limitations.append(
            "No intervention or exposure is specified."
        )

    # --------------------------------------------------------
    # Comparator
    # --------------------------------------------------------

    if _has(context.comparator):

        idea.strengths.append(
            "A comparator is available."
        )

    else:

        if context.research_goal in {
            "Treatment Outcomes",
            "Risk Factors",
        }:

            idea.limitations.append(
                "A comparator is not specified; "
                "this may limit comparative analysis."
            )

    # --------------------------------------------------------
    # Study design
    # --------------------------------------------------------

    if _has(context.study_design):

        idea.strengths.append(
            "A study design is specified."
        )

    else:

        idea.warnings.append(
            "Study design has not been specified."
        )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    if not _has(context.location):

        idea.limitations.append(
            "Study location is not specified."
        )

    # --------------------------------------------------------
    # Study period
    # --------------------------------------------------------

    if not _has(context.study_period):

        idea.limitations.append(
            "Study period is not specified."
        )

    return idea


# ============================================================
# TREATMENT OUTCOMES
# ============================================================

def _generate_treatment_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    intervention = _clean(context.intervention_exposure)
    comparator = _clean(context.comparator)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    ideas = []

    # --------------------------------------------------------
    # Comparative treatment idea
    # --------------------------------------------------------

    if intervention and comparator:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Comparison of {intervention} and "
                    f"{comparator} for {outcome} among "
                    f"{population} with {topic}"
                ),
                rationale=(
                    "This idea directly evaluates the specified "
                    "intervention against the specified comparator "
                    "using the stated primary outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # Intervention-focused idea
    # --------------------------------------------------------

    if intervention:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Treatment outcomes associated with "
                    f"{intervention} in {population} with {topic}"
                ),
                rationale=(
                    "This idea focuses on the real-world outcome "
                    "associated with the specified intervention."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # Outcome-focused idea
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"{outcome} among {population} with {topic}"
            ),
            rationale=(
                "This idea describes the specified primary "
                "outcome in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    return ideas


# ============================================================
# RISK FACTORS
# ============================================================

def _generate_risk_factor_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    exposure = _clean(context.intervention_exposure)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    ideas = []

    if exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {exposure} and "
                    f"{outcome} among {population} with {topic}"
                ),
                rationale=(
                    "This idea evaluates the relationship between "
                    "the specified exposure and outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    ideas.append(
        ResearchIdea(
            title=(
                f"Risk factors associated with {outcome} "
                f"among {population} with {topic}"
            ),
            rationale=(
                "This idea focuses on identifying factors "
                "associated with the specified outcome."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    ideas.append(
        ResearchIdea(
            title=(
                f"Factors associated with {outcome} "
                f"in {population} with {topic}"
            ),
            rationale=(
                "This idea explores associations with the "
                "specified outcome without assuming a specific "
                "causal relationship."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    return ideas


# ============================================================
# SURVIVAL ANALYSIS
# ============================================================

def _generate_survival_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    exposure = _clean(context.intervention_exposure)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    ideas = []

    if exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {exposure} and "
                    f"{outcome} among {population} with {topic}"
                ),
                rationale=(
                    "This idea evaluates the specified exposure "
                    "in relation to the survival-related outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    ideas.append(
        ResearchIdea(
            title=(
                f"{outcome} among {population} "
                f"with {topic}"
            ),
            rationale=(
                "This idea focuses on the specified survival "
                "outcome in the target population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    return ideas


# ============================================================
# INCIDENCE
# ============================================================

def _generate_incidence_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    ideas = [
        ResearchIdea(
            title=(
                f"Incidence of {outcome} among "
                f"{population} with {topic}"
            ),
            rationale=(
                "This idea measures the occurrence of the "
                "specified outcome in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    ]

    if context.study_period:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Incidence of {outcome} among "
                    f"{population} with {topic} during "
                    f"{_clean(context.study_period)}"
                ),
                rationale=(
                    "This idea incorporates the specified "
                    "study period into the incidence assessment."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    return ideas


# ============================================================
# PREVALENCE
# ============================================================

def _generate_prevalence_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    return [
        ResearchIdea(
            title=(
                f"Prevalence of {outcome} among "
                f"{population} with {topic}"
            ),
            rationale=(
                "This idea estimates the prevalence of the "
                "specified outcome in the target population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        ),
        ResearchIdea(
            title=(
                f"Burden of {outcome} among "
                f"{population} with {topic}"
            ),
            rationale=(
                "This idea describes the burden of the "
                "specified outcome in the target population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        ),
    ]


# ============================================================
# TREND ANALYSIS
# ============================================================

def _generate_trend_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)
    period = _clean(context.study_period)

    ideas = [
        ResearchIdea(
            title=(
                f"Temporal trends in {outcome} among "
                f"{population} with {topic}"
            ),
            rationale=(
                "This idea evaluates how the specified outcome "
                "changes over time."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    ]

    if period:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Trends in {outcome} among "
                    f"{population} with {topic} during "
                    f"{period}"
                ),
                rationale=(
                    "This idea evaluates temporal changes during "
                    "the specified study period."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    return ideas


# ============================================================
# DIAGNOSTIC ACCURACY
# ============================================================

def _generate_diagnostic_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    test_or_exposure = _clean(
        context.intervention_exposure
    )
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    ideas = []

    if test_or_exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Diagnostic accuracy of "
                    f"{test_or_exposure} for {outcome} "
                    f"among {population} with {topic}"
                ),
                rationale=(
                    "This idea evaluates the diagnostic performance "
                    "of the specified test or intervention."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    else:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Diagnostic accuracy assessment for "
                    f"{outcome} among {population} "
                    f"with {topic}"
                ),
                rationale=(
                    "This idea focuses on diagnostic accuracy "
                    "for the specified outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    return ideas


# ============================================================
# PREDICTION MODEL
# ============================================================

def _generate_prediction_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    return [
        ResearchIdea(
            title=(
                f"Prediction of {outcome} among "
                f"{population} with {topic}"
            ),
            rationale=(
                "This idea focuses on prediction of the "
                "specified outcome in the target population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        ),
        ResearchIdea(
            title=(
                f"Development of a prediction model for "
                f"{outcome} among {population} "
                f"with {topic}"
            ),
            rationale=(
                "This idea proposes development of a prediction "
                "model using the defined population and outcome."
            ),
            study_design=design,
            research_goal=context.research_goal,
        ),
    ]


# ============================================================
# SYSTEMATIC REVIEW
# ============================================================

def _generate_systematic_review_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    intervention = _clean(
        context.intervention_exposure
    )
    comparator = _clean(context.comparator)
    outcome = _clean(context.outcome)
    design = _clean(context.study_design)

    ideas = []

    if intervention and comparator:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Effectiveness of {intervention} "
                    f"compared with {comparator} for "
                    f"{outcome} among {population} "
                    f"with {topic}: a systematic review"
                ),
                rationale=(
                    "This idea converts the specified comparison "
                    "into an evidence-synthesis question."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    elif intervention:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Effectiveness of {intervention} for "
                    f"{outcome} among {population} "
                    f"with {topic}: a systematic review"
                ),
                rationale=(
                    "This idea synthesizes evidence about the "
                    "specified intervention and outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    else:

        ideas.append(
            ResearchIdea(
                title=(
                    f"{outcome} among {population} "
                    f"with {topic}: a systematic review"
                ),
                rationale=(
                    "This idea synthesizes available evidence "
                    "about the specified outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    return ideas


# ============================================================
# GENERIC FALLBACK
# ============================================================

def _generate_generic_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    exposure = _clean(
        context.intervention_exposure
    )
    design = _clean(context.study_design)

    ideas = []

    if exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {exposure} and "
                    f"{outcome} among {population} "
                    f"with {topic}"
                ),
                rationale=(
                    "This idea uses the available exposure, "
                    "population, and outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    ideas.append(
        ResearchIdea(
            title=(
                f"{outcome} among {population} "
                f"with {topic}"
            ),
            rationale=(
                "This idea focuses on the primary outcome "
                "within the specified population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    return ideas


# ============================================================
# MAIN IDEA GENERATOR
# ============================================================

def generate_research_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    """
    Generate deterministic research ideas from ResearchContext.

    Important:
    - No AI
    - No external evidence
    - No invented variables
    - No fabricated literature gaps
    """

    # --------------------------------------------------------
    # Check minimum context
    # --------------------------------------------------------

    missing = assess_idea_context(context)

    if missing:

        return []

    goal = _clean(context.research_goal)

    # --------------------------------------------------------
    # Select generation strategy
    # --------------------------------------------------------

    if goal == "Treatment Outcomes":

        ideas = _generate_treatment_ideas(context)

    elif goal == "Risk Factors":

        ideas = _generate_risk_factor_ideas(context)

    elif goal == "Survival Analysis":

        ideas = _generate_survival_ideas(context)

    elif goal == "Incidence":

        ideas = _generate_incidence_ideas(context)

    elif goal == "Prevalence":

        ideas = _generate_prevalence_ideas(context)

    elif goal == "Trend Analysis":

        ideas = _generate_trend_ideas(context)

    elif goal == "Diagnostic Accuracy":

        ideas = _generate_diagnostic_ideas(context)

    elif goal == "Prediction Model":

        ideas = _generate_prediction_ideas(context)

    elif goal == "Systematic Review":

        ideas = _generate_systematic_review_ideas(context)

    else:

        ideas = _generate_generic_ideas(context)

    # --------------------------------------------------------
    # Validate every idea
    # --------------------------------------------------------

    validated = []

    for idea in ideas:

        validated_idea = validate_generated_idea(
            idea,
            context,
        )

        validated.append(validated_idea)

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    validated = _unique_ideas(validated)

    # --------------------------------------------------------
    # Limit output
    # --------------------------------------------------------

    return validated[:5]
