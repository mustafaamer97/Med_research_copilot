import streamlit as st

from core.models.research_project import ResearchProject
from core.rules.research_rules import STUDY_DESIGNS
from core.validators.research_validator import validate_context


# ============================================================
# Constants
# ============================================================

DATA_SOURCES = [
    "Hospital Records",
    "Registry Database",
    "Survey / Questionnaire",
    "Published Literature",
]

RESEARCH_TYPES = [
    "Primary Research",
    "Secondary Research",
    "Evidence Synthesis",
]

RESEARCH_GOALS = [
    "Trend Analysis",
    "Incidence",
    "Prevalence",
    "Risk Factors",
    "Treatment Outcomes",
    "Survival Analysis",
    "Diagnostic Accuracy",
    "Prediction Model",
    "Systematic Review",
]


# ============================================================
# Auto Detect Design
# ============================================================

def auto_detect_design(
    goal: str,
    data_source: str,
) -> str:

    if data_source == "Published Literature":
        return "Systematic Review"

    if goal == "Prevalence":
        return "Cross-Sectional Study"

    if goal == "Incidence":
        return "Retrospective Cohort Study"

    if goal == "Trend Analysis":
        return "Retrospective Cohort Study"

    if goal == "Risk Factors":
        return "Case-Control Study"

    if goal == "Treatment Outcomes":
        return "Retrospective Cohort Study"

    if goal == "Diagnostic Accuracy":
        return "Diagnostic Accuracy Study"

    if goal == "Prediction Model":
        return "Prediction Model Study"

    if goal == "Survival Analysis":
        return "Retrospective Cohort Study"

    return "Cross-Sectional Study"


# ============================================================
# Step 1
# ============================================================

def render_step1(
    project: ResearchProject,
) -> ResearchProject:

    st.header("🧭 Step 1 — Research Context")

    st.write(
        "Define the research context before generating ideas "
        "or building a research question."
    )

    context = project.context

    # --------------------------------------------------------
    # Research Type
    # --------------------------------------------------------

    context.research_type = st.selectbox(
        "Research Type",
        RESEARCH_TYPES,
        index=(
            RESEARCH_TYPES.index(
                context.research_type
            )
            if context.research_type in RESEARCH_TYPES
            else 0
        ),
    )

    # --------------------------------------------------------
    # Topic
    # --------------------------------------------------------

    context.research_topic = st.text_input(
        "Research Topic",
        value=context.research_topic,
        placeholder="e.g. Type 2 Diabetes Mellitus",
    )

    # --------------------------------------------------------
    # Population
    # --------------------------------------------------------

    context.population = st.text_input(
        "Population",
        value=context.population,
        placeholder="e.g. Adults with Type 2 Diabetes",
    )

    # --------------------------------------------------------
    # Exposure
    # --------------------------------------------------------

    context.intervention_exposure = st.text_input(
        "Intervention / Exposure",
        value=context.intervention_exposure,
        placeholder="e.g. GLP-1 receptor agonists",
    )

    # --------------------------------------------------------
    # Comparator
    # --------------------------------------------------------

    context.comparator = st.text_input(
        "Comparator",
        value=context.comparator,
        placeholder="e.g. Metformin",
    )

    # --------------------------------------------------------
    # Outcome
    # --------------------------------------------------------

    context.outcome = st.text_input(
        "Primary Outcome",
        value=context.outcome,
        placeholder="e.g. HbA1c Reduction",
    )

    # --------------------------------------------------------
    # Goal
    # --------------------------------------------------------

    context.research_goal = st.selectbox(
        "Research Goal",
        RESEARCH_GOALS,
        index=(
            RESEARCH_GOALS.index(
                context.research_goal
            )
            if context.research_goal in RESEARCH_GOALS
            else 0
        ),
    )

    # --------------------------------------------------------
    # Data Source
    # --------------------------------------------------------

    context.data_source = st.selectbox(
        "Available Data Source",
        DATA_SOURCES,
        index=(
            DATA_SOURCES.index(
                context.data_source
            )
            if context.data_source in DATA_SOURCES
            else 0
        ),
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    context.location = st.text_input(
        "Study Location",
        value=context.location,
        placeholder="e.g. Sana'a, Yemen",
    )

    # --------------------------------------------------------
    # Study Period
    # --------------------------------------------------------

    context.study_period = st.text_input(
        "Study Period",
        value=context.study_period,
        placeholder="e.g. 2020–2025",
    )

    # --------------------------------------------------------
    # Study Design
    # --------------------------------------------------------

    context.study_design = st.selectbox(
        "Study Design",
        STUDY_DESIGNS,
        index=(
            STUDY_DESIGNS.index(
                context.study_design
            )
            if context.study_design in STUDY_DESIGNS
            else 0
        ),
    )

    # --------------------------------------------------------
    # Auto Detect Recommendation
    # --------------------------------------------------------

    if context.study_design == "Auto Detect":

        detected_design = auto_detect_design(
            context.research_goal,
            context.data_source,
        )

        st.info(
            f"Recommended Design: {detected_design}"
        )

    # --------------------------------------------------------
    # Context Summary
    # --------------------------------------------------------

    st.divider()

    st.subheader("📋 Research Context Summary")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Topic:** "
            f"{context.research_topic or 'Not specified'}"
        )

        st.write(
            f"**Population:** "
            f"{context.population or 'Not specified'}"
        )

        st.write(
            f"**Outcome:** "
            f"{context.outcome or 'Not specified'}"
        )

    with col2:

        st.write(
            f"**Goal:** "
            f"{context.research_goal or 'Not specified'}"
        )

        st.write(
            f"**Data Source:** "
            f"{context.data_source or 'Not specified'}"
        )

        st.write(
            f"**Design:** "
            f"{context.study_design or 'Not specified'}"
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "✅ Validate Research Context",
        type="primary",
        use_container_width=True,
    ):

        project.clear_validation()

        project.validation_messages = (
            validate_context(context)
        )

        if project.has_errors:

            st.error(
                "Research context contains errors."
            )

        elif project.has_warnings:

            st.warning(
                "Research context is valid but "
                "contains warnings."
            )

        else:

            st.success(
                "Research context is valid."
            )

    # --------------------------------------------------------
    # Validation Results
    # --------------------------------------------------------

    if project.validation_messages:

        st.subheader("🔍 Validation Results")

        for message in (
            project.validation_messages
        ):

            if message.level == "ERROR":

                st.error(
                    f"**{message.field}** — "
                    f"{message.message}"
                )

            elif message.level == "WARNING":

                st.warning(
                    f"**{message.field}** — "
                    f"{message.message}"
                )

    # --------------------------------------------------------
    # Step Readiness
    # --------------------------------------------------------

    if (
        project.validation_messages
        and not project.has_errors
    ):

        st.success(
            "🎯 Step 1 completed successfully. "
            "You can now proceed to Step 2."
        )

    return project
