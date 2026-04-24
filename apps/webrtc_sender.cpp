#include <rtc/rtc.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <thread>
#include <chrono>
#include <memory>
#include <vector>
#include <cmath>
#include <algorithm>

using json = nlohmann::json;

// =========================================
// MODEL: DE BRUIJN / LYNDON GENERATOR
// =========================================
std::vector<int> generateDeBruijn(int k, int n) {
    std::vector<int> seq;
    std::vector<int> a(n + 1, 0);
    std::function<void(int, int)> fkm = [&](int t, int p) {
        if (t > n) {
            if (n % p == 0) {
                for (int i = 1; i <= p; ++i) seq.push_back(a[i]);
            }
        } else {
            a[t] = a[t - p];
            fkm(t + 1, p);
            for (int j = a[t - p] + 1; j < k; ++j) {
                a[t] = j;
                fkm(t + 1, t);
            }
        }
    };
    fkm(1, 1);
    return seq;
}

// =========================================
// HELUO BITCODE PAYLOAD (Packed voor netwerk)
// =========================================
#pragma pack(push, 1)
struct HeluoPayload {
    float entropy;       // De 'step' waarde
    float anomaly;       // De Gray Code waarde
    float ccw;           // Continuous Color Weight (0.0 - 1.0)
    uint8_t mainNum;     // Luoshu Hoofdgetal
    uint8_t subNum;      // Luoshu Subgetal (uit de Bruijn)
    uint8_t c_index;     // De verstoringstap (0-10)
    uint8_t status;      // 0 = OK, 1 = RED ERROR
};
#pragma pack(pop)

int main() {
    rtc::InitLogger(rtc::LogLevel::Warning);

    // Initialiseer Luoshu en de Bruijn modellen
    std::vector<int> mainPattern = {9, 5, 7, 8, 1, 3, 4, 6, 2};
    auto debruijn_states = generateDeBruijn(3, 3); // Canonieke cyclus

    rtc::Configuration config;
    config.iceServers.emplace_back("stun:stun.l.google.com:19302");

    rtc::WebSocketServerConfiguration wsConfig;
    wsConfig.port = 8081;
    rtc::WebSocketServer wsServer(wsConfig);

    std::cout << "[SERVER] Heluo Qi DataPipe gestart op ws://127.0.0.1:8081..." << std::endl;

    wsServer.onClient([&config, mainPattern, debruijn_states](std::shared_ptr<rtc::WebSocket> ws) {
        std::cout << "[SIGNALING] Client verbonden." << std::endl;

        auto pc = std::make_shared<rtc::PeerConnection>(config);
        auto dc_wrapper = std::make_shared<std::shared_ptr<rtc::DataChannel>>();

        // STAP 1: WebRTC Signalerings Callbacks
        pc->onLocalDescription([ws](rtc::Description description) {
            json desc_msg = {{"type", description.typeString()}, {"sdp", std::string(description)}};
            ws->send(desc_msg.dump());
        });

        pc->onLocalCandidate([ws](rtc::Candidate candidate) {
            json ice_msg = {{"type", "candidate"}, {"candidate", {{"candidate", candidate.candidate()}, {"sdpMid", candidate.mid()}}}};
            ws->send(ice_msg.dump());
        });

        // STAP 2: Berichten van browser afhandelen
        ws->onMessage([ws, pc, dc_wrapper, mainPattern, debruijn_states](std::variant<rtc::binary, rtc::string> data) {
            if (!std::holds_alternative<rtc::string>(data)) return;
            json msg = json::parse(std::get<rtc::string>(data), nullptr, false);
            if (msg.is_discarded()) return;

            std::string type = msg["type"];

            if (type == "join") {
                *dc_wrapper = pc->createDataChannel("heluo-stream");

                (*dc_wrapper)->onOpen([dc_wrapper, mainPattern, debruijn_states]() {
                    std::cout << "[DATACHANNEL] OPEN! Starten Luoshu/Lyndon pipeline..." << std::endl;
                    auto dc = *dc_wrapper;

                    std::thread([dc, mainPattern, debruijn_states]() {
                        uint32_t counter = 0;

                        while (dc && dc->isOpen()) {
                            // Bepaal huidige posities in de cycli
                            size_t patternIdx = (counter / 11) % mainPattern.size();
                            int mainVal = mainPattern[patternIdx];
                            int subVal = debruijn_states[patternIdx % debruijn_states.size()];
                            
                            // 11-staps verstoring (c)
                            int c_step = counter % 11;
                            double c_factor = c_step / 10.0;

                            // Gray code berekening voor anomaly
                            uint32_t gray = c_step ^ (c_step >> 1);

                            // Bereken de Continuous Color Weight (CCW)
                            double noise = std::sin(mainVal + c_factor);
                            float calculated_ccw = static_cast<float>(std::clamp((subVal / 9.0) + (c_factor * noise * 0.1), 0.0, 1.0));

                            // Bouw de binaire payload
                            HeluoPayload payload;
                            payload.entropy = static_cast<float>(c_step);
                            payload.anomaly = static_cast<float>(gray);
                            payload.ccw = calculated_ccw;
                            payload.mainNum = static_cast<uint8_t>(mainVal);
                            payload.subNum = static_cast<uint8_t>(subVal);
                            payload.c_index = static_cast<uint8_t>(c_step);
                            
                            // Operational Error logic (Red reserved)
                            payload.status = (std::isnan(calculated_ccw)) ? 1 : 0;

                            // Verzenden
                            dc->send(reinterpret_cast<const std::byte*>(&payload), sizeof(payload));

                            counter++;
                            std::this_thread::sleep_for(std::chrono::milliseconds(150));
                        }
                    }).detach();
                });

            } else if (type == "answer") {
                pc->setRemoteDescription(rtc::Description(msg["sdp"].get<std::string>(), type));
            } else if (type == "candidate") {
                pc->addRemoteCandidate(rtc::Candidate(msg["candidate"]["candidate"].get<std::string>(), msg["candidate"]["sdpMid"].get<std::string>()));
            }
        });
    });

    while (true) std::this_thread::sleep_for(std::chrono::seconds(1));
    return 0;
}