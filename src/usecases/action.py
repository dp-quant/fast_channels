"""Shared business logic (service layer)."""

from src.core.logging import logger

from src.schemas.commands import ActionCreate
from src.schemas.internal import ActionInternal

def create_action(cmd: ActionCreate) -> ActionInternal:
    """Create action from command; returns internal result model."""
    logger.info("Order create: {}", cmd.model_dump())
    return ActionInternal(
        id="placeholder-id",
        name=cmd.name,
        description=cmd.description,
        tags=cmd.tags,
        data=cmd.data,
        action_at=cmd.action_at,
    )
