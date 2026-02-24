"""OrderInternal — result / truth models (internal API)."""

from datetime import datetime
from pydantic import BaseModel


class ActionInternal(BaseModel):
    """Result of action creation or update (internal representation)."""

    id: str
    name: str
    description: str
    tags: list[str]
    data: dict
    action_at: datetime