# a CLI tool to diff two JSON files
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Markdown, Static

from .utils import diff_directories


class DiffApp(App):
    CSS_PATH = "diff_app.tcss"

    def __init__(self, directories: list[Path], changed: str = None):
        super().__init__()
        # Only include the first directory if the second is not provided
        self.directories = directories
        self.changed = changed
        self.data_dicts = []  # Store dicts keyed by question
        self.result_index = 0  # Based on results in the first directory

    def on_mount(self):
        self.data_dicts = diff_directories(self.directories)
        self.next_question()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.exit()
        else:
            self.next_question()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(id="question")
            with Horizontal(id="sources"):
                for directory in self.directories:
                    yield Static(directory.name, classes="source")
                if len(self.directories) == 1:
                    yield Static("Ground truth answer", classes="source")
            with Horizontal(id="answers"):
                for ind in range(len(self.directories)):
                    with VerticalScroll(classes="answer"):
                        yield Markdown(id=f"answer{ind}")
                if len(self.directories) == 1:
                    with VerticalScroll(classes="answer"):
                        yield Markdown(id="answer_truth")
            with Horizontal(id="metrics"):
                for ind in range(len(self.directories)):
                    yield DataTable(id=f"metrics{ind}", show_cursor=False, cell_padding=1)
            with Horizontal(id="buttons"):
                yield Button.success("Next question", classes="button")
                yield Button.error("Quit", id="quit", classes="button")

    def next_question(self):
        if self.result_index >= len(self.data_dicts[0]):
            self.exit()
            return
        question = list(self.data_dicts[0].keys())[self.result_index]
        self.query_one("#question", Static).update(question)

        for ind in range(len(self.directories)):
            try:
                self.query_one(f"#answer{ind}", Markdown).update(self.data_dicts[ind][question]["answer"])
                if len(self.directories) == 1:
                    self.query_one("#answer_truth", Markdown).update(self.data_dicts[0][question]["truth"])
            except KeyError:
                self.query_one(f"#answer{ind}", Markdown).update("No answer found for that question")
                continue

            # Find all fields in the result that have numeric values
            metric_columns = []
            metric_values = []
            question_results = self.data_dicts[ind][question]
            for column, value in question_results.items():
                if isinstance(value, int | float):
                    metric_columns.append(column)
                    metric_values.append(round(value, 1) if isinstance(value, float) else value)
            datatable = self.query_one(f"#metrics{ind}", DataTable)
            datatable.clear(columns=True).add_columns(*metric_columns)
            datatable.add_row(*metric_values)
            datatable.add_row("" * len(metric_columns))

        self.result_index += 1


def main(directories: list[Path], changed: str | None = None):
    app = DiffApp(directories, changed)
    app.run()
