from flask import Flask, jsonify, request, render_template
import os
import socket

from db import (
    device_exists,
    get_devices,
    get_measurements,
    get_latest_measurement,
    get_measurements_for_device,
    insert_measurement,
    get_statistics,
)
from validation import validate_measurement
from cache import get_latest_from_cache, set_latest_in_cache

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1")
POD_NAME = socket.gethostname()


@app.get("/")
def dashboard():
    return render_template("index.html", version=APP_VERSION, pod=POD_NAME)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "pod": POD_NAME,
    }), 200

@app.get("/devices")
def devices():
    return jsonify(get_devices()), 200


@app.get("/measurements")
def measurements():
    return jsonify(get_measurements()), 200


@app.get("/devices/<device_id>/latest")
def latest(device_id):
    if not device_exists(device_id):
        return jsonify({
            "error": "device not found"
        }), 404

    measurement = get_latest_from_cache(device_id)

    if measurement is not None:
        return jsonify(measurement), 200

    measurement = get_latest_measurement(device_id)

    if measurement is None:
        return jsonify({
            "error": "no measurements found"
        }), 404

    set_latest_in_cache(device_id, measurement)

    return jsonify(measurement), 200
    
@app.get("/devices/<device_id>/measurements")
def device_history(device_id):
    if not device_exists(device_id):
        return jsonify({
            "error": "device not found"
        }), 404

    measurements = get_measurements_for_device(device_id)
    return jsonify(measurements), 200


@app.post("/measurements")
def create_measurement():
    data = request.get_json(silent=True) or {}
    errors = validate_measurement(data)

    if errors:
        print(f"INVALID measurement from {data.get('deviceId', 'unknown')}: {errors}")
        return jsonify({"errors": errors}), 400

    if not device_exists(data["deviceId"]):
        print(f"UNKNOWN device: {data['deviceId']}")
        return jsonify({
            "errors": ["unknown deviceId"]
        }), 400

    measurement = insert_measurement(data)
    set_latest_in_cache(data["deviceId"], measurement)
    print(f"VALID measurement stored: {measurement}")
    return jsonify({"status": "created", "measurement": measurement}), 201

@app.get("/statistics")
def statistics():
    stats = get_statistics()

    return jsonify(stats), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
