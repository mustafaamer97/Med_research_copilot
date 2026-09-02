# ============================================================
# Med Research Copilot
# core/idea_generator.py
#
# Step 2 — Research Idea Generation & Quality Ranking
#
# Deterministic v0.3
# No AI
# No external dependencies
# No literature-gap claims
# ============================================================

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from core.models.research_project import ResearchContext, ResearchIdea


# ============================================================
# Basic helpers
# ============================================================

def _clean(value: str | None) -> str:
    """Normalize whitespace while preserving original wording."""
    if not value:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def _lower(value: str | None) -> str:
    return _clean(value).lower()


def _has(value: str | None) -> bool:
    return bool(_clean(value))


def _unique_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result = []

    for item in items:
        key = _lower(item)

        if key and key not in seen:
            seen.add(key)
            result.append(item)

    return result


# ============================================================
# Semantic-ish topic / population handling
# ============================================================

_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "with",
    "in",
    "on",
    "for",
    "to",
    "among",
    "patients",
    "patient",
    "adults",
    "adult",
    "children",
    "child",
    "people",
    "persons",
    "individuals",
    "population",
    "population-based",
}


def _tokens(text: str | None) -> set[str]:
    """
    Create lightweight semantic tokens.

    This is intentionally simple and deterministic.
    It is NOT a clinical NLP model.
    """
    normalized = _lower(text)

    if not normalized:
        return set()

    tokens = re.findall(r"[a-z0-9]+", normalized)

    return {
        token
        for token in tokens
        if token not in _STOPWORDS
    }


def _population_mentions_topic(
    population: str,
    topic: str,
) -> bool:
    """
    Detect whether the population already contains the core topic.

    Example:
        population = "Adults with Type 2 Diabetes"
        topic = "Type 2 Diabetes Mellitus"

    -> True
    """

    population_tokens = _tokens(population)
    topic_tokens = _tokens(topic)

    if not population_tokens or not topic_tokens:
        return False

    overlap = population_tokens.intersection(topic_tokens)

    # Core topic overlap.
    overlap_ratio = len(overlap) / len(topic_tokens)

    if overlap_ratio >= 0.50:
        return True

    # Stronger protection for short topics.
    if len(topic_tokens) <= 2 and overlap:
        return True

    return False


def _format_population(
    population: str,
    topic: str,
) -> str:
    """
    Prevent awkward constructions such as:

    Adults with Type 2 Diabetes
    + Type 2 Diabetes Mellitus

    becoming:

    Adults with Type 2 Diabetes with Type 2 Diabetes Mellitus
    """

    population = _clean(population)
    topic = _clean(topic)

    if not population:
        return topic

    if not topic:
        return population

    if _population_mentions_topic(population, topic):
        return population

    return f"{population} with {topic}"


# ============================================================
# Study design helpers
# ============================================================

def _design(context: ResearchContext) -> str:
    return _clean(context.study_design)


def _design_is(context: ResearchContext, *designs: str) -> bool:
    current = _lower(_design(context))
    return any(current == _lower(design) for design in designs)


# ============================================================
# Outcome classification
# ============================================================

def _detect_outcome_categories(outcome: str) -> set[str]:
    """
    Lightweight deterministic classification of the primary outcome.

    This is intentionally conservative.
    """

    normalized = _lower(outcome)
    detected: set[str] = set()

    if not normalized:
        return detected

    # Treatment / response
    treatment_terms = [
        "reduction",
        "improvement",
        "response",
        "control",
        "change",
        "treatment outcome",
        "clinical outcome",
        "therapeutic outcome",
        "symptom improvement",
    ]

    if any(term in normalized for term in treatment_terms):
        detected.add("treatment")

    # Survival
    survival_terms = [
        "overall survival",
        "progression-free survival",
        "disease-free survival",
        "survival",
        "mortality",
        "death",
        "time to death",
    ]

    if any(term in normalized for term in survival_terms):
        detected.add("survival")

    # Incidence
    incidence_terms = [
        "incidence",
        "new cases",
        "new onset",
        "development of",
        "occurrence of",
        "risk of",
    ]

    if any(term in normalized for term in incidence_terms):
        detected.add("incidence")

    # Prevalence
    if "prevalence" in normalized:
        detected.add("prevalence")

    # Diagnostic accuracy
    diagnostic_terms = [
        "sensitivity",
        "specificity",
        "diagnostic accuracy",
        "positive predictive value",
        "negative predictive value",
        "auc",
        "area under the curve",
    ]

    if any(term in normalized for term in diagnostic_terms):
        detected.add("diagnostic_accuracy")

    # Trend
    if "over time" in normalized:
        detected.add("trend")

    if (
        "annual" in normalized
        and ("incidence" in normalized or "mortality" in normalized)
    ):
        detected.add("trend")

    if (
        "yearly" in normalized
        and ("incidence" in normalized or "mortality" in normalized)
    ):
        detected.add("trend")

    if "temporal trend" in normalized:
        detected.add("trend")

    return detected


