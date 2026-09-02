# ============================================================
# Med Research Copilot
# Step 2 — Research Idea Generator
# Version: 0.2
#
# Deterministic medical research idea generation.
# No AI dependency.
# No literature-gap claims without evidence.
# ============================================================

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from core.models.research_project import ResearchContext, ResearchIdea


# ============================================================
# General helpers
# ============================================================

def _clean(value: str | None) -> str:
    """Normalize user-entered text."""
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def _lower(value: str | None) -> str:
    return _clean(value).lower()


def _has(value: str | None) -> bool:
    return bool(_clean(value))


def _format_population(
    population: str,
    topic: str,
) -> str:
    """
    Avoid awkward repetition such as:

    Adults with Type 2 Diabetes with Type 2 Diabetes Mellitus
    """
    population = _clean(population)
    topic = _clean(topic)

    if not population:
        return "the target population"

    if not topic:
        return population

    p_lower = population.lower()
    t_lower = topic.lower()

    if t_lower in p_lower:
        return population

    return f"{population} with {topic}"


def _design(context: ResearchContext) -> str:
    """Return the selected study design or Auto Detect."""
    design = _clean(context.study_design)

    if not design:
        return "Auto Detect"

    return design


def _unique_preserve_order(items: List[str]) -> List[str]:
    """Remove duplicate strings while preserving order."""
    seen = set()
    result = []

    for item in items:
        normalized = _lower(item)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(item)

    return result


# ============================================================
# Outcome classification
# ============================================================

def _detect_outcome_categories(outcome: str) -> set[str]:
    """
    Classify the primary outcome using deterministic keyword rules.

    This is intentionally conservative.
    It does not attempt to infer unsupported outcomes.
    """
    normalized = _lower(outcome)
    categories: set[str] = set()

    if not normalized:
        return categories

    # Survival
    if any(
        term in normalized
        for term in [
            "survival",
            "mortality",
            "death",
            "overall survival",
            "progression-free survival",
            "disease-free survival",
        ]
    ):
        categories.add("survival")

    # Diagnostic accuracy
    if any(
        term in normalized
        for term in [
            "sensitivity",
            "specificity",
            "diagnostic accuracy",
            "positive predictive value",
            "negative predictive value",
            "roc",
            "auc",
        ]
    ):
        categories.add("diagnostic_accuracy")

    # Incidence
    if any(
        term in normalized
        for term in [
            "incidence",
            "new cases",
            "new onset",
            "occurrence",
            "development of",
            "risk of",
        ]
    ):
        categories.add("incidence")

    # Prevalence
    if "prevalence" in normalized:
        categories.add("prevalence")

    # Trend
    if (
        ("annual" in normalized or "yearly" in normalized)
        and any(
            term in normalized
            for term in [
                "incidence",
                "prevalence",
                "mortality",
                "rate",
                "cases",
            ]
        )
    ):
        categories.add("trend")

    if "over time" in normalized or "temporal trend" in normalized:
        categories.add("trend")

    # Treatment response/outcome
    if any(
        term in normalized
        for term in [
            "reduction",
            "improvement",
            "response",
            "treatment outcome",
            "clinical outcome",
            "symptom improvement",
            "change in",
        ]
    ):
        categories.add("treatment")

    return categories


# ============================================================
# Research-goal compatibility
# ============================================================

GOAL_EXPECTED_CATEGORIES: Dict[str, set[str]] = {
    "Trend Analysis": {"trend"},
    "Incidence": {"incidence"},
    "Prevalence": {"prevalence"},
    "Risk Factors": {"incidence", "survival"},
    "Treatment Outcomes": {
        "treatment",
        "survival",
        "diagnostic_accuracy",
    },
    "Survival Analysis": {"survival"},
    "Diagnostic Accuracy": {"diagnostic_accuracy"},
    "Prediction Model": {
        "survival",
        "incidence",
        "prevalence",
        "treatment",
        "diagnostic_accuracy",
    },
    "Systematic Review": set(),
}


GOAL_RECOMMENDED_DESIGNS: Dict[str, List[str]] = {
    "Trend Analysis": [
        "Retrospective Cohort Study",
        "Cross-Sectional Study",
    ],
    "Incidence": [
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Prevalence": [
        "Cross-Sectional Study",
    ],
    "Risk Factors": [
        "Case-Control Study",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Treatment Outcomes": [
        "Randomized Controlled Trial",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Survival Analysis": [
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Diagnostic Accuracy": [
        "Diagnostic Accuracy Study",
    ],
    "Prediction Model": [
        "Prediction Model Study",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Systematic Review": [
        "Systematic Review",
        "Meta-Analysis",
        "Scoping Review",
    ],
}


