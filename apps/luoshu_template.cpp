#include "rtc/rtc.hpp"
#include <iostream>
#include <nlohmann/json.hpp> // Voor data-format

using namespace std;
using json = nlohmann::json;

int main() {
    // 1. Initialiseer WebRTC configuratie
    rtc::Configuration config;
    config.iceServers.emplace_back("stun:stun.l.google.com:19302");

    // 2. Maak de PeerConnection aan
    auto pc = make_shared<rtc::PeerConnection>(config);

    // 3. Maak het DataChannel voor de "Sheaf Stream"
    auto dc = pc->createDataChannel("sheaf-locality-stream");

    dc->onOpen([&]() {
        cout << "[SYSTEM] DataChannel geopend. Starten van chirale stream..." << endl;
        
        // Simuleer de deeltjesstroom tussen Greenwich en Laren
        double delta_t = 208.0; 
        json data = {{"location", "Laren"}, {"delta_t", delta_t}, {"chiral_sync", true}};
        
        dc->send(data.dump());
    });

    dc->onMessage([](rtc::message_variant data) {
        if (holds_alternative<string>(data))
            cout << "[INCOMING] " << get<string>(data) << endl;
    });

    // 4. Signaling (Signaling moet handmatig of via een kleine WebSocket server)
    // Hier zou de code komen om de Offer/Answer te genereren, zoals in je HTML module.
    
    return 0;
}