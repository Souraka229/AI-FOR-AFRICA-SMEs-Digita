"""Graphe durable Afrosite : raisonnement, gates et approbation humaine."""

from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from runtime.tools import AgentTools


class RunState(TypedDict, total=False):
    prompt: str
    intent: dict
    blueprint: dict
    gate1: dict
    approved: bool
    artifact: dict
    security: dict
    qa: dict
    preview: dict
    release: dict
    stage: str


def build_graph(tools: AgentTools, checkpointer=None):
    builder = StateGraph(RunState)

    def intent_node(state: RunState) -> RunState:
        return {
            "intent": tools.classify_intent(state["prompt"]),
            "stage": "intent",
        }

    def architect_node(state: RunState) -> RunState:
        return {
            "blueprint": tools.build_blueprint(state["intent"]),
            "stage": "architect",
        }

    def gate1_node(state: RunState) -> RunState:
        return {
            "gate1": tools.validate_blueprint(state["blueprint"]),
            "stage": "gate1",
        }

    def approval_node(state: RunState) -> RunState:
        if not state["gate1"].get("passed"):
            return {"approved": False, "stage": "blocked"}
        approved = bool(
            interrupt(
                {
                    "type": "blueprint_approval",
                    "blueprint": state["blueprint"],
                    "gate": state["gate1"],
                }
            )
        )
        return {
            "approved": approved,
            "stage": "approved" if approved else "rejected",
        }

    def code_node(state: RunState) -> RunState:
        return {
            "artifact": tools.generate_overlay(state["blueprint"]),
            "stage": "code",
        }

    def security_node(state: RunState) -> RunState:
        return {
            "security": tools.scan_generated(state["artifact"]),
            "stage": "security",
        }

    def qa_node(state: RunState) -> RunState:
        return {
            "qa": tools.run_checks(state["artifact"]),
            "stage": "qa",
        }

    def preview_node(state: RunState) -> RunState:
        return {
            "preview": tools.create_preview(state["artifact"]),
            "stage": "preview",
        }

    def deployment_node(state: RunState) -> RunState:
        return {
            "release": tools.prepare_release(
                {
                    "artifact": state["artifact"],
                    "preview": state["preview"],
                    "blueprint": state["blueprint"],
                }
            ),
            "stage": "deployment",
        }

    def after_gate(state: RunState) -> Literal["approval", "__end__"]:
        return "approval" if state["gate1"].get("passed") else END

    def after_approval(state: RunState) -> Literal["code", "__end__"]:
        return "code" if state.get("approved") else END

    def after_security(state: RunState) -> Literal["qa", "__end__"]:
        return "qa" if state["security"].get("passed") else END

    def after_qa(state: RunState) -> Literal["preview", "__end__"]:
        return "preview" if state["qa"].get("passed") else END

    builder.add_node("intent", intent_node)
    builder.add_node("architect", architect_node)
    builder.add_node("gate1", gate1_node)
    builder.add_node("approval", approval_node)
    builder.add_node("code", code_node)
    builder.add_node("security", security_node)
    builder.add_node("qa", qa_node)
    builder.add_node("preview", preview_node)
    builder.add_node("deployment", deployment_node)

    builder.add_edge(START, "intent")
    builder.add_edge("intent", "architect")
    builder.add_edge("architect", "gate1")
    builder.add_conditional_edges("gate1", after_gate)
    builder.add_conditional_edges("approval", after_approval)
    builder.add_edge("code", "security")
    builder.add_conditional_edges("security", after_security)
    builder.add_conditional_edges("qa", after_qa)
    builder.add_edge("preview", "deployment")
    builder.add_edge("deployment", END)
    return builder.compile(checkpointer=checkpointer or MemorySaver())
