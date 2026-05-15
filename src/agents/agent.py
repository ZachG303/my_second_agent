from typing import Any, Dict

from langgraph.graph import StateGraph, START

from src.scraper import scrape_earnings_reports
from src.ml_pipeline import train_and_save_model


def scrape_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    reports = scrape_earnings_reports(limit=5)
    return {"reports": reports, "status": "scraped"}


def preprocess_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    reports = state.get("reports", [])
    processed = [
        {
            "ticker": item["ticker"],
            "metrics": item["data"],
        }
        for item in reports
    ]
    return {"processed": processed, "status": "processed"}


def train_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    train_and_save_model(period="Q1", metric="eps")
    return {"status": "trained", "model": "trained"}


def build_agent_graph() -> Any:
    graph = StateGraph(dict)
    graph.add_node("scrape", scrape_agent)
    graph.add_node("preprocess", preprocess_agent)
    graph.add_node("train", train_agent)
    graph.add_edge("scrape", "preprocess")
    graph.add_edge("preprocess", "train")
    graph.set_entry_point("scrape")
    graph.set_finish_point("train")
    return graph.compile()

agent_graph = build_agent_graph()