# ============================================================
# Goal rules
# ============================================================

GOAL_EXPECTED_OUTCOMES: Dict[str, set[str]] = {
    "Survival Analysis": {
        "survival",
    },
    "Diagnostic Accuracy": {
        "diagnostic_accuracy",
    },
    "Incidence": {
        "incidence",
    },
    "Prevalence": {
        "prevalence",
    },
    "Trend Analysis": {
        "trend",
        "incidence",
        "survival",
    },
    "Treatment Outcomes": {
        "treatment",
        "survival",
        "diagnostic_accuracy",
    },
    "Risk Factors": {
        "incidence",
        "survival",
    },
    "Prediction Model": {
        "survival",
        "incidence",
        "prevalence",
        "treatment",
        "diagnostic_accuracy",
    },
    "Systematic Review": {
        "treatment",
        "survival",
        "incidence",
        "prevalence",
        "diagnostic_accuracy",
    },
}


GOAL_RECOMMENDED_DESIGNS: Dict[str, List[str]] = {
    "Survival Analysis": [
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Diagnostic Accuracy": [
        "Diagnostic Accuracy Study",
    ],
    "Incidence": [
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Prevalence": [
        "Cross-Sectional Study",
    ],
    "Trend Analysis": [
        "Retrospective Cohort Study",
        "Cross-Sectional Study",
    ],
    "Treatment Outcomes": [
        "Randomized Controlled Trial",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Risk Factors": [
        "Case-Control Study",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Prediction Model": [
        "Prediction Model Study",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    ],
    "Systematic Review": [
        "Systematic Review",
        "Meta-Analysis",
    ],
}


# ============================================================
# Context gap assessment
# ============================================================

def assess_context_gaps(
    context: ResearchContext,
) -> List[str]:
    """
    Identify missing information that prevents meaningful
    idea generation.
    """

    gaps: List[str] = []

    required_fields = {
        "Research topic": context.research_topic,
        "Population": context.population,
        "Primary outcome": context.outcome,
        "Research goal": context.research_goal,
        "Data source": context.data_source,
        "Study design": context.study_design,
    }

    for label, value in required_fields.items():
        if not _has(value):
            gaps.append(f"{label} is missing.")

    return gaps


# ============================================================
# Feasibility signals
# ============================================================

def _feasibility_signals(
    context: ResearchContext,
) -> Tuple[List[str], List[str]]:
    strengths: List[str] = []
    limitations: List[str] = []

    data_source = _lower(context.data_source)

    if _has(context.location):
        strengths.append("Study location is specified.")
    else:
        limitations.append("Study location is not specified.")

    if _has(context.study_period):
        strengths.append("Study period is specified.")
    else:
        limitations.append("Study period is not specified.")

    if data_source in {
        "hospital records",
        "registry database",
        "electronic health records (ehr)",
        "laboratory data",
        "imaging data",
    }:
        strengths.append("The proposed question can use routinely collected clinical data.")

    if data_source == "survey / questionnaire":
        strengths.append("The proposed question can be evaluated using survey data.")

    if data_source == "published literature":
        strengths.append("The proposed question can be addressed using published evidence.")

    return _unique_preserve_order(strengths), _unique_preserve_order(limitations)


# ============================================================
# Idea-level scientific checks
# ============================================================

def _idea_contains_comparison(
    title: str,
    intervention: str,
    comparator: str,
) -> bool:
    normalized = _lower(title)

    if not _has(intervention) or not _has(comparator):
        return False

    return (
        _lower(intervention) in normalized
        and _lower(comparator) in normalized
    )


def _idea_has_trend_language(title: str) -> bool:
    normalized = _lower(title)

    trend_terms = [
        "over the study period",
        "over time",
        "temporal trend",
        "annual",
        "yearly",
        "trend",
    ]

    return any(term in normalized for term in trend_terms)


