import argparse
import json
from pathlib import Path
from markitdown import MarkItDown
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from typing import Annotated
from openai import OpenAI


def add_text(a: list[str], b: str):
    return [*a, b]


def state_partial(func, *args, **kwargs):
    def wrapper(state):
        return func(state=state, *args, **kwargs)
    return wrapper


promt_get_topics = """以下の文章を読んで、トピックを抽出してください。
```
{source}
```

結果は以下のjson形式で出力してください。
{{"list": ["トピック1", "トピック2", ...]}}
"""

promt_get_title = """次のトピックにタイトルをつけてしてください。出力は、タイトルのみを返してください。
{topic}
"""
promt_get_detail = """以下の文章を読んで、トピックの詳細を抽出してください。

# トピック
{topic}

# ソース
{source}
"""

promt_get_summary = """以下の文章を読んで、トピックを要約してください。
# トピック
```
{topic}
```

# ソース
```
{source}
```
"""

promt_get_knowledge = """以下の文章を読んで、トピックの知識を抽出してください。ただし、次の制限を守る必要があります。
# 制限（既知の事項は抽出しない）
以下の事項は既知のため、抽出しないこと。
{knowledge}

# トピック
```
{topic}
```

# ソース
```
{source}

```
"""

promt_get_knowledge_for_query = """以下の文章を読んで、質問に対する知識を抽出してください。ただし、次の制限を守る必要があります。
# 制限（既知の事項は抽出しない）
以下の事項は既知のため、抽出しないこと。
{knowledge}

# 質問
{query}

# トピック
```
{topic}
```
# ソース
```
{source}
```
"""

promt_get_total_summary = """以下の文章を読んで、全体の要約をしてください。
# タイトル
{title}

# トピック毎の要約
{summaries}
"""

promt_get_answer = """以下の質問に回答してください。。
# 質問
{query}

# ソース概要
{total_summary}

# トピック毎の知識
{knowledge}
"""


def get_openai_moldel(model_name: str, json_mode: bool = False):
    client = OpenAI()

    def fn(prompt: str):
        additional_kwargs = {}
        if json_mode:
            additional_kwargs["text"] = {"format": {"type": "json_object"}}
        response = client.responses.create(
            model=model_name,
            input=prompt,
            **additional_kwargs,
        )
        if json_mode:
            return json.loads(response.output_text)
        else:
            return response.output_text

    return fn


class State(TypedDict):
    query: str
    source_target: str  # URLなりパスなり（markitdown対応していればOK）
    source_title: str
    source_text: str
    source_markdown: str
    topics: list[str]
    tmp_i_topic: int
    title_per_topic: Annotated[list[str], add_text]
    detail_per_topic: Annotated[list[str], add_text]
    summary_per_topic: Annotated[list[str], add_text]
    knowledge_per_topic: Annotated[list[str], add_text]
    knowledge_for_query_per_topic: Annotated[list[str], add_text]
    total_summary: str
    answer: str


def export_state(state: State, workspace: Path):
    with open(workspace / "details.json", "w") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)
    with open(workspace / "summary.md", "w") as f:
        f.write(state["total_summary"])

    source_dir = workspace / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_file = source_dir / "source.md"
    with open(source_file, "w") as f:
        f.write(state["source_markdown"])

    topics_dir = workspace / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)
    for i, (title, detail, summary, knowledge, knowledge_for_query) in enumerate(
            zip(
                state["title_per_topic"],
                state["detail_per_topic"],
                state["summary_per_topic"],
                state["knowledge_per_topic"],
                state["knowledge_for_query_per_topic"],
            ), start=1):
        title = title.replace("/", "_")
        topic_dir = topics_dir / f"topic_{i:02d}_{title}"
        assert topic_dir.resolve().is_relative_to(topics_dir.resolve())
        topic_dir.mkdir(parents=True, exist_ok=True)
        with open(topic_dir / "detail.md", "w") as f:
            f.write(detail)
        with open(topic_dir / "summary.md", "w") as f:
            f.write(summary)
        with open(topic_dir / "knowledge.md", "w") as f:
            f.write(knowledge)
        with open(topic_dir / "knowledge_for_query.md", "w") as f:
            f.write(knowledge_for_query)


def build_graph(llm_fn, llm_fn_json_mode):
    graph = StateGraph(State)
    graph.add_node("get_source", get_source)
    graph.add_node("get_topics", state_partial(
        get_topics, llm_fn=llm_fn_json_mode, prompt=promt_get_topics))
    graph.add_node("iterate_topics", iterate_topics)
    graph.add_node("get_title", state_partial(
        get_title, llm_fn=llm_fn, prompt=promt_get_title))
    graph.add_node("get_detail", state_partial(
        get_detail, llm_fn=llm_fn, prompt=promt_get_detail))
    graph.add_node("get_summary", state_partial(
        get_summary, llm_fn=llm_fn, prompt=promt_get_summary))
    graph.add_node("get_knowledge", state_partial(
        get_knowledge, llm_fn=llm_fn, prompt=promt_get_knowledge))
    graph.add_node("get_knowledge_for_query", state_partial(
        get_knowledge_for_query, llm_fn=llm_fn, prompt=promt_get_knowledge_for_query))
    graph.add_node("get_total_summary", state_partial(
        get_total_summary, llm_fn=llm_fn, prompt=promt_get_total_summary))
    graph.add_node("get_answer", state_partial(
        get_answer, llm_fn=llm_fn, prompt=promt_get_answer))

    graph.add_edge(START, "get_source")
    graph.add_edge("get_source", "get_topics")
    graph.add_edge("get_topics", "iterate_topics")
    graph.add_conditional_edges(
        "iterate_topics", path=does_finish_topics_iteration,
        path_map={True: "get_total_summary", False: "get_title"}
    )
    graph.add_edge("get_title", "get_detail")
    graph.add_edge("get_detail", "get_summary")
    graph.add_edge("get_summary", "get_knowledge")
    graph.add_edge("get_knowledge", "get_knowledge_for_query")
    graph.add_edge("get_knowledge_for_query", "iterate_topics")

    graph.add_edge("get_total_summary", "get_answer")
    graph.add_edge("get_answer", END)
    return graph


