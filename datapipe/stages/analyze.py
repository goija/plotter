cat << 'EOF' > /home/ontwerp/Downloads/plotter/weathatmos/datapipe/stages/analyze.py
import math
import random
import pandas as pd
import numpy as np
import json
import cbor2
import socket
import os
from datapipe.model import choose_optimal_drift, classify_color
from datapipe.utils import write_csv, load_config
from datapipe.word_selection import choose_word

# UDP Setup
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def build_daily_analytics(run_date, drift_grid, threshold):
    print(f"--- Analyse van {run_date} ---")
    input_path = f"data/curated/{run_date}.csv"
    if not os.path.exists(input_path):
        return

    df = pd.read_csv(input_path)
    p_opt, entropy_p = choose_optimal_drift(df, drift_grid)
    
    # dummy offsets voor de fix op regel 182
    offsets = [float(p_opt)] 
    anomaly_score = abs(entropy_p - 0.5) * 2.0
    status_label = choose_word(anomaly_score)

    # De beruchte regel 182 fix
    payload = {
        "entropy": float(entropy_p),
        "anomaly_score": float(anomaly_score),
        "drift": float(p_opt),
        "label": str(status_label),
        "offsets": json.dumps(offsets) 
    }

    # Verstuur als CBOR
    try:
        message = cbor2.dumps(payload)
        udp_sock.sendto(message, (UDP_IP, UDP_PORT))
        print(f"✅ Data verzonden (CBOR)")
    except Exception as e:
        print(f"❌ Verzendfout: {e}")

    # Opslaan
    output_path = f"data/analytics/{run_date}.csv"
    write_csv([payload], output_path)

EOF