# ============================================================
# Context Gap Check
# ============================================================

def assess_context_gaps(
    context: ResearchContext,
) -> List[str]:
    """
    Identify missing information that may limit idea generation.

    These are context gaps, NOT literature gaps.
    """
    gaps: List[str] = []

    if not _has(context.research_topic):
        gaps.append("Research topic is missing.")

    if not _has(context.population):
        gaps.append("Target population is missing.")

    if not _has(context.outcome):
        gaps.append("Primary outcome is missing.")

    if not _has(context.research_goal):
        gaps.append("Research goal is missing.")

    if not _has(context.data_source):
        gaps.append("Available data source is missing.")

    # Some goals benefit strongly from an intervention/exposure.
    if context.research_goal in {
        "Treatment Outcomes",
        "Risk Factors",
        "Survival Analysis",
        "Prediction Model",
    }:
        if not _has(context.intervention_exposure):
            gaps.append(
                "Intervention / exposure is not specified."
            )

    # Treatment comparisons benefit from a comparator.
    if context.research_goal == "Treatment Outcomes":
        if (
            _has(context.intervention_exposure)
            and not _has(context.comparator)
        ):
            gaps.append(
                "Comparator is not specified; comparative ideas "
                "will therefore be limited."
            )

    return gaps


# ============================================================
# Idea construction helpers
# ============================================================

def _base_parts(
    context: ResearchContext,
) -> Tuple[str, str, str, str, str, str]:
    """
    Return normalized context components.
    """
    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    intervention = _clean(context.intervention_exposure)
    comparator = _clean(context.comparator)
    goal = _clean(context.research_goal)

    return (
        topic,
        population,
        outcome,
        intervention,
        comparator,
        goal,
    )


def _common_strengths(
    title: str,
    context: ResearchContext,
) -> List[str]:
    """
    Evaluate the actual generated idea rather than merely
    repeating the research context.
    """
    title_lower = _lower(title)
    strengths: List[str] = []

    topic = _lower(context.research_topic)
    population = _lower(context.population)
    outcome = _lower(context.outcome)
    intervention = _lower(context.intervention_exposure)
    comparator = _lower(context.comparator)

    if topic and topic in title_lower:
        strengths.append("Research topic is represented.")

    if population:
        population_core = population
        if population_core in title_lower:
            strengths.append(
                "Target population is clearly represented."
            )

    if outcome and outcome in title_lower:
        strengths.append(
            "Primary outcome is explicitly represented."
        )

    if intervention and intervention in title_lower:
        strengths.append(
            "Specified intervention / exposure is used."
        )

    if comparator and comparator in title_lower:
        strengths.append(
            "Specified comparator is used."
        )

    if context.study_design:
        strengths.append("Study design is specified.")

    return _unique_preserve_order(strengths)


def _feasibility_notes(
    context: ResearchContext,
) -> Tuple[List[str], List[str]]:
    """
    Conservative feasibility assessment based only on supplied
    context. We do not invent access to data.
    """
    strengths: List[str] = []
    warnings: List[str] = []

    data_source = _lower(context.data_source)
    design = _lower(context.study_design)

    if data_source:
        strengths.append(
            f"Uses the specified data source: {context.data_source}."
        )

    if context.location:
        strengths.append(
            "Study setting/location is specified."
        )

    if context.study_period:
        strengths.append(
            "Study period is specified."
        )

    if "retrospective" in design:
        if "hospital" in data_source or "registry" in data_source:
            strengths.append(
                "The retrospective design is compatible with "
                "the stated record/registry source."
            )

    if not context.location:
        warnings.append(
            "Study location is not specified; local feasibility "
            "cannot be fully assessed."
        )

    if not context.study_period:
        warnings.append(
            "Study period is not specified; temporal feasibility "
            "cannot be fully assessed."
        )

    return strengths, warnings


# ============================================================
# Idea-specific generators
# ============================================================

