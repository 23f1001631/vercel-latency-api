from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data
with open("q-vercel-latency (1).json", "r") as f:
    telemetry = json.load(f)


@app.post("/api/latency")
async def latency(request: Request):

    body = await request.json()

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}

    for region in regions:

        records = [x for x in telemetry if x["region"] == region]

        latencies = [x["latency_ms"] for x in records]
        uptimes = [x["uptime_pct"] for x in records]

        breaches = len([x for x in latencies if x > threshold])

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": breaches,
        }

    return result
