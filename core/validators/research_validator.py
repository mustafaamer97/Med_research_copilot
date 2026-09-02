from core.models.research_project import (
    ResearchContext,
    ValidationMessage,
)

from core.rules.research_rules import (
    REQUIRED_CONTEXT_FIELDS,
    DATA_SOURCE_DESIGNS,
    OUTCOME_KEYWORDS,
    GOAL_OUTCOME_CATEGORIES,
    GOAL_STUDY_DESIGNS,
)


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _detect_outcome_categories(outcome: str) -> set[str]:
    """
    Detect broad outcome categories from the user's outcome text.

    This is intentionally conservative.
    Failure to detect a category does NOT mean the outcome is invalid.
    """

    normalized = _normalize(outcome)

    detected = set()

    for category, keywords in OUTCOME_KEYWORDS.items():

        for keyword in keywords:

            if _normalize(keyword) in normalized:
                detected.add(category)
                break

    # Risk-factor style outcomes
    if (
        "development of" in normalized
        or "occurrence of" in normalized
        or "new onset" in normalized
        or normalized.startswith("risk of")
    ):
        detected.add("incidence")

    # Trend-style outcomes
    if (
        "annual" in normalized
        and "incidence" in normalized
    ):
        detected.add("trend")

    if (
        "yearly" in normalized
        and "incidence" in normalized
    ):
        detected.add("trend")

    if (
        "annual" in normalized
        and "mortality" in normalized
    ):
        detected.add("trend")

    if (
        "yearly" in normalized
        and "mortality" in normalized
    ):
        detected.add("trend")

    if "over time" in normalized:
        detected.add("trend")

    return detected


def validate_context(
    context: ResearchContext,
) -> list[ValidationMessage]:

    messages: list[ValidationMessage] = []

    # =====================================================
    # 1. Required fields
    # =====================================================

    for field_name, display_name in REQUIRED_CONTEXT_FIELDS.items():

        value = getattr(context, field_name, "").strip()

        if not value:

            messages.append(
                ValidationMessage(
                    level="ERROR",
                    field=field_name,
                    message=f"{display_name} is required.",
                )
            )

    # =====================================================
    # 2. Data Source ↔ Study Design
    # =====================================================

    if context.data_source and context.study_design:

        allowed_designs = DATA_SOURCE_DESIGNS.get(
            context.data_source
        )

        if (
            allowed_designs
            and context.study_design != "Auto Detect"
            and context.study_design not in allowed_designs
        ):

            messages.append(
                ValidationMessage(
                    level="ERROR",
                    field="study_design",
                    message=(
                        f"'{context.study_design}' is not currently "
                        f"supported with '{context.data_source}' "
                        f"in the Phase 1 rule set."
                    ),
                )
            )

    # =====================================================
    # 3. Research Goal ↔ Outcome
    # =====================================================

    if context.research_goal and context.outcome:

        expected_categories = GOAL_OUTCOME_CATEGORIES.get(
            context.research_goal
        )

        detected_categories = _detect_outcome_categories(
            context.outcome
        )

        if expected_categories and not (
            expected_categories & detected_categories
        ):

            messages.append(
                ValidationMessage(
                    level="WARNING",
                    field="outcome",
                    message=(
                        f"The outcome '{context.outcome}' may not "
                        f"match the research goal "
                        f"'{context.research_goal}'. "
                        f"Please confirm that the outcome directly "
                        f"answers the stated research goal."
                    ),
                )
            )

    # =====================================================
    # 4. Research Goal ↔ Study Design
    # =====================================================

    if (
        context.research_goal
        and context.study_design
        and context.study_design != "Auto Detect"
    ):

        recommended_designs = GOAL_STUDY_DESIGNS.get(
            context.research_goal
        )

        if (
            recommended_designs
            and context.study_design not in recommended_designs
        ):

            messages.append(
                ValidationMessage(
                    level="WARNING",
                    field="study_design",
                    message=(
                        f"'{context.study_design}' is not among "
                        f"the usual study designs for "
                        f"'{context.research_goal}'. "
                        f"Review whether the design is appropriate "
                        f"for the research objective."
                    ),
                )
            )

    # =====================================================
    # 5. Optional information
    # =====================================================

    if not context.location.strip():

        messages.append(
            ValidationMessage(
                level="WARNING",
                field="location",
                message="Study location has not been specified.",
            )
        )

    if not context.study_period.strip():

        messages.append(
            ValidationMessage(
                level="WARNING",
                field="study_period",
                message="Study period has not been specified.",
            )
        )

    return messages
