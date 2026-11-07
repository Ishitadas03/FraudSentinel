"""
Module II Graph Search Algorithms Package for FraudSentinel.

Exposes:
1. Breadth-First Search (breadth_first_search)
2. Depth-First Search (depth_first_search)
3. Greedy Best-First Search (best_first_search)
4. A* Search (a_star_search)
5. Graph classes: FraudInvestigationGraph, GraphNode, GraphEdge, SearchResult
6. Heuristics: euclidean_heuristic, manhattan_heuristic, risk_guided_heuristic, zero_heuristic
"""

from backend.ml.search.astar import a_star_search
from backend.ml.search.best_first import best_first_search
from backend.ml.search.bfs import breadth_first_search
from backend.ml.search.dfs import depth_first_search
from backend.ml.search.graph import (
    FraudInvestigationGraph,
    GraphEdge,
    GraphNode,
    SearchResult,
)
from backend.ml.search.heuristics import (
    HeuristicFn,
    euclidean_heuristic,
    manhattan_heuristic,
    risk_guided_heuristic,
    verify_admissibility_and_consistency,
    zero_heuristic,
)

try:
    from backend.ml.search.benchmark import (
        generate_benchmark_visualization,
        run_comprehensive_benchmark,
        run_single_comparison,
    )
except ImportError:
    try:
        from ml.search.benchmark import (
            generate_benchmark_visualization,
            run_comprehensive_benchmark,
            run_single_comparison,
        )
    except ImportError:
        generate_benchmark_visualization = None
        run_comprehensive_benchmark = None
        run_single_comparison = None

__all__ = [
    "breadth_first_search",
    "depth_first_search",
    "best_first_search",
    "a_star_search",
    "FraudInvestigationGraph",
    "GraphNode",
    "GraphEdge",
    "SearchResult",
    "HeuristicFn",
    "euclidean_heuristic",
    "manhattan_heuristic",
    "risk_guided_heuristic",
    "zero_heuristic",
    "verify_admissibility_and_consistency",
    "run_comprehensive_benchmark",
    "run_single_comparison",
    "generate_benchmark_visualization",
]
