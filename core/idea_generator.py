from typing import List

from core.models.research_project import (
    ResearchContext,
    ResearchIdea,
)


# ============================================================
# TEXT HELPERS
# ============================================================

def _clean(value: str) -> str:
    """
    Normalize user-provided text while preserving the
    original wording as much as possible.
    """

    return " ".join(
        (value or "").strip().split()
    )


def _has(value: str) -> bool:
    return bool(_clean(value))


def _lower(value: str) -> str:
    return _clean(value).lower()


def _unique_ideas(
    ideas: List[ResearchIdea],
) -> List[ResearchIdea]:
    """
    Remove duplicate ideas while preserving their order.
    """

    seen = set()
    unique = []

    for idea in ideas:

        key = _lower(idea.title)

        if key not in seen:

            seen.add(key)
            unique.append(idea)

    return unique


# ============================================================
# POPULATION / TOPIC NORMALIZATION
# ============================================================

def _population_mentions_topic(
    population: str,
    topic: str,
) -> bool:
    """
    Determine whether the population already contains
    the research topic.

    Example:

    Population:
        Adults with Type 2 Diabetes

    Topic:
        Type 2 Diabetes Mellitus

    These refer to the same underlying condition, so the
    topic should not be repeated in the generated title.
    """

    population_normalized = _lower(population)
    topic_normalized = _lower(topic)

    if not population_normalized or not topic_normalized:
        return False

    # Direct containment
    if topic_normalized in population_normalized:
        return True

    # Common simplified comparison
    population_words = set(
        population_normalized.replace("-", " ").split()
    )

    topic_words = set(
        topic_normalized.replace("-", " ").split()
    )

    # Remove generic words
    generic_words = {
        "type",
        "patients",
        "patient",
        "adults",
        "adult",
        "children",
        "child",
        "with",
        "the",
        "of",
        "and",
    }

    population_core = (
        population_words - generic_words
    )

    topic_core = (
        topic_words - generic_words
    )

    if not topic_core:
        return False

    overlap = population_core.intersection(
        topic_core
    )

    # If most meaningful topic words already occur
    # in the population, avoid repeating the topic.
    return len(overlap) >= max(
        1,
        len(topic_core) * 0.6,
    )


def _format_population(
    population: str,
    topic: str,
) -> str:
    """
    Return a clean population phrase.

    If the population already contains the topic,
    return only the population.

    Otherwise, append the topic naturally.
    """

    population = _clean(population)
    topic = _clean(topic)

    if not population:
        return topic

    if not topic:
        return population

    if _population_mentions_topic(
        population,
        topic,
    ):
        return population

    return f"{population} with {topic}"


# ============================================================
# DESIGN HELPERS
# ============================================================

def _design(context: ResearchContext) -> str:
    return _clean(context.study_design)


# ============================================================
# CONTEXT QUALITY
# ============================================================

def assess_idea_context(
    context: ResearchContext,
) -> List[str]:
    """
    Identify missing information that may limit
    research idea generation.

    IMPORTANT:
    These are context/design gaps only.

    They are NOT literature gaps.
    """

    gaps = []

    if not _has(context.research_topic):

        gaps.append(
            "Research topic is missing."
        )

    if not _has(context.population):

        gaps.append(
            "Population is missing."
        )

    if not _has(context.outcome):

        gaps.append(
            "Primary outcome is missing."
        )

    if not _has(context.research_goal):

        gaps.append(
            "Research goal is missing."
        )

    if not _has(context.data_source):

        gaps.append(
            "Data source is missing."
        )

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
# IDEA VALIDATION
# ============================================================

