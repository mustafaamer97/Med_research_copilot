import streamlit as st

from core.models.research_project import ResearchContext, ResearchProject
from core.rules.research_rules import STUDY_DESIGNS
from core.validators.research_validator import validate_context


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


def render_step1(project: ResearchProject) -> ResearchProject:

    st.header("🧭 Step 1 — Research Context")

    st.write(
        "Define the basic research context before building the research question."
    )

    context = project.context

    context.research_type = st.selectbox(
        "Research Type",
        RESEARCH_TYPES,
        index=(
            RESEARCH_TYPES.index(context.research_type)
            if context.research_type in RESEARCH_TYPES
            else 0
        ),
    )

    context.research_topic = st.text_input(
        "Research Topic",
        value=context.research_topic,
        placeholder="e.g. Type 2 Diabetes Mellitus",
    )

    context.population = st.text_input(
        "Population",
        value=context.population,
        placeholder="e.g. Adults with Type 2 Diabetes",
    )

    context.intervention_exposure = st.text_input(
        "Intervention / Exposure",
        value=context.intervention_exposure,
        placeholder="e.g. GLP-1 receptor agonists",
    )

    context.comparator = st.text_input(
        "Comparator",
        value=context.comparator,
        placeholder="e.g. Metformin",
    )

    context.outcome = st.text_input(
        "Primary Outcome",
        value=context.outcome,
        placeholder="e.g. HbA1c reduction",
    )

    context.research_goal = st.selectbox(
        "Research Goal",
        RESEARCH_GOALS,
        index=(
            RESEARCH_GOALS.index(context.research_goal)
            if context.research_goal in RESEARCH_GOALS
            else 0
        ),
    )

    context.data_source = st.selectbox(
        "Available Data Source",
        DATA_SOURCES,
        index=(
            DATA_SOURCES.index(context.data_source)
            if context.data_source in DATA_SOURCES
            else 0
        ),
    )

    context.location = st.text_input(
        "Study Location",
        value=context.location,
        placeholder="e.g. Sana'a, Yemen",
    )

    context.study_period = st.text_input(
        "Study Period",
        value=context.study_period,
        placeholder="e.g. 2020–2025",
    )

    context.study_design = st.selectbox(
        "Study Design",
        STUDY_DESIGNS,
        index=(
            STUDY_DESIGNS.index(context.study_design)
            if context.study_design in STUDY_DESIGNS
            else 0
        ),
    )

    st.divider()

    if st.button("Validate Research Context", type="primary"):

        project.clear_validation()

        project.validation_messages = validate_context(context)

        if project.has_errors:
            st.error("Research context contains errors.")

        elif project.has_warnings:
            st.warning("Research context is valid but incomplete.")

        else:
            st.success("Research context is valid.")

    if project.validation_messages:

        st.subheader("Validation Results")

        for message in project.validation_messages:

            if message.level == "ERROR":
                st.error(f"**{message.field}** — {message.message}")

            elif message.level == "WARNING":
                st.warning(f"**{message.field}** — {message.message}")

    return project
