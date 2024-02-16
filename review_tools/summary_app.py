import json
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, TextArea


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
        # first find the shared metrics across the runs
        metric_counts = {}
        self.row_parameters = {}

        run_summaries = {}
        folders = [f for f in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, f))]
        folders.sort()
        for folder in folders:
            with open(Path(results_dir) / folder / "summary.json") as f:
                summary = json.load(f)
                run_summaries[folder] = summary
                # first find the common parameters across the runs
                for metric_name in summary:
                    metric_counts[metric_name] = metric_counts.get(metric_name, 0) + 1

        # Only show metrics that have shown up at least twice across runs
        shared_metric_names = [metric_name for metric_name, count in metric_counts.items() if count > 1]
        shared_metric_stats = {metric_name: set() for metric_name in shared_metric_names}

        # Now figure out what stat to show about each metric
        for folder, summary in run_summaries.items():
            for metric_name in shared_metric_names:
                if metric_name in summary:
                    metric = summary[metric_name]
                    if "mean_rating" in metric:
                        shared_metric_stats[metric_name].add("mean_rating")
                    elif "mean" in metric:
                        shared_metric_stats[metric_name].add("mean")
                    if "pass_rate" in metric:
                        shared_metric_stats[metric_name].add("pass_rate")
                    elif "rate" in metric:
                        shared_metric_stats[metric_name].add("rate")

        first_row = ["folder"]
        second_row = [""]
        for metric_name in shared_metric_names:
            # The first row of columns should have metric name followed by blank column for each stat above 1 stat
            first_row.append(metric_name)
            if len(shared_metric_stats[metric_name]) > 1:
                first_row.extend([""] * (len(shared_metric_stats[metric_name]) - 1))
            # The second row of columns should just have the stat names
            for stat in shared_metric_stats[metric_name]:
                second_row.append(stat)

        self.rows = [first_row, second_row]

        for folder, summary in run_summaries.items():
            run_row = [folder]
            for metric_name in shared_metric_names:
                for stat in shared_metric_stats[metric_name]:
                    if stat in summary.get(metric_name, {}):
                        run_row.append(summary[metric_name][stat])
                    else:
                        run_row.append("?")
            self.rows.append(run_row)

            with open(Path(results_dir) / folder / "evaluate_parameters.json") as f:
                self.row_parameters[folder] = json.load(f)

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
