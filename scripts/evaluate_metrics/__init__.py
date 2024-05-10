from .builtin_metrics import (
    BuiltinCoherenceMetric, BuiltinGroundednessMetric, BuiltinRelevanceMetric,
    BuiltinFluencyMetric, BuiltinHateUnfairnessyMetric, BuiltinSelfHarmMetric,
    BuiltinSexualMetric, BuiltinSimilarityMetric, BuiltinViolenceMetric,
)
from .code_metrics import (
    AnswerLengthMetric, CitationMatchMetric, HasCitationMetric,
    LatencyMetric, ContextSimilarityMetric, AnswerSimilarityMetric,
)
from .prompt_metrics import (
    CoherenceMetric, DontKnownessMetric, GroundednessMetric,
    RelevanceMetric, FaithfullnessMetric, AnswerRelevanceMetric,
    ContextRelevanceMetric,
)

metrics = [
    BuiltinCoherenceMetric,
    BuiltinRelevanceMetric,
    BuiltinGroundednessMetric,
    BuiltinFluencyMetric,
    BuiltinHateUnfairnessyMetric,
    BuiltinSelfHarmMetric,
    BuiltinSexualMetric,
    BuiltinSimilarityMetric,
    BuiltinViolenceMetric,

    CoherenceMetric,
    RelevanceMetric,
    GroundednessMetric,
    DontKnownessMetric,
    FaithfullnessMetric,
    AnswerRelevanceMetric,
    ContextRelevanceMetric,

    LatencyMetric,
    AnswerLengthMetric,
    HasCitationMetric,
    CitationMatchMetric,
    AnswerSimilarityMetric,
    ContextSimilarityMetric,
]

metrics_by_name = {metric.METRIC_NAME: metric for metric in metrics}

# Faithfulness
# Answer Relevance
# Context Relevance
# Answer-Expectation Similarity
# Context-Question Similarity

