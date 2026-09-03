import streamlit as st

from core.question_builder import (
    build_research_question,
    build_primary_objective,
    build_hypothesis,
    build_framework,
    build_search_query,
    validate_step3,
)


# ==========================================
# Step 3
# ==========================================

def render_step3(project):

    st.header("❓ Step 3: Research Question Builder")

    context = project.context

    final_idea = context.get(
        "final_research_idea",
        ""
    )

    if not final_idea:

        st.warning(
            "Please complete Step 2 and save a final research idea first."
        )

        return

    st.info(
        f"Selected Research Idea:\n\n{final_idea}"
    )

    st.divider()

    # ==========================================
    # Generate Outputs
    # ==========================================

    if st.button(
        "Generate Research Question Package",
        type="primary",
        use_container_width=True,
    ):

        context["research_question"] = (
            build_research_question(context)
        )

        context["primary_objective"] = (
            build_primary_objective(context)
        )

        context["research_hypothesis"] = (
            build_hypothesis(context)
        )

        context["framework"] = (
            build_framework(context)
        )

        context["search_query"] = (
            build_search_query(context)
        )

    # ==========================================
    # Display Results
    # ==========================================

    if context.get("research_question"):

        st.subheader("Research Question")

        edited_question = st.text_area(
            "Edit Research Question",
            value=context["research_question"],
            height=120,
        )

        context["research_question"] = edited_question

    if context.get("primary_objective"):

        st.subheader("Primary Objective")

        edited_objective = st.text_area(
            "Edit Primary Objective",
            value=context["primary_objective"],
            height=120,
        )

        context["primary_objective"] = edited_objective

    if context.get("research_hypothesis"):

        st.subheader("Research Hypothesis")

        edited_hypothesis = st.text_area(
            "Edit Research Hypothesis",
            value=context["research_hypothesis"],
            height=120,
        )

        context["research_hypothesis"] = edited_hypothesis

    # ==========================================
    # PICO / PECO
    # ==========================================

    framework = context.get("framework")

    if framework:

        st.subheader(
            framework.get(
                "framework_type",
                "Framework"
            )
        )

        st.json(framework)

    # ==========================================
    # Search Query
    # ==========================================

    if context.get("search_query"):

        st.subheader("Search Query")

        edited_query = st.text_area(
            "Edit Search Query",
            value=context["search_query"],
            height=120,
        )

        context["search_query"] = edited_query

    st.divider()

    # ==========================================
    # Validation
    # ==========================================

    if st.button(
        "Validate Step 3",
        use_container_width=True,
    ):

        validation = validate_step3(context)

        score = validation["score"]

        if score >= 85:

            st.success(
                f"Ready for Literature Search ({score}/100)"
            )

        elif score >= 60:

            st.warning(
                f"Needs Refinement ({score}/100)"
            )

        else:

            st.error(
                f"Incomplete ({score}/100)"
            )

        for issue in validation["issues"]:

            st.warning(issue)

    # ==========================================
    # Save Final Package
    # ==========================================

    if st.button(
        "Save Step 3 Outputs",
        type="primary",
        use_container_width=True,
    ):

        validation = validate_step3(context)

        if validation["score"] < 60:

            st.error(
                "Please complete the missing components before saving."
            )

            return

        context["step3_completed"] = True

        st.success(
            "Step 3 completed successfully."
        )

    # ==========================================
    # Final Package Preview
    # ==========================================

    if context.get("step3_completed"):

        st.divider()

        st.subheader(
            "📦 Research Package"
        )

        st.markdown(
            f"""
### Research Idea
{context.get("final_research_idea", "")}

### Research Question
{context.get("research_question", "")}

### Primary Objective
{context.get("primary_objective", "")}

### Hypothesis
{context.get("research_hypothesis", "")}

### Search Query
{context.get("search_query", "")}
"""
        )

        if context.get("framework"):

            st.subheader(
                "Framework"
            )

            st.json(
                context["framework"]
            )