def _idea_has_multiple_axes(title: str) -> bool:
    """
    Detect titles that unintentionally combine different
    research objectives.

    Example:
        "Comparison ... and factors associated with ..."
    """

    normalized = _lower(title)

    comparison_terms = [
        "comparison of",
        "compared with",
        "versus",
        "difference between",
        "comparative",
    ]

    association_terms = [
        "factors associated with",
        "predictors of",
        "determinants of",
        "association between",
    ]

    has_comparison = any(term in normalized for term in comparison_terms)
    has_association = any(term in normalized for term in association_terms)

    return has_comparison and has_association


def _scientific_focus_score(
    title: str,
    context: ResearchContext,
) -> Tuple[int, List[str], List[str]]:
    score = 10
    strengths: List[str] = []
    limitations: List[str] = []

    if _idea_has_multiple_axes(title):
        score -= 6
        limitations.append(
            "The idea mixes comparative and association objectives."
        )
    else:
        strengths.append("The idea has a single primary research objective.")

    goal = _lower(context.research_goal)

    if goal != "trend analysis" and _idea_has_trend_language(title):
        score -= 5
        limitations.append(
            "The idea introduces a time-trend objective that is not the selected research goal."
        )

    if score >= 9:
        strengths.append("The research focus is appropriately narrow.")

    return max(score, 0), strengths, limitations


# ============================================================
# Idea validation
# ============================================================

