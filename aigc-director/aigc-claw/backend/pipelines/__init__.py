"""Standalone API-only pipelines migrated from Pixelle-Video."""

from .runner import PIPELINE_REGISTRY, run_pipeline_task

__all__ = ["PIPELINE_REGISTRY", "run_pipeline_task"]
