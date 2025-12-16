# CityBrain Backend

A FastAPI backend for the CityBrain project.  
It provides metro routing (shortest path by time), station listing, recommendations, and simple museum tour endpoints.

## Requirements
- Python 3.12+
- Virtual environment (venv)

## Setup (first time)
```bash
cd "/Users/navikaloganathan/Documents/Isep/Smart City/citybrain-backend"
source venv/bin/activate
pip install -r requirements.txt  # if you have it
# OR (if you don't have requirements.txt yet)
pip install fastapi "uvicorn[standard]" networkx
