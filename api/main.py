import os, json, asyncio, time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from influxdb_client import InfluxDBClient, Point, WriteOptions
from aiomqtt import Client as AioMQTT
import datetime as dt

# === ENV ===
ORG    = os.getenv("INFLUXDB_ORG", "myorg")
BUCKET = os.getenv("INFLUXDB_BUCKET", "tracking")
TOKEN  = os.getenv("INFLUXDB_ADMIN_TOKEN")
INFLUX = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
MQTT_H = os.getenv("MQTT_HOST", "mosquitto")
MQTT_P = int(os.getenv("MQTT_PORT", "1883"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Tulis cepat agar langsung kelihatan di Influx
iclient = InfluxDBClient(url=INFLUX, token=TOKEN, org=ORG)
writer  = iclient.write_api(write_options=WriteOptions(batch_size=1, flush_interval=1000))

WS = set()

async def mqtt_worker():
    try:
        async with AioMQTT(MQTT_H, MQTT_P) as client:
            await client.subscribe("sim/+/+/position")
            print("[MQTT] Subscribed: sim/+/+/position")
            async with client.unfiltered_messages() as messages:
                async for m in messages:
                    try:
                        payload = json.loads(m.payload.decode())
                        _, a_type, a_id, _ = m.topic.split("/")
                        print(f"[MQTT] {m.topic} -> {payload}")

                        # Pastikan payload berisi timestamp
                        timestamp = payload.get("ts")
                        if timestamp is None:
                            print(f"[WARNING] No timestamp in message, using server time.")
                            timestamp = time.time()  # Gunakan server time sebagai fallback

                        # Validasi format timestamp
                        try:
                            # Pastikan timestamp dalam format nanodetik, jika perlu konversi
                            timestamp = int(float(timestamp) * 1e9)  # Ubah ke nanodetik
                            timestamp = dt.datetime.utcfromtimestamp(timestamp / 1e9)  # Convert ke datetime
                        except ValueError:
                            print("[ERROR] Invalid timestamp format, using current time.")
                            timestamp = dt.datetime.utcnow()  # Gunakan waktu UTC saat ini

                        # Tanpa .time(...) -> menggunakan server time (UTC now)
                        p = (Point("positions")
                             .tag("asset_id", a_id)
                             .tag("type", a_type)
                             .field("lat", float(payload["lat"]))
                             .field("lon", float(payload["lon"]))
                             .field("speed", float(payload.get("speed", 0)))
                             .field("heading", float(payload.get("heading", 0)))
                             .time(timestamp))  # Gunakan timestamp yang valid

                        writer.write(BUCKET, ORG, p)
                        print(f"[INFLUX] WROTE {a_type}/{a_id} lat={payload['lat']} lon={payload['lon']}")

                        # Broadcast ke WebSocket (opsional untuk frontend)
                        for ws in list(WS):
                            try:
                                await ws.send_json({"id": a_id, "type": a_type, **payload})
                            except Exception:
                                WS.discard(ws)

                    except Exception as e:
                        print("[ERROR] processing MQTT message:", e)
    except Exception as e:
        print("[ERROR] MQTT connect:", e)

@app.on_event("startup")
async def boot():
    asyncio.create_task(mqtt_worker())

@app.websocket("/ws/stream")
async def ws_stream(ws: WebSocket):
    await ws.accept(); WS.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        WS.discard(ws)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
