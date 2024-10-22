from pathlib import Path

from .utils import diff_directories


def main(directories: list[Path], changed: str | None = None):
    data_dicts = diff_directories(directories, changed)

    markdown_str = ""
    for question in data_dicts[0].keys():
        markdown_str += f"**{question}**\n\n"
        # now make a table with the answers
        markdown_str += "|   | " + " | ".join([directory.name for directory in directories]) + " | ground_truth |\n"
        markdown_str += "|" + " |".join(["---"] * (len(directories) + 2)) + " |\n"
        markdown_str += (
            "| answer | "
            + " | ".join([data_dict[question]["answer"] for data_dict in data_dicts])
            + " | "
            + data_dicts[0][question]["truth"]
            + " |\n"
        )
        # now make a table with the metrics
        metrics = {}
        question_results = data_dicts[0][question]
        for column, value in question_results.items():
            if isinstance(value, int | float):
                metrics[column] = []
        for metric_name in metrics.keys():
            for data_dict in data_dicts:
                value = data_dict[question].get(metric_name)
                metrics[metric_name].append(str(round(value, 1) if isinstance(value, float) else str(value)))
        # make a row for each metric
        for metric_name, metric_values in metrics.items():
            markdown_str += f"| {metric_name} | " + " | ".join(metric_values) + " | N/A |\n"
        markdown_str += "\n"
    return markdown_str
