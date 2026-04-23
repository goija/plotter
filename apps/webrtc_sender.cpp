#include <rtc/rtc.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <thread>
#include <chrono>
#include <memory>

using json = nlohmann::json;

// =========================================
// BITCODE PAYLOAD (Exact 8 bytes in memory)
// =========================================
#pragma pack(push, 1) 
struct AtmosPayload {
    float entropy; // Wordt de normale teller
    float anomaly; // Wordt de Gray Code waarde
};
#pragma pack(pop)

int main() {
    rtc::InitLogger(rtc::LogLevel::Warning); 

    rtc::Configuration config;
    config.iceServers.emplace_back("stun:stun.l.google.com:19302");

    rtc::WebSocketServerConfiguration wsConfig;
    wsConfig.port = 8081;
    rtc::WebSocketServer wsServer(wsConfig);
    
    std::cout << "[SERVER] GrayCodePlotter WebRTC Sender start op ws://127.0.0.1:8081..." << std::endl;

    wsServer.onClient([&config](std::shared_ptr<rtc::WebSocket> ws) {
        std::cout << "[SIGNALING] Nieuwe client verbonden. Wachten op 'join'..." << std::endl;

        auto pc = std::make_shared<rtc::PeerConnection>(config);
        
        // Een slimme pointer wrapper om ons DataChannel later veilig in op te slaan
        auto dc_wrapper = std::make_shared<std::shared_ptr<rtc::DataChannel>>();

        // =========================================
        // STAP 1: ZET DE ANTENNES AAN (Callbacks)
        // =========================================
        pc->onLocalDescription([ws](rtc::Description description) {
            std::cout << "[WEBRTC] Offer gegenereerd! Verzenden naar browser..." << std::endl;
            json desc_msg = {
                {"type", description.typeString()},
                {"sdp", std::string(description)}
            };
            ws->send(desc_msg.dump());
        });

        pc->onLocalCandidate([ws](rtc::Candidate candidate) {
            json ice_msg = {
                {"type", "candidate"},
                {"candidate", {
                    {"candidate", candidate.candidate()},
                    {"sdpMid", candidate.mid()}
                }}
            };
            ws->send(ice_msg.dump());
        });

        // =========================================
        // STAP 2: LUISTEREN NAAR DE BROWSER
        // =========================================
        ws->onMessage([ws, pc, dc_wrapper](std::variant<rtc::binary, rtc::string> data) {
            if (!std::holds_alternative<rtc::string>(data)) return;
            
            json msg = json::parse(std::get<rtc::string>(data), nullptr, false);
            if (msg.is_discarded() || !msg.contains("type")) return;

            std::string type = msg["type"];

            if (type == "join") {
                std::cout << "[WEBRTC] 'Join' ontvangen! Tunnel aanmaken..." << std::endl;

                // STAP 3: NU PAS HET KANAAL MAKEN!
                // Omdat de antennes aanstaan, triggert dit direct en veilig de Offer.
                *dc_wrapper = pc->createDataChannel("atmos-tunnel");

                (*dc_wrapper)->onOpen([dc_wrapper]() {
                    std::cout << "[DATACHANNEL] OPEN! Starten Gray Code stroom..." << std::endl;
                    auto dc = *dc_wrapper; // Haal het kanaal uit de wrapper
                    
                    std::thread([dc]() {
                        uint32_t counter = 0;

                        while (dc && dc->isOpen()) {
                            uint32_t step = counter % 32;
                            uint32_t gray = step ^ (step >> 1); // Bereken de Gray Code

                            AtmosPayload payload;
                            payload.entropy = static_cast<float>(step); 
                            payload.anomaly = static_cast<float>(gray); 

                            // Stuur de binaire payload naar de browser
                            dc->send(reinterpret_cast<const std::byte*>(&payload), sizeof(payload));

                            counter++;
                            std::this_thread::sleep_for(std::chrono::milliseconds(200)); 
                        }
                        std::cout << "[DATACHANNEL] Gesloten. Stroom gestopt." << std::endl;
                    }).detach();
                });

            } else if (type == "answer") {
                std::cout << "[WEBRTC] Answer ontvangen van browser! Connectie opbouwen..." << std::endl;
                rtc::Description desc(msg["sdp"].get<std::string>(), type);
                pc->setRemoteDescription(desc);
            } else if (type == "candidate") {
                rtc::Candidate cand(msg["candidate"]["candidate"].get<std::string>(), msg["candidate"]["sdpMid"].get<std::string>());
                pc->addRemoteCandidate(cand);
            }
        });
    });

    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    return 0;
}