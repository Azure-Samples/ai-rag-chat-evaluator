import os
import re
import numpy as np

from abc import abstractmethod

from .base_metric import BaseMetric
from core.azure import ClientService



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


# Init client used for embeddings generation
client = ClientService(
    open_ai_service=os.getenv("AZURE_OPENAI_SERVICE"),
    open_ai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    open_ai_emb_deployment=os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT"),
    open_ai_emb_model=os.getenv("AZURE_OPENAI_EMB_MODEL"),
)


class SimilarityMetric(BaseMetric):
    METRIC_NAME = "similarity_metric"

    @classmethod
    @abstractmethod
    def get_metric(cls):
        ...

    @classmethod
    def calc_cosine_similarity(cls, q1: str, q2: str):
        embd_1 = np.array(client.compute_text_embedding(q1))
        embd_2 = np.array(client.compute_text_embedding(q2))
        score = np.dot(embd_1, embd_2) / (np.linalg.norm(embd_1) * np.linalg.norm(embd_2))
        return score

    @classmethod
    def get_aggregate_stats(cls, df):
        return {
            "mean": round(df[cls.METRIC_NAME].mean(), 2),
            "max": df[cls.METRIC_NAME].max(),
            "min": df[cls.METRIC_NAME].min(),
        }


class AnswerSimilarityMetric(SimilarityMetric):
    METRIC_NAME = "answer_similarity"

    @classmethod
    def get_metric(cls):
        def answer_similarity(*, data, **kwargs):
            # Return no additional data, since latency is already stored in the target response
            truth = data["truth"]
            answer = data["answer"]
            score = cls.calc_cosine_similarity(truth, answer)
            return {'answer_similarity': score}

        return answer_similarity


class ContextSimilarityMetric(SimilarityMetric):
    METRIC_NAME = "context_similarity"

    @classmethod
    def get_metric(cls):
        def context_similarity(*, data, **kwargs):
            # Return no additional data, since latency is already stored in the target response
            question = data["question"]
            context = data["context"]
            score = cls.calc_cosine_similarity(question, context)
            return {'context_similarity': score}

        return context_similarity
