import json
import random
import time
from datetime import datetime

print(">>> INITIALIZING VORTEX OMNI-BRIDGE ENGINE v26.5...")
print(">>> LOADING CHERRY-GRAPH TOPOLOGY MODULE...\n")

class VortexNode:
    def __init__(self, node_id, name, lat, lon, is_master=False):
        self.id = node_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.is_master = is_master
        self.connections = [] # Voor de grafentheorie

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
            return {"lat": -52.2200, "lon": -174.8300} # Hardcoded override
        
        anti_lat = -lat
        anti_lon = lon - 180 if lon > 0 else lon + 180
        return {"lat": round(anti_lat, 4), "lon": round(anti_lon, 4)}

    def find_cherries(self):
        """
        GRAFENTHEORIE MODULE: 
        Zoek naar 'Cherries' (P3 subgrafen / Stergraaf S2).
        Dit zijn centrale hubs verbonden met exact 2 'leaf' nodes (eindpunten).
        Groepentheorie: Automorfismegroep is isomorf met S2.
        """
        cherries = []
        for node_id, node in self.nodes.items():
            # Vind alle connecties van deze node die zelf maar 1 connectie hebben (leaves)
            leaves = [n for n in node.connections if len(n.connections) == 1]
            
            # Als een hub exact 2 leaves heeft, is het een 'Cherry'
            if len(leaves) == 2:
                cherries.append({
                    "hub": node.name,
                    "leaf_a": leaves[0].name,
                    "leaf_b": leaves[1].name,
                    "algebraic_symmetry": "S2 / Z2",
                    "routing_status": "MIRROR_BALANCED"
                })
        return cherries

    def generate_astrometric_telemetry(self):
        jitter = lambda base, var: round(base + random.uniform(-var, var), 2)
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ISS_NS_VELOCITY_KMS": jitter(7.66, 0.05),
            "MOON_DELAY_SEC": jitter(1.282, 0.005),
            "VEGA_JITTER_MS": jitter(45.0, 8.0),
            "DENEB_JITTER_MS": jitter(82.0, 12.0),
            "ORION_JITTER_MS": jitter(104.0, 20.0),
            "LEO_JITTER_MS": jitter(38.0, 5.0)
        }

# ==========================================
# 1. NETWERK OPBOUWEN
# ==========================================
network = VortexNetwork()

# Nodes aanmaken
master = VortexNode("MASTER", "Laren (NH) // COMMAND", 52.2200, 5.1700, is_master=True)
zwolle = VortexNode(202, "Zwolle", 52.51, 6.09)
franeker = VortexNode(203, "Franeker", 53.18, 5.54)
sat_alpha = VortexNode(301, "Sat-Alpha", 45.0, -12.0)
sat_beta = VortexNode(302, "Sat-Beta", -30.0, 140.0)

network.add_node(master)
network.add_node(zwolle)
network.add_node(franeker)
network.add_node(sat_alpha)
network.add_node(sat_beta)

# Topologie / Graaf verbinden (Master is hub, Zwolle en Franeker zijn leaves)
master.connect(zwolle)
master.connect(franeker)
master.connect(sat_alpha)

# Sat-Alpha is ook een hub voor een andere cherry
sat_alpha.connect(sat_beta)
sat_gamma = VortexNode(303, "Sat-Gamma", 10.0, 20.0)
network.add_node(sat_gamma)
sat_alpha.connect(sat_gamma)


# ==========================================
# 2. DATA EXTRACTIE & SYNC LOOP
# ==========================================
try:
    while True:
        # A. Telemetrie ophalen
        telemetry = network.generate_astrometric_telemetry()
        
        # B. Groepentheorie: Zoek Symmetrische Cherries voor load balancing
        active_cherries = network.find_cherries()

        # C. Output bouwen (Dit kan later via een REST API naar je HTML gestuurd worden)
        system_state = {
            "telemetry": telemetry,
            "active_cherries": active_cherries,
            "master_antipodal": network.get_antipodal(master.lat, master.lon, True)
        }

        print(json.dumps(system_state, indent=2))
        print("-" * 60)
        
        time.sleep(2) # Update elke 2 seconden

except KeyboardInterrupt:
    print("\n>>> VORTEX ENGINE SHUTDOWN SEQUENCE INITIATED.")