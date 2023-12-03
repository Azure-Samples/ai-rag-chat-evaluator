import argparse
import json
import logging
import os
import re
import time
from pathlib import Path

import dotenv
import urllib3
from azure.ai.generative.evaluate import evaluate
from azure.identity import AzureDeveloperCliCredential


def send_question_to_target(question: str, target_url: str, parameters: dict = {}):
    http = urllib3.PoolManager()
    headers = {"Content-Type": "application/json"}
    body = {
        "messages": [{"content": question, "role": "user"}],
        "stream": False,
        "context": parameters,
    }
    r = http.request("POST", target_url, headers=headers, body=json.dumps(body))
    try:
        response_dict = json.loads(r.data.decode("utf-8"))
        return {
            "question": question,
            "answer": response_dict["choices"][0]["message"]["content"],
            "context": "\n\n".join(response_dict["choices"][0]["context"]["data_points"]),
        }
    except Exception as e:
        logging.error(e)
        return {
            "question": question,
            "answer": "ERROR",
            "context": "ERROR",
        }


def load_jsonl(path: Path) -> list[dict()]:
    with open(path) as f:
        return [json.loads(line) for line in f.readlines()]


def run_evaluation(
    openai_config: dict,
    testdata_path: Path,
    results_dir: Path,
    target_url: str,
    target_parameters={},
    num_questions=None,
):
    testdata = load_jsonl(testdata_path)
    if num_questions:
        testdata = testdata[:num_questions]

    # Wrap the target function so that it can be called with a single argument
    async def wrap_target(question: str):
        return send_question_to_target(question, target_url, target_parameters)

    gpt_metrics = ["gpt_groundedness", "gpt_relevance", "gpt_coherence", "gpt_similarity"]
    results = evaluate(
        evaluation_name="baseline-evaluation",
        target=wrap_target,
        data=testdata,
        task_type="qa",
        metrics_list=gpt_metrics,
        model_config=openai_config,
        data_mapping={
            # Must match qa.jsonl
            "questions": "question",  # column of data providing input to model
            "y_test": "truth",  # column of data providing ground truth answer, optional for default metrics
            # Must match return value of target function
            "contexts": "context",  # column of data providing context for each input
            "y_pred": "answer",  # column of data providing output from model
        },
        tracking=False,
        output_path=results_dir,
    )

    eval_results_filename = list(results.artifacts.keys())[0]
    with open(results_dir / eval_results_filename) as f:
        questions_with_ratings = [json.loads(question_json) for question_json in f.readlines()]

    metrics = {
        metric_name: {
            "mean_rating": round(results.metrics_summary[f"mean_{metric_name}"], 2),
            "pass_count": 0,
            "pass_rate": 0,
        }
        for metric_name in gpt_metrics
    }
    total_length = 0
    max_length = 0
    min_length = 9999999999
    total_with_citation = 0

    def passes_threshold(rating):
        return int(rating) >= 4

    for ind, question_with_rating in enumerate(questions_with_ratings):
        total_length += len(question_with_rating["answer"])
        max_length = max(max_length, len(question_with_rating["answer"]))
        min_length = min(min_length, len(question_with_rating["answer"]))
        total_with_citation += 1 if re.search(r"\[[^\]]+\]", question_with_rating["answer"]) else 0
        for metric_name in gpt_metrics:
            if passes_threshold(question_with_rating[metric_name]):
                metrics[metric_name]["pass_count"] += 1
            metrics[metric_name]["pass_rate"] = round(metrics[metric_name]["pass_count"] / (ind + 1), 2)
    metrics["answer_length"] = {
        "total": total_length,
        "mean": round(total_length / len(questions_with_ratings), 2),
        "max": max_length,
        "min": min_length,
    }
    metrics["answer_has_citation"] = {
        "total": total_with_citation,
        "rate": round(total_with_citation / len(questions_with_ratings), 2),
    }

    # summary statistics
    with open(results_dir / "summary.json", "w") as summary_file:
        summary_file.write(json.dumps(metrics, indent=4))

    with open(results_dir / "evaluate_parameters.json", "w") as parameters_file:
        parameters = {
            "evaluation_gpt_model": openai_config["model"],
            "evaluation_timestamp": int(time.time()),
            "testdata_path": str(testdata_path),
            "target_url": target_url,
            "target_parameters": target_parameters,
            "num_questions": num_questions,
        }
        parameters_file.write(json.dumps(parameters, indent=4))


if __name__ == "__main__":
    dotenv.load_dotenv()

    logging.basicConfig(level=logging.DEBUG)

    WORKING_DIR = Path.cwd()

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to config.json", default="config.json")
    parser.add_argument("--numquestions", type=int, help="Number of questions to evaluate")
    args = parser.parse_args()

    # Read config from config.json
    config_path = WORKING_DIR / Path(args.config)
    with open(config_path) as f:
        config = json.load(f)

        def replace_special_markers(obj):
            if isinstance(obj, dict):
                for key in obj:
                    if isinstance(obj[key], dict):
                        replace_special_markers(obj[key])
                    elif isinstance(obj[key], str) and "<TIMESTAMP>" in obj[key]:
                        obj[key] = obj[key].replace("<TIMESTAMP>", str(int(time.time())))
                    elif isinstance(obj[key], str) and "<READFILE>" in obj[key]:
                        with open(obj[key].replace("<READFILE>", "")) as f:
                            obj[key] = f.read()

        replace_special_markers(config)

    results_dir = Path(config["results_dir"])

    # OpenAI API config
    if os.environ.get("OPENAI_HOST") == "azure":
        if os.environ.get("AZURE_OPENAI_API_KEY"):
            api_type = "azure"
            api_key = os.environ["AZURE_OPENAI_API_KEY"]
        else:
            api_type = "azure_ad"
            azure_credential = AzureDeveloperCliCredential()
            api_key = azure_credential.get_token("https://cognitiveservices.azure.com/.default").token
        openai_config = {
            "api_type": api_type,
            "api_base": f"https://{os.environ['AZURE_OPENAI_SERVICE']}.openai.azure.com",
            "api_key": api_key,
            "api_version": "2023-07-01-preview",
            "deployment_id": os.environ["AZURE_OPENAI_EVAL_DEPLOYMENT"],
            "model": os.environ["OPENAI_GPT_MODEL"],
        }
    else:
        openai_config = {
            "api_key": os.environ["OPENAI_API_KEY"],
            "model": os.environ["OPENAI_GPT_MODEL"],
        }

    run_evaluation(
        openai_config=openai_config,
        testdata_path=WORKING_DIR / config["testdata_path"],
        results_dir=results_dir,
        target_url=config["target_url"],
        target_parameters=config["target_parameters"],
        num_questions=args.numquestions,
    )

    # copy config.json to results dir
    with open(config_path) as f:
        with open(results_dir / "config.json", "w") as f2:
            f2.write(f.read())
