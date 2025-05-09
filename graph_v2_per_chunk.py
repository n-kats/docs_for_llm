from typing import Annotated, Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from model_utils import update_dict

prompt_update_topics = """以下に文脈・前提知識と文章を記載するのでそれ読んで、トピックを抽出してください（既存のトピックと新規のトピックは区別して扱う）
# 既存のトピック
```
{previous_topics}
```

# 文脈・前提知識
```
{knowledge}
```

# 本文
```
{source_text}
```

結果は以下のjson形式で出力でそのトピック名を抽出してください。
{{"new_topics": ["新規トピック名1", "新規トピック名2", ...], "update_topics": ["既存トピック名1", "既存トピック名2", ...]}}"
update_topicsの既存トピックは、本文に含まれるもののみを記載してください。記載のないトピックはupdate_topicsに含めないでください。情報が増えたトピックが知りたいからです。
トピック名は、ファイル名に使える程度の簡潔な日本語の名前にしてください。
"""

prompt_update_topic = """以下に文脈・前提知識と文章を記載するのでそれ読んで、トピックを要約してください。
# トピック
```
{topic}
```
# 文脈・前提知識
```
{knowledge}
```
# 本文
```
{source_text}
```
"""

class SubState(TypedDict):
    source_text: str
    previous_topicwise_knowledge: dict[str, str]
    previous_global_knowledge: str

    i_new_topic: int
    new_topics: list[str]
    i_update_topic: int
    update_topics: list[str]
    keep_topics: list[str]

    topicwise_knowledge: Annotated[dict[str, str], update_dict]
    global_knowledge: str
    topicwise_summary: dict[str, str]


def build_analyze_chunck_graph(llm_fn: Callable[[str], str], llm_fn_json_mode: Callable[[str], Any]) -> StateGraph:
    graph = StateGraph(SubState)
    graph.add_node("update_topics", lambda state: update_topics(state=state, llm_fn=llm_fn, prompt=promt_update_topics))
    graph.add_node("iterate_tpoics", lambda state: {"i_new_topic": state.get("i_new_topic", -1) + 1})
    graph.add_node("update_topic", lambda state: update_topic(state=state, llm_fn=llm_fn, prompt=promt_update_topic))
    graph.add_node(
        "update_knowledge", lambda state: update_knowledge(state=state, llm_fn=llm_fn, prompt=promt_update_knowledge)
    )

    graph.add_node("new_topic", lambda state: new_topic(state=state, llm_fn=llm_fn, prompt=promt_new_topic))
    graph.add_node("new_knowledge", lambda state: new_knowledge(state=state, llm_fn=llm_fn, prompt=promt_new_knowledge))

    graph.add_node("global_summary", lambda state: global_summary(state=state, llm_fn=llm_fn, prompt=promt_new_summary))
    graph.add_node(
        "global_knowledge", lambda state: global_knowledge(state=state, llm_fn=llm_fn, prompt=promt_new_knowledge)
    )
    graph.add_node("restore_keep_topics", restore_keep_topics)

    graph.add_edge(START, "update_topics")
    graph.add_edge("update_topics", "iterate_new_topics")
    graph.add_conditional_edges(
        "iterate_new_topics", did_iterate_new_topics_finish, {False: "new_topic", True: "iterate_update_topics"}
    )
    graph.add_edge("new_topic", "new_knowledge")
    graph.add_edge("new_knowledge", "iterate_new_topics")
    graph.add_conditional_edges(
        "iterate_update_topics", did_iterate_update_topics_finish, {False: "update_topic", True: "global_summary"}
    )
    graph.add_edge("global_summary", "global_knowledge")
    graph.add_edge("global_knowledge", "restore_keep_topics")
    graph.add_edge("restore_keep_topics", END)

    return graph


def update_topics(state: SubState, llm_fn: Callable[[str], Any], prompt: str) -> dict[str, str]:
    previous_topics = set(state["previous_topicwise_knowledge"].keys())
    previous_topics_str = "".join([f"- {topic}\n" for topic in previous_topics])
    response = llm_fn(
        prompt.format(
            source_text=state["source_text"],
            knowledge=state["previous_global_knowledge"],
            previous_topics=previous_topics_str,
        )
    )
    new_topics = response["new_topics"]
    update_topics = response["update_topics"]
    keep_topics = [topic for topic in previous_topics if topic not in new_topics and topic not in update_topics]

    return {
        "new_topics": new_topics,
        "update_topics": update_topics,
        "keep_topics": keep_topics,
    }


def update_topic(state: SubState, llm_fn: Callable[[str], Any], prompt: str) -> dict[str, str]:
    topic = state["update_topics"][state["i_update_topic"]]
    knowledge = state["topicwise_knowledge"][topic]
    response = llm_fn(
        prompt.format(
            source_text=state["source_text"],
            topic=topic,
            knowledge=knowledge,
        )
    )

    return {
        "topicwise_summary": {topic: response["summary"]},
        "topicwise_knowledge": {topic: response["knowledge"]},
    }
