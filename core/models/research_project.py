from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResearchContext:
    research_type: str = ""
    research_topic: str = ""
    population: str = ""
    intervention_exposure: str = ""
    comparator: str = ""
    outcome: str = ""
    research_goal: str = ""
    data_source: str = ""
    location: str = ""
    study_period: str = ""
    study_design: str = ""


@dataclass
class ValidationMessage:
    level: str
    field: str
    message: str


@dataclass
class ResearchProject:
    context: ResearchContext = field(default_factory=ResearchContext)
    validation_messages: List[ValidationMessage] = field(default_factory=list)

    def clear_validation(self) -> None:
        self.validation_messages.clear()

    @property
    def has_errors(self) -> bool:
        return any(
            message.level == "ERROR"
            for message in self.validation_messages
        )

    @property
    def has_warnings(self) -> bool:
        return any(
            message.level == "WARNING"
            for message in self.validation_messages
        )