def get_source(state: State):
    target = state["source_target"]
    md = MarkItDown()
    converted = md.convert(target)
    return {
        "source_title": converted.title,
        "source_text": converted.text_content,
        "source_markdown": converted.markdown,
    }


def get_topics(llm_fn, prompt: str, state: State):
    source_md = state["source_markdown"]
    topics = llm_fn(prompt.format(source=source_md))["list"]

    return {"topics": topics}


def iterate_topics(state: State):
    tmp_i_topic = state.get("tmp_i_topic", -1)
    return {
        "tmp_i_topic": tmp_i_topic + 1
    }


def does_finish_topics_iteration(state: State):
    tmp_i_topic = state["tmp_i_topic"]
    topics = state["topics"]
    return tmp_i_topic >= len(topics)


def get_title(state: State, llm_fn, prompt: str):
    topic = state["topics"][state["tmp_i_topic"]]
    title = llm_fn(prompt.format(topic=topic))

    i = state["tmp_i_topic"] + 1
    n = len(state["topics"])
    print(f"start topic[{i}/{n}]: {topic}")

    return {
        "title_per_topic": title.strip(),
    }


def get_detail(state: State, llm_fn, prompt: str):
    topic = state["topics"][state["tmp_i_topic"]]
    source_md = state["source_markdown"]
    detail = llm_fn(prompt.format(topic=topic, source=source_md))
    return {
        "detail_per_topic": detail,
    }


def get_summary(state: State, llm_fn, prompt: str):
    topic = state["topics"][state["tmp_i_topic"]]
    detail = state["detail_per_topic"][state["tmp_i_topic"]]
    summary = llm_fn(prompt.format(
        topic=topic, source=detail))
    return {
        "summary_per_topic": summary,
    }


def get_knowledge(state: State, llm_fn, prompt: str):
    topic = state["topics"][state["tmp_i_topic"]]
    detail = state["detail_per_topic"][state["tmp_i_topic"]]
    old_knowledges = state["knowledge_per_topic"]
    if old_knowledges:
        old_knowledge = "（なし）"
    else:
        old_knowledge = []
        for k in old_knowledges:
            old_knowledge.append(f"- {k}")
        old_knowledge = "\n".join(old_knowledge)

    knowledge = llm_fn(prompt.format(
        topic=topic, source=detail, knowledge=old_knowledge))
    return {
        "knowledge_per_topic": knowledge,
    }


def get_knowledge_for_query(state: State, llm_fn, prompt: str):
    query = state["query"]
    topic = state["topics"][state["tmp_i_topic"]]
    detail = state["detail_per_topic"][state["tmp_i_topic"]]
    old_knowledges = state["knowledge_for_query_per_topic"]
    if old_knowledges:
        old_knowledge = "（なし）"
    else:
        old_knowledges = []
        for k in old_knowledges:
            old_knowledges.append(f"- {k}")
        old_knowledge = "\n".join(old_knowledges)
    knowledge_for_query = llm_fn(prompt.format(
        query=query,
        topic=topic, source=detail, knowledge=old_knowledge))
    return {
        "knowledge_for_query_per_topic": knowledge_for_query,
    }


def get_total_summary(state: State, llm_fn, prompt: str):
    title = state["source_title"]
    title_per_topic = state["title_per_topic"]
    summary_per_topic = state["summary_per_topic"]

    summaries = []
    for t_title, t_summary in zip(title_per_topic, summary_per_topic):
        summaries.append(f"## {t_title}\n{t_summary}")

    total_summary = llm_fn(prompt.format(
        title=title,
        summaries="\n\n".join(summaries),
    ))
    return {
        "total_summary": total_summary,
    }


def get_answer(state: State, llm_fn, prompt: str):
    query = state["query"]
    title_per_topic = state["title_per_topic"]
    knowledge_for_query_per_topic = state["knowledge_for_query_per_topic"]
    total_summary = state["total_summary"]

    knowledges = []
    for t_title, t_knowledge in zip(title_per_topic, knowledge_for_query_per_topic):
        knowledges.append(f"## {t_title}\n{t_knowledge}")

    answer = llm_fn(prompt.format(
        query=query,
        total_summary=total_summary,
        knowledge="\n\n".join(knowledges)
    ))
    return {
        "answer": answer,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-q", "--query", required=True)
    parser.add_argument("-w", "--workspace", required=True, type=Path)
    parser.add_argument("-m", "--model", default="gpt-4o")
    return parser.parse_args()


def main():
    args = parse_args()
    args.workspace.mkdir(parents=True, exist_ok=True)
    llm_fn = get_openai_moldel(args.model)
    llm_fn_json_mode = get_openai_moldel(args.model, json_mode=True)
    graph = build_graph(llm_fn=llm_fn, llm_fn_json_mode=llm_fn_json_mode)
    graph = graph.compile()
    with open("graph.png", "wb") as f:
        f.write(graph.get_graph().draw_png())
    result = graph.invoke(
        {"query": args.query, "source_target": args.target},
        {"recursion_limit": 1000},
    )

    export_state(result, args.workspace)


if __name__ == "__main__":
    main()
