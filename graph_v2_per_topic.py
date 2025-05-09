from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph


class TopicAnalzeState(TypedDict):
    topic: str
    topic_history: list[str]
    knowledge_history: list[str]
    topic_summary: str
    knowledge_summary: str


def build_analyze_topic_graph(llm_fn: Callable[[str], str], llm_fn_json_mode: Callable[[str], Any]) -> StateGraph:
    graph = StateGraph(TopicAnalzeState)
    graph.add_node("summrize_topic", lambda state: {"topic_summary": state["topic_history"][-1]})
    graph.add_node("summarize_knowledge", lambda state: {"knowledge_summary": state["knowledge_history"][-1]})
    graph.add_edge(START, "summrize_topic")
    graph.add_edge("summrize_topic", "summarize_knowledge")
    graph.add_edge("summarize_knowledge", END)
    return graph
