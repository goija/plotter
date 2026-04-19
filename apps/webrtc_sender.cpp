#include <rtc/rtc.hpp>
#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <cstring>

int main() {
    // We zetten info logs uit om de Offer niet te vervuilen
    rtc::InitLogger(rtc::LogLevel::None); 

    rtc::Configuration config;
    // We gebruiken GEEN servers, puur lokaal.
    config.iceServers = {}; 

    auto pc = std::make_shared<rtc::PeerConnection>(config);
    auto dc = pc->createDataChannel("graycode_stream");

    // Zodra de verbinding echt open is:
    dc->onOpen([]() {
        std::cout << "\n[!!!] VERBONDEN! De grafiek zou nu moeten bewegen.\n" << std::endl;
    });

    // 1. Maak de Offer aan
    pc->setLocalDescription();

    // 2. Wacht heel even en print de Offer
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    auto description = pc->localDescription();
    
    if (description) {
        std::cout << "\n========== KOPIEER DIT (STAP 1) ==========\n";
        std::cout << std::string(*description) << std::endl;
        std::cout << "==========================================\n";
    }

    std::cout << "\nPlak nu de Answer uit de browser, typ 'END' en druk op Enter:\n";

    // 3. Vang het antwoord op
    std::string line, remoteAnswer;
    while (std::getline(std::cin, line)) {
        if (line == "END") break;
        remoteAnswer += line + "\n";
    }

    try {
        pc->setRemoteDescription(rtc::Description(remoteAnswer, "answer"));
        std::cout << "[INFO] Antwoord geaccepteerd. Wachten op verbinding..." << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Fout: " << e.what() << std::endl;
        return 1;
    }

    // 4. Stuur data zodra het kan
    uint32_t val = 0;
    while (true) {
        if (dc->isOpen()) {
            rtc::binary bin(sizeof(val));
            std::memcpy(bin.data(), &val, sizeof(val));
            dc->send(bin);
            val += 5; 
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return 0;
}