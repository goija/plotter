cmake_minimum_required(VERSION 3.10)
project(GrayCodePlotter)

# Zoek de bibliotheek die we net hebben geïnstalleerd
find_package(LibDataChannel REQUIRED)

# Zorg dat de headers gevonden worden
include_directories(apps)

# Bouw de zender
add_executable(webrtc_sender apps/webrtc_sender.cpp)

# Link de WebRTC bibliotheek aan je programma
target_link_libraries(webrtc_sender LibDataChannel::LibDataChannel)
