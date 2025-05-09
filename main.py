import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from openai.types import ResponsesModel

import graph_v1
import graph_v2
from llm_logger import UsageLogger
from model_utils import get_openai_moldel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-q", "--query", required=True)
    parser.add_argument("-w", "--workspace", required=True, type=Path)
    parser.add_argument("-m", "--model", default="gpt-4o")
    parser.add_argument("-g", "--graph", choices=["v1"], default="v1")
    return parser.parse_args()


def run_graph_v1(args: argparse.Namespace) -> None:
    args.workspace.mkdir(parents=True, exist_ok=True)
    usage_logger = UsageLogger(args.workspace / "usage")
    model = cast(ResponsesModel, args.model)
    llm_fn = cast(Callable[[str], str], get_openai_moldel(model, usage_logger))
    llm_fn_json_mode = cast(Callable[[str], Any], get_openai_moldel(model, usage_logger, json_mode=True))
    graph = graph_v1.build_graph(llm_fn=llm_fn, llm_fn_json_mode=llm_fn_json_mode).compile()
    graph.get_graph().draw_png("graph_v1.png")
    result = graph.invoke(
        {"query": args.query, "source_target": args.target},
        {"recursion_limit": 1000},
    )
    print(result["answer"])

    graph_v1.export_state(cast(State, result), args.workspace)
    usage_logger.save_csv_logs()
    usage_logger.show_summary()
    print("Exported state to", args.workspace)


def run_graph_v2(args: argparse.Namespace) -> None:
    args.workspace.mkdir(parents=True, exist_ok=True)
    usage_logger = UsageLogger(args.workspace / "usage")
    model = cast(ResponsesModel, args.model)
    llm_fn = cast(Callable[[str], str], get_openai_moldel(model, usage_logger))
    llm_fn_json_mode = cast(Callable[[str], Any], get_openai_moldel(model, usage_logger, json_mode=True))
    graph = graph_v2.build_graph(llm_fn=llm_fn, llm_fn_json_mode=llm_fn_json_mode).compile()
    graph.get_graph().draw_png("graph_v2.png")
    result = graph.invoke(
        {"query": args.query, "source_target": args.target},
        {"recursion_limit": 1000},
    )
    print(result["answer"])

    graph_v2.export_state(cast(State, result), args.workspace)
    usage_logger.save_csv_logs()
    usage_logger.show_summary()
    print("Exported state to", args.workspace)


def main() -> None:
    args = parse_args()
    match args.graph:
        case "v1":
            run_graph_v1(args)
        case "v2":
            run_graph_v2(args)
        case _:
            raise ValueError(f"Unknown graph version: {args.graph}")


if __name__ == "__main__":
    main()
