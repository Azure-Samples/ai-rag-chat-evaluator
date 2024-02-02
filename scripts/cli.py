import logging
from pathlib import Path

import dotenv
import typer

from . import service_setup
from .evaluate import run_evaluate_from_config
from .generate import generate_test_qa_data

app = typer.Typer(pretty_exceptions_enable=False)

logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(name)s: %(message)s", datefmt="%H:%M:%S")

dotenv.load_dotenv()


def int_or_none(raw: str) -> int | None:
    return None if raw == "None" else int(raw)


@app.command()
def evaluate(
    config: Path = typer.Option(
        exists=True, dir_okay=False, file_okay=True, help="Path to config.json", default="config.json"
    ),
    numquestions: int | None = typer.Option(
        help="Number of questions to evaluate (defaults to all if not specified).", default=None, parser=int_or_none
    ),
):
    run_evaluate_from_config(Path.cwd(), config, numquestions)


@app.command()
def generate(
    output: Path = typer.Option(exists=False, dir_okay=False, file_okay=True),
    numquestions: int = typer.Option(help="Number of questions to generate", default=200),
    persource: int = typer.Option(help="Number of questions to generate per source", default=5),
):
    generate_test_qa_data(
        openai_config=service_setup.get_openai_config(),
        search_client=service_setup.get_search_client(),
        num_questions_total=numquestions,
        num_questions_per_source=persource,
        output_file=Path.cwd() / output,
    )


def cli():
    app()
