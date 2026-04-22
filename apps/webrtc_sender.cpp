#include <rtc/rtc.hpp>
#include "nlohmann/json.hpp"
#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

using json = nlohmann::json;

int main() {
    // 1. WebRTC Configuratie
    rtc::Configuration config;
    config.iceServers.emplace_back("stun:stun.l.google.com:19302");

    // 2. WebSocket Signaling Server Configuratie op poort 8081
    rtc::WebSocketServer::Configuration serverConfig;
    serverConfig.port = 8081; 
    serverConfig.bindAddress = "127.0.0.1";

    auto signaling_server = std::make_shared<rtc::WebSocketServer>(serverConfig);

    std::cout << "=================================================" << std::endl;
    std::cout << ">>> WEATHATMOS WEBRTC SENDER ACTIEF OP 8081   <<<" << std::endl;
    std::cout << ">>> Wachten tot interface verbindt...         <<<" << std::endl;
    std::cout << "=================================================" << std::endl;

    signaling_server->onClient([&config](std::shared_ptr<rtc::WebSocket> ws) {
        std::cout << ">>> [SIGNALING] Browser probeert te verbinden..." << std::endl;

        auto pc = std::make_shared<rtc::PeerConnection>(config);
        auto dc = pc->createDataChannel("sensor_data");

        dc->onOpen([dc]() {
            std::cout << "✅ [WEBRTC] DataChannel geopend! Luisteren naar Python (UDP 5005)..." << std::endl;
            
            std::thread([dc]() {
                int sockfd;
                struct sockaddr_in servaddr, cliaddr;
                sockfd = socket(AF_INET, SOCK_DGRAM, 0);
                servaddr.sin_family = AF_INET;
                servaddr.sin_addr.s_addr = INADDR_ANY;
                servaddr.sin_port = htons(5005); 
                
                if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
                    std::cerr << "❌ UDP Bind fout op poort 5005" << std::endl;
                    return;
                }
                
                char buffer[2048];
                while (dc->isOpen()) {
                    socklen_t len = sizeof(cliaddr);
                    int n = recvfrom(sockfd, (char *)buffer, 2048, MSG_WAITALL, (struct sockaddr *) &cliaddr, &len);
                    if (n > 0) {
                        buffer[n] = '\0';
                        dc->send(std::string(buffer));
                    }
                }
                close(sockfd);
            }).detach();
        });

        pc->onLocalCandidate([ws](rtc::Candidate candidate) {
            json msg = {{"type", "candidate"}, {"candidate", candidate.candidate()}, {"mid", candidate.mid()}};
            ws->send(msg.dump());
        });

        pc->onLocalDescription([ws](rtc::Description description) {
            json msg = {{"type", description.typeString()}, {"sdp", std::string(description)}};
            ws->send(msg.dump());
        });

        ws->onMessage([pc](std::variant<rtc::binary, rtc::string> message) {
            if (std::holds_alternative<rtc::string>(message)) {
                try {
                    json msg = json::parse(std::get<rtc::string>(message));
                    std::string type = msg["type"].get<std::string>();
                    
                    if (type == "offer" || type == "answer") {
                        pc->setRemoteDescription(rtc::Description(msg["sdp"].get<std::string>(), type));
                    } else if (type == "candidate") {
                        // Cruciaal: Alleen toevoegen als de remote description al bekend is
                        if (pc->remoteDescription().has_value()) {
                            pc->addRemoteCandidate(rtc::Candidate(msg["candidate"].get<std::string>(), msg["mid"].get<std::string>()));
                        }
                    }
                } catch (const std::exception &e) {
                    std::cerr << "❌ Fout: " << e.what() << std::endl;
                }
            }
        });
    });

    while (true) { std::this_thread::sleep_for(std::chrono::seconds(1)); }
    return 0;
}