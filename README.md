# Lotus // Universal Media Scrobbler

A high-precision, lightweight, standalone utility for casting media playback metadata to Last.fm and ListenBrainz. Built for power users who demand reliability, security, and zero bloat. Includes a HD-skinnable GUI with a matrix visualizer and live track marquee.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Core Features

* **MPC-HC Precision:** Directly interfaces with your MPC-HC web server for perfect, sub-second metadata accuracy. This does not use WSMT, opting for full MPC integration.
* **Universal SMTC Fallback:** When your player is not MPC, Lotus pivots to the native Windows System Media Transport Controls. It automatically scrobbles from browsers, Spotify, foobar2000, and any other media source without additional plugins or configuration.
* **Automated Cache Resilience:** If your internet connection drops, Lotus caches all playback data locally in a secure SQLite database and automatically syncs it once the connection is restored.
* **Dynamic Visualizer:** The UI features a real-time, matrix-style visualizer that reacts to playback state and theme shifts.
* **Low-Impact Design:** Operates as a transparent background process with zero registry footprint, no startup folders, and minimal CPU/RAM overhead.

## Security & Privacy Architecture

Lotus is engineered for maximum security through strict isolation and local-only processing.

* **Local-Only Interception:** All communication with your local media player is strictly restricted to the 127.0.0.1 loopback interface. No external network traffic ever touches your media player's internal interface.
* **Zero-Exposed Ports:** The application does not broadcast to your local network. It binds exclusively to the loopback address; no malicious scripts or local-network actors can hijack your session or poll your playback status.
* **Encrypted Transmission:** Every payload sent to external APIs (Last.fm and ListenBrainz) is processed via TLS/HTTPS. Your API tokens and session keys remain encrypted in transit.
* **Zero Registry Footprint:** Lotus is fully portable. It does not write to the Windows Registry, install background services, or hide processes in your startup folder. It lives only in the directory where you place it. It has a one running instance rule.

## Quick Setup

### 1. MPC-HC Configuration
* Open MPC-HC -> View -> Options -> Player -> Web Interface.
* Enable "Listen on port 13579" and check "Allow access from localhost only".

### 2. Authentication
* Run `lotus.exe`.
* Input your API credentials. Use the provided UI tools to link your accounts securely via browser handshake.
* Click [ COMM_SAVE ] to store your configuration locally.

### 3. Operation
* The background monitor starts immediately. It will detect your media playback automatically.
* If you switch to a browser or other media player, Lotus seamlessly pivots to OS-level tracking.

## Security Verification

To verify the integrity of the downloaded `Lotus.7z`, run the following in PowerShell:
```bash
Get-FileHash -Path "Lotus.7z" -Algorithm SHA256
```

Lotus.7z:
`B620569AB1D3DAE6F8CBC18E291C9EB1EF17AC67AE869369700C5FC399D853D7`

lotus.exe:
`E04B183A6F4E8B49648C3F75521E17A1496733FA111B45CB9A5DBC616F3E3ACD`

## Compilation From Source

Building `lotus.exe` locally requires an exact file structure. If the source file, icon, or assets are missing from the root, the compilation will fail.

### Prerequisites
Install the required dependencies:
```bash
pip install pyinstaller
pip install -r requirements.txt
```

### Required Directory Structure
You must have `lotus.py`, `icon.ico`, and the `assets/` folder in the same root directory before running the build command:
```text
[Root Directory]/
├── lotus.py
├── icon.ico
├── requirements.txt
└── assets/
    └── MPCLotus.png
```

### Build Command

Open your terminal in the root directory and execute:
```bash
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." --add-data "assets/MPCLotus.png;assets" lotus.py
```

The resulting `lotus.exe` will be generated inside the newly created `/dist` folder.

## Customization

* **Modular Assets:** Place any `.png` file in the `assets` folder to customize the interface. For best results, use HD dimensions.
* **Dynamic Scaling:** Assets are rendered to match your display resolution automatically.
* **Theme Shuffle:** Cycle through skins in-app via the UI.

## Roadmap & Platform Compatibility

### Roadmap
* **Multi-Format Caching:** Expand SQL storage to handle high-volume offline session logging.
* **Auto-Update Mechanism:** Implementation of a silent check-for-updates service.
* **Extended Player Support:** Direct API integration for additional local media players.

### Why Lotus?
Lotus was developed to provide a reliable, aesthetically pleasing scrobbling solution for Media Player Classic, specifically optimized for high-resolution displays like homelab television setups. It transforms a passive listening session into a curated data feed, ensuring your playback history is captured with precision while you focus entirely on the enjoyment of your media.

