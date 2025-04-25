from datetime import datetime
from pathlib import Path
from typing import cast

import polars as pl
from openai.types.responses.response_usage import ResponseUsage

# 1M トークンあたりの価格定義（例: cached_input は input の半額）
PRICES_PER_1M_TOKENS = {
    "gpt-4.1": {"input": 3.0, "output": 12.0, "cached_input": 8.0},
    "gpt-4.1-mini": {"input": 0.8, "output": 3.2, "cached_input": 1.6},
    "gpt-4o": {"input": 3.75, "output": 15.0, "cached_input": 1.25},
    "o4-mini": {"input": 1.1, "output": 4.4, "cached_input": 4.4},
}


class UsageLogger:
    def __init__(
        self,
        log_dir: Path,
        prices_per_1m_tokens: dict[str, dict[str, float]] | None = None,
    ):
        self.__records: list[dict[str, bool | str | float | datetime]] = []
        self.__log_dir = log_dir
        self.__prices = prices_per_1m_tokens or PRICES_PER_1M_TOKENS

    def add_openai_usage(
        self,
        usage: ResponseUsage,
        model_name: str,
        elapsed_time_sec: float,
    ) -> None:
        pricing = self.__prices.get(model_name)
        if not pricing:
            raise ValueError(f"モデル '{model_name}' の価格情報が未登録です")

        # --- トークン数の取得 ---
        input_tokens = usage.input_tokens
        cached_input_tokens = usage.input_tokens_details.cached_tokens
        billed_input_tokens = input_tokens - cached_input_tokens

        output_tokens = usage.output_tokens
        reasoning_tokens = usage.output_tokens_details.reasoning_tokens
        total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens)

        # --- コスト計算 ---
        factor = 1_000_000
        cost_billed_input = (billed_input_tokens / factor) * pricing["input"]
        cost_cached_input = (cached_input_tokens / factor) * pricing["cached_input"]
        cost_output = (output_tokens / factor) * pricing["output"]
        total_cost = cost_billed_input + cost_cached_input + cost_output

        # --- レコードに保存 ---
        self.__records.append(
            {
                "timestamp": datetime.now().isoformat(),
                "model": model_name,
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_input_tokens,
                "billed_input_tokens": billed_input_tokens,
                "output_tokens": output_tokens,
                "reasoning_tokens": reasoning_tokens,
                "total_tokens": total_tokens,
                "cost_billed_input": cost_billed_input,
                "cost_cached_input": cost_cached_input,
                "cost_output": cost_output,
                "total_cost_usd": total_cost,
                "elapsed_sec": elapsed_time_sec,
            }
        )

    def summary(self) -> pl.DataFrame:
        """
        モデルごとの合計トークン数、合計コスト、平均処理時間(秒/トークン)を返す。
        """
        df = pl.DataFrame(self.__records)
        return df.group_by("model").agg(
            [
                pl.sum("total_tokens").alias("total_tokens"),
                pl.sum("total_cost_usd").alias("total_cost_usd"),
                (pl.sum("elapsed_sec") / pl.sum("total_tokens")).alias("avg_sec_per_token"),
            ]
        )

    def show_summary(self) -> None:
        """
        summary DataFrame を表示
        """
        summary_df = self.summary()
        print(summary_df)

    def show_last_usage(self) -> None:
        """
        最後のレコードを表示
        """
        if not self.__records:
            print("No records found.")
            return

        print("[Usage]")
        last_record = self.__records[-1]
        last_model = last_record["model"]
        last_tokens = last_record["total_tokens"]
        last_cost = last_record["total_cost_usd"]
        last_elapsed_sec = last_record["elapsed_sec"]
        print(
            f"    [Last] Model: {last_model}, Tokens: {last_tokens}, Cost($): {last_cost:.2f}, Time(s): {last_elapsed_sec:.2f}"  # noqa: E501
        )

        total_tokens = self.total_tokens()
        total_cost = self.total_cost_usd()
        total_elapsed_sec = self.total_elapsed_sec()
        print(
            f"    [Total] Tokens: {total_tokens}, Cost($): {total_cost:.2f}, Time(s): {total_elapsed_sec:.2f}"  # noqa: E501
        )

    def total_cost_usd(self) -> float:
        return sum(cast(float, r["total_cost_usd"]) for r in self.__records)

    def total_elapsed_sec(self) -> float:
        return sum(cast(float, r["elapsed_sec"]) for r in self.__records)

    def total_tokens(self) -> int:
        return sum(cast(int, r["total_tokens"]) for r in self.__records)

    def save_csv_logs(self) -> None:
        """
        詳細ログとサマリーログを CSV 形式で保存
        """
        self.__log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.__log_dir / "usage_log.csv"
        # 詳細ログを書き出し
        pl.DataFrame(self.__records).write_csv(str(log_path))

        summary_path = self.__log_dir / "usage_summary.csv"
        # サマリーを書き出し
        self.summary().write_csv(str(summary_path))

    def reset(self) -> None:
        self.__records = []
