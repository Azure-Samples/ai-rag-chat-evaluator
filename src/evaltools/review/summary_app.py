import json
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, TextArea

from .utils import summarize_results


class ParametersScreen(ModalScreen):
    CSS_PATH = "parameters_screen.tcss"

    def __init__(self, folder, parameters) -> None:
        super().__init__()
        self.folder = folder
        self.parameters = parameters

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"Parameters for: {self.folder}", id="header"),
            TextArea(json.dumps(self.parameters, indent=4), language="json", id="body"),
            Button("Close", variant="primary", id="button"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()


class TableApp(App):
    CSS_PATH = "summary_app.tcss"

    def __init__(self, results_dir: Path) -> None:
        super().__init__()
        self.rows, self.row_parameters = summarize_results(results_dir)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield DataTable(id="table")
        with Horizontal(id="buttons"):
            yield Button.error("Quit", id="quit", classes="button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.exit()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.rows[0])
        table.add_rows(self.rows[1:])

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.coordinate.column == 0:
            folder = event.value
            if folder in self.row_parameters:
                parameters = self.row_parameters[folder]
                self.push_screen(ParametersScreen(folder, parameters))


def main(directory: Path):
    app = TableApp(directory)
    app.run()
