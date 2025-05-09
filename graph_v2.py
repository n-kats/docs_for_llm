from typing import Annotated, Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph
from markitdown import MarkItDown

from graph_v2_per_chunk import SubState
from model_utils import add_object, add_text
from source_utils import split_text


class State(TypedDict):
    in_query: str
    in_target: str

    source_title: str
    source_chunks: list[str]

    i_chunk: int
    analyze_history: Annotated[list[dict[str, SubState]], add_object]

    i_topic: int
    topics: list[str]
    topicwise_summaries: list[str]
    topicwise_knowledges: list[str]

    total_summary: str
    total_knowledge: str
    total_knowledge: str


def build_graph(
    llm_fn: Callable[[str], str],
    llm_fn_json_mode: Callable[[str], Any],
    subgraph_chunk: StateGraph,
    subgraph_topic: StateGraph,
) -> StateGraph:
    graph = StateGraph(State)
    graph.add_node("get_source_chunks", get_source_chunks)
    graph.add_node("iterate_source_chunks", iterate_source_chunks)
    graph.add_node("analyze_chunk", lambda state: analyze_chunk(
        state=state, subgraph=subgraph_chunk))
    graph.add_node("iterate_topics", iterate_topics)
    graph.add_node("analyze_topic", lambda state: analyze_topic(
        state=state, subgraph=subgraph_topic))
    graph.add_node(
        "get_total_summary", lambda state: get_total_summary(
            state=state, llm_fn=llm_fn, prompt=promt_get_total_summary)
    )
    graph.add_node("get_knowledge", lambda state: get_knowledge(
        state=state, llm_fn=llm_fn, prompt=promt_get_knowledge))
    graph.add_node("get_answer", lambda state: get_answer(
        state=state, llm_fn=llm_fn, prompt=promt_get_answer))


def get_source_chunks(state: State) -> dict[str, str | None]:
    md = MarkItDown()
    converted = md.convert(state["in_target"])
    chunks = split_text(
        converted.text_markdown,
        max_length=5000,
        max_overwrap=1000,
        splitters=["\n", "。", "、", "．", "，"],
        splitter_limit=500,
    )
    return {
        "source_title": converted.title,
        "source_chunks": chunks,
    }


def iterate_source_chunks(state: State) -> dict[str, Any]:
    i_chunk = state.get("i_chunk", -1) + 1
    return {"i_chunk": i_chunk}


def iterate_topics(state: State) -> dict[str, Any]:
    i_topic = state.get("i_topic", -1) + 1
    return {"i_topic": i_topic}


def analyze_chunk(state: State, subgraph: StateGraph) -> dict[str, Any]:
    i_chunk = state["i_chunk"]
    chunk = state["source_chunks"][i_chunk]
    result = subgraph.invoke(
        {"query": state["in_query"], "chunk": chunk,
            "history": state["analyze_history"]},  # TODO
        {"recursion_limit": 1000},
    )
    return {
        "analyze_history": add_object(state["analyze_history"], result),
        "topicwise_summaries": add_text(state["topicwise_summaries"], result["summary"]),
        "topicwise_knowledges": add_text(state["topicwise_knowledges"], result["knowledge"]),
    }


def analyze_topic(
    state: State,
    subgraph: StateGraph,
) -> dict[str, Any]:
    i_topic = state["i_topic"]
    topic = state["topics"][i_topic]
    result = subgraph.invoke(
        {"query": state["in_query"], "topic": topic,
            "history": state["analyze_history"]},
        {"recursion_limit": 1000},
    )  # TODO
    return {
        "analyze_history": add_object(state["analyze_history"], result),
        "topicwise_summaries": add_text(state["topicwise_summaries"], result["summary"]),
        "topicwise_knowledges": add_text(state["topicwise_knowledges"], result["knowledge"]),
    }


def get_total_summary(state: State, llm_fn: Callable[[str], Any], prompt: str) -> dict[str, str]:
    summaries = state["topicwise_summaries"]
    total_summary = llm_fn(prompt.format(summaries="\n".join(summaries)))
    return {"total_summary": total_summary}


def get_total_knowledge(state: State, llm_fn: Callable[[str], Any], prompt: str) -> dict[str, str]:
    knowledge = state["topicwise_knowledges"]
    total_knowledge = llm_fn(prompt.format(knowledge="\n".join(knowledge)))
    return {"total_knowledge": total_knowledge}


def get_answer(state: State, llm_fn: Callable[[str], Any], prompt: str) -> dict[str, str]:
    total_summary = state["total_summary"]
    total_knowledge = state["total_knowledge"]
    answer = llm_fn(prompt.format(
        summary=total_summary, knowledge=total_knowledge))
    return {"answer": answer}