### Platform Compatibility & Security Expectations
Lotus is currently built specifically for the Windows environment, leveraging native Windows APIs for universal media tracking. I made an attempt to have the Windows version as secure as possible before V1 hit GitHub. If you plan to release Linux and Apple versions, I ask that you please keep code contributions security-forward. Porting to Linux or macOS requires replacing the Windows-specific System Media Transport Controls (SMTC) module with platform-native alternatives (e.g., MPRIS for Linux). If you are a developer interested in contributing a security-focused tracking module for these platforms, pull requests are welcome.

## Requirements & Disclaimer

* **Requirements:** Python 3.11+
* **Disclaimer:** Background assets are fan-created artwork and belong to their respective copyright holders. This software is provided for personal, non-commercial use. Any skinning or theming is fully up to the end-user; I am not responsible for the skins and themes used by end-users.

## Support & Contact

* **Inquiries & Security:** cannibox.bsky@gmail.com
* **Donations:** https://ko-fi.com/k4hlu4
* **Alternative Donations:** If you have alternative donations other than fiat currency, feel free to send an email beforehand.
```text
                ░█▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                     ▓░   
                      ▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                    ▒▒   
                    ▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                   ░▓   
                   █▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                    ▓   
                    ▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒▒░                   ▓   
░                     ▓▓▒▒▒▒▒▒▒▒▒▒▒▒░    ▒▒▒▒▒            ░▒      ▓░  
░                      ▒▓▒▒▒▒▒▒▒▒▒▒░░     ░▒▒▒            ▒  ░    ▓▓░░
              ▒▒▒▒░     ▒█▒▒▒▒▒▒▒▒▒░░       ▒▒            ▓   ░   ░ ▓ 
          ▒▓▒▒▒▒▒▒▓      ▓█▒▒▒▒▒▒▒░  ░       ░            ▓    ▒ ░   ▒
       ▒▓▒▒▒▒▒▒▒▒▒▓▒      ▓▓▒▒▒▒▒▒   ▒                    ▒█▓░   ▒▓   
     ░▓▒▒▒▓▓▓▓▓▓▓▓▓▓       █▓▒▒▒▒░   ▒                  █▓▒▓▓   ░   
    ▒▒▓▓▓▓▒░░     ░░       ▒▓▒▒▒░   ░▓                  ▓▓▓▓▓▓▓▒     
   ▓▓▒░                    ▓▓▒▒░   ▒▓▒                ▓▒    ░▓▓▓     
  ░                        ▓▓▒▒   ▒▒██░              ▓▒         ░   
                           ▓▓▒░  ▒▒▓█▒▒             ▓▒               
       ░░░                 ▒▓▒ ░▒▒▒▓░ ▒          ▒▓░   ░░░         
   ▒██████████▓░           ░▓░▒▒▒▒▓▓  ▒        ░▓▒░▓█████████▓░     
 ▒█████▓▓████████▒         ▒▓▒▒▒▒▓▓   ▒      ░▓▓▓███████▓▓▓█████▒   
██▓  ▒     ▓███████▒       ▒▓▒▒▒▓▓    ░    ▒▓▒▓███████▒     ▒  ▓██░ 
▓    ░    ░▓█▓▓▓▒  ░▓      ▒▓▒▓█▒    ▒   ▒░ ░████▓▓         ▒    ▓█▓
     ░    ░██▓▒      ▓      ▓▓▓█      ▓░▒   ▒▓██▓▓░          ▒     ██
           ██▓▒      █░      ▓▓       ░░     ▒█▓▓▓░    ▒      ▒     ▓ 
▓    ░     ░   ▓▓▓▓▓█▒               ▓▓   ░▓▓▓█▒     ▒    ▒  
 ░   ░     ░▒░▓▓▓▓▓▓█▓               ██▓▓▓▓▓▓█▓      ▒       
     ▒      ▒█▓▓▓▓▓▓██               ░██▓▓▓▓▓▓█░             
      ▒      ░█▓▓▓▓█▓▒               ▒▒▓█▓▓▓▓▓       ░       
       ░        ▒▒▒                 ▒   ▒▒▒        ░         
      ░█░                                              ▒▓         
         ░▒░       ░░                         ░░      ░▒▒            
                                                                     
                                                                     
                                                                     
                      ▓▓▓▓▒▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                        
                     ▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓░                       
                      ▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓                        
   ██▓                ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒               ░██▓     
    ▒██                ▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒                ██▒
    ```
