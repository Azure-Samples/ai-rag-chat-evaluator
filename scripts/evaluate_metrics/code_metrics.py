import re


class AnswerLengthMetric:

    METRIC_NAME = "answer_length"

    @staticmethod
    def get_metric():
        def answer_length(*, data, **kwargs):
            return {"answer_length": len(data["answer"])}

        return answer_length

    @staticmethod
    def get_aggregate_stats(df):
        return {
            "mean": round(df["answer_length"].mean(), 2),
            "max": int(df["answer_length"].max()),
            "min": int(df["answer_length"].min()),
        }


class HasCitationMetric:

    METRIC_NAME = "has_citation"

    @staticmethod
    def get_metric():
        def has_citation(*, data, **kwargs):
            return {"has_citation": bool(re.search(r"\[[^\]]+\]", data["answer"]))}

        return has_citation

    @staticmethod
    def get_aggregate_stats(df):
        return {
            "total": int(df["has_citation"].sum()),
            "rate": round(df["has_citation"].mean(), 2),
        }


class LatencyMetric:

    METRIC_NAME = "latency"

    @staticmethod
    def get_metric():
        def latency(*, data, **kwargs):
            return {}

        return latency

    @staticmethod
    def get_aggregate_stats(df):
        return {
            "mean": round(df["latency"].mean(), 2),
            "max": df["latency"].max(),
            "min": df["latency"].min(),
        }
