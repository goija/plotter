#include <rtc/rtc.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <thread>
#include <chrono>
#include <cmath>

using namespace rtc;
using namespace std;
using json = nlohmann::json;

int main() {
    // Initialiseer de WebRTC logging
    InitLogger(LogLevel::Warning); 
    
    Configuration config;
    config.iceServers.emplace_back("stun:stun.l.google.com:19302");

    // === NIEUW: Stel de poort in via Configuratie ===
    WebSocketServer::Configuration ws_config;
    ws_config.port = 8081;
    
    // Start de lokale WebSocket server direct op met deze instellingen
    WebSocketServer wss(ws_config);
    
    wss.onClient([&config](shared_ptr<WebSocket> ws) {
        cout << "\n>>> [SIGNALING] Browser verbonden via WebSocket!" << endl;
        
        auto pc = make_shared<PeerConnection>(config);
        auto dc = pc->createDataChannel("vortex");

        // 1. Zodra WebRTC verbonden is, start de P2P datastroom
        dc->onOpen([dc]() {
            cout << ">>> [WEBRTC] P2P TUNNEL OPEN! Data verzenden (20 FPS)..." << endl;
            float time_counter = 0.0f;
            
            while(true) {
                // Genereer een test-signaal (sinusgolf)
                float sensor_val = sin(time_counter); 
                time_counter += 0.1f;
                
                // Verstuur puur binaire data (zeer lage latency)
                dc->send(reinterpret_cast<const std::byte*>(&sensor_val), sizeof(sensor_val));
                
                this_thread::sleep_for(chrono::milliseconds(50));
            }
        });

        // 2. Genereer WebRTC Offer en stuur naar de Browser
        pc->onLocalDescription([ws](Description desc) {
            json msg = {{"type", desc.typeString()}, {"sdp", string(desc)}};
            ws->send(msg.dump());
            cout << ">>> [SIGNALING] Offer verzonden naar browser." << endl;
        });

        // 3. Stuur netwerkpaden (ICE candidates) naar de Browser
        pc->onLocalCandidate([ws](Candidate cand) {
            json msg = {{"type", "candidate"}, {"candidate", cand.candidate()}, {"mid", cand.mid()}};
            ws->send(msg.dump());
        });

        // 4. Luister naar antwoorden van de Browser (Answer & ICE)
        ws->onMessage([pc](variant<binary, string> data) {
            if (holds_alternative<string>(data)) {
                json msg = json::parse(get<string>(data));
                
                if (msg["type"] == "answer") {
                    pc->setRemoteDescription(Description(msg["sdp"].get<string>(), msg["type"].get<string>()));
                    cout << ">>> [SIGNALING] Answer ontvangen. Tunnel wordt opgebouwd..." << endl;
                } 
                else if (msg["type"] == "candidate") {
                    pc->addRemoteCandidate(Candidate(msg["candidate"].get<string>(), msg["mid"].get<string>()));
                }
            }
        });
    });

    cout << "=================================================" << endl;
    cout << ">>> VORTEX WEBRTC SENDER ACTIEF OP POORT 8081 <<<" << endl;
    cout << ">>> Wachten tot interface verbindt...         <<<" << endl;
    cout << "=================================================" << endl;

    // Houd het programma oneindig in de lucht
    while (true) { this_thread::sleep_for(chrono::seconds(1)); }
    return 0;
}