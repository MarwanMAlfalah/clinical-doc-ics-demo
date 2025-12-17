from graphviz import Digraph


def build_state_diagram() -> Digraph:
    dot = Digraph("ICS_State_Machine")
    dot.attr(rankdir="LR", bgcolor="transparent")

    # Node styles
    dot.attr("node", shape="box", style="rounded", fontsize="12")

    dot.node("S0", "S0\nStart")
    dot.node("S_ASR", "S_ASR\nASR Agent\n(audio → text)")
    dot.node("S_LLM", "S_LLM\nLLM Agent\n(text → SOAP)")
    dot.node("S_STD", "S_STD\nStandardizer\n(ontology mapping)")
    dot.node("S_SUP", "S_SUP\nSupervisor\n(safety & quality)")
    dot.node("S_final", "S_final\nFinal Output")

    # Decision nodes
    dot.attr("node", shape="diamond", style="rounded", fontsize="12")
    dot.node("D1", "Decision")

    # Edges
    dot.attr("node", shape="box", style="rounded", fontsize="12")
    dot.edge("S0", "S_ASR", label="u_asr")
    dot.edge("S_ASR", "S_LLM", label="u_llm")
    dot.edge("S_LLM", "S_STD", label="u_std")
    dot.edge("S_STD", "S_SUP", label="u_sup")
    dot.edge("S_SUP", "D1", label="evaluate")

    dot.edge("D1", "S_final", label="APPROVE")
    dot.edge("D1", "S_LLM", label="REGENERATE (retry)")
    dot.edge("D1", "S_final", label="HUMAN_REVIEW")

    return dot
