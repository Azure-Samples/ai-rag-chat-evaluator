import json
import logging
from pathlib import Path

from azure.ai.generative.synthetic.qa import QADataGenerator, QAType
from azure.search.documents import SearchClient


def generate_test_qa_data(
    openai_config: dict,
    search_client: SearchClient,
    num_questions_total: int,
    num_questions_per_source: int,
    output_file: Path,
):
    logging.info(
        "Generating %d questions total, %d per source, based on search results",
        num_questions_total,
        num_questions_per_source,
    )
    # Account for evaluate vs. generate SDK differences
    openai_config["deployment"] = openai_config["deployment_id"]

    qa_generator = QADataGenerator(model_config=openai_config)

    r = search_client.search("", top=1000)
    qa: list[dict] = []
    for doc in r:
        if len(qa) > num_questions_total:
            break
        logging.info("Processing search document %s", doc["sourcepage"])
        text = doc["content"]

        result = qa_generator.generate(
            text=text,
            qa_type=QAType.LONG_ANSWER,
            num_questions=num_questions_per_source,
        )

        for question, answer in result["question_answers"]:
            citation = f"[{doc['sourcepage']}]"
            qa.append({"question": question, "answer": answer + citation})

    logging.info("Writing %d questions to %s", len(qa), output_file)
    with open(output_file, "w") as f:
        for item in qa:
            f.write(json.dumps(item) + "\n")
