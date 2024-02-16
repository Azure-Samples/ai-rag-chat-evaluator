import pandas as pd
from azure.ai.generative.evaluate.metrics import PromptMetric

from scripts.evaluate_metrics import builtin_metrics, code_metrics, prompt_metrics


def test_answer_length():
    metric = code_metrics.AnswerLengthMetric()
    metric_function = metric.get_metric()
    assert callable(metric_function)
    assert metric_function(data={"answer": "Hello, world!"}) == {"answer_length": 13}
    df = pd.DataFrame([{"answer_length": 20}, {"answer_length": 10}, {"answer_length": 5}])
    assert metric.get_aggregate_stats(df) == {"mean": 11.67, "max": 20, "min": 5}


def test_has_citation():
    metric = code_metrics.HasCitationMetric()
    metric_function = metric.get_metric()
    assert callable(metric_function)
    assert metric_function(data={"answer": "Hello, world!"}) == {"has_citation": False}
    assert metric_function(data={"answer": "Hello, [world.pdf]!"}) == {"has_citation": True}

    df = pd.DataFrame([{"has_citation": True}, {"has_citation": False}, {"has_citation": True}])
    assert metric.get_aggregate_stats(df) == {"total": 2, "rate": 0.67}


def test_latency():
    metric = code_metrics.LatencyMetric()
    metric_function = metric.get_metric()
    assert callable(metric_function)
    assert metric_function(data={"latency": 20}) == {}
    df = pd.DataFrame([{"latency": 20}, {"latency": 10}, {"latency": 5}])
    assert metric.get_aggregate_stats(df) == {"mean": 11.67, "max": 20, "min": 5}


def test_custom_relevance():
    metric = prompt_metrics.RelevanceMetric()

    assert isinstance(metric.get_metric(), PromptMetric)
    df = pd.DataFrame([{"relevance_score": 5}, {"relevance_score": 4}, {"relevance_score": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 4.0, "pass_count": 2, "pass_rate": 0.67}


def test_custom_coherence():
    metric = prompt_metrics.CoherenceMetric()

    assert isinstance(metric.get_metric(), PromptMetric)
    df = pd.DataFrame([{"coherence_score": 5}, {"coherence_score": 4}, {"coherence_score": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 4.0, "pass_count": 2, "pass_rate": 0.67}


def test_custom_groundedness():
    metric = prompt_metrics.GroundednessMetric()

    assert isinstance(metric.get_metric(), PromptMetric)
    df = pd.DataFrame([{"groundedness_score": 5}, {"groundedness_score": 4}, {"groundedness_score": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 4.0, "pass_count": 2, "pass_rate": 0.67}


def test_custom_relevance_missing_values():
    metric = prompt_metrics.RelevanceMetric()

    assert isinstance(metric.get_metric(), PromptMetric)
    df = pd.DataFrame([{"relevance_score": 2}, {"relevance_score": 4}, {"relevance_score": "Failed"}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 3.0, "pass_count": 1, "pass_rate": 0.33}


def test_builtin_coherence():
    metric = builtin_metrics.BuiltinCoherenceMetric()
    assert metric.get_metric() == "gpt_coherence"
    df = pd.DataFrame([{"gpt_coherence": 5}, {"gpt_coherence": 4}, {"gpt_coherence": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 4.0, "pass_count": 2, "pass_rate": 0.67}


def test_builtin_relevance():
    metric = builtin_metrics.BuiltinRelevanceMetric()
    assert metric.get_metric() == "gpt_relevance"
    df = pd.DataFrame([{"gpt_relevance": 5}, {"gpt_relevance": 4}, {"gpt_relevance": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 4.0, "pass_count": 2, "pass_rate": 0.67}


def test_builtin_groundedness():
    metric = builtin_metrics.BuiltinGroundednessMetric()
    assert metric.get_metric() == "gpt_groundedness"
    df = pd.DataFrame([{"gpt_groundedness": 5}, {"gpt_groundedness": 4}, {"gpt_groundedness": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 4.0, "pass_count": 2, "pass_rate": 0.67}


def test_builtin_coherence_missing_values():
    metric = builtin_metrics.BuiltinCoherenceMetric()
    assert metric.get_metric() == "gpt_coherence"
    df = pd.DataFrame([{"gpt_coherence": "Failed"}, {"gpt_coherence": 4}, {"gpt_coherence": 3}])
    assert metric.get_aggregate_stats(df) == {"mean_rating": 3.5, "pass_count": 1, "pass_rate": 0.33}