def validate_generated_idea(
    title: str,
    context: ResearchContext,
) -> Dict:
    """
    Validate one generated idea against the research context.

    Returns deterministic quality information.
    """

    title = _clean(title)

    strengths: List[str] = []
    limitations: List[str] = []
    warnings: List[str] = []

    score = 0

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    intervention = _clean(context.intervention_exposure)
    comparator = _clean(context.comparator)
    goal = _clean(context.research_goal)
    design = _clean(context.study_design)

    normalized_title = _lower(title)

    # --------------------------------------------------------
    # 1. Context fidelity — 20 points
    # --------------------------------------------------------

    context_score = 0

    if topic and _lower(topic) in normalized_title:
        context_score += 7

    if population and _lower(population) in normalized_title:
        context_score += 5

    if outcome and _lower(outcome) in normalized_title:
        context_score += 8

    score += min(context_score, 20)

    if context_score >= 18:
        strengths.append("Strong alignment with the research context.")
    elif context_score >= 12:
        strengths.append("Good alignment with the research context.")
    else:
        limitations.append("Some core context elements are not explicit in the idea.")

    # --------------------------------------------------------
    # 2. Goal alignment — 20 points
    # --------------------------------------------------------

    goal_score = 0
    expected_outcomes = GOAL_EXPECTED_OUTCOMES.get(
        goal,
        set(),
    )

    detected_outcomes = _detect_outcome_categories(outcome)

    if expected_outcomes.intersection(detected_outcomes):
        goal_score += 12

    # Goal-specific wording
    goal_patterns = {
        "Treatment Outcomes": [
            "comparison",
            "association",
            "outcome",
            "treated with",
            "treatment",
        ],
        "Risk Factors": [
            "associated with",
            "risk factors",
            "predictors",
        ],
        "Survival Analysis": [
            "survival",
            "mortality",
            "time",
        ],
        "Incidence": [
            "incidence",
            "new",
            "development",
            "occurrence",
        ],
        "Prevalence": [
            "prevalence",
        ],
        "Trend Analysis": [
            "trend",
            "over time",
            "annual",
            "yearly",
        ],
        "Diagnostic Accuracy": [
            "diagnostic",
            "sensitivity",
            "specificity",
            "accuracy",
        ],
        "Prediction Model": [
            "prediction",
            "predictors",
            "model",
        ],
        "Systematic Review": [
            "systematic review",
            "meta-analysis",
            "evidence",
        ],
    }

    patterns = goal_patterns.get(goal, [])

    if any(pattern in normalized_title for pattern in patterns):
        goal_score += 8

    score += min(goal_score, 20)

    if goal_score >= 18:
        strengths.append("Strong alignment with the selected research goal.")
    elif goal_score >= 12:
        strengths.append("Reasonable alignment with the selected research goal.")
    else:
        limitations.append(
            "The wording does not strongly express the selected research goal."
        )

    # --------------------------------------------------------
    # 3. Outcome clarity — 15 points
    # --------------------------------------------------------

    outcome_score = 0

    if outcome and _lower(outcome) in normalized_title:
        outcome_score += 15

    score += outcome_score

    if outcome_score == 15:
        strengths.append("Primary outcome is explicit.")
    else:
        limitations.append("Primary outcome is not clearly stated.")

    # --------------------------------------------------------
    # 4. Population fit — 10 points
    # --------------------------------------------------------

    population_score = 0

    if population and _lower(population) in normalized_title:
        population_score = 10
    elif population:
        population_score = 5

    score += population_score

    if population_score == 10:
        strengths.append("Target population is explicit.")
    elif population_score > 0:
        limitations.append("Population is only partially explicit.")

    # --------------------------------------------------------
    # 5. Intervention / comparator logic — 15 points
    # --------------------------------------------------------

    intervention_score = 0

    intervention_present = (
        _has(intervention)
        and _lower(intervention) in normalized_title
    )

    comparator_present = (
        _has(comparator)
        and _lower(comparator) in normalized_title
    )

    is_comparative_goal = goal in {
        "Treatment Outcomes",
        "Diagnostic Accuracy",
    }

    if intervention_present:
        intervention_score += 8

    if comparator_present:
        intervention_score += 7

    # For non-comparative ideas, do not punish the absence
    # of a comparator unless the title claims comparison.
    if not is_comparative_goal and not comparator_present:
        intervention_score = min(intervention_score + 4, 15)

    score += min(intervention_score, 15)

    if intervention_present:
        strengths.append("Intervention/exposure is clearly represented.")

    if comparator_present:
        strengths.append("Comparator is explicitly represented.")

    # --------------------------------------------------------
    # 6. Study design fit — 10 points
    # --------------------------------------------------------

    design_score = 0

    recommended = GOAL_RECOMMENDED_DESIGNS.get(goal, [])

    if design in recommended:
        design_score = 10
        strengths.append("Idea is compatible with the selected study design.")
    elif design == "Auto Detect":
        design_score = 7
        strengths.append("Study design will require final confirmation.")
    else:
        design_score = 5
        limitations.append(
            "The study design is not among the usual designs for this goal."
        )

    score += design_score

    # --------------------------------------------------------
    # 7. Feasibility — 5 points
    # --------------------------------------------------------

    feasibility_score = 0

    if _has(context.data_source):
        feasibility_score += 2

    if _has(context.location):
        feasibility_score += 1

    if _has(context.study_period):
        feasibility_score += 1

    if (
        _lower(context.data_source)
        in {
            "hospital records",
            "registry database",
            "electronic health records (ehr)",
        }
    ):
        feasibility_score += 1

    score += min(feasibility_score, 5)

    # --------------------------------------------------------
    # 8. Scientific focus — 5 points
    # --------------------------------------------------------

    focus_score, focus_strengths, focus_limitations = (
        _scientific_focus_score(title, context)
    )

    # Scale 0–10 down to maximum 5.
    focus_points = min(round(focus_score / 2), 5)

    score += focus_points

    strengths.extend(focus_strengths)
    limitations.extend(focus_limitations)

    # --------------------------------------------------------
    # Explicit penalties
    # --------------------------------------------------------

    penalty = 0

    if _idea_has_multiple_axes(title):
        penalty += 8

        warnings.append(
            "This idea combines more than one main research objective."
        )

    if (
        _lower(context.research_goal) != "trend analysis"
        and _idea_has_trend_language(title)
    ):
        penalty += 8

        warnings.append(
            "Trend language is inconsistent with the selected research goal."
        )

    # A comparative title must actually contain both sides.
    if any(
        term in normalized_title
        for term in ["versus", "compared with", "comparison of", "difference between"]
    ):
        if not comparator_present:
            penalty += 5

            warnings.append(
                "The idea is framed as comparative but no comparator is explicit."
            )

    final_score = max(0, min(100, score - penalty))

    # --------------------------------------------------------
    # Quality label
    # --------------------------------------------------------

    if final_score >= 90:
        quality = "Strong Candidate"
    elif final_score >= 80:
        quality = "Good Candidate"
    elif final_score >= 70:
        quality = "Moderate Candidate"
    else:
        quality = "Needs Refinement"

    return {
        "score": final_score,
        "quality": quality,
        "strengths": _unique_preserve_order(strengths),
        "limitations": _unique_preserve_order(limitations),
        "warnings": _unique_preserve_order(warnings),
        "novelty_status": "Not assessed yet",
    }


