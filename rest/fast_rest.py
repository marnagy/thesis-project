import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from typing import List, Tuple
from math import sqrt

# import osmnx as ox

# print("Loading map data...")
# graph = ox.graph_from_xml("prague.osm")

import multiprocessing
pool = multiprocessing.Pool(processes=4)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

async def get_distance(point1, point2):
    return sqrt( (point1[0] - point2[0])*(point1[0] - point2[0]) +
        (point1[1] - point2[1])*(point1[1] - point2[1]) )

@app.get("/distance/{start_x}:{start_y};{dest_x}:{dest_y}")
async def distance(start_x: float, start_y: float, dest_x: float, dest_y: float):
    result = await get_distance((start_x, start_y), (dest_x, dest_y))
    return {
        'distance': result
    }

class Path(BaseModel):
    amount: int
    path: List[float]

@app.post("/path")
async def path_dist(path: Path):
    points = list(map(lambda x: (x[0], x[1]), zip(path.path[::2], path.path[1::2])))
    distances_coroutines = list(map(lambda x: get_distance(x[0], x[1]), zip(points[-1:], points)))
    distances = [ await coroutine for coroutine in distances_coroutines ]
    return {
        'distance': sum(distances)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)