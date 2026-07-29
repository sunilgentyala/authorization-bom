"""Render an analysis result (see authbom.cli `analyze`) as JSON, Markdown, or SARIF."""

from authbom.reporters import json_reporter, markdown_reporter, sarif_reporter  # noqa: F401

RENDERERS = {
    "json": json_reporter.render,
    "markdown": markdown_reporter.render,
    "sarif": sarif_reporter.render,
}
