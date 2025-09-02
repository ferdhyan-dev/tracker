import time, json, random
import paho.mqtt.client as mqtt

# Connect ke broker Mosquitto (service dari docker-compose)
client = mqtt.Client()
client.connect("mosquitto", 1883, 60)

# Daftar kendaraan darat (truck)
land_vehicles = [f"TRUCK-{i:02}" for i in range(1, 6)]

# Daftar kapal laut (ship)
sea_vehicles = [f"SHIP-{i:02}" for i in range(1, 4)]

while True:
    # Simulasi kendaraan darat
    for vehicle in land_vehicles:
        payload = {
            "lat": -6.2 + random.uniform(-0.01, 0.01),
            "lon": 106.8 + random.uniform(-0.01, 0.01),
            "speed": random.uniform(20, 80),
            "heading": random.randint(0, 360),
            "ts": int(time.time())
        }
        topic = f"sim/land/{vehicle}/position"
        client.publish(topic, json.dumps(payload))
        print(f"PUB {topic} {payload}")

    # Simulasi kapal laut
    for vehicle in sea_vehicles:
        payload = {
            "lat": -5.5 + random.uniform(-0.05, 0.05),
            "lon": 110.5 + random.uniform(-0.05, 0.05),
            "speed": random.uniform(5, 25),
            "heading": random.randint(0, 360),
            "ts": int(time.time())
        }
        topic = f"sim/sea/{vehicle}/position"
        client.publish(topic, json.dumps(payload))
        print(f"PUB {topic} {payload}")

    time.sleep(3)