def validate_generated_idea(
    idea: ResearchIdea,
    context: ResearchContext,
) -> ResearchIdea:
    """
    Validate an individual generated research idea.

    Validation is based on the actual content of the idea
    and the supplied ResearchContext.

    No external evidence is used here.
    """

    idea.strengths = []
    idea.limitations = []
    idea.warnings = []

    title = _lower(idea.title)

    topic = _lower(
        context.research_topic
    )

    population = _lower(
        context.population
    )

    outcome = _lower(
        context.outcome
    )

    intervention = _lower(
        context.intervention_exposure
    )

    comparator = _lower(
        context.comparator
    )

    # --------------------------------------------------------
    # Topic
    # --------------------------------------------------------

    if topic and (
        topic in title
        or _population_mentions_topic(
            population,
            topic,
        )
    ):

        idea.strengths.append(
            "Research topic is represented."
        )

    else:

        idea.warnings.append(
            "Research topic is not clearly represented."
        )

    # --------------------------------------------------------
    # Population
    # --------------------------------------------------------

    if population and population in title:

        idea.strengths.append(
            "Target population is clearly specified."
        )

    elif population:

        idea.warnings.append(
            "Target population is not clearly represented."
        )

    # --------------------------------------------------------
    # Outcome
    # --------------------------------------------------------

    if outcome and outcome in title:

        idea.strengths.append(
            "Primary outcome is explicitly represented."
        )

    elif outcome:

        idea.warnings.append(
            "Primary outcome is not explicitly represented."
        )

    # --------------------------------------------------------
    # Intervention / Exposure
    # --------------------------------------------------------

    uses_intervention = (
        bool(intervention)
        and intervention in title
    )

    if uses_intervention:

        idea.strengths.append(
            "Specified intervention/exposure is used."
        )

    # --------------------------------------------------------
    # Comparator
    # --------------------------------------------------------

    uses_comparator = (
        bool(comparator)
        and comparator in title
    )

    if uses_comparator:

        idea.strengths.append(
            "Specified comparator is used."
        )

    # --------------------------------------------------------
    # Design
    # --------------------------------------------------------

    if _has(context.study_design):

        idea.strengths.append(
            "Study design is specified in the research context."
        )

    else:

        idea.limitations.append(
            "Study design has not yet been specified."
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

    # --------------------------------------------------------
    # Comparator-specific limitation
    # --------------------------------------------------------

    if (
        context.research_goal
        in {
            "Treatment Outcomes",
            "Risk Factors",
        }
        and not comparator
    ):

        if uses_intervention:

            idea.limitations.append(
                "No comparator is specified for this "
                "comparative research context."
            )

    return idea


# ============================================================
# TREATMENT OUTCOMES
# ============================================================

def _generate_treatment_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    intervention = _clean(
        context.intervention_exposure
    )

    comparator = _clean(
        context.comparator
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # IDEA 1 — Comparative effectiveness
    # --------------------------------------------------------

    if intervention and comparator:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Comparison of {intervention} "
                    f"and {comparator} for {outcome} "
                    f"among {population}"
                ),
                rationale=(
                    "This idea directly compares the specified "
                    "intervention and comparator using the "
                    "specified primary outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # IDEA 2 — Association
    # --------------------------------------------------------

    if intervention:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {intervention.rstrip('s')} "
                    f"use and {outcome} among "
                    f"{population}"
                ),
                rationale=(
                    "This idea evaluates the association between "
                    "the specified intervention/exposure and the "
                    "primary outcome without assuming causation."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # IDEA 3 — Real-world outcome
    # --------------------------------------------------------

    if intervention:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Real-world {outcome} among "
                    f"{population} treated with "
                    f"{intervention}"
                ),
                rationale=(
                    "This idea focuses on the observed real-world "
                    "outcome among patients receiving the "
                    "specified intervention."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # Fallback if no intervention
    # --------------------------------------------------------

    if not intervention:

        ideas.append(
            ResearchIdea(
                title=(
                    f"{outcome} among {population}"
                ),
                rationale=(
                    "This idea focuses on the specified "
                    "treatment outcome within the target "
                    "population."
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    exposure = _clean(
        context.intervention_exposure
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # IDEA 1 — Specific exposure
    # --------------------------------------------------------

    if exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {exposure} "
                    f"and {outcome} among "
                    f"{population}"
                ),
                rationale=(
                    "This idea evaluates the relationship between "
                    "the specified exposure and outcome without "
                    "assuming a causal effect."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # IDEA 2 — Risk factors
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"Risk factors associated with {outcome} "
                f"among {population}"
            ),
            rationale=(
                "This idea focuses on identifying factors "
                "associated with the specified outcome."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    # --------------------------------------------------------
    # IDEA 3 — Factors associated with outcome
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"Factors associated with {outcome} "
                f"in {population}"
            ),
            rationale=(
                "This idea explores associations with the "
                "specified outcome while avoiding an assumption "
                "of causality."
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    exposure = _clean(
        context.intervention_exposure
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # IDEA 1 — Exposure and survival outcome
    # --------------------------------------------------------

    if exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {exposure} "
                    f"and {outcome} among "
                    f"{population}"
                ),
                rationale=(
                    "This idea evaluates the association between "
                    "the specified exposure and survival-related "
                    "outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # IDEA 2 — Survival outcome
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"{outcome} among {population}"
            ),
            rationale=(
                "This idea focuses on the specified survival "
                "outcome within the target population."
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # IDEA 1 — Incidence
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"Incidence of {outcome} among "
                f"{population}"
            ),
            rationale=(
                "This idea measures the occurrence of the "
                "specified outcome in the target population."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    # --------------------------------------------------------
    # IDEA 2 — Incidence over study period
    # --------------------------------------------------------

    if _has(context.study_period):

        ideas.append(
            ResearchIdea(
                title=(
                    f"Incidence of {outcome} among "
                    f"{population} during "
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    return [

        ResearchIdea(
            title=(
                f"Prevalence of {outcome} among "
                f"{population}"
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
                f"{population}"
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # IDEA 1 — Temporal trends
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"Temporal trends in {outcome} among "
                f"{population}"
            ),
            rationale=(
                "This idea evaluates how the specified outcome "
                "changes over time."
            ),
            study_design=design,
            research_goal=context.research_goal,
        )
    )

    # --------------------------------------------------------
    # IDEA 2 — Study period
    # --------------------------------------------------------

    if _has(context.study_period):

        ideas.append(
            ResearchIdea(
                title=(
                    f"Trends in {outcome} among "
                    f"{population} during "
                    f"{_clean(context.study_period)}"
                ),
                rationale=(
                    "This idea evaluates temporal changes "
                    "during the specified study period."
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    test_or_exposure = _clean(
        context.intervention_exposure
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # IDEA 1 — Specific test
    # --------------------------------------------------------

    if test_or_exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Diagnostic accuracy of "
                    f"{test_or_exposure} for "
                    f"{outcome} among "
                    f"{population}"
                ),
                rationale=(
                    "This idea evaluates the diagnostic performance "
                    "of the specified test or diagnostic intervention."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # IDEA 2 — General diagnostic assessment
    # --------------------------------------------------------

    else:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Diagnostic accuracy assessment for "
                    f"{outcome} among "
                    f"{population}"
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    return [

        ResearchIdea(
            title=(
                f"Prediction of {outcome} among "
                f"{population}"
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
                f"{outcome} among "
                f"{population}"
            ),
            rationale=(
                "This idea proposes development of a prediction "
                "model for the defined outcome and population."
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    intervention = _clean(
        context.intervention_exposure
    )

    comparator = _clean(
        context.comparator
    )

    outcome = _clean(
        context.outcome
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # Comparative systematic review
    # --------------------------------------------------------

    if intervention and comparator:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Effectiveness of {intervention} "
                    f"compared with {comparator} for "
                    f"{outcome} among {population}: "
                    f"a systematic review"
                ),
                rationale=(
                    "This idea converts the specified treatment "
                    "comparison into an evidence-synthesis question."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # Intervention systematic review
    # --------------------------------------------------------

    elif intervention:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Effectiveness of {intervention} "
                    f"for {outcome} among "
                    f"{population}: a systematic review"
                ),
                rationale=(
                    "This idea synthesizes evidence about the "
                    "specified intervention and outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # Outcome systematic review
    # --------------------------------------------------------

    else:

        ideas.append(
            ResearchIdea(
                title=(
                    f"{outcome} among {population}: "
                    f"a systematic review"
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

    topic = _clean(
        context.research_topic
    )

    population = _format_population(
        context.population,
        topic,
    )

    outcome = _clean(
        context.outcome
    )

    exposure = _clean(
        context.intervention_exposure
    )

    design = _design(context)

    ideas = []

    # --------------------------------------------------------
    # Association idea
    # --------------------------------------------------------

    if exposure:

        ideas.append(
            ResearchIdea(
                title=(
                    f"Association between {exposure} "
                    f"and {outcome} among "
                    f"{population}"
                ),
                rationale=(
                    "This idea uses the available exposure, "
                    "population, and primary outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
            )
        )

    # --------------------------------------------------------
    # Outcome idea
    # --------------------------------------------------------

    ideas.append(
        ResearchIdea(
            title=(
                f"{outcome} among {population}"
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
# MAIN GENERATOR
# ============================================================

def generate_research_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    """
    Generate deterministic research ideas from ResearchContext.

    Design principles:

    1. No AI.
    2. No external evidence.
    3. No fabricated variables.
    4. No fabricated literature gaps.
    5. Every idea must remain grounded in the context.
    6. Ideas should differ in research angle where possible.
    7. Maximum of five ideas are returned.
    """

    # ========================================================
    # MINIMUM CONTEXT
    # ========================================================

    missing = assess_idea_context(
        context
    )

    if missing:

        return []

    goal = _clean(
        context.research_goal
    )

    # ========================================================
    # GENERATION STRATEGY
    # ========================================================

    if goal == "Treatment Outcomes":

        ideas = _generate_treatment_ideas(
            context
        )

    elif goal == "Risk Factors":

        ideas = _generate_risk_factor_ideas(
            context
        )

    elif goal == "Survival Analysis":

        ideas = _generate_survival_ideas(
            context
        )

    elif goal == "Incidence":

        ideas = _generate_incidence_ideas(
            context
        )

    elif goal == "Prevalence":

        ideas = _generate_prevalence_ideas(
            context
        )

    elif goal == "Trend Analysis":

        ideas = _generate_trend_ideas(
            context
        )

    elif goal == "Diagnostic Accuracy":

        ideas = _generate_diagnostic_ideas(
            context
        )

    elif goal == "Prediction Model":

        ideas = _generate_prediction_ideas(
            context
        )

    elif goal == "Systematic Review":

        ideas = _generate_systematic_review_ideas(
            context
        )

    else:

        ideas = _generate_generic_ideas(
            context
        )

    # ========================================================
    # VALIDATE
    # ========================================================

    validated_ideas = []

    for idea in ideas:

        validated_idea = validate_generated_idea(
            idea,
            context,
        )

        validated_ideas.append(
            validated_idea
        )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    validated_ideas = _unique_ideas(
        validated_ideas
    )

    # ========================================================
    # LIMIT
    # ========================================================

    return validated_ideas[:5]
