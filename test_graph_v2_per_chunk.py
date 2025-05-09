from graph_v2_per_chunk import build_analyze_chunck_graph

def test_build_analyze_chunk_graph():
    def dummy_llm_fn(prompt: str) -> str:
        return "dummy response"

    def dummy_llm_fn_json_mode(prompt: str) -> dict[str, str]:
        return {"new_topics": ["topic1", "topic2"], "update_topics": ["topic3"]}

    graph = build_analyze_chunck_graph(dummy_llm_fn, dummy_llm_fn_json_mode)
    assert graph is not None
    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0
