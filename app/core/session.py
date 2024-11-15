from uuid import uuid4
from app.core.cache import get_redis
from app.core.exceptions import APIError


def get_or_create_session(user_id: int, timeout_minutes: int = 30) -> str:
    """Get existing session or create new one if expired/none exists"""
    try:
        redis = get_redis()
        session_key = f"storage_session:{user_id}"
        session_id = redis.get(session_key)

        if not session_id:
            session_id = str(uuid4())
            redis.set(session_key, session_id, ex=timeout_minutes * 60)
        else:
            # Extend session timeout
            redis.expire(session_key, timeout_minutes * 60)

        return session_id
    except APIError:
        # Fallback: generate new session ID if Redis is unavailable
        return str(uuid4())
