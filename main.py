import csv
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT credentials and broker info
MQTT_BROKER = "192.168.50.102"
MQTT_PORT = 1883
MQTT_USERNAME = "bramconsole"
MQTT_PASSWORD = "ostostost"

# Topics you want to monitor (add more if needed)
TOPICS = [
    "solar_assistant/inverter_1/pv_power/state",
    "solar_assistant/inverter_1/load_power/state",
    "solar_assistant/inverter_1/battery_power/state",
    "solar_assistant/inverter_1/grid_power/state",
    "solar_assistant/inverter_1/pv_voltage_1/state",
    "solar_assistant/inverter_1/pv_current_1/state",
    "solar_assistant/inverter_1/pv_voltage_2/state",
    "solar_assistant/inverter_1/pv_current_2/state",
    "solar_assistant/inverter_1/battery_state_of_charge/state",
    "solar_assistant/inverter_1/temperature/state",
]

# A dictionary to store the latest values from each topic
data_store = {}

# Output file
CSV_FILE = "solar_training_data.csv"

# Called when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in TOPICS:
        client.subscribe(topic)

# Called when a message is received
def on_message(client, userdata, msg):
    topic = msg.topic.split("/")[-2] + "_" + msg.topic.split("/")[-1]  # inverter_1_pv_power_state
    try:
        value = float(msg.payload.decode())
    except ValueError:
        value = msg.payload.decode()

    data_store[topic] = value

# Save data to CSV periodically
def save_data():
    headers_written = False
    with open(CSV_FILE, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        while True:
            if len(data_store) >= len(TOPICS):  # only write when we have all values
                row = [datetime.now().isoformat()]
                headers = ["timestamp"] + list(data_store.keys())
                row += [data_store[k] for k in data_store.keys()]

                if not headers_written:
                    writer.writerow(headers)
                    headers_written = True

                writer.writerow(row)
                csvfile.flush()
                time.sleep(10)  # interval in seconds

# Main
if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Start MQTT loop in a thread
    client.loop_start()

    try:
        save_data()
    except KeyboardInterrupt:
        print("Stopping logger.")
        client.loop_stop()
        client.disconnect()
