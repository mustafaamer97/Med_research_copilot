# ============================================================
# Med Research Copilot
# Step 2 — Research Idea Generation & Gap Analysis
# Version: 0.2
# ============================================================

from __future__ import annotations

import streamlit as st

from core.idea_generator import (
    assess_context_gaps,
    generate_and_rank_research_ideas,
)
from core.models.research_project import ResearchProject


# ============================================================
# UI helpers
# ============================================================

def _score_label(score: int) -> str:
    if score >= 80:
        return "🟢 Strong Candidate"
    if score >= 65:
        return "🟡 Good Candidate"
    if score >= 50:
        return "🟠 Needs Refinement"

    return "🔴 Reject / Regenerate"


def _show_context(project: ResearchProject) -> None:
    context = project.context

    st.subheader("📋 Research Context")

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            f"**Research Topic:** "
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

        st.write(
            f"**Research Goal:** "
            f"{context.research_goal or 'Not specified'}"
        )

    with col2:
        st.write(
            f"**Intervention / Exposure:** "
            f"{context.intervention_exposure or 'Not specified'}"
        )

        st.write(
            f"**Comparator:** "
            f"{context.comparator or 'Not specified'}"
        )

        st.write(
            f"**Data Source:** "
            f"{context.data_source or 'Not specified'}"
        )

        st.write(
            f"**Study Design:** "
            f"{context.study_design or 'Auto Detect'}"
        )


def _show_context_gaps(
    project: ResearchProject,
) -> bool:
    """
    Show context gaps.

    Returns True when essential information is missing.
    """

    gaps = assess_context_gaps(
        project.context
    )

    st.subheader("🔎 Context & Design Check")

    essential_missing = {
        "Research topic is missing.",
        "Target population is missing.",
        "Primary outcome is missing.",
        "Research goal is missing.",
        "Available data source is missing.",
    }

    hard_gaps = [
        gap
        for gap in gaps
        if gap in essential_missing
    ]

    soft_gaps = [
        gap
        for gap in gaps
        if gap not in essential_missing
    ]

    if hard_gaps:
        st.error(
            "Idea generation cannot proceed because "
            "essential research context is missing."
        )

        for gap in hard_gaps:
            st.write(f"• {gap}")

        return True

    if soft_gaps:
        st.warning(
            "The context is sufficient for preliminary idea "
            "generation, but some elements should be refined."
        )

        for gap in soft_gaps:
            st.write(f"• {gap}")

    else:
        st.success(
            "The research context contains the minimum "
            "information required for idea generation.",
            icon="✅",
        )

    st.info(
        "These are context/design checks only. "
        "A true literature gap or novelty claim will be assessed "
        "later after evidence retrieval.",
        icon="ℹ️",
    )

    return False


def _show_assessment(
    assessment: dict,
) -> None:

    score = assessment["score"]
    rating = assessment["rating"]

    st.metric(
        "Idea Quality Score",
        f"{score}/100",
    )

    st.write(
        f"**Classification:** {_score_label(score)}"
    )

    if assessment.get("issues"):
        st.error("Issues")

        for issue in assessment["issues"]:
            st.write(f"• {issue}")

    if assessment.get("warnings"):
        st.warning("Warnings")

        for warning in assessment["warnings"]:
            st.write(f"• {warning}")

    feasibility = assessment.get(
        "feasibility",
        [],
    )

    if feasibility:
        st.write("**Feasibility signals:**")

        for item in feasibility:
            st.write(f"• {item}")

    feasibility_warnings = assessment.get(
        "feasibility_warnings",
        [],
    )

    if feasibility_warnings:
        st.write("**Feasibility limitations:**")

        for item in feasibility_warnings:
            st.write(f"• {item}")

    st.info(
        "Novelty status: Not assessed yet. "
        "Literature search is required before claiming a "
        "research gap or novelty.",
        icon="🔬",
    )


def _show_idea_card(
    project: ResearchProject,
    index: int,
    idea,
    assessment: dict,
) -> None:

    score = assessment["score"]

    st.markdown("---")

    st.subheader(
        f"Idea {index + 1}: {idea.title}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            f"**Research Goal:** "
            f"{idea.research_goal}"
        )

    with col2:
        st.write(
            f"**Study Design:** "
            f"{idea.study_design}"
        )

    st.write(
        f"**Quality:** {_score_label(score)} "
        f"— **{score}/100**"
    )

    st.write("### 💡 Rationale")

    st.write(idea.rationale)

    strengths = list(
        dict.fromkeys(
            idea.strengths
            + assessment.get("strengths", [])
        )
    )

    if strengths:
        st.write("### ✅ Strengths")

        for strength in strengths:
            st.success(
                strength,
                icon="✅",
            )

    if idea.limitations:
        st.write("### ⚠️ Limitations")

        for limitation in idea.limitations:
            st.warning(
                limitation,
                icon="⚠️",
            )

    _show_assessment(
        assessment
    )

    # --------------------------------------------------------
    # Selection
    # --------------------------------------------------------

    already_selected = (
        project.selected_idea is idea
    )

    button_label = (
        "✓ Selected"
        if already_selected
        else "Select This Idea"
    )

    if st.button(
        button_label,
        key=f"select_idea_{index}",
        use_container_width=True,
        disabled=already_selected,
    ):
        project.select_idea(index)

        st.session_state[
            "step2_selected_index"
        ] = index

        st.rerun()


