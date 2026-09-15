from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Question:
    id: str
    skill: str
    level: str
    question: str
    options: List[str]
    answer: int   # index of correct option
    difficulty: str
    rationale: Optional[str] = None

@dataclass
class Assessment:
    id: int
    employee: str
    skill: str
    questions: List[Question]
    score: Optional[float] = None
    status: str = "draft"

@dataclass
class EmployeeSkill:
    employee: str
    skill: str
    level: str
    confirmed: bool = False
    evidence: Optional[str] = None
