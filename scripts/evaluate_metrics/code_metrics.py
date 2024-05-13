import re

from .base_metric import BaseMetric


class AnswerLengthMetric(BaseMetric):

    METRIC_NAME = "answer_length"

    @classmethod
    def evaluator_fn(cls, **kwargs):
        def answer_length(*, answer, **kwargs):
            return {AnswerLengthMetric.METRIC_NAME: len(answer)}

        return answer_length

    @classmethod
    def get_aggregate_stats(cls, df):
        return {
            "mean": round(df[cls.METRIC_NAME].mean(), 2),
            "max": int(df[cls.METRIC_NAME].max()),
            "min": int(df[cls.METRIC_NAME].min()),
        }


class HasCitationMetric(BaseMetric):

    METRIC_NAME = "has_citation"

    @classmethod
    def evaluator_fn(cls, **kwargs):
        def has_citation(*, answer, **kwargs):
            return {"has_citation": bool(re.search(r"\[[^\]]+\]", answer))}

        return has_citation

    @classmethod
    def get_aggregate_stats(cls, df):
        return {
            "total": int(df[cls.METRIC_NAME].sum()),
            "rate": round(df[cls.METRIC_NAME].mean(), 2),
        }


class CitationMatchMetric(BaseMetric):

    METRIC_NAME = "citation_match"

    @classmethod
    def evaluator_fn(cls, **kwargs):
        def citation_match(*, answer, ground_truth, **kwargs):
            # Return true if all citations in the truth are present in the answer
            truth_citations = set(re.findall(r"\[([^\]]+)\.\w{3,4}\]", ground_truth))
            answer_citations = set(re.findall(r"\[([^\]]+)\.\w{3,4}\]", answer))
            citation_match = truth_citations.issubset(answer_citations)
            return {"citation_match": citation_match}

        return citation_match

    @classmethod
    def get_aggregate_stats(cls, df):
        return {
            "total": int(df[cls.METRIC_NAME].sum()),
            "rate": round(df[cls.METRIC_NAME].mean(), 2),
        }


class LatencyMetric(BaseMetric):

    METRIC_NAME = "latency"

    @classmethod
    def evaluator_fn(cls, **kwargs):
        def latency(**kwargs):
            # Return no additional data, since latency is already stored in the target response
            return {}

        return latency

    @classmethod
    def get_aggregate_stats(cls, df):
        return {
            "mean": round(df[cls.METRIC_NAME].mean(), 2),
            "max": df[cls.METRIC_NAME].max(),
            "min": df[cls.METRIC_NAME].min(),
        }
