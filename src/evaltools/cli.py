import logging
from pathlib import Path

import dotenv
import typer
from rich.logging import RichHandler

from evaltools import service_setup
from evaltools.eval.evaluate import run_evaluate_from_config
from evaltools.gen.generate import generate_dontknows_qa_data, generate_test_qa_data_for_search_index
from evaltools.review import diff_app, summary_app, summary_markdown

app = typer.Typer(pretty_exceptions_enable=False)

logging.basicConfig(
    level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("evaltools")
# We only set the level to INFO for our logger,
# to avoid seeing the noisy INFO level logs from the Azure SDKs
logger.setLevel(logging.INFO)

dotenv.load_dotenv(override=True)


def int_or_none(raw: str) -> int | None:
    return None if raw == "None" else int(raw)


def str_or_none(raw: str) -> str | None:
    return None if raw == "None" else raw


def path_or_none(raw: str) -> Path | None:
    return None if raw == "None" else Path(raw)


@app.command()
def generate(
    output: Path = typer.Option(exists=False, dir_okay=False, file_okay=True),
    numquestions: int = typer.Option(help="Number of questions to generate", default=200),
    persource: int = typer.Option(help="Number of questions to generate per source", default=5),
    citationfieldname: str = typer.Option(help="Name of citiation field in ai search index", default="sourcepage"),
):
    generate_test_qa_data_for_search_index(
        openai_config=service_setup.get_openai_config_dict(),
        search_client=service_setup.get_search_client(),
        num_questions_total=numquestions,
        num_questions_per_source=persource,
        output_file=Path.cwd() / output,
        citation_field_name=citationfieldname,
    )


@app.command()
def generate_dontknows(
    input: Path = typer.Option(exists=True, dir_okay=False, file_okay=True),
    output: Path = typer.Option(exists=False, dir_okay=False, file_okay=True),
    numquestions: int = typer.Option(help="Number of questions to generate", default=40),
):
    generate_dontknows_qa_data(
        openai_config=service_setup.get_openai_config(),
        num_questions_total=numquestions,
        input_file=Path.cwd() / input,
        output_file=Path.cwd() / output,
    )


@app.command()
def evaluate(
    config: Path = typer.Option(
        exists=True, dir_okay=False, file_okay=True, help="Path to config.json", default="config.json"
    ),
    numquestions: int | None = typer.Option(
        help="Number of questions to evaluate (defaults to all if not specified).", default=None, parser=int_or_none
    ),
    targeturl: str | None = typer.Option(
        help="URL of the target service to evaluate against (defaults to the one in the config).",
        default=None,
        parser=str_or_none,
    ),
    resultsdir: Path = typer.Option(
        help="Directory to save the results of the evaluation", default=None, parser=path_or_none
    ),
):
    run_evaluate_from_config(Path.cwd(), config, numquestions, targeturl, resultsdir)


def str_or_none(value: str) -> str | None:
    return value if value != "None" else None


@app.command()
def diff(
    directory1: Path = typer.Argument(exists=True, dir_okay=True, file_okay=False),
    directory2: Path = typer.Argument(default=None, exists=True, dir_okay=True, file_okay=False),
    changed: str | None = typer.Option(
        help="Show only questions whose values changed for the given column", default=None, parser=str_or_none
    ),
):
    diff_app.main(directory1, directory2, changed)


@app.command()
def summary(
    results_dir: Path = typer.Argument(exists=True, dir_okay=True, file_okay=False),
    output: str | None = typer.Option(help="Output type, can be 'app' or 'markdown'", default=None, parser=str_or_none),
    highlight: str | None = typer.Option(
        help="Highlight a specific run in the summary", default=None, parser=str_or_none
    ),
):
    if output == "markdown":
        print(summary_markdown.main(results_dir, highlight_run=highlight))
    else:
        summary_app.main(results_dir)


def cli():
    app()
