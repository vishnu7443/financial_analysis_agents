import asyncio
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from backend.models.report import ReportState
from backend.agents.market_agent import run_market_agent
from backend.agents.sentiment_agent import run_sentiment_agent
from backend.agents.report_agent import stream_report_agent

logger = logging.getLogger(__name__)

# Define LangGraph State
class GraphState(ReportState):
    pass

async def market_node(state: GraphState, emitter_callback=None) -> Dict[str, Any]:
    """LangGraph node for Market Analysis"""
    updated_state = await run_market_agent(state, emitter_callback)
    return {"market_data": updated_state.market_data, "logs": updated_state.logs}

async def sentiment_node(state: GraphState, emitter_callback=None) -> Dict[str, Any]:
    """LangGraph node for Sentiment Analysis"""
    updated_state = await run_sentiment_agent(state, emitter_callback)
    return {"sentiment_data": updated_state.sentiment_data, "logs": updated_state.logs}

async def build_and_run_analysis_graph(
    job_id: str,
    tickers: List[str],
    weights: Dict[str, float],
    emitter_callback=None
) -> ReportState:
    """
    Constructs and executes the LangGraph state graph.
    Runs Market and Sentiment agents in parallel (using asyncio.gather),
    and then feeds the merged state into the Report Agent.
    """
    # 1. Initialize State
    initial_state = GraphState(
        job_id=job_id,
        tickers=tickers,
        weights=weights,
        market_data={},
        sentiment_data={},
        risk_score=0.0,
        report_markdown="",
        logs=[]
    )

    logger.info(f"Orchestrator: Building LangGraph workflow for Job {job_id}...")

    # Define the StateGraph
    workflow = StateGraph(GraphState)

    # In our orchestrator, we define the parallel nodes
    # To implement high-performance parallel execution in LangGraph, we can run nodes concurrently.
    # We will trigger the nodes using asyncio.gather to guarantee ultra-fast sub-30s execution.
    
    async def parallel_execution_node(state: GraphState) -> Dict[str, Any]:
        """Runs market_node and sentiment_node in parallel"""
        # Execute concurrent agents
        market_task = market_node(state, emitter_callback)
        sentiment_task = sentiment_node(state, emitter_callback)
        
        market_res, sentiment_res = await asyncio.gather(market_task, sentiment_task)
        
        # Merge outputs into a single update dict
        merged_logs = state.logs + market_res["logs"] + sentiment_res["logs"]
        # Sort logs by timestamp to keep the terminal timeline sequential
        merged_logs.sort(key=lambda x: x.get("timestamp", ""))
        
        return {
            "market_data": market_res["market_data"],
            "sentiment_data": sentiment_res["sentiment_data"],
            "logs": merged_logs
        }

    async def report_execution_node(state: GraphState) -> Dict[str, Any]:
        """Runs the streaming report agent node"""
        accumulated_report = ""
        # We invoke the async generator and gather all report output tokens
        async for event in stream_report_agent(state, emitter_callback):
            if event["type"] == "token":
                token = event["content"]
                accumulated_report += token
                if emitter_callback:
                    emitter_callback({"type": "token", "content": token})
            elif event["type"] == "status" and emitter_callback:
                emitter_callback({"type": "status", "content": event["content"]})
                
        return {
            "report_markdown": accumulated_report,
            "risk_score": state.risk_score,
            "logs": state.logs
        }

    # Register Nodes
    workflow.add_node("parallel_analysis", parallel_execution_node)
    workflow.add_node("report_generation", report_execution_node)

    # Set Entry Point and Edges
    workflow.set_entry_point("parallel_analysis")
    workflow.add_edge("parallel_analysis", "report_generation")
    workflow.add_edge("report_generation", END)

    # Compile Graph
    app = workflow.compile()
    
    logger.info(f"Orchestrator: Executing Graph for Job {job_id}...")
    final_output = await app.ainvoke(initial_state)
    
    logger.info(f"Orchestrator: Graph execution completed for Job {job_id}.")
    return ReportState(**final_output)

if __name__ == "__main__":
    # Test script to execute graph locally with mock data
    logging.basicConfig(level=logging.INFO)
    
    async def main_test():
        test_job_id = "test-job-uuid-123"
        test_tickers = ["AAPL", "MSFT", "TSLA"]
        test_weights = {"AAPL": 0.4, "MSFT": 0.4, "TSLA": 0.2}
        
        def dummy_emitter(event):
            if "agent" in event:
                print(f"-> [SSE Log] {event['agent']} | {event['phase']} | {event['message']}")
            elif "type" in event and event["type"] == "token":
                print(event["content"], end="", flush=True)

        print("=== STARTING LANGGRAPH ORCHESTRATOR LOCAL TEST ===")
        res = await build_and_run_analysis_graph(test_job_id, test_tickers, test_weights, dummy_emitter)
        print("\n=== GRAPH RUN COMPLETE ===")
        print(f"Calculated Risk Score: {res.risk_score}/10")
        print(f"Report Length: {len(res.report_markdown)} characters")
        
    asyncio.run(main_test())
