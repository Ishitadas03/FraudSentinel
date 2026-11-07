"""
Benchmark and Evaluation Runner for Search Algorithms in FraudSentinel.

Compares Breadth-First Search (BFS), Depth-First Search (DFS), Greedy Best-First Search,
and A* Search across representative banking fraud investigation scenarios.
Generates comprehensive performance metric tables and a visual comparison chart.
"""

from dataclasses import asdict
import os
from typing import Any, Dict, List, Optional, Tuple
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from backend.ml.search.astar import a_star_search
from backend.ml.search.best_first import best_first_search
from backend.ml.search.bfs import breadth_first_search
from backend.ml.search.dfs import depth_first_search
from backend.ml.search.graph import FraudInvestigationGraph, SearchResult
from backend.ml.search.heuristics import (
    euclidean_heuristic,
    risk_guided_heuristic,
    verify_admissibility_and_consistency,
)


def run_single_comparison(
    graph: FraudInvestigationGraph,
    start: str,
    goal: str,
    scenario_name: str,
) -> List[SearchResult]:
    """Execute all 4 search algorithms on a single investigation scenario."""
    bfs_res = breadth_first_search(graph, start, goal)
    dfs_res = depth_first_search(graph, start, goal)
    best_res = best_first_search(graph, start, goal, heuristic=risk_guided_heuristic)
    astar_res = a_star_search(graph, start, goal, heuristic=euclidean_heuristic)

    return [bfs_res, dfs_res, best_res, astar_res]


def run_comprehensive_benchmark(output_image_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run full comparative benchmark across multiple fraud network scenarios.
    Returns structured results dictionary and saves visualization chart.
    """
    graph = FraudInvestigationGraph.create_benchmark_fraud_network()

    scenarios = [
        ("Primary Syndicate Ring (VIC_1 -> HUB_ALPHA)", "VIC_1", "HUB_ALPHA"),
        ("Offshore Mule Network (VIC_3 -> HUB_BETA)", "VIC_3", "HUB_BETA"),
        ("Cross-Conduit Tracing (VIC_2 -> HUB_ALPHA)", "VIC_2", "HUB_ALPHA"),
    ]

    all_results: Dict[str, List[SearchResult]] = {}
    summary_table: List[Dict[str, Any]] = []

    for name, start, goal in scenarios:
        results = run_single_comparison(graph, start, goal, name)
        all_results[name] = results

        for res in results:
            summary_table.append({
                "scenario": name,
                "algorithm": res.algorithm_name,
                "found": res.found,
                "hops": len(res.path) - 1 if res.found else 0,
                "path_cost": round(res.path_cost, 2),
                "nodes_explored": res.nodes_explored,
                "execution_time_ms": round(res.execution_time_ms, 4),
                "memory_bytes": res.memory_usage_bytes,
                "path_str": " -> ".join(res.path) if res.found else "NONE",
            })

    # Generate visualization for the Primary Syndicate Ring scenario
    primary_results = all_results[scenarios[0][0]]
    if output_image_path:
        generate_benchmark_visualization(primary_results, output_image_path)

    return {
        "scenarios": scenarios,
        "results": all_results,
        "summary_table": summary_table,
    }


def generate_benchmark_visualization(results: List[SearchResult], output_path: str):
    """
    Generate professional multi-panel comparison chart:
    1. Nodes Explored (Search Efficiency)
    2. Path Cost (Solution Optimality)
    3. Execution Latency in ms
    """
    if plt is None:
        return
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    algos = [r.algorithm_name.replace(" (BFS)", "").replace(" (DFS)", "") for r in results]
    nodes = [r.nodes_explored for r in results]
    costs = [r.path_cost for r in results]
    times = [r.execution_time_ms for r in results]

    palette = ["#3498db", "#e74c3c", "#f39c12", "#2ecc71"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.suptitle(
        "Module II Graph Search Benchmark: Fraud Investigation Traversal",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    # 1. Nodes Explored
    bars1 = axes[0].bar(algos, nodes, color=palette, edgecolor="black", alpha=0.85)
    axes[0].set_title("Search Effort (Nodes Explored)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Nodes Explored")
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars1:
        yval = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2.0, yval + 0.3, int(yval), ha='center', va='bottom', fontweight="bold")

    # 2. Path Cost
    bars2 = axes[1].bar(algos, costs, color=palette, edgecolor="black", alpha=0.85)
    axes[1].set_title("Path Cost (Lower is Optimal)", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Cumulative Edge Cost")
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars2:
        yval = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{yval:.1f}", ha='center', va='bottom', fontweight="bold")

    # 3. Execution Latency
    bars3 = axes[2].bar(algos, times, color=palette, edgecolor="black", alpha=0.85)
    axes[2].set_title("Execution Latency (ms)", fontsize=11, fontweight="bold")
    axes[2].set_ylabel("Time (ms)")
    axes[2].grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars3:
        yval = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, f"{yval:.3f}", ha='center', va='bottom', fontweight="bold")

    for ax in axes:
        ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def print_markdown_benchmark():
    """CLI helper to run and print benchmark tables in markdown."""
    img_path = os.path.join("docs", "reports", "figures", "search_benchmark.png")
    benchmark_data = run_comprehensive_benchmark(output_image_path=img_path)

    print("\n### Search Algorithms Benchmark Results\n")
    print("| Scenario | Algorithm | Found | Hops | Path Cost | Nodes Explored | Latency (ms) | Peak Memory (Bytes) |")
    print("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |")

    for row in benchmark_data["summary_table"]:
        print(
            f"| {row['scenario'][:30]}... | {row['algorithm']} | {row['found']} | "
            f"{row['hops']} | **{row['path_cost']}** | {row['nodes_explored']} | "
            f"{row['execution_time_ms']:.3f} | {row['memory_bytes']} |"
        )

    print(f"\nBenchmark visualization saved to: {img_path}")


if __name__ == "__main__":
    print_markdown_benchmark()
