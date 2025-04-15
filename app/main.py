import paho.mqtt.client as mqtt
import configparser
import os
import time
import threading
from datetime import datetime
import math

# --- Automatisk oprettelse af config.ini hvis den ikke findes ---
CONFIG_FILE = "config.ini"
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

# --- Beregning og visning ---
def check_and_print(data):
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
            surplus = float(math.floor(potential_production - solar_production))
            if surplus < 0:
                surplus = 0

            if potential_production > 0 and surplus > 0:
                recommended_export_limit = (surplus / potential_production) * 100
            else:
                recommended_export_limit = 0
                
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n--- Live fra SolarAssistant ---")
            print(f"🧠 Inverter mode: {inverter_mode}")
            print(f"🔋 Batteri SoC: {battery_soc:.1f} %")
            print(f"☀️  Solproduktion: {solar_production:.1f} W")
            print(f"🌞 Potentiel solproduktion: {potential_production:.1f} W")
            print(f"⚡ Forbrug (load): {load_power:.1f} W")
            print(f"🔋 Batteri produktion: {battery_power:.1f} W")
            print(f"🌍 Net-import: {grid_power:.1f} W")
            print(f"🚫 Export Limit (nu): {export_limit:.0f} %")
            print(f"📊 Soloverskud: {surplus:.0f} W")
            print(f"🧮 Anbefalet Export Limit for at beskytte batteriet: {recommended_export_limit:.0f} %")

            # --- SYSTEMKONTROL ALGORITME ---
            car_home = False  # <- sæt denne baseret på input eller sensor
            export_price = 0  # <- hent aktuel pris hvis muligt

            if surplus <= 0:
                print("🔄 Brug paneler + batteri til at dække husets behov")
                # evt. mqtt_publish("car/charging", "off")
                # evt. mqtt_publish("export_limit", "0")

            elif battery_soc < 100:
                print("⚡ Oplader batteriet med overskud")
                # mqtt_publish("battery/charging", "on")
                # mqtt_publish("export_limit", "0")

            elif battery_soc >= 100:
                if car_home:
                    print("🚗 Elbil er hjemme – oplad med overskud")
                    car_amp = int(surplus / 230)
                    print(f"➡️ Justerer bil-ladning til ca. {car_amp} A")
                    # mqtt_publish("car/charging", "on")
                    # mqtt_publish("car/charging_ampere", str(car_amp))
                    # mqtt_publish("export_limit", "0")
                elif export_price > 5:
                    print("🌍 Eksporterer overskud (pris > 5 øre)")
                    export_pct = min(max(int(recommended_export_limit), 0), 100)
                    print(f"➡️ Sætter eksportgrænse til {export_pct} %")
                    # mqtt_publish("car/charging", "off")
                    # mqtt_publish("export_limit", str(export_pct))
                else:
                    print("🛑 Ingen elbil hjemme og eksportpris for lav – gør ingenting")
                    # mqtt_publish("car/charging", "off")
                    # mqtt_publish("export_limit", "0")

        except Exception as e:
            print("⚠️ Fejl i beregning:", e)

# --- MQTT callbacks ---
def on_message(client, userdata, msg):
    for key, topic in topics.items():
        if msg.topic == topic:
            userdata["data"][key] = msg.payload.decode()
            check_and_print(userdata["data"])

def start_service():
    # Opret config hvis den ikke findes
    # --- Læs config.ini ---
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    MQTT_BROKER = config.get("mqtt", "broker")
    MQTT_PORT = config.getint("mqtt", "port")
    MQTT_USERNAME = config.get("mqtt", "username")
    MQTT_PASSWORD = config.get("mqtt", "password")
    
    # --- MQTT setup ---
    client = mqtt.Client(userdata={"data": data})
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    for topic in topics.values():
        client.subscribe(topic)

    print("🔌 Forbinder til SolarAssistant...")
    client.loop_forever()

if __name__ == '__main__':
    start_service()