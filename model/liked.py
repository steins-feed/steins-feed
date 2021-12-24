#!/usr/bin/env python3

import sqlalchemy as sqla

from . import get_session
from .orm import feeds as orm_feeds, items as orm_items
from .schema import feeds as schema_feeds, items as schema_items

def liked_languages(user_id: int) -> list[schema_feeds.Language]:
    """
    Languages with training data.

    Args:
      user_id: User ID.

    Returns:
      List of Language objects.
    """
    q = sqla.select(
        orm_feeds.Feed.Language,
    ).select_from(
        orm_items.Like,
    ).join(
        orm_items.Like.item
    ).join(
        orm_items.Item.feed
    ).where(
        orm_items.Like.UserID == user_id,
        orm_items.Like.Score != schema_items.Like.MEH.name,
    ).distinct()

    with get_session() as session:
        return [schema_feeds.Language[e["Language"]] for e in session.execute(q)]

def liked_items(
    user_id: int,
    lang: schema_feeds.Language,
    score: schema_items.Like = schema_items.Like.UP,
) -> list[orm_items.Item]:
    """
    Training data.

    Args:
      user_id: User ID.
      lang: Language.
      score: Like value.

    Returns:
      List of liked items.
    """
    q = sqla.select(
        orm_items.Item,
    ).join(
        orm_items.Item.feed
    ).join(
        orm_items.Item.likes
    ).where(
        orm_feeds.Feed.Language == lang.name,
        orm_items.Like.UserID == user_id,
        orm_items.Like.Score == score.name,
    )

    with get_session() as session:
        return [e[0] for e in session.execute(q)]

def disliked_items(
    user_id: int,
    lang: schema_feeds.Language,
) -> list[orm_items.Item]:
    """
    Training data.

    Args:
      user_id: User ID.
      lang: Language.

    Returns:
      List of disliked items.
    """
    return liked_items(user_id, lang, schema_items.Like.DOWN)

