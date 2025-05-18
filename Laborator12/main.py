from flask import Flask, request, jsonify, abort
import os
import time
import random
from pathlib import Path


app = Flask(__name__)

CONFIG_FOLDER = "config"
os.makedirs(CONFIG_FOLDER, exist_ok=True)

simulated_sensors = {

    "temperature_sensor" : lambda: { "value": round(random.uniform(20.0, 30.0), 2) },
    "humidity_sensor"    : lambda: { "value": round(random.uniform(30.0, 70.0), 2) },
    "airflow_sensor"     : lambda: { "value": round(random.uniform(1000.0, 3000.0), 2)},
    "pressure_sensor"    : lambda: { "value": round(random.uniform(950.0, 1050.0), 2) }
}

valid_sensor_types = ["temperature_sensor", "humidity_sensor", "airflow_sensor", "pressure_sensor"]

def generate_random_config(sensor_id):
    units = {
        "temperature_sensor": "C",
        "humidity_sensor": "%",
        "airflow_sensor": "L/min",
        "pressure_sensor": "hPa"
    }

    unit = units.get(sensor_id, "")
    config = {
        "scale": round(random.uniform(0.8, 1.5), 2),
        "offset": round(random.uniform(-2.0, 2.0), 2),
        "unit": unit, 
        "decimal": random.choice([1, 2, 3]),
        "enabled": random.choice(["true", "false"]),
        "sampling_rate": random.choice([500, 1000, 2000]),
        "mode": random.choice(["live", "cached", "manual"]),
        "alert": random.choice(["true", "false"])
    }

    # Convertim într-un fișier .txt format key=value
    lines = [f"{key}={value}" for key, value in config.items()]
    return "\n".join(lines)

# se va citi o valoare furnizata de la un senzor
# metoda GET

@app.route("/sensor/<sensor_id>", methods=['GET'])
def get_sensor_value(sensor_id):
    if sensor_id in simulated_sensors:
        results = simulated_sensors[sensor_id]()
        return jsonify({
            "sensor_id": sensor_id,
            "value"    : results["value"]
            })
    abort(404, description=f"Invalid sensor type. Must be one of: {valid_sensor_types}")

# se va crea un fisier de configurare care va permite, de exemplu, modificarea scalei de reprezentare a valorii masurate:
# metoda POST

@app.route("/sensor/<sensor_id>", methods = ['POST'])
def create_config_file(sensor_id):
    if sensor_id not in valid_sensor_types:
        abort(404, description=f"Invalid sensor type. Must be one of: {valid_sensor_types}")

    filename = f"{sensor_id}_config.txt"
    filepath = os.path.join(CONFIG_FOLDER, filename)  

    if os.path.exists(filepath):
        abort(409, description="Configuration file already exists")
    
    config_content = generate_random_config(sensor_id)

    try:
        with open(filepath, "w") as f:
            f.write(config_content + "\n")
        
        #abort(201, description = "Fisierul de configurare a fost creat automat")
        return jsonify({
            "message": "Configuration file created successfully",
            "sensor_id": sensor_id,
            "config": config_content,
            "filepath": filepath
        }), 201

    except Exception as e:
        abort(500, description=f"Error creating configuration file: {str(e)}")


# inlocuire fisier de configurare
# metoda PUT
@app.route("/sensor/<sensor_id>", methods=['PUT'])
def update_config_file(sensor_id):
    if sensor_id not in valid_sensor_types:
        abort(400, description=f"Invalid sensor type. Must be one of: {valid_sensor_types}")

    filename = f"{sensor_id}_config.txt"
    filepath = os.path.join(CONFIG_FOLDER, filename)

    if not os.path.exists(filepath):
        abort(404, description="Configuration file does not exist. Use POST to create it.")

    try:
        config_content = generate_random_config(sensor_id)
        with open(filepath, "w") as f:
            f.write(config_content + "\n")
        
        return jsonify({
            "message": "Configuration file updated successfully",
            "sensor_id": sensor_id,
            "config": config_content,
            "filepath": filepath
        }), 200
    except Exception as e:
        abort(500, description=f"Internal server error: {str(e)}")


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(406)
@app.errorhandler(409)
@app.errorhandler(500)
def handle_errors(error):
    return jsonify({'error': error.description}), error.code


if __name__ == '__main__':
    app.run(debug=True)    

