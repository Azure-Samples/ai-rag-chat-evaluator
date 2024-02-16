from pathlib import Path

from azure.ai.generative.evaluate.metrics import PromptMetric

from .base_metric import BaseMetric

PROMPT_TEMPLATE_DIR = Path(__file__).resolve().parent / "prompts"


class CustomRatingMetric(BaseMetric):

    @classmethod
    def get_metric(cls):
        return PromptMetric.from_template(path=PROMPT_TEMPLATE_DIR / f"{cls.METRIC_NAME}.jinja2", name=cls.METRIC_NAME)

    @classmethod
    def get_aggregate_stats(cls, df):
        return cls.get_aggregate_stats_for_numeric_rating(df, f"{cls.METRIC_NAME}_score")


class RelevanceMetric(CustomRatingMetric):

    METRIC_NAME = "relevance"


class CoherenceMetric(CustomRatingMetric):

    METRIC_NAME = "coherence"


class GroundednessMetric(CustomRatingMetric):

    METRIC_NAME = "groundedness"
