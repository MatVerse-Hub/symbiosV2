"""Executable GitHub adapter for the MatVerse Native Network Layer."""

from .event_to_connection import github_event_to_connection_event
from .runner import process_github_event_file

__all__ = ["github_event_to_connection_event", "process_github_event_file"]
