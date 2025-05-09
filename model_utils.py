import json
import time
from collections.abc import Callable
from typing import Any

from openai import OpenAI
from openai.types import ResponsesModel

from llm_logger import UsageLogger


def add_text(a: list[str], b: str) -> list[str]:
    return [*a, b]


def add_object(a: list[Any], b: Any) -> list[Any]:
    return [*a, b]


def update_dict(a: dict, b: dict) -> dict:
    return a.copy().update(b)


def get_openai_moldel(
    model_name: ResponsesModel, usage_logger: UsageLogger, json_mode: bool = False
) -> Callable[[str], str | Any]:
    client = OpenAI()

    def fn(prompt: str) -> str | Any:
        additional_kwargs: dict[str, Any] = {}
        if json_mode:
            additional_kwargs["text"] = {"format": {"type": "json_object"}}
        start = time.perf_counter()
        try:
            response = client.responses.create(
                model=model_name,
                input=prompt,
                **additional_kwargs,
            )
        except Exception as e:
            print("Error:", e)
            usage_logger.save_csv_logs()
            usage_logger.show_summary()
            raise

        end = time.perf_counter()
        usage_logger.add_openai_usage(
            usage=response.usage,
            model_name=model_name,
            elapsed_time_sec=end - start,
        )
        usage_logger.show_last_usage()
        output_text: str = response.output_text
        if json_mode:
            return json.loads(output_text)
        else:
            return output_text

    return fn
