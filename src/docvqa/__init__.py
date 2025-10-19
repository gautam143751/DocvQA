"""DocVQA orchestration package."""

from importlib.metadata import version


def get_version() -> str:
    """Return the distribution version."""
    try:
        return version("docvqa")
    except Exception:
        return "0.0.0"


__all__ = ["get_version"]
