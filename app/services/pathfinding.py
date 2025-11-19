import heapq
import math
from typing import Dict, List, Optional, Tuple

import networkx as nx

from app.core.config import settings


class Node:
    def __init__(self, name: str, x: float, y: float):
        self.name = name
        self.x = x
        self.y = y

    def distance_to(self, other: "Node") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)/100

    def __repr__(self):
        return f"Node({self.name}, {self.x}, {self.y})"


class PathfindingService:
    """
    PathfindingService dùng networkx để lưu graph và chạy A*.
    Giữ API tương thích: find_nearest_node(...) và get_path_with_coordinates(...)
    """

    def __init__(self, db_session):
        self.db_session = db_session
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self._build_graph()

    def _build_graph(self):
        """Load nodes/edges từ DB và build networkx graph"""
        from app.db.models import EdgeModel, NodeModel

        map_h = getattr(settings, "MAP_HEIGHT", None)
        origin = getattr(settings, "MAP_ORIGIN", "top-left")

        # Load nodes
        nodes_data = self.db_session.query(NodeModel).all()
        for node in nodes_data:
            x = node.x
            y = node.y
            if map_h and origin == "bottom-left":
                y = map_h - y
            self.nodes[node.name] = Node(node.name, x, y)
            # add node with position attributes
            self.graph.add_node(node.name, x=x, y=y)

        # Load edges (directed)
        edges_data = self.db_session.query(EdgeModel).all()
        for edge in edges_data:
            # ensure nodes exist (defensive)
            if edge.node_from in self.graph.nodes and edge.node_to in self.graph.nodes:
                self.graph.add_edge(edge.node_from, edge.node_to, weight=edge.weight)

    def find_nearest_node(self, x: float, y: float, max_distance: float = 100) -> Optional[str]:
        """Tìm node gần nhất với pixel (x, y). Trả về tên node hoặc None."""
        if not self.nodes:
            return None

        target = Node("tmp", x, y)
        nearest = None
        min_dist = max_distance
        for name, node in self.nodes.items():
            d = node.distance_to(target)
            if d < min_dist:
                min_dist = d
                nearest = name
        return nearest

    def _heuristic(self, u: str, v: str) -> float:
        """Heuristic Euclidean dùng cho networkx A*"""
        if u not in self.nodes or v not in self.nodes:
            return 0.0
        return self.nodes[u].distance_to(self.nodes[v])

    def a_star(self, start: str, goal: str) -> Tuple[Optional[List[str]], float]:
        """
        Chạy A* bằng networkx, trả về (path_list, total_cost) hoặc (None, inf)
        """
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            return None, float("inf")

        try:
            path = nx.astar_path(self.graph, start, goal, heuristic=self._heuristic, weight="weight")
            cost = nx.astar_path_length(self.graph, start, goal, heuristic=self._heuristic, weight="weight")
            return path, float(cost)
        except nx.NetworkXNoPath:
            return None, float("inf")
        except Exception:
            # Bất kỳ lỗi nào khác coi như không tìm thấy đường
            return None, float("inf")

    def get_path_with_coordinates(self, start: str, goal: str) -> Optional[Dict]:
        """
        Trả về dict giống với bản cũ:
        {
            'path': [...],
            'coordinates': [[x1,y1], ...],
            'total_distance': float
        }
        """
        path, distance = self.a_star(start, goal)
        if path is None:
            return None

        coordinates = [[self.nodes[n].x, self.nodes[n].y] for n in path]
        return {"path": path, "coordinates": coordinates, "total_distance": distance}