"""Shared business logic (service layer)."""

from datetime import datetime
import random
import uuid
from src.core.logging import logger

from src.schemas.commands import ActionCreate
from src.schemas.entities import Action, ActionContext


def create_action(cmd: ActionCreate) -> Action:
    """Create action from command; returns internal result model."""
    logger.info("Action create: {}", cmd.model_dump())
    action = Action(
        id=str(uuid.uuid4()),
        name=cmd.name,
        description=cmd.description,
        tags=cmd.tags,
    )
    context = ActionContext(seed=random.randint(1, 1000000))
    action.add_context(context)
    return action


def update_action(action: Action, context: ActionContext) -> Action:
    """Update action from command; returns internal result model."""

    action.add_context(context)
    return action