# ============================================================
# Treatment Outcomes ideas
# ============================================================

def _generate_treatment_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    intervention = _clean(context.intervention_exposure)
    comparator = _clean(context.comparator)
    design = _design(context)

    ideas: List[ResearchIdea] = []

    # --------------------------------------------------------
    # Idea 1 — Direct comparative effectiveness
    # --------------------------------------------------------

    if intervention and comparator:
        title = (
            f"Comparison of {intervention} and {comparator} "
            f"for {outcome} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "Directly compares the specified intervention and comparator "
                    "using the primary outcome in the defined population."
                ),
                study_design=design,
                research_goal=context.research_goal,
                strengths=[
                    "Directly addresses the treatment comparison.",
                    "Primary outcome is explicit.",
                    "Population is explicit.",
                ],
                limitations=[],
                warnings=[],
            )
        )

    # --------------------------------------------------------
    # Idea 2 — Association with treatment exposure
    # --------------------------------------------------------

    if intervention:
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
                    "Evaluates whether exposure to the specified treatment "
                    "is associated with the primary outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
                strengths=[
                    "Uses a single clearly defined exposure.",
                    "Primary outcome is explicit.",
                    "Suitable for observational treatment-outcome analysis.",
                ],
                limitations=[
                    "Observational association does not by itself establish causality."
                ],
                warnings=[],
            )
        )

    # --------------------------------------------------------
    # Idea 3 — Real-world treatment outcome
    # --------------------------------------------------------

    if intervention:
        title = (
            f"Real-world {outcome} among {population} "
            f"treated with {intervention}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "Describes the observed treatment outcome among patients "
                    "receiving the specified intervention in routine practice."
                ),
                study_design=design,
                research_goal=context.research_goal,
                strengths=[
                    "Clearly focused on a real-world treatment outcome.",
                    "Primary outcome is explicit.",
                    "Can be aligned with routinely collected clinical data.",
                ],
                limitations=[
                    "Without a comparator, causal treatment effects are limited."
                ],
                warnings=[],
            )
        )

    # --------------------------------------------------------
    # Idea 4 — Outcome difference
    # --------------------------------------------------------

    if intervention and comparator:
        title = (
            f"Difference in {outcome} between patients receiving "
            f"{intervention} and {comparator} among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "Estimates the difference in the primary outcome between "
                    "the two specified treatment groups."
                ),
                study_design=design,
                research_goal=context.research_goal,
                strengths=[
                    "Keeps one primary treatment-comparison objective.",
                    "Explicitly defines both treatment groups.",
                    "Primary outcome is explicit.",
                ],
                limitations=[
                    "Confounding should be considered in observational designs."
                ],
                warnings=[],
            )
        )

    # --------------------------------------------------------
    # Idea 5 — Treatment response
    # --------------------------------------------------------

    if intervention:
        title = (
            f"Treatment response in {outcome} among {population} "
            f"receiving {intervention}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "Focuses on the observed response to the specified "
                    "intervention without introducing a second research objective."
                ),
                study_design=design,
                research_goal=context.research_goal,
                strengths=[
                    "Single focused treatment-response objective.",
                    "Primary outcome is explicit.",
                    "Does not introduce an unsupported literature gap.",
                ],
                limitations=[
                    "A comparator is not included in this formulation."
                ],
                warnings=[],
            )
        )

    return ideas


# ============================================================
# Risk Factors
# ============================================================

def _generate_risk_factor_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    ideas: List[ResearchIdea] = []

    title = (
        f"Factors associated with {outcome} among {population}"
    )

    ideas.append(
        ResearchIdea(
            title=title,
            rationale=(
                "Identifies factors associated with the selected outcome "
                "in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Directly targets risk-factor identification.",
                "Primary outcome is explicit.",
                "Population is explicit.",
            ],
            limitations=[
                "Potential confounding should be addressed."
            ],
            warnings=[],
        )
    )

    if context.intervention_exposure:
        exposure = _clean(context.intervention_exposure)

        title = (
            f"Association between {exposure} and {outcome} "
            f"among {population}"
        )

        ideas.append(
            ResearchIdea(
                title=title,
                rationale=(
                    "Examines the association between the specified exposure "
                    "and the primary outcome."
                ),
                study_design=design,
                research_goal=context.research_goal,
                strengths=[
                    "Clearly defined exposure.",
                    "Clearly defined outcome.",
                ],
                limitations=[
                    "Association should not be interpreted as causation without appropriate design and analysis."
                ],
                warnings=[],
            )
        )

    return ideas


