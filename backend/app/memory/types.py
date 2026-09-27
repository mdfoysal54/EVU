from enum import Enum


class MemoryType(str, Enum):
    OBSERVATION = "observation"
    FACT = "fact"
    PREFERENCE = "preference"
    DECISION = "decision"
    LESSON = "lesson"
    PROCEDURE = "procedure"
    PATTERN = "pattern"
    SKILL = "skill"
    INSIGHT = "insight"
    CRYSTAL = "crystal"
    EVENT = "event"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"