from pathlib import Path

import pytest
from openai.types.responses.response_usage import (
    InputTokensDetails,
    OutputTokensDetails,
    ResponseUsage,
)

from llm_logger import UsageLogger


def test_add_openai_usage() -> None:
    try:
        logger = UsageLogger(log_dir=Path("_tmp/logs"))
        logger.add_openai_usage(
            usage=ResponseUsage(
                input_tokens=1000,
                output_tokens=2000,
                total_tokens=3000,
                input_tokens_details=InputTokensDetails(cached_tokens=100),
                output_tokens_details=OutputTokensDetails(reasoning_tokens=50),
            ),
            model_name="gpt-4o",
            elapsed_time_sec=1.5,
        )
        logger.add_openai_usage(
            usage=ResponseUsage(
                input_tokens=1500,
                output_tokens=2500,
                total_tokens=3500,
                input_tokens_details=InputTokensDetails(cached_tokens=150),
                output_tokens_details=OutputTokensDetails(reasoning_tokens=55),
            ),
            model_name="gpt-4.1",
            elapsed_time_sec=1.5,
        )
        logger.add_openai_usage(
            usage=ResponseUsage(
                input_tokens=1500,
                output_tokens=2500,
                total_tokens=3500,
                input_tokens_details=InputTokensDetails(cached_tokens=150),
                output_tokens_details=OutputTokensDetails(reasoning_tokens=55),
            ),
            model_name="gpt-4o",
            elapsed_time_sec=1.5,
        )
        logger.summary()
        logger.total_cost_usd()
        logger.save_csv_logs()
        logger.show_summary()

    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
