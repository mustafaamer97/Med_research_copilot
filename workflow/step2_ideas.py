import streamlit as st

from core.idea_generator import (
    assess_idea_context,
    generate_research_ideas,
)

from core.models.research_project import (
    ResearchProject,
)


# ============================================================
# STEP 2 UI
# ============================================================

def render_step2(project: ResearchProject) -> None:

    st.header(
        "💡 Step 2: Research Idea & Gap Analysis"
    )

    st.caption(
        "Generate structured research ideas from the "
        "validated research context."
    )

    context = project.context

    # ========================================================
    # STEP 1 CHECK
    # ========================================================

    if project.has_errors:

        st.error(
            "Step 1 contains validation errors. "
            "Please fix them before generating research ideas."
        )

        return

    if not context.research_topic:

        st.warning(
            "Please complete Step 1 before continuing."
        )

        return

    # ========================================================
    # RESEARCH CONTEXT SUMMARY
    # ========================================================

    st.subheader(
        "📋 Research Context"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Topic:** {context.research_topic}"
        )

        st.write(
            f"**Population:** {context.population}"
        )

        st.write(
            f"**Outcome:** {context.outcome}"
        )

        st.write(
            f"**Research Goal:** {context.research_goal}"
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
            f"{context.data_source}"
        )

        st.write(
            f"**Study Design:** "
            f"{context.study_design}"
        )

    st.divider()

    # ========================================================
    # CONTEXT GAPS
    # ========================================================

    st.subheader(
        "🔎 Context & Design Gaps"
    )

    gaps = assess_idea_context(context)

    if gaps:

        for gap in gaps:

            st.warning(gap)

    else:

        st.success(
            "The research context contains the minimum "
            "information required for idea generation."
        )

    st.info(
        "Note: These are context/design gaps only. "
        "A true literature gap will be assessed later "
        "after evidence retrieval."
    )

    st.divider()

    # ========================================================
    # GENERATE IDEAS
    # ========================================================

    st.subheader(
        "💡 Generate Research Ideas"
    )

    if st.button(
        "Generate Research Ideas",
        type="primary",
        use_container_width=True,
    ):

        ideas = generate_research_ideas(
            context
        )

        project.generated_ideas = ideas
        project.selected_idea = None

        if ideas:

            st.success(
                f"{len(ideas)} research ideas generated."
            )

        else:

            st.error(
                "Unable to generate research ideas. "
                "Please complete the required research context."
            )

    # ========================================================
    # DISPLAY IDEAS
    # ========================================================

    if not project.generated_ideas:

        st.info(
            "Click **Generate Research Ideas** "
            "to create candidate research questions."
        )

        return

    st.divider()

    st.subheader(
        "🧠 Candidate Research Ideas"
    )

    for index, idea in enumerate(
        project.generated_ideas,
        start=1,
    ):

        with st.container(
            border=True
        ):

            st.markdown(
                f"### Idea {index}"
            )

            st.markdown(
                f"**{idea.title}**"
            )

            st.write(
                idea.rationale
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
                    f"{idea.study_design or 'Not specified'}"
                )

            # ------------------------------------------------
            # Strengths
            # ------------------------------------------------

            if idea.strengths:

                st.markdown(
                    "**Strengths**"
                )

                for strength in idea.strengths:

                    st.success(
                        strength,
                        icon="✓",
                    )

            # ------------------------------------------------
            # Limitations
            # ------------------------------------------------

            if idea.limitations:

                st.markdown(
                    "**Limitations / Missing Information**"
                )

                for limitation in idea.limitations:

                    st.warning(
                        limitation,
                        icon="!",
                    )

            # ------------------------------------------------
            # Warnings
            # ------------------------------------------------

            if idea.warnings:

                for warning in idea.warnings:

                    st.warning(
                        warning
                    )

            # ------------------------------------------------
            # Select idea
            # ------------------------------------------------

            selected = (
                project.selected_idea is idea
            )

            button_label = (
                "✓ Selected"
                if selected
                else "Select This Idea"
            )

            if st.button(
                button_label,
                key=f"select_idea_{index}",
                use_container_width=True,
            ):

                project.select_idea(index - 1)

                st.rerun()

    # ========================================================
    # SELECTED IDEA
    # ========================================================

    if project.selected_idea:

        st.divider()

        st.subheader(
            "✅ Selected Research Idea"
        )

        selected = project.selected_idea

        st.success(
            selected.title
        )

        st.write(
            f"**Rationale:** {selected.rationale}"
        )

        st.write(
            f"**Research Goal:** "
            f"{selected.research_goal}"
        )

        st.write(
            f"**Study Design:** "
            f"{selected.study_design or 'Not specified'}"
        )

        st.info(
            "This selected idea will be used as the starting "
            "point for Step 3: Research Question."
        )
