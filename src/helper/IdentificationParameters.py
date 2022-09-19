from dataclasses import dataclass


@dataclass
class IdentificationParameters:
    ignoreNonFatalRequestChecks: bool = None
    eventSubscriptions: int = None
