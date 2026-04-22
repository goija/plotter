import json
import random
import time
from datetime import datetime
from flask import Flask
from flask_socketio import SocketIO

# Initialiseer de Flask server en WebSocket
app = Flask(__name__)
app.config['SECRET_KEY'] = 'vortex_secret_265'
socketio = SocketIO(app, cors_allowed_origins="*") # CORS allow all voor lokaal testen

print(">>> INITIALIZING VORTEX OMNI-BRIDGE ENGINE v26.5...")
print(">>> WEBSOCKET SERVER STARTING...\n")

class VortexNode:
    def __init__(self, node_id, name, lat, lon, is_master=False):
        self.id = node_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.is_master = is_master
        self.connections = []

    def connect(self, other_node):
        if other_node not in self.connections:
            self.connections.append(other_node)
            other_node.connections.append(self)

class VortexNetwork:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.id] = node

    def get_antipodal(self, lat, lon, is_master):
        if is_master:
            return {"lat": -52.2200, "lon": -174.8300}
        anti_lat = -lat
        anti_lon = lon - 180 if lon > 0 else lon + 180
        return {"lat": round(anti_lat, 4), "lon": round(anti_lon, 4)}

    def find_cherries(self):
        cherries = []
        for node_id, node in self.nodes.items():
            leaves = [n for n in node.connections if len(n.connections) == 1]
            if len(leaves) == 2:
                cherries.append({
                    "hub": node.name,
                    "leaf_a": leaves[0].name,
                    "leaf_b": leaves[1].name,
                    "status": "MIRROR_BALANCED"
                })
        return cherries

    def generate_astrometric_telemetry(self):
        jitter = lambda base, var: round(base + random.uniform(-var, var), 2)
        return {
            "iss_vel": jitter(7.66, 0.05),
            "moon_del": jitter(1.282, 0.005),
            "moon_jit": random.randint(5, 20),
            "vega_jit": jitter(45.0, 8.0),
            "deneb_jit": jitter(82.0, 12.0),
            "orion_jit": jitter(104.0, 20.0),
            "leo_jit": jitter(38.0, 5.0)
        }

# Netwerk opbouwen
network = VortexNetwork()
master = VortexNode("MASTER", "Laren (NH)", 52.2200, 5.1700, is_master=True)
zwolle = VortexNode(202, "Zwolle", 52.51, 6.09)
franeker = VortexNode(203, "Franeker", 53.18, 5.54)
sat_alpha = VortexNode(301, "Sat-Alpha", 45.0, -12.0)
sat_beta = VortexNode(302, "Sat-Beta", -30.0, 140.0)
sat_gamma = VortexNode(303, "Sat-Gamma", 10.0, 20.0)

for n in [master, zwolle, franeker, sat_alpha, sat_beta, sat_gamma]:
    network.add_node(n)

master.connect(zwolle)
master.connect(franeker)
master.connect(sat_alpha)
sat_alpha.connect(sat_beta)
sat_alpha.connect(sat_gamma)

# Achtergrondtaak die continu data pusht naar de browser
def background_telemetry_loop():
    while True:
        telemetry = network.generate_astrometric_telemetry()
        cherries = network.find_cherries()
        antipodal = network.get_antipodal(master.lat, master.lon, True)
        
        payload = {
            "telemetry": telemetry,
            "cherries": cherries,
            "master_antipodal": antipodal,
            "timestamp": datetime.utcnow().strftime('%H:%M:%S UTC')
        }
        
        # Zend de data uit via de websocket
        socketio.emit('vortex_update', payload)
        socketio.sleep(1) # Update elke seconde

@socketio.on('connect')
def handle_connect():
    print(">>> BROWSER VERBONDEN MET OMNI-BRIDGE.")
    socketio.start_background_task(background_telemetry_loop)

if __name__ == '__main__':
    # Start de server op poort 5000
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)