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
    GOAL_REQUIRED_FIELDS,
)


# ============================================================
# Helpers
# ============================================================

def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _detect_outcome_categories(
    outcome: str,
) -> set[str]:
    """
    Detect broad outcome categories from the outcome text.

    Conservative classification:
    Failure to detect a category does not imply
    that the outcome is invalid.
    """

    normalized = _normalize(outcome)

    detected: set[str] = set()

    for category, keywords in OUTCOME_KEYWORDS.items():

        for keyword in keywords:

            if _normalize(keyword) in normalized:
                detected.add(category)
                break

    # -----------------------------------------
    # Extra deterministic rules
    # -----------------------------------------

    if (
        "development of" in normalized
        or "occurrence of" in normalized
        or "new onset" in normalized
        or normalized.startswith("risk of")
    ):
        detected.add("incidence")

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


# ============================================================
# Main Validator
# ============================================================

def validate_context(
    context: ResearchContext,
) -> list[ValidationMessage]:

    messages: list[ValidationMessage] = []

    # =====================================================
    # 1. Required Fields
    # =====================================================

    for field_name, display_name in (
        REQUIRED_CONTEXT_FIELDS.items()
    ):

        value = getattr(
            context,
            field_name,
            "",
        )

        if not str(value).strip():

            messages.append(
                ValidationMessage(
                    level="ERROR",
                    field=field_name,
                    message=f"{display_name} is required.",
                )
            )

    # Stop early if required fields are missing
    if any(msg.level == "ERROR" for msg in messages):
        return messages

    # =====================================================
    # 2. Data Source ↔ Study Design
    # =====================================================

    if (
        context.data_source
        and context.study_design
        and context.study_design != "Auto Detect"
    ):

        allowed_designs = DATA_SOURCE_DESIGNS.get(
            context.data_source
        )

        if (
            allowed_designs
            and context.study_design
            not in allowed_designs
        ):

            messages.append(
                ValidationMessage(
                    level="ERROR",
                    field="study_design",
                    message=(
                        f"'{context.study_design}' is not supported "
                        f"with '{context.data_source}'."
                    ),
                )
            )

    # =====================================================
    # 3. Goal ↔ Outcome Consistency
    # =====================================================

    if (
        context.research_goal
        and context.outcome
    ):

        expected_categories = (
            GOAL_OUTCOME_CATEGORIES.get(
                context.research_goal
            )
        )

        detected_categories = (
            _detect_outcome_categories(
                context.outcome
            )
        )

        if (
            expected_categories
            and detected_categories
            and not (
                expected_categories
                & detected_categories
            )
        ):

            messages.append(
                ValidationMessage(
                    level="WARNING",
                    field="outcome",
                    message=(
                        f"The outcome may not fully align "
                        f"with the selected research goal "
                        f"('{context.research_goal}')."
                    ),
                )
            )

    # =====================================================
    # 4. Goal ↔ Study Design
    # =====================================================

    if (
        context.research_goal
        and context.study_design
        and context.study_design != "Auto Detect"
    ):

        recommended_designs = (
            GOAL_STUDY_DESIGNS.get(
                context.research_goal
            )
        )

        if (
            recommended_designs
            and context.study_design
            not in recommended_designs
        ):

            messages.append(
                ValidationMessage(
                    level="WARNING",
                    field="study_design",
                    message=(
                        f"'{context.study_design}' is not among "
                        f"the usual study designs for "
                        f"'{context.research_goal}'."
                    ),
                )
            )

    # =====================================================
    # 5. Goal-Specific Required Fields
    # =====================================================

    required_fields = (
        GOAL_REQUIRED_FIELDS.get(
            context.research_goal,
            set(),
        )
    )

    for field_name in required_fields:

        value = getattr(
            context,
            field_name,
            "",
        )

        if not str(value).strip():

            display_name = (
                field_name
                .replace("_", " ")
                .title()
            )

            messages.append(
                ValidationMessage(
                    level="ERROR",
                    field=field_name,
                    message=(
                        f"{display_name} is required "
                        f"for '{context.research_goal}'."
                    ),
                )
            )

    # =====================================================
    # 6. Optional Context Warnings
    # =====================================================

    if not context.location.strip():

        messages.append(
            ValidationMessage(
                level="WARNING",
                field="location",
                message=(
                    "Study location has not been specified."
                ),
            )
        )

    if not context.study_period.strip():

        messages.append(
            ValidationMessage(
                level="WARNING",
                field="study_period",
                message=(
                    "Study period has not been specified."
                ),
            )
        )

    return messages