# ============================================================
# Survival
# ============================================================

def _generate_survival_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    return [
        ResearchIdea(
            title=(
                f"Survival outcomes among {population} "
                f"with {topic}"
            ),
            rationale=(
                f"Evaluates {outcome} in the specified population."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Focused on a survival-related outcome.",
                "Population is explicit.",
            ],
            limitations=[],
            warnings=[],
        )
    ]


# ============================================================
# Incidence
# ============================================================

def _generate_incidence_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    return [
        ResearchIdea(
            title=(
                f"Incidence of {outcome} among {population}"
            ),
            rationale=(
                "Estimates occurrence of the specified outcome in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Directly targets incidence.",
                "Population is explicit.",
            ],
            limitations=[],
            warnings=[],
        )
    ]


# ============================================================
# Prevalence
# ============================================================

def _generate_prevalence_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    return [
        ResearchIdea(
            title=(
                f"Prevalence of {outcome} among {population}"
            ),
            rationale=(
                "Estimates the prevalence of the selected outcome in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Directly targets prevalence.",
                "Population is explicit.",
            ],
            limitations=[],
            warnings=[],
        )
    ]


# ============================================================
# Trend Analysis
# ============================================================

def _generate_trend_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    return [
        ResearchIdea(
            title=(
                f"Temporal trends in {outcome} among {population}"
            ),
            rationale=(
                "Evaluates how the selected outcome changes over time "
                "in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Explicitly targets temporal change.",
                "Outcome is explicit.",
                "Population is explicit.",
            ],
            limitations=[],
            warnings=[],
        )
    ]


# ============================================================
# Diagnostic Accuracy
# ============================================================

def _generate_diagnostic_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    intervention = _clean(context.intervention_exposure)
    design = _design(context)

    test_name = intervention or "the diagnostic test"

    return [
        ResearchIdea(
            title=(
                f"Diagnostic accuracy of {test_name} "
                f"for {outcome} among {population}"
            ),
            rationale=(
                "Evaluates diagnostic performance using the specified outcome "
                "in the defined population."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Diagnostic test is explicit.",
                "Diagnostic outcome is explicit.",
                "Population is explicit.",
            ],
            limitations=[],
            warnings=[],
        )
    ]


# ============================================================
# Prediction Model
# ============================================================

def _generate_prediction_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    return [
        ResearchIdea(
            title=(
                f"Prediction of {outcome} among {population}"
            ),
            rationale=(
                "Develops or evaluates a prediction approach for the specified outcome."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Prediction target is explicit.",
                "Population is explicit.",
            ],
            limitations=[
                "Predictor selection and model validation will need to be defined later."
            ],
            warnings=[],
        )
    ]


# ============================================================
# Systematic Review
# ============================================================

def _generate_systematic_review_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _clean(context.population)
    outcome = _clean(context.outcome)
    intervention = _clean(context.intervention_exposure)
    comparator = _clean(context.comparator)
    design = _design(context)

    if intervention and comparator:
        title = (
            f"Systematic review of {intervention} versus {comparator} "
            f"for {outcome} among {population}"
        )
    elif intervention:
        title = (
            f"Systematic review of {intervention} "
            f"for {outcome} among {population}"
        )
    else:
        title = (
            f"Systematic review of {outcome} among {population}"
        )

    return [
        ResearchIdea(
            title=title,
            rationale=(
                "Synthesizes published evidence addressing the specified "
                "population, intervention/exposure, comparator, and outcome."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Structured around explicit evidence-synthesis elements.",
                "Outcome is explicit.",
                "Population is explicit.",
            ],
            limitations=[
                "A literature search is required before judging the evidence gap or novelty."
            ],
            warnings=[],
        )
    ]


# ============================================================
# Generic idea
# ============================================================

