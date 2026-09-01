from core.models.research_project import ResearchContext, ValidationMessage
from core.rules.research_rules import (
    REQUIRED_CONTEXT_FIELDS,
    DATA_SOURCE_DESIGNS,
)


def validate_context(context: ResearchContext) -> list[ValidationMessage]:
    messages: list[ValidationMessage] = []

    # -----------------------------------------
    # Required fields
    # -----------------------------------------
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

    # -----------------------------------------
    # Study design / data source compatibility
    # -----------------------------------------
    if context.data_source and context.study_design:
        allowed_designs = DATA_SOURCE_DESIGNS.get(context.data_source)

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
                        f"'{context.study_design}' is not currently supported "
                        f"with '{context.data_source}' in the Phase 1 rule set."
                    ),
                )
            )

    # -----------------------------------------
    # Optional information
    # -----------------------------------------
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
