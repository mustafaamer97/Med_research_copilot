REQUIRED_CONTEXT_FIELDS = {
    "research_topic": "Research Topic",
    "population": "Population",
    "outcome": "Outcome",
    "research_goal": "Research Goal",
    "data_source": "Data Source",
}


DATA_SOURCE_DESIGNS = {
    "Hospital Records": {
        "Retrospective Cohort Study",
        "Case-Control Study",
        "Cross-Sectional Study",
    },
    "Registry Database": {
        "Retrospective Cohort Study",
        "Case-Control Study",
        "Cross-Sectional Study",
    },
    "Survey / Questionnaire": {
        "Cross-Sectional Study",
        "Prospective Cohort Study",
    },
    "Published Literature": {
        "Systematic Review",
        "Meta-Analysis",
        "Scoping Review",
    },
}


STUDY_DESIGNS = [
    "Auto Detect",
    "Cross-Sectional Study",
    "Case-Control Study",
    "Prospective Cohort Study",
    "Retrospective Cohort Study",
    "Randomized Controlled Trial",
    "Diagnostic Accuracy Study",
    "Prediction Model Study",
    "Systematic Review",
    "Meta-Analysis",
    "Scoping Review",
]
