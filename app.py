import streamlit as st

from core.models.research_project import (
    ResearchProject,
)

from workflow.step1_context import (
    render_step1,
)

from workflow.step2_ideas import (
    render_step2,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Med Research Copilot",
    page_icon="🧬",
    layout="wide",
)


# ============================================================
# APP TITLE
# ============================================================

st.title(
    "🧬 Med Research Copilot"
)

st.caption(
    "A structured research methodology assistant."
)


# ============================================================
# SESSION STATE
# ============================================================

if "research_project" not in st.session_state:

    st.session_state.research_project = (
        ResearchProject()
    )


project = st.session_state.research_project


# ============================================================
# NAVIGATION
# ============================================================

st.sidebar.title(
    "Research Workflow"
)

step = st.sidebar.radio(
    "Current Step",
    [
        "Step 1 — Research Context",
        "Step 2 — Research Ideas",
    ],
)


# ============================================================
# STEP 1
# ============================================================

if step == "Step 1 — Research Context":

    render_step1(project)


# ============================================================
# STEP 2
# ============================================================

elif step == "Step 2 — Research Ideas":

    render_step2(project)


# ============================================================
# CURRENT CONTEXT
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "Project Status"
)

if project.context.research_topic:

    st.sidebar.success(
        "✓ Research Context"
    )

else:

    st.sidebar.warning(
        "○ Research Context"
    )


if project.generated_ideas:

    st.sidebar.success(
        "✓ Research Ideas"
    )

else:

    st.sidebar.info(
        "○ Research Ideas"
    )


if project.selected_idea:

    st.sidebar.success(
        "✓ Idea Selected"
    )

else:

    st.sidebar.info(
        "○ No Idea Selected"
    )


# ============================================================
# DEBUG / CURRENT CONTEXT
# ============================================================

st.divider()

with st.expander(
    "🔧 Current Research Context"
):

    st.json(
        {
            "research_type":
                project.context.research_type,

            "research_topic":
                project.context.research_topic,

            "population":
                project.context.population,

            "intervention_exposure":
                project.context.intervention_exposure,

            "comparator":
                project.context.comparator,

            "outcome":
                project.context.outcome,

            "research_goal":
                project.context.research_goal,

            "data_source":
                project.context.data_source,

            "location":
                project.context.location,

            "study_period":
                project.context.study_period,

            "study_design":
                project.context.study_design,

            "generated_ideas":
                len(project.generated_ideas),

            "selected_idea":
                (
                    project.selected_idea.title
                    if project.selected_idea
                    else None
                ),
        }
    )
