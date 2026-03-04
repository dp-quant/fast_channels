"""Shared business logic (service layer) — UseCase protocol and implementations."""

import random
import uuid
from typing import Protocol, TypeVar

from src.core.logging import logger

from src.schemas.commands import ActionCreate, ReseedCommand
from src.schemas.entities import Action, ActionContext

In = TypeVar("In", contravariant=True)
Out = TypeVar("Out", covariant=True)


class UseCase(Protocol[In, Out]):
    """Protocol for use cases: process(command) -> result."""

    def process(self, command: In) -> Out:
        ...
        raise NotImplementedError


class CreateActionUseCase:
    """Create action from command; returns internal result model."""

    def process(self, command: ActionCreate) -> Action:
        logger.info("Action create: {}", command.model_dump())
        action = Action(
            id=str(uuid.uuid4()),
            name=command.name,
            description=command.description,
            tags=command.tags,
        )
        context = ActionContext(seed=random.randint(1, 1000000))
        action.add_context(context)
        return action


class ReseedActionUseCase:
    """Reseed action with new context; returns updated action."""

    def process(self, command: ReseedCommand) -> Action:
        command.action.add_context(command.context)
        return command.action


# Convenience instances for backward-compatible call sites
create_action_use_case = CreateActionUseCase()
reseed_action_use_case = ReseedActionUseCase()


def create_action(command: ActionCreate) -> Action:
    """Backward-compatible: create action from command."""
    return create_action_use_case.process(command)


def reseed_action(action: Action, context: ActionContext) -> Action:
    """Backward-compatible: reseed action with new context."""
    return reseed_action_use_case.process(ReseedCommand(action=action, context=context))
