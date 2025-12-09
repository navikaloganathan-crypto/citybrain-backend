import json
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Load recommendations from JSON
with open("data/recommendations.json") as f:
    RECOMMENDATIONS: Dict[str, List[Dict[str, Any]]] = json.load(f)


@router.get("/recommendations")
def get_recommendations(
    station: str,
    type: Optional[str] = None,
    min_rating: float = 0.0,
):
    """
    Return recommendations near a given station.

    Query params:
    - station: station code, e.g. "A"
    - type (optional): filter by type (e.g. "museum", "park")
    - min_rating (optional): minimum rating filter
    """
    station = station.upper()

    if station not in RECOMMENDATIONS:
        raise HTTPException(status_code=404, detail="No recommendations for this station")

    places = RECOMMENDATIONS[station]

    # apply filters
    filtered = []
    for place in places:
        if type is not None and place.get("type") != type:
            continue
        if place.get("rating", 0) < min_rating:
            continue
        filtered.append(place)

    return {
        "station": station,
        "count": len(filtered),
        "results": filtered,
    }


@router.get("/recommendations/all")
def get_all_recommendations():
    """
    Return all recommendations for all stations.
    """
    return RECOMMENDATIONS


@router.get("/tour/museums")
def get_museum_tour(
    station: str,
    max_places: int = 3,
    min_rating: float = 4.0,
):
    """
    Simple museum tour:
    - Input: station code
    - Output: up to `max_places` museums near that station,
      sorted by rating (highest first).
    """
    station = station.upper()

    if station not in RECOMMENDATIONS:
        raise HTTPException(status_code=404, detail="No recommendations for this station")

    places = RECOMMENDATIONS[station]

    # filter only museums with rating above threshold
    museums = [
        p for p in places
        if p.get("type") == "museum" and p.get("rating", 0) >= min_rating
    ]

    # sort by rating descending
    museums.sort(key=lambda p: p.get("rating", 0), reverse=True)

    # limit the number of places
    tour = museums[:max_places]

    return {
        "station": station,
        "count": len(tour),
        "tour": tour,
    }
