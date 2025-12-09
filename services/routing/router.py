import json
from itertools import islice

import networkx as nx
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Load graph
with open("data/metro_graph.json") as f:
    data = json.load(f)

G = nx.Graph()

# Add edges
for edge in data["edges"]:
    G.add_edge(
        edge["from"],
        edge["to"],
        time=edge["time"],
        line=edge.get("line", "M?"),  # default if missing
    )



@router.get("/route")
def get_route(origin: str, destination: str):
    """
    Return the fastest route (by time) between two stations.
    """
    try:
        path = nx.shortest_path(G, origin, destination, weight="time")
        total_time = nx.shortest_path_length(G, origin, destination, weight="time")
        return {"best_route": path, "time": total_time}
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=400, detail="No path between these stations")
    except nx.NodeNotFound:
        raise HTTPException(status_code=400, detail="Unknown station name")


@router.get("/stations")
def get_stations():
    """
    Return the list of all stations in the graph.
    """
    return {"stations": list(G.nodes())}


@router.get("/route/details")
def get_route_details(origin: str, destination: str):
    """
    Return a detailed route:
    - total time
    - number of stops
    - number of transfers
    - segments grouped by line (M1, M2, etc.)
    """
    try:
        path = nx.shortest_path(G, origin, destination, weight="time")
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=400, detail="No path between these stations")
    except nx.NodeNotFound:
        raise HTTPException(status_code=400, detail="Unknown station name")

    # compute total time
    total_time = nx.shortest_path_length(G, origin, destination, weight="time")

    # number of stops (nodes visited minus 1)
    total_stops = max(0, len(path) - 1)

    # build segments: consecutive edges with the same line
    segments = []
    if len(path) >= 2:
        current_line = None
        current_start = path[0]
        current_time = 0
        current_stops = 0

        for u, v in zip(path, path[1:]):
            edge_data = G.get_edge_data(u, v) or {}
            line = edge_data.get("line", "M?")
            time = edge_data.get("time", 0)

            if current_line is None:
                # first edge
                current_line = line

            if line != current_line:
                # line changed → close previous segment
                segments.append(
                    {
                        "from": current_start,
                        "to": u,
                        "line": current_line,
                        "time": current_time,
                        "stops": current_stops,
                    }
                )
                # start new segment
                current_line = line
                current_start = u
                current_time = 0
                current_stops = 0

            # accumulate edge into current segment
            current_time += time
            current_stops += 1
            last_station = v

        # close last segment
        segments.append(
            {
                "from": current_start,
                "to": last_station,
                "line": current_line,
                "time": current_time,
                "stops": current_stops,
            }
        )

    # transfers = segments - 1 (each segment after the first is a transfer)
    transfers = max(0, len(segments) - 1)

    return {
        "origin": origin,
        "destination": destination,
        "path": path,
        "total_time": total_time,
        "total_stops": total_stops,
        "transfers": transfers,
        "segments": segments,
    }

