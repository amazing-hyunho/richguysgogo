"""Evidence-first research-to-market signal radar.

The package turns a point-in-time JSON evidence bundle into a deterministic
five-stage assessment.  It deliberately does not fetch data, call an LLM, or
make buy/sell recommendations; collection and interpretation stay separate
from the scoring core so every output can be reproduced from its inputs.
"""

from committee.research_radar.models import RadarValidationError, ThemeInput
from committee.research_radar.report import render_markdown
from committee.research_radar.runner import load_theme_input, write_report_artifacts
from committee.research_radar.scoring import analyze_theme

__all__ = [
    "RadarValidationError",
    "ThemeInput",
    "analyze_theme",
    "load_theme_input",
    "render_markdown",
    "write_report_artifacts",
]
