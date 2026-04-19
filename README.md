# 📈 WebRTC Live Data Plotter

Een real-time data visualisatie project waarbij binaire data vanuit een **C++ applicatie** via **WebRTC** rechtstreeks naar een **Browser Dashboard** wordt gestuurd.
Dit project maakt gebruik van Peer-to-Peer verbindingen voor minimale latency.

---

## 🚀 Features
* **C++ Backend:** Maakt gebruik van `libdatachannel` voor WebRTC verbindingen.
* **Web Dashboard:** Gehost op Vercel, gebouwd met Chart.js.
* **Real-time:** Directe data-overdracht zonder tussenkomst van een database.

* libdatachannel is een krachtige, lichtgewicht C++ bibliotheek die WebRTC (Data Channels) en WebSockets implementeert. Het is de motor achter dit project en de reden waarom een C++ applicatie rechtstreeks met een browser kan praten zonder zware servers.

Hier is een overzicht van wat deze bibliotheek zo bijzonder maakt en hoe het onder de motorkap werkt:
🚀 Kernkenmerken

    Geen afhankelijkheden: In tegenstelling tot de officiële Google WebRTC-stack (die gigantisch is), is libdatachannel klein en geoptimaliseerd voor embedded systemen en snelle applicaties.

    Pure Data Channels: Het richt zich op het verzenden van data (SCTP) in plaats van video/audio, wat het perfect maakt voor sensordata, robotica en mijn plotter.

    Cross-platform: Werkt op Linux, Windows, macOS, en zelfs op Android/iOS.

🏗 Hoe het werkt in jouw project

Wanneer je ./webrtc_sender uitvoert, doorloopt de bibliotheek de volgende technische stappen:

    ICE Gathering: De bibliotheek zoekt naar netwerkpaden (IP-adressen en poorten) om een gaatje in de firewall te vinden.

    SCTP over DTLS: Het bouwt een beveiligde, versleutelde tunnel.

    Binaire Stream: Het zet je C++ uint32_t getallen om in binaire pakketjes die de browser via JavaScript (ArrayBuffer) weer kan inlezen.

💻 Belangrijke klassen in de code

Als je de code verder wilt uitbreiden, zijn dit de belangrijkste onderdelen van de bibliotheek die je gebruikt:
Klasse	Functie
rtc::PeerConnection	De "manager" die de hele verbinding en de handshake (Offer/Answer) regelt.
rtc::DataChannel	De feitelijke tunnel waarover je de data verstuurt (dc->send()).
rtc::Configuration	Hier stel je de STUN en TURN servers in voor internettoegang.
rtc::Description	De container voor de SDP-tekst (de Offer en Answer).
🛠 Waarom we STUN/TURN nodig hebben

Omdat libdatachannel Peer-to-Peer werkt, moeten de apparaten elkaar vinden.

    STUN: Vertelt je computer: "Dit is je publieke IP-adres."

    TURN: Wordt gebruikt als de firewall te streng is; de data gaat dan via een tussenstation (relay).

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