# ============================================================
# Selected idea
# ============================================================

def _show_selected_idea(
    project: ResearchProject,
) -> None:

    if project.selected_idea is None:
        return

    st.markdown("---")

    st.subheader(
        "🎯 Selected Research Idea"
    )

    idea = project.selected_idea

    st.success(
        idea.title,
        icon="🎯",
    )

    st.write(
        f"**Research Goal:** {idea.research_goal}"
    )

    st.write(
        f"**Study Design:** {idea.study_design}"
    )

    st.write("**Rationale:**")

    st.write(idea.rationale)

    st.info(
        "This selected idea will be used as the starting point "
        "for Step 3 — Research Question.",
        icon="➡️",
    )


# ============================================================
# Main Step 2
# ============================================================

def render_step2(
    project: ResearchProject,
) -> None:

    st.title(
        "💡 Step 2: Research Idea Generation & Gap Analysis"
    )

    st.caption(
        "Generate, validate, rank, and select a research idea "
        "using deterministic medical research rules."
    )

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    _show_context(project)

    st.markdown("---")

    # --------------------------------------------------------
    # Context validation
    # --------------------------------------------------------

    has_hard_gaps = _show_context_gaps(
        project
    )

    if has_hard_gaps:
        st.stop()

    # --------------------------------------------------------
    # Existing validation errors from Step 1
    # --------------------------------------------------------

    if project.has_errors:
        st.error(
            "The Research Context contains validation errors. "
            "Please return to Step 1 and correct them before "
            "generating research ideas."
        )

        for message in project.validation_messages:
            if message.level == "ERROR":
                st.write(
                    f"• **{message.field}:** "
                    f"{message.message}"
                )

        st.stop()

    # --------------------------------------------------------
    # Generate ideas
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "🧠 Candidate Research Ideas"
    )

    st.write(
        "The system will generate up to five structurally "
        "different candidate ideas and rank them using "
        "research-context alignment, goal alignment, outcome "
        "clarity, population fit, study-design fit, feasibility, "
        "and preliminary distinctiveness."
    )

    if st.button(
        "🚀 Generate & Rank Research Ideas",
        type="primary",
        use_container_width=True,
    ):

        ranked_ideas = (
            generate_and_rank_research_ideas(
                project.context,
                max_ideas=5,
            )
        )

        project.clear_ideas()

        for idea, _assessment in ranked_ideas:
            project.generated_ideas.append(
                idea
            )

        st.session_state[
            "step2_generated"
        ] = True

        st.session_state[
            "step2_ranked_assessments"
        ] = ranked_ideas

        st.session_state[
            "step2_selected_index"
        ] = None

        st.rerun()

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    ranked_ideas = st.session_state.get(
        "step2_ranked_assessments",
        [],
    )

    if not ranked_ideas:
        if project.generated_ideas:
            ranked_ideas = [
                (
                    idea,
                    {
                        "score": 0,
                        "rating": "Not assessed",
                        "strengths": [],
                        "warnings": [],
                        "issues": [],
                        "feasibility": [],
                        "feasibility_warnings": [],
                        "novelty_status": "Not assessed yet",
                    },
                )
                for idea in project.generated_ideas
            ]
        else:
            st.info(
                "Click **Generate & Rank Research Ideas** "
                "to create candidate ideas."
            )

            st.stop()

    # --------------------------------------------------------
    # Ranking summary
    # --------------------------------------------------------

    st.success(
        f"{len(ranked_ideas)} candidate idea(s) generated "
        "and ranked.",
        icon="🏆",
    )

    st.subheader(
        "🏆 Ranked Candidates"
    )

    for rank, (idea, assessment) in enumerate(
        ranked_ideas,
        start=1,
    ):

        score = assessment["score"]

        st.write(
            f"**#{rank} — {score}/100 — "
            f"{assessment['rating']}**"
        )

        st.write(
            f"**{idea.title}**"
        )

    # --------------------------------------------------------
    # Top 3
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "⭐ Top Research Ideas"
    )

    top_ideas = ranked_ideas[:3]

    for index, (idea, assessment) in enumerate(
        top_ideas
    ):
        _show_idea_card(
            project=project,
            index=index,
            idea=idea,
            assessment=assessment,
        )

    # --------------------------------------------------------
    # Novelty notice
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "🔬 Novelty & Literature Gap"
    )

    st.info(
        """
**Not assessed yet.**

The current Step 2 version does **not** claim that any idea is
novel or that a literature gap exists.

A defensible literature-gap assessment requires actual evidence
retrieval and review, which will be handled in the later
Literature Search / Evidence Screening stages.
""",
        icon="🔬",
    )

    # --------------------------------------------------------
    # Selected idea
    # --------------------------------------------------------

    _show_selected_idea(
        project
    )
