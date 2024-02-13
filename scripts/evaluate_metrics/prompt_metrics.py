from pathlib import Path

from azure.ai.generative.evaluate.metrics import PromptMetric

PROMPT_TEMPLATE_DIR = Path(__file__).resolve().parent / "prompts"


class CustomRatingMetric:

    @classmethod
    def get_metric(cls):
        return PromptMetric.from_template(path=PROMPT_TEMPLATE_DIR / f"{cls.METRIC_NAME}.jinja2", name=cls.METRIC_NAME)

    @classmethod
    def get_aggregate_stats(cls, df):
        score_column = f"{cls.METRIC_NAME}_score"
        pass_count = int(df[score_column].apply(lambda x: int(x) >= 4).sum())
        return {
            "mean_rating": round(df[score_column].mean(), 2),
            "pass_count": pass_count,
            "pass_rate": round(pass_count / len(df), 2),
        }


class RelevanceMetric(CustomRatingMetric):

    METRIC_NAME = "relevance"


class CoherenceMetric(CustomRatingMetric):

    METRIC_NAME = "coherence"


class GroundednessMetric(CustomRatingMetric):

    METRIC_NAME = "groundedness"
