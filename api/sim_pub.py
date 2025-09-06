import time, json, random
import paho.mqtt.client as mqtt

# Connect ke broker Mosquitto (service dari docker-compose)
client = mqtt.Client()
client.connect("localhost", 1883, 60)

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
        # Menggunakan wildcard '+' untuk jenis kendaraan dan ID kendaraan
        topic = f"sim/land/{vehicle}/position"  # Topik untuk kendaraan darat
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
        # Menggunakan wildcard '+' untuk jenis kendaraan dan ID kapal
        topic = f"sim/sea/{vehicle}/position"  # Topik untuk kapal laut
        client.publish(topic, json.dumps(payload))
        print(f"PUB {topic} {payload}")

    time.sleep(3)  # Delay 3 detik untuk tiap iterasi
