# 📈 WebRTC Live Data Plotter

Een real-time data visualisatie project waarbij binaire data vanuit een **C++ applicatie** via **WebRTC** rechtstreeks naar een **Browser Dashboard** wordt gestuurd.
Dit project maakt gebruik van Peer-to-Peer verbindingen voor minimale latency.

---

## 🚀 Features
* **C++ Backend:** Maakt gebruik van `libdatachannel` voor WebRTC verbindingen.
* **Web Dashboard:** Gehost op Vercel, gebouwd met Chart.js.
* **Real-time:** Directe data-overdracht zonder tussenkomst van een database.

---

## 🛠 Installatie & Setup

### 1. Vereisten
* Ubuntu 20.04+ (of andere Linux distributie)
* CMake & GCC/G++
* Node.js & npm (voor deployment)
* `libdatachannel` bibliotheek

### 2. C++ Applicatie Bouwen
Navigeer naar de build map en compileer de broncode:
```bash
cd build
cmake ..
make