def _generate_treatment_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)

    ideas: List[ResearchIdea] = []

    if intervention and comparator:
        title = (
            f"Comparison of {intervention} and {comparator} "
            f"for {outcome} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea directly compares the specified "
                    "intervention and comparator using the "
                    "specified primary outcome."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Causal interpretation should be limited if "
                    "the study is observational."
                ],
                warnings=[],
            )
        )

    if intervention:
        # Conservative grammatical improvement for common plural forms.
        intervention_subject = intervention
        if intervention_subject.lower().endswith("s"):
            intervention_subject = intervention_subject[:-1]

        title = (
            f"Association between {intervention_subject} use "
            f"and {outcome} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea evaluates the association between "
                    "the specified intervention/exposure and the "
                    "primary outcome without assuming causation."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Residual confounding may affect an observational "
                    "association."
                ],
                warnings=[],
            )
        )

        title = (
            f"Real-world {outcome} among {population} "
            f"treated with {intervention}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea focuses on the observed real-world "
                    "outcome among patients receiving the specified "
                    "intervention."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Treatment selection and baseline differences "
                    "may influence observed outcomes."
                ],
                warnings=[],
            )
        )

    if intervention and comparator:
        title = (
            f"Factors associated with {outcome} following "
            f"{intervention} versus {comparator} among "
            f"{population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea examines outcome differences between "
                    "the specified treatment groups while allowing "
                    "assessment of factors associated with the outcome."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "The analysis may require adjustment for "
                    "important baseline differences."
                ],
                warnings=[],
            )
        )

        title = (
            f"Change in {outcome} over the study period among "
            f"{population} receiving {intervention} or {comparator}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea evaluates change in the primary "
                    "outcome over the available study period across "
                    "the specified treatment groups."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Longitudinal completeness and consistency of "
                    "outcome measurements may affect feasibility."
                ],
                warnings=[],
            )
        )

    return ideas


def _generate_risk_factor_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    exposure = intervention or "selected clinical or demographic factors"

    title = (
        f"Association between {exposure} and {outcome} "
        f"among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea examines whether the specified "
                "exposure is associated with the primary outcome."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Association does not establish causation.",
                "Potential confounding should be addressed."
            ],
            warnings=[],
        )
    )

    title = (
        f"Risk factors associated with {outcome} among "
        f"{population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea identifies factors associated with "
                "the specified outcome within the target population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "The available dataset must contain sufficient "
                "candidate predictors."
            ],
            warnings=[],
        )
    )

    if intervention:
        title = (
            f"Association between {intervention} exposure and "
            f"{outcome} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea focuses specifically on the "
                    "relationship between the stated exposure "
                    "and the primary outcome."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Exposure measurement and confounding may "
                    "affect the observed association."
                ],
                warnings=[],
            )
        )

    return ideas


def _generate_survival_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    title = (
        f"{outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea directly evaluates the specified "
                "survival-related outcome in the target population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Time-to-event data and follow-up completeness "
                "are required."
            ],
            warnings=[],
        )
    )

    if intervention:
        title = (
            f"{outcome} according to {intervention} exposure "
            f"among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea evaluates whether survival differs "
                    "according to the specified exposure."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Confounding and differences in follow-up "
                    "may affect survival comparisons."
                ],
                warnings=[],
            )
        )

    if intervention and comparator:
        title = (
            f"Comparison of {outcome} between patients receiving "
            f"{intervention} and {comparator} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea compares the specified survival "
                    "outcome between the intervention and comparator."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Observational treatment comparisons may be "
                    "affected by confounding by indication."
                ],
                warnings=[],
            )
        )

    return ideas


def _generate_incidence_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    title = (
        f"Incidence of {topic} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea estimates occurrence of the specified "
                "condition in the target population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "A clearly defined at-risk population and "
                "observation period are required."
            ],
            warnings=[],
        )
    )

    title = (
        f"Incidence of {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea focuses specifically on the incidence "
                "of the stated outcome."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Case ascertainment and denominator definition "
                "must be consistent."
            ],
            warnings=[],
        )
    )

    if intervention:
        title = (
            f"Incidence of {outcome} according to {intervention} "
            f"exposure among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea explores incidence according to "
                    "the specified exposure."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Differences in exposure groups may introduce "
                    "confounding."
                ],
                warnings=[],
            )
        )

    return ideas


def _generate_prevalence_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    title = (
        f"Prevalence of {topic} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea estimates the prevalence of the "
                "specified condition in the target population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Sampling strategy and case definition can strongly "
                "affect prevalence estimates."
            ],
            warnings=[],
        )
    )

    title = (
        f"Prevalence of {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea estimates the prevalence of the "
                "specified primary outcome."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Cross-sectional measurements may not establish "
                "temporality."
            ],
            warnings=[],
        )
    )

    return ideas


