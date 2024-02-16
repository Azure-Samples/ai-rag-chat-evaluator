from .base_metric import BaseMetric


class BuiltinRatingMetric(BaseMetric):

    @classmethod
    def get_metric(cls):
        return cls.METRIC_NAME

    @classmethod
    def get_aggregate_stats(cls, df):
        return cls.get_aggregate_stats_for_numeric_rating(df, cls.METRIC_NAME)


class BuiltinRelevanceMetric(BuiltinRatingMetric):

    METRIC_NAME = "gpt_relevance"


class BuiltinCoherenceMetric(BuiltinRatingMetric):

    METRIC_NAME = "gpt_coherence"


class BuiltinGroundednessMetric(BuiltinRatingMetric):

    METRIC_NAME = "gpt_groundedness"
