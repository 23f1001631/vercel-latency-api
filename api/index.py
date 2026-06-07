from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json

app = FastAPI()

# VERY IMPORTANT CORS SETUP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON data
with open("q-vercel-latency (1).json", "r") as f:
    telemetry = json.load(f)


# Root route
@app.get("/")
async def root():
    return {"message": "working"}


# Explicit OPTIONS handler
@app.options("/api/latency")
async def options_handler():
    return JSONResponse(
        content={"message": "ok"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


# POST endpoint
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

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": len([x for x in latencies if x > threshold]),
        }

    return JSONResponse(content=result, headers={"Access-Control-Allow-Origin": "*"})
