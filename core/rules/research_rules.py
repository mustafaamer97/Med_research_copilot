# ============================================================
# core/rules/research_rules.py
# Med Research Copilot
# Central Research Rules Engine
# ============================================================

# ============================================================
# Required Context Fields
# ============================================================

REQUIRED_CONTEXT_FIELDS = {
    "research_topic": "Research Topic",
    "population": "Population",
    "outcome": "Outcome",
    "research_goal": "Research Goal",
    "data_source": "Data Source",
}

# ============================================================
# Research Types
# ============================================================

RESEARCH_TYPES = [
    "Primary Research",
    "Secondary Research",
    "Evidence Synthesis",
]

# ============================================================
# Research Goals
# ============================================================

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
# Data Sources
# ============================================================

DATA_SOURCES = [
    "Hospital Records",
    "Registry Database",
    "Survey / Questionnaire",
    "Electronic Health Records (EHR)",
    "Laboratory Data",
    "Imaging Data",
    "Published Literature",
]

# ============================================================
# Study Designs
# ============================================================

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

# ============================================================
# Study Design Categories
# ============================================================

OBSERVATIONAL_DESIGNS = {
    "Cross-Sectional Study",
    "Case-Control Study",
    "Prospective Cohort Study",
    "Retrospective Cohort Study",
}

EXPERIMENTAL_DESIGNS = {
    "Randomized Controlled Trial",
}

REVIEW_DESIGNS = {
    "Systematic Review",
    "Meta-Analysis",
    "Scoping Review",
}

# ============================================================
# Data Source → Allowed Designs
# ============================================================

DATA_SOURCE_DESIGNS = {

    "Hospital Records": {
        "Retrospective Cohort Study",
        "Case-Control Study",
        "Cross-Sectional Study",
        "Diagnostic Accuracy Study",
    },

    "Registry Database": {
        "Retrospective Cohort Study",
        "Case-Control Study",
        "Cross-Sectional Study",
        "Diagnostic Accuracy Study",
    },

    "Electronic Health Records (EHR)": {
        "Retrospective Cohort Study",
        "Case-Control Study",
        "Cross-Sectional Study",
        "Diagnostic Accuracy Study",
        "Prediction Model Study",
    },

    "Laboratory Data": {
        "Cross-Sectional Study",
        "Diagnostic Accuracy Study",
    },

    "Imaging Data": {
        "Cross-Sectional Study",
        "Diagnostic Accuracy Study",
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

# ============================================================
# Outcome Keyword Groups
# ============================================================

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
        "development of",
        "occurrence of",
        "new onset",
        "incident",
        "risk of",
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
        "annual incidence",
        "annual prevalence",
        "annual mortality",
        "yearly incidence",
        "yearly prevalence",
        "yearly mortality",
        "over time",
        "temporal change",
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

# ============================================================
# Goal → Expected Outcome Categories
# ============================================================

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
        "survival",
    },

    "Prediction Model": {
        "survival",
        "incidence",
        "prevalence",
        "treatment",
        "diagnostic_accuracy",
    },

    "Systematic Review": {
        "survival",
        "incidence",
        "prevalence",
        "treatment",
        "diagnostic_accuracy",
    },
}

# ============================================================
# Goal → Recommended Study Designs
# ============================================================

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

    "Systematic Review": {
        "Systematic Review",
        "Meta-Analysis",
        "Scoping Review",
    },
}

# ============================================================
# Goal → Auto Recommended Design
# Used when Study Design = Auto Detect
# ============================================================

AUTO_DESIGN_BY_GOAL = {

    "Survival Analysis":
        "Retrospective Cohort Study",

    "Diagnostic Accuracy":
        "Diagnostic Accuracy Study",

    "Incidence":
        "Retrospective Cohort Study",

    "Prevalence":
        "Cross-Sectional Study",

    "Trend Analysis":
        "Retrospective Cohort Study",

    "Treatment Outcomes":
        "Retrospective Cohort Study",

    "Risk Factors":
        "Case-Control Study",

    "Prediction Model":
        "Prediction Model Study",

    "Systematic Review":
        "Systematic Review",
}
