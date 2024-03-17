from pathlib import Path

import typer

from . import diff_app, summary_app

app = typer.Typer()


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
def summary(results_dir: Path = typer.Argument(exists=True, dir_okay=True, file_okay=False)):
    summary_app.main(results_dir)


def cli():
    app()
