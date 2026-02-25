"""Action — result / truth models (entities)."""

import random
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ActionContext(BaseModel):
    """Action context."""

    seed: int = 0
    updated_at: datetime = Field(default_factory=datetime.now)


class Action(BaseModel):
    """Action (entity representation)."""

    id: str
    name: str
    description: str
    tags: set[str]
    context: ActionContext
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)

    def __init__(self, **data: Any):
        if not data.get("context"):
            data["context"] = ActionContext(
                seed=random.randint(1, 1000000), updated_at=datetime.now()
            )

        super().__init__(**data)

    def add_tag(self, tag: str):
        """Add a tag to the action."""
        self.tags.add(tag)

    def remove_tag(self, tag: str):
        """Remove a tag from the action."""
        self.tags.remove(tag)

    def add_context(self, context: ActionContext):
        """Set the context."""
        self.context = context
