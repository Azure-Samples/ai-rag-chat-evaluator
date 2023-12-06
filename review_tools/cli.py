from pathlib import Path

import typer

from . import diff_app, summary_app

app = typer.Typer()


@app.command()
def diff(
    directory1: Path = typer.Argument(exists=True, dir_okay=True, file_okay=False),
    directory2: Path = typer.Argument(exists=True, dir_okay=True, file_okay=False),
):
    diff_app.main(directory1, directory2)


@app.command()
def summary(results_dir: Path = typer.Argument(exists=True, dir_okay=True, file_okay=False)):
    summary_app.main(results_dir)


def cli():
    app()
