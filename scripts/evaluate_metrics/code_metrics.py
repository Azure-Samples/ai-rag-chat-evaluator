import re

from .base_metric import BaseMetric


class AnswerLengthMetric(BaseMetric):

    METRIC_NAME = "answer_length"

    @classmethod
    def get_metric(cls):
        def answer_length(*, data, **kwargs):
            return {AnswerLengthMetric.METRIC_NAME: len(data["answer"])}

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
    def get_metric(cls):
        def has_citation(*, data, **kwargs):
            return {"has_citation": bool(re.search(r"\[[^\]]+\]", data["answer"]))}

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
    def get_metric(cls):
        def citation_match(*, data, **kwargs):
            # Return true if all citations in the truth are present in the answer
            truth_citations = set(re.findall(r"\[([^\]]+)\.\w{3,4}\]", data["truth"]))
            answer_citations = set(re.findall(r"\[([^\]]+)\.\w{3,4}\]", data["answer"]))
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
    def get_metric(cls):
        def latency(*, data, **kwargs):
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
