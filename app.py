import streamlit as st

from core.models.research_project import ResearchProject
from workflow.step1_context import render_step1


st.set_page_config(
    page_title="Med Research Copilot",
    page_icon="🧬",
    layout="wide",
)


st.title("🧬 Med Research Copilot")

st.caption(
    "A structured research methodology assistant."
)


if "research_project" not in st.session_state:
    st.session_state.research_project = ResearchProject()


project = st.session_state.research_project


render_step1(project)


st.divider()

st.subheader("Current Research Context")

st.json({
    "research_type": project.context.research_type,
    "research_topic": project.context.research_topic,
    "population": project.context.population,
    "intervention_exposure": project.context.intervention_exposure,
    "comparator": project.context.comparator,
    "outcome": project.context.outcome,
    "research_goal": project.context.research_goal,
    "data_source": project.context.data_source,
    "location": project.context.location,
    "study_period": project.context.study_period,
    "study_design": project.context.study_design,
})
