import re

EXPECTED_HEADERS = [
    "## Problem",
    "## Approach",
    "## Key Claims",
    "## Evidence Quality",
    "## Assumptions",
    "## Limitations",
    "## Practical Usefulness (Engineer)",
    "## Decision Usefulness (PM)",
    "## Novelty/Validity (Analyst)",
    "## Red Flags",
]


def format_output(text: str) -> str:
    """
    Cleans and normalizes Gemini markdown output into readable sections.
    """

    if not text:
        return ""

    # Normalize newlines
    text = text.replace("\\n", "\n").strip()

    sections = {}
    current_header = None
    buffer = []

    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if line in EXPECTED_HEADERS:
            if current_header and buffer:
                sections[current_header] = "\n".join(buffer).strip()
            current_header = line
            buffer = []
        else:
            if line.startswith("*"):
                buffer.append(f"- {line.lstrip('* ').strip()}")
            elif line:
                buffer.append(line)

    if current_header and buffer:
        sections[current_header] = "\n".join(buffer).strip()

    # Rebuild clean output
    formatted = []
    for header in EXPECTED_HEADERS:
        formatted.append(header)
        content = sections.get(header, "- Not addressed explicitly.")
        formatted.append(content)
        formatted.append("")

    return "\n".join(formatted).strip()