def _generate_generic_idea(
    context: ResearchContext,
) -> List[ResearchIdea]:

    topic = _clean(context.research_topic)
    population = _format_population(
        context.population,
        topic,
    )
    outcome = _clean(context.outcome)
    design = _design(context)

    return [
        ResearchIdea(
            title=(
                f"{outcome} among {population}"
            ),
            rationale=(
                "A focused starting point based on the supplied research context."
            ),
            study_design=design,
            research_goal=context.research_goal,
            strengths=[
                "Uses the supplied population and outcome.",
            ],
            limitations=[
                "The research objective may require further refinement."
            ],
            warnings=[],
        )
    ]


# ============================================================
# Generate ideas
# ============================================================

def generate_research_ideas(
    context: ResearchContext,
) -> List[ResearchIdea]:
    """
    Generate candidate ideas according to the selected research goal.

    Important:
    - No literature gap is claimed.
    - No novelty is claimed.
    - No AI is used.
    - Weak ideas are not forced merely to reach five candidates.
    """

    gaps = assess_context_gaps(context)

    if gaps:
        return []

    goal = _clean(context.research_goal)

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
        ideas = _generate_generic_idea(context)

    return _unique_ideas(ideas)


# ============================================================
# Deduplication
# ============================================================

def _idea_similarity_key(title: str) -> str:
    normalized = _lower(title)

    normalized = re.sub(
        r"[^a-z0-9\s]",
        " ",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()

    return normalized


def _unique_ideas(
    ideas: List[ResearchIdea],
) -> List[ResearchIdea]:

    seen = set()
    unique: List[ResearchIdea] = []

    for idea in ideas:
        key = _idea_similarity_key(idea.title)

        if key in seen:
            continue

        seen.add(key)
        unique.append(idea)

    return unique


# ============================================================
# Ranking
# ============================================================

def rank_ideas(
    ideas: List[ResearchIdea],
    context: ResearchContext,
) -> List[Tuple[ResearchIdea, Dict]]:
    """
    Validate and rank ideas using deterministic quality scoring.

    Returns:
        [(idea, assessment), ...]
    """

    scored: List[Tuple[ResearchIdea, Dict]] = []

    for idea in ideas:
        assessment = validate_generated_idea(
            idea.title,
            context,
        )

        scored.append(
            (
                idea,
                assessment,
            )
        )

    # --------------------------------------------------------
    # Diversity / redundancy penalty
    # --------------------------------------------------------

    ranked: List[Tuple[ResearchIdea, Dict]] = []

    for index, (idea, assessment) in enumerate(scored):

        score = assessment["score"]

        title_lower = _lower(idea.title)

        # Penalize secondary ideas that are almost identical
        # to the direct comparison.
        if index > 0:
            previous_titles = [
                _lower(previous_idea.title)
                for previous_idea, _ in scored[:index]
            ]

            for previous_title in previous_titles:
                common_terms = {
                    token
                    for token in _tokens(title_lower)
                    if token in _tokens(previous_title)
                }

                if len(common_terms) >= 8:
                    score -= 3
                    break

        assessment["score"] = max(0, min(100, score))

        if assessment["score"] >= 90:
            assessment["quality"] = "Strong Candidate"
        elif assessment["score"] >= 80:
            assessment["quality"] = "Good Candidate"
        elif assessment["score"] >= 70:
            assessment["quality"] = "Moderate Candidate"
        else:
            assessment["quality"] = "Needs Refinement"

        ranked.append(
            (
                idea,
                assessment,
            )
        )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    ranked.sort(
        key=lambda item: (
            item[1]["score"],
            -len(item[1]["warnings"]),
            -len(item[1]["limitations"]),
        ),
        reverse=True,
    )

    return ranked


# ============================================================
# Combined generation + ranking
# ============================================================

def generate_and_rank_research_ideas(
    context: ResearchContext,
    max_ideas: int | None = None,
) -> List[Tuple[ResearchIdea, Dict]]:
    """
    Main Step 2 API.

    Parameters
    ----------
    context:
        Current ResearchContext.

    max_ideas:
        Optional maximum number of ideas to return.
        If None, all generated ideas are returned.

    Returns
    -------
    List[Tuple[ResearchIdea, Dict]]
        Ranked ideas with their deterministic quality assessments.

    Notes
    -----
    - No AI is used.
    - No literature gap is claimed.
    - Novelty is not assessed at this stage.
    """

    ideas = generate_research_ideas(context)

    if not ideas:
        return []

    ranked = rank_ideas(
        ideas,
        context,
    )

    if max_ideas is not None:
        if max_ideas <= 0:
            return []

        ranked = ranked[:max_ideas]

    return ranked
