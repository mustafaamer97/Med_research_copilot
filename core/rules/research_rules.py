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


# ---------------------------------------------------------
# Outcome keyword groups
# ---------------------------------------------------------

OUTCOME_KEYWORDS = {
    "survival": {
        "survival",
        "overall survival",
        "disease-free survival",
        "progression-free survival",
        "event-free survival",
        "time to death",
        "time-to-death",
        "time to recurrence",
        "time-to-recurrence",
        "time to event",
        "time-to-event",
        "mortality",
    },

    "diagnostic_accuracy": {
        "sensitivity",
        "specificity",
        "positive predictive value",
        "negative predictive value",
        "ppv",
        "npv",
        "diagnostic accuracy",
        "diagnostic performance",
        "auc",
        "area under the curve",
        "roc",
        "roc curve",
    },

    "incidence": {
        "incidence",
        "new cases",
        "incident cases",
        "incidence rate",
    },

    "prevalence": {
        "prevalence",
        "proportion affected",
        "proportion with",
    },

    "trend": {
        "trend",
        "time trend",
        "temporal trend",
        "annual change",
        "yearly change",
        "change over time",
    },

    "treatment": {
        "treatment outcome",
        "treatment response",
        "response to treatment",
        "clinical response",
        "symptom improvement",
        "disease control",
        "hba1c",
        "blood pressure",
        "pain score",
        "quality of life",
        "mortality",
        "hospitalization",
        "readmission",
    },
}


# ---------------------------------------------------------
# Goal → expected outcome categories
# ---------------------------------------------------------

GOAL_OUTCOME_CATEGORIES = {
    "Survival Analysis": {
        "survival",
    },

    "Diagnostic Accuracy": {
        "diagnostic_accuracy",
    },

    "Incidence": {
        "incidence",
    },

    "Prevalence": {
        "prevalence",
    },

    "Trend Analysis": {
        "trend",
    },

    "Treatment Outcomes": {
        "treatment",
        "survival",
        "diagnostic_accuracy",
    },

    "Risk Factors": {
        "incidence",
        "prevalence",
        "survival",
        "treatment",
    },

    "Prediction Model": {
        "survival",
        "incidence",
        "prevalence",
        "treatment",
        "diagnostic_accuracy",
    },
}


# ---------------------------------------------------------
# Goal → recommended study designs
# ---------------------------------------------------------

GOAL_STUDY_DESIGNS = {
    "Survival Analysis": {
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    },

    "Diagnostic Accuracy": {
        "Diagnostic Accuracy Study",
    },

    "Incidence": {
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    },

    "Prevalence": {
        "Cross-Sectional Study",
    },

    "Trend Analysis": {
        "Retrospective Cohort Study",
        "Cross-Sectional Study",
    },

    "Treatment Outcomes": {
        "Randomized Controlled Trial",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    },

    "Risk Factors": {
        "Case-Control Study",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    },

    "Prediction Model": {
        "Prediction Model Study",
        "Prospective Cohort Study",
        "Retrospective Cohort Study",
    },
}
