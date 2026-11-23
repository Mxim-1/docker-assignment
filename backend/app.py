import json
import os
import re
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from redis import Redis

app = Flask(__name__)

redis_db = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True,
)

CAPACITY = 20
INSIDE_KEY = "parking:inside"


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@app.get("/api/health")
def health():
    redis_db.ping()
    return jsonify(status="ok")


@app.get("/api/cars")
def get_cars():
    plates = redis_db.smembers(INSIDE_KEY)
    cars = [redis_db.hgetall(f"parking:car:{plate}") for plate in plates]
    cars.sort(key=lambda car: car.get("entry_time", ""), reverse=True)
    return jsonify(cars)


@app.get("/api/stats")
def get_stats():
    inside = redis_db.scard(INSIDE_KEY)
    return jsonify(inside=inside, capacity=CAPACITY, full=inside >= CAPACITY)


@app.post("/api/cars")
def add_car():
    data = request.get_json(silent=True) or {}
    plate = str(data.get("plate", "")).strip().upper()
    category = str(data.get("category", "REGULAR")).upper()

    if not re.fullmatch(r"[A-Z0-9-]{3,15}", plate):
        return jsonify(error="Use 3-15 letters, digits or hyphens."), 400
    if category not in {"REGULAR", "VIP"}:
        return jsonify(error="Category must be REGULAR or VIP."), 400
    if redis_db.sismember(INSIDE_KEY, plate):
        return jsonify(error="This car is already inside."), 409
    if redis_db.scard(INSIDE_KEY) >= CAPACITY:
        return jsonify(error="The parking lot is full."), 409

    car = {"plate": plate, "category": category, "entry_time": now_iso()}
    redis_db.hset(f"parking:car:{plate}", mapping=car)
    redis_db.sadd(INSIDE_KEY, plate)
    redis_db.lpush("parking:events", json.dumps({"action": "enter", **car}))
    return jsonify(car), 201


@app.post("/api/cars/<plate>/exit")
def release_car(plate):
    plate = plate.strip().upper()
    if not redis_db.sismember(INSIDE_KEY, plate):
        return jsonify(error="Car not found inside."), 404

    redis_db.srem(INSIDE_KEY, plate)
    redis_db.delete(f"parking:car:{plate}")
    redis_db.lpush(
        "parking:events",
        json.dumps({"action": "exit", "plate": plate, "time": now_iso()}),
    )
    return jsonify(message=f"{plate} left the parking lot.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