def _generate_trend_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    title = (
        f"Temporal trends in {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea evaluates how the specified outcome "
                "changes over time in the target population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Changes in case ascertainment, coding, or "
                "population structure may influence observed trends."
            ],
            warnings=[],
        )
    )

    title = (
        f"Annual trends in {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea focuses on annual changes in the "
                "specified outcome."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Annual estimates require sufficiently complete "
                "data across the study period."
            ],
            warnings=[],
        )
    )

    if intervention:
        title = (
            f"Temporal trends in {outcome} according to "
            f"{intervention} exposure among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea examines temporal outcome patterns "
                    "according to the specified exposure."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Changes in exposure patterns over time may "
                    "complicate interpretation."
                ],
                warnings=[],
            )
        )

    return ideas


def _generate_diagnostic_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    test = intervention or "the specified diagnostic test"

    title = (
        f"Diagnostic accuracy of {test} for {topic} among "
        f"{population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea evaluates the diagnostic performance "
                "of the specified test in the target population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "A suitable reference standard is required."
            ],
            warnings=[],
        )
    )

    title = (
        f"Diagnostic performance of {test} using {outcome} "
        f"among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea evaluates the specified diagnostic "
                "outcome for the proposed test."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Verification and spectrum bias should be considered."
            ],
            warnings=[],
        )
    )

    return ideas


def _generate_prediction_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    title = (
        f"Prediction of {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea develops or evaluates a model for "
                "predicting the specified outcome."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Adequate sample size, predictor quality, and "
                "internal/external validation are required."
            ],
            warnings=[],
        )
    )

    if intervention:
        title = (
            f"Prediction of {outcome} using clinical factors "
            f"including {intervention} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "This idea evaluates prediction of the "
                    "specified outcome using available clinical "
                    "information."
                ),
                study_design=design,
                research_goal=goal,
                strengths=_common_strengths(title, context),
                limitations=[
                    "Model performance depends on data quality "
                    "and adequate validation."
                ],
                warnings=[],
            )
        )

    return ideas


def _generate_systematic_review_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    if intervention and comparator:
        title = (
            f"Systematic review of {intervention} versus "
            f"{comparator} for {outcome} among {population}"
        )
    else:
        title = (
            f"Systematic review of {outcome} among {population}"
        )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea synthesizes available evidence addressing "
                "the specified research context."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "The strength of conclusions depends on the "
                "availability and quality of eligible studies."
            ],
            warnings=[
                "A literature search is required before making "
                "claims about evidence gaps or novelty."
            ],
        )
    )

    title = (
        f"Evidence synthesis on {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea provides a broader evidence synthesis "
                "around the specified outcome and population."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "Scope and eligibility criteria must be defined "
                "before the review begins."
            ],
            warnings=[
                "This does not establish a literature gap by itself."
            ],
        )
    )

    return ideas


def _generate_generic_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    topic, population, outcome, intervention, comparator, goal = (
        _base_parts(context)
    )

    design = _design(context)
    ideas: List[ResearchIdea] = []

    title = (
        f"Study of {outcome} among {population} with {topic}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "This idea uses the available research context "
                "without adding unsupported assumptions."
            ),
            study_design=design,
            research_goal=goal,
            strengths=_common_strengths(title, context),
            limitations=[
                "The research question requires further refinement "
                "before protocol development."
            ],
            warnings=[],
        )
    )

    return ideas


# ============================================================
# Idea generation dispatcher
# ============================================================

def _generate_raw_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    goal = _clean(context.research_goal)

    if goal == "Treatment Outcomes":
        return _generate_treatment_ideas(context)

    if goal == "Risk Factors":
        return _generate_risk_factor_ideas(context)

    if goal == "Survival Analysis":
        return _generate_survival_ideas(context)

    if goal == "Incidence":
        return _generate_incidence_ideas(context)

    if goal == "Prevalence":
        return _generate_prevalence_ideas(context)

    if goal == "Trend Analysis":
        return _generate_trend_ideas(context)

    if goal == "Diagnostic Accuracy":
        return _generate_diagnostic_ideas(context)

    if goal == "Prediction Model":
        return _generate_prediction_ideas(context)

    if goal == "Systematic Review":
        return _generate_systematic_review_ideas(context)

    return _generate_generic_ideas(context)


# ============================================================
# Generated idea validation
# ============================================================

