class BuiltinRatingMetric:

    @classmethod
    def get_metric(cls):
        return cls.METRIC_NAME

    @classmethod
    def get_aggregate_stats(cls, df):
        pass_count = int(df[cls.METRIC_NAME].apply(lambda x: int(x) >= 4).sum())
        return {
            "mean_rating": round(df[cls.METRIC_NAME].mean(), 2),
            "pass_count": pass_count,
            "pass_rate": round(pass_count / len(df), 2),
        }


class BuiltinRelevanceMetric(BuiltinRatingMetric):

    METRIC_NAME = "gpt_relevance"


class BuiltinCoherenceMetric(BuiltinRatingMetric):

    METRIC_NAME = "gpt_coherence"


class BuiltinGroundednessMetric(BuiltinRatingMetric):

    METRIC_NAME = "gpt_groundedness"
