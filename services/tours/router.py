import json
from typing import Dict, Any, List, Tuple

import networkx as nx
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Load graph
with open("data/metro_graph.json") as f:
    metro_data = json.load(f)

G = nx.Graph()
for edge in metro_data["edges"]:
    G.add_edge(
        edge["from"],
        edge["to"],
        time=edge["time"],
        line=edge.get("line", "M?"),
    )

# Load recommendations
with open("data/recommendations.json") as f:
    RECOMMENDATIONS: Dict[str, List[Dict[str, Any]]] = json.load(f)


@router.get("/tour/best-museum-trip")
def best_museum_trip(origin: str):
    """
    Find the best (fastest) museum trip starting from `origin`:
    - checks all stations that have museums
    - computes route time + walking time
    - returns the fastest option with route details
    """
    origin = origin.upper()

    if origin not in G.nodes:
        raise HTTPException(status_code=400, detail="Unknown origin station")

    best: Tuple[float, Dict[str, Any]] | None = None

    # Loop over all stations that have recommendations
    for station, places in RECOMMENDATIONS.items():
        station = station.upper()

        # Filter only museums
        museums = [p for p in places if p.get("type") == "museum"]
        if not museums:
            continue

        # Try computing a route from origin -> this station
        try:
            route_time = nx.shortest_path_length(G, origin, station, weight="time")
            route_path = nx.shortest_path(G, origin, station, weight="time")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue  # can't reach this station

        for museum in museums:
            walk_minutes = museum.get("walk_minutes", 0)
            total_time = route_time + walk_minutes

            candidate = {
                "origin": origin,
                "museum_station": station,
                "museum": museum,
                "route_path": route_path,
                "route_time": route_time,
                "walk_minutes": walk_minutes,
                "total_time": total_time,
            }

            if best is None or total_time < best[0]:
                best = (total_time, candidate)

    if best is None:
        raise HTTPException(status_code=404, detail="No reachable museums found")

    # return only the candidate dict
    return best[1]