def validate_generated_idea(
    idea: ResearchIdea,
    context: ResearchContext,
) -> Dict:
    """
    Score an idea using deterministic quality criteria.

    Score:
        Context alignment       25
        Research goal alignment 20
        Outcome clarity         15
        Population fit          10
        Design fit              15
        Feasibility             10
        Distinctiveness          5
                              ----
                               100

    Novelty is intentionally NOT scored here.
    """

    score = 0
    strengths: List[str] = []
    warnings: List[str] = []
    issues: List[str] = []

    title_lower = _lower(idea.title)
    rationale_lower = _lower(idea.rationale)

    topic = _lower(context.research_topic)
    population = _lower(context.population)
    outcome = _lower(context.outcome)
    intervention = _lower(context.intervention_exposure)
    comparator = _lower(context.comparator)
    goal = _clean(context.research_goal)
    design = _clean(context.study_design)

    # --------------------------------------------------------
    # 1. Context alignment — 25
    # --------------------------------------------------------

    context_score = 0

    if topic and topic in title_lower:
        context_score += 8
    else:
        issues.append(
            "Research topic is not clearly represented in the idea."
        )

    if outcome and outcome in title_lower:
        context_score += 7
    else:
        issues.append(
            "Primary outcome is not explicitly represented."
        )

    if intervention and intervention in title_lower:
        context_score += 5

    if comparator and comparator in title_lower:
        context_score += 5

    # If no intervention/comparator is required, redistribute the
    # unused comparative points to basic context alignment.
    if not intervention:
        context_score += 5

    if not comparator:
        context_score += 5

    context_score = min(context_score, 25)
    score += context_score

    # --------------------------------------------------------
    # 2. Research goal alignment — 20
    # --------------------------------------------------------

    goal_score = 0

    expected_categories = GOAL_EXPECTED_CATEGORIES.get(
        goal,
        set(),
    )

    detected_categories = _detect_outcome_categories(
        context.outcome
    )

    if goal == "Systematic Review":
        if "review" in title_lower or "synthesis" in title_lower:
            goal_score = 20
        else:
            goal_score = 10

    elif expected_categories & detected_categories:
        goal_score = 20

    elif goal:
        goal_score = 8
        warnings.append(
            "The primary outcome may not fully represent the "
            "selected research goal."
        )

    else:
        goal_score = 0
        issues.append("Research goal is missing.")

    score += goal_score

    # --------------------------------------------------------
    # 3. Outcome clarity — 15
    # --------------------------------------------------------

    if outcome and outcome in title_lower:
        score += 15
    elif outcome and outcome in rationale_lower:
        score += 8
        warnings.append(
            "The primary outcome appears in the rationale but "
            "not clearly in the title."
        )
    else:
        issues.append(
            "Outcome is insufficiently represented."
        )

    # --------------------------------------------------------
    # 4. Population fit — 10
    # --------------------------------------------------------

    if population and population in title_lower:
        score += 10
    elif population:
        # Population may have been reformatted by the generator.
        population_tokens = [
            token
            for token in re.findall(
                r"[a-zA-Z0-9]+",
                population,
            )
            if len(token) > 3
        ]

        token_matches = sum(
            1
            for token in population_tokens
            if token in title_lower
        )

        if population_tokens and (
            token_matches / len(population_tokens)
        ) >= 0.5:
            score += 7
            warnings.append(
                "Population is represented but the wording "
                "is not identical to the original context."
            )
        else:
            issues.append(
                "Target population is not clearly represented."
            )
    else:
        issues.append(
            "Target population is missing."
        )

    # --------------------------------------------------------
    # 5. Study design fit — 15
    # --------------------------------------------------------

    recommended = GOAL_RECOMMENDED_DESIGNS.get(
        goal,
        [],
    )

    if not design or design == "Auto Detect":
        score += 8
        warnings.append(
            "Study design is not explicitly fixed; design "
            "compatibility should be confirmed later."
        )

    elif design in recommended:
        score += 15

    else:
        # Keep this as a warning rather than automatically rejecting
        # because some legitimate designs may be context-dependent.
        score += 6
        warnings.append(
            f"{design} is not among the usual designs for "
            f"{goal}. Review design compatibility."
        )

    # --------------------------------------------------------
    # 6. Feasibility — 10
    # --------------------------------------------------------

    feasibility_score = 0

    if _has(context.data_source):
        feasibility_score += 4

    if _has(context.location):
        feasibility_score += 2

    if _has(context.study_period):
        feasibility_score += 2

    if (
        "retrospective" in _lower(design)
        and _lower(context.data_source)
        in {
            "hospital records",
            "registry database",
        }
    ):
        feasibility_score += 2

    score += min(feasibility_score, 10)

    # --------------------------------------------------------
    # 7. Distinctiveness — 5
    # --------------------------------------------------------
    #
    # The generator itself produces different structures.
    # We award the full preliminary score here.
    #
    # Actual novelty is NOT claimed.
    # --------------------------------------------------------

    score += 5

    # --------------------------------------------------------
    # Final classification
    # --------------------------------------------------------

    score = min(max(score, 0), 100)

    if score >= 80:
        rating = "Strong Candidate"
    elif score >= 65:
        rating = "Good Candidate"
    elif score >= 50:
        rating = "Needs Refinement"
    else:
        rating = "Reject / Regenerate"

    return {
        "score": score,
        "rating": rating,
        "strengths": _unique_preserve_order(
            strengths + idea.strengths
        ),
        "warnings": _unique_preserve_order(
            warnings + idea.warnings
        ),
        "issues": _unique_preserve_order(issues),
        "feasibility": (
            _feasibility_notes(context)[0]
        ),
        "feasibility_warnings": (
            _feasibility_notes(context)[1]
        ),
        "novelty_status": "Not assessed yet",
        "novelty_reason": (
            "Literature search has not been performed. "
            "No literature-gap or novelty claim should be made."
        ),
    }


