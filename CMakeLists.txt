# We zetten deze op 3.14 omdat FetchContent vanaf die versie standaard is
cmake_minimum_required(VERSION 3.14)
project(GrayCodePlotter)

# Gebruik de C++17 standaard
set(CMAKE_CXX_STANDARD 17)

# 1. Zoek de WebRTC bibliotheek (die je al geïnstalleerd hebt)
find_package(LibDataChannel REQUIRED)

# 2. Laat CMake de JSON bibliotheek AUTOMATISCH downloaden
include(FetchContent)
FetchContent_Declare(json
    URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
)
FetchContent_MakeAvailable(json)

# Zorg dat de headers gevonden worden
include_directories(apps)

# Bouw de zender vanuit de apps map
add_executable(webrtc_sender apps/webrtc_sender.cpp)

# Link BEIDE bibliotheken aan je programma
target_link_libraries(webrtc_sender PRIVATE LibDataChannel::LibDataChannel nlohmann_json::nlohmann_json)