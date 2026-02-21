import json
import statistics
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    data = json.load(f)

@app.post("/api/analytics")
async def analytics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        region_data = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]

        avg_latency = sum(latencies) / len(latencies)

        sorted_lat = sorted(latencies)
        index_95 = int(0.95 * len(sorted_lat)) - 1
        p95_latency = sorted_lat[index_95]

        avg_uptime = sum(uptimes) / len(uptimes)

        breaches = len([l for l in latencies if l > threshold])

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return result
