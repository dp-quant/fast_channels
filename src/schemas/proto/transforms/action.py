from google.protobuf import timestamp_pb2
from datetime import datetime, timezone

from src.schemas.entities import Action, ActionContext
from src.schemas.proto import action_pb2

from .base import timestamp_to_datetime, datetime_to_timestamp


def proto_to_actioncontext(msg) -> ActionContext:
    """Map proto ActionContext to internal ActionContext."""
    if msg is None:
        return ActionContext(seed=0, updated_at=datetime.now(timezone.utc))
    return ActionContext(
        seed=msg.seed,
        updated_at=timestamp_to_datetime(msg.updated_at),
    )


def actioncontext_to_proto(ctx: ActionContext) -> action_pb2.ActionContext:
    """Map internal ActionContext to proto ActionContext."""
    ts = datetime_to_timestamp(ctx.updated_at)
    return action_pb2.ActionContext(seed=ctx.seed, updated_at=ts)


def action_to_proto(action: Action) -> action_pb2.Action:
    """Map internal Action model to gRPC Action message."""
    created_ts = datetime_to_timestamp(action.created_at)
    return action_pb2.Action(
        id=action.id,
        name=action.name,
        description=action.description,
        tags=list(action.tags),
        context=actioncontext_to_proto(action.context),
        created_at=created_ts,
    )


def proto_to_action(msg: action_pb2.Action) -> Action:
    """Map proto Action to internal Action."""
    return Action(
        id=msg.id,
        name=msg.name,
        description=msg.description,
        tags=set(msg.tags),
        context=proto_to_actioncontext(msg.context),
        created_at=timestamp_to_datetime(msg.created_at),
    )
