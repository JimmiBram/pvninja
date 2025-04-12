import paho.mqtt.client as mqtt
import configparser
import sqlite3
import time
import threading
from datetime import datetime

# --- Læs konfiguration ---
config = configparser.ConfigParser()
config.read("config.ini")

MQTT_BROKER = config.get("mqtt", "broker")
MQTT_PORT = config.getint("mqtt", "port")
MQTT_USERNAME = config.get("mqtt", "username")
MQTT_PASSWORD = config.get("mqtt", "password")

# --- Data holder ---
data = {
    "pv_power_1": None,
    "pv_power_2": None,
    "pv_voltage_1": None,
    "pv_current_1": None,
    "pv_voltage_2": None,
    "pv_current_2": None,
    "load_power": None,
    "battery_power": None,
    "battery_soc": None,
    "grid_power": None,
    "work_mode_priority": None,
    "export_limit": None
}

# --- MQTT topics ---
topics = {
    "pv_power_1": "solar_assistant/inverter_1/pv_power_1/state",
    "pv_power_2": "solar_assistant/inverter_1/pv_power_2/state",
    "pv_voltage_1": "solar_assistant/inverter_1/pv_voltage_1/state",
    "pv_current_1": "solar_assistant/inverter_1/pv_current_1/state",
    "pv_voltage_2": "solar_assistant/inverter_1/pv_voltage_2/state",
    "pv_current_2": "solar_assistant/inverter_1/pv_current_2/state",
    "load_power": "solar_assistant/inverter_1/load_power/state",
    "battery_power": "solar_assistant/total/battery_power/state",
    "battery_soc": "solar_assistant/total/battery_state_of_charge/state",
    "grid_power": "solar_assistant/inverter_1/grid_power/state",
    "work_mode_priority": "solar_assistant/inverter_1/work_mode_priority/state",
    "export_limit": "solar_assistant/inverter_1/export_power_rate/state"
}

# --- SQLite setup ---
db_file = "solar_data_final.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS mqtt_log (
        timestamp TEXT,
        inverter_mode TEXT,
        battery_soc REAL,
        solar_production REAL,
        potential_production REAL,
        load_power REAL,
        battery_power REAL,
        grid_power REAL,
        export_limit REAL,
        solar_surplus REAL,
        recommended_export_limit REAL
    )
""")
conn.commit()
conn.close()

# --- Funktion til at logge data til databasen ---
def log_to_db(log_data):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mqtt_log (
            timestamp, inverter_mode, battery_soc, solar_production,
            potential_production, load_power, battery_power,
            grid_power, export_limit, solar_surplus, recommended_export_limit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, log_data)
    conn.commit()
    conn.close()

# --- Beregning og visning ---
def check_and_print():
    if all(data[k] is not None for k in data):
        try:
            pv_power_1 = float(data["pv_power_1"])
            pv_power_2 = float(data["pv_power_2"])
            pv_voltage_1 = float(data["pv_voltage_1"])
            pv_current_1 = float(data["pv_current_1"])
            pv_voltage_2 = float(data["pv_voltage_2"])
            pv_current_2 = float(data["pv_current_2"])
            load_power = float(data["load_power"])
            battery_power = float(data["battery_power"])
            battery_soc = float(data["battery_soc"])
            grid_power = float(data["grid_power"])
            export_limit = float(data["export_limit"])
            inverter_mode = data["work_mode_priority"]

            potential_1 = pv_voltage_1 * pv_current_1 if pv_current_1 > 0 else 0
            potential_2 = pv_voltage_2 * pv_current_2 if pv_current_2 > 0 else 0
            potential_production = potential_1 + potential_2
            solar_production = pv_power_1 + pv_power_2
            surplus = potential_production - solar_production

            if potential_production > 0 and surplus > 0:
                recommended_export_limit = (surplus / potential_production) * 100
            else:
                recommended_export_limit = 0

            print("\n--- Live fra SolarAssistant ---")
            print(f"🧠 Inverter mode: {inverter_mode}")
            print(f"🔋 Batteri SoC: {battery_soc:.1f} %")
            print(f"☀️  Solproduktion: {solar_production:.1f} W")
            print(f"🌞 Potentiel solproduktion: {potential_production:.1f} W")
            print(f"⚡ Inverterproduktion (load): {load_power:.1f} W")
            print(f"🔋 Batteriproduktion: {battery_power:.1f} W")
            print(f"🌍 Net-import: {grid_power:.1f} W")
            print(f"🚫 Export Limit (nu): {export_limit:.0f} %")
            print(f"📊 Soloverskud: {surplus:.1f} W")
            print(f"🧮 Anbefalet Export Limit for at beskytte batteriet: {recommended_export_limit:.0f} %")

            # Log til database
            timestamp = datetime.now().isoformat()
            log_row = (
                timestamp, inverter_mode, battery_soc, solar_production,
                potential_production, load_power, battery_power,
                grid_power, export_limit, surplus, recommended_export_limit
            )
            log_to_db(log_row)

        except Exception as e:
            print("⚠️ Fejl i beregning:", e)

# --- MQTT callbacks ---
def on_message(client, userdata, msg):
    for key, topic in topics.items():
        if msg.topic == topic:
            data[key] = msg.payload.decode()
            check_and_print()

# --- MQTT setup ---
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

for topic in topics.values():
    client.subscribe(topic)

print("🔌 Forbinder til SolarAssistant og logger til SQLite...")
client.loop_forever()
