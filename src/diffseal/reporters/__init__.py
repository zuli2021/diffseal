"""Reporters emit canonical JSON first and derived Markdown second."""

from diffseal.reporters.json import write_json
from diffseal.reporters.markdown import render_markdown, write_markdown

__all__ = ["write_json", "render_markdown", "write_markdown"]
