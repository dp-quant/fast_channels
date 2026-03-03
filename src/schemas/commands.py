"""ActionCreate — input validation (commands)."""

from pydantic import BaseModel, Field

from src.schemas.entities import Action, ActionContext


class ActionCreate(BaseModel):
    """Command to create an action."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class ReseedCommand(BaseModel):
    """Command to reseed an action (set new context)."""

    action: Action
    context: ActionContext