# ============================================================
# Diversity / ranking
# ============================================================

def _idea_similarity_key(idea: ResearchIdea) -> str:
    """
    Create a lightweight structural signature.

    This is not semantic similarity. It is only used to prevent
    exact or near-exact duplicate templates.
    """
    title = _lower(idea.title)

    title = re.sub(
        r"\b(comparison|association|real-world|temporal|annual|"
        r"risk factors|systematic review|evidence synthesis)\b",
        "",
        title,
    )

    title = re.sub(r"\s+", " ", title).strip()

    return title


def _unique_ideas(
    ideas: List[ResearchIdea],
) -> List[ResearchIdea]:
    seen = set()
    result = []

    for idea in ideas:
        key = _idea_similarity_key(idea)

        if key in seen:
            continue

        seen.add(key)
        result.append(idea)

    return result


def rank_ideas(
    ideas: List[ResearchIdea],
    context: ResearchContext,
) -> List[Tuple[ResearchIdea, Dict]]:
    """
    Validate and rank generated ideas.

    Returns:
        [(idea, assessment), ...]
    """

    unique_ideas = _unique_ideas(ideas)

    assessed = []

    for idea in unique_ideas:
        assessment = validate_generated_idea(
            idea,
            context,
        )

        assessed.append(
            (idea, assessment)
        )

    assessed.sort(
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    return assessed


# ============================================================
# Public API
# ============================================================

def generate_research_ideas(
    context: ResearchContext,
    max_ideas: int = 5,
) -> List[ResearchIdea]:
    """
    Generate up to max_ideas candidate research ideas.

    The function is deterministic and does not perform literature
    searching or claim novelty.
    """

    gaps = assess_context_gaps(context)

    # Do not generate ideas when essential fields are missing.
    essential_missing = {
        "Research topic is missing.",
        "Target population is missing.",
        "Primary outcome is missing.",
        "Research goal is missing.",
        "Available data source is missing.",
    }

    if any(gap in essential_missing for gap in gaps):
        return []

    ideas = _generate_raw_ideas(context)
    ideas = _unique_ideas(ideas)

    # Rank before limiting.
    ranked = rank_ideas(
        ideas,
        context,
    )

    selected = [
        idea
        for idea, _assessment in ranked[:max_ideas]
    ]

    return selected


def generate_and_rank_research_ideas(
    context: ResearchContext,
    max_ideas: int = 5,
) -> List[Tuple[ResearchIdea, Dict]]:
    """
    Public helper used by the Streamlit workflow.

    Returns ideas together with their full deterministic assessment.
    """

    gaps = assess_context_gaps(context)

    essential_missing = {
        "Research topic is missing.",
        "Target population is missing.",
        "Primary outcome is missing.",
        "Research goal is missing.",
        "Available data source is missing.",
    }

    if any(gap in essential_missing for gap in gaps):
        return []

    ideas = _generate_raw_ideas(context)

    ranked = rank_ideas(
        ideas,
        context,
    )

    return ranked[:max_ideas]
