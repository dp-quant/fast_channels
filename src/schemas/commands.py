"""ActionCreate — input validation (commands)."""

from datetime import datetime
from pydantic import BaseModel, Field


class ActionCreate(BaseModel):
    """Command to create an action."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
