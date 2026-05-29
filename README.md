<img width="800" height="544" alt="LotusDemo" src="https://github.com/user-attachments/assets/b80524c4-5f5d-44b8-99ab-6a8c7c184ed0" />

# Lotus // Universal Media Telemetry Core

A high-precision, lightweight, standalone utility for casting media playback metadata to Last.fm, ListenBrainz, and Trakt. Built for power users who demand reliability, security, and zero bloat. Includes an HD-skinnable GUI with a matrix visualizer, live track marquee, and unobtrusive system tray integration.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Core Features

* **Triple-Stream Sync Engine:** Simultaneously broadcasts your music and video consumption to Last.fm, ListenBrainz, and Trakt through a unified, heavily optimized background queue.
* **MPC-HC Precision:** Directly interfaces with your MPC-HC web server for perfect, sub-second metadata accuracy. This does not use WSMT, opting for full MPC integration and accurate video/movie file parsing.
* **Universal SMTC Fallback:** When your player is not MPC, Lotus pivots to the native Windows System Media Transport Controls. It automatically scrobbles from browsers, Spotify, foobar2000, and any other media source without additional plugins or configuration.
* **Automated Cache Resilience:** If your internet connection drops, Lotus caches all playback data locally in a secure SQLite database and automatically syncs it once the connection is restored.
* **Dynamic Visualizer & System Tray:** The UI features a real-time, Pillow-rendered matrix visualizer that reacts to playback state and theme shifts. The application can be minimized to the system tray for a completely invisible background footprint.
* **Low-Impact Design:** Operates as a transparent background process with zero registry footprint, no startup folders, and minimal CPU/RAM overhead.

## Security & Privacy Architecture

Lotus is engineered for maximum security through strict isolation, local-only processing, and credential obfuscation.

* **Local Configuration Obfuscation:** API keys and session tokens are obfuscated in the local mpcscrobbler_config.ini file using a specialized cipher to prevent casual exposure and credential scraping.
* **Local-Only Interception:** All communication with your local media player is strictly restricted to the 127.0.0.1 loopback interface. No external network traffic ever touches your media player's internal interface.
* **Zero-Exposed Ports:** The application does not broadcast to your local network. It binds exclusively to the loopback address; no malicious scripts or local-network actors can hijack your session or poll your playback status.
* **Encrypted Transmission:** Every payload sent to external APIs is processed via TLS/HTTPS. Your encrypted tokens remain secure in transit.
* **Zero Registry Footprint:** Lotus is fully portable. It does not write to the Windows Registry, install background services, or hide processes in your startup folder. It lives only in the directory where you place it and enforces a one-running-instance rule.

## Quick Setup

### 1. MPC-HC Configuration
* Open MPC-HC -> View -> Options -> Player -> Web Interface.
* Enable "Listen on port 13579" and check "Allow access from localhost only".

### 2. Authentication
* Run `lotus.exe`.
* Use the provided UI tools to securely link your accounts via browser handshakes (Last.fm, ListenBrainz, and the Trakt PIN-override matrix).
* Click [ COMM_SAVE ] to generate your obfuscated configuration locally.

### 3. Operation
* The background monitor starts immediately. It will detect your media playback automatically.
* If you switch to a browser or other media player, Lotus seamlessly pivots to OS-level tracking.
* Close the window to minimize Lotus directly to your system tray.

## Security Verification

To verify the integrity of the `Lotus.7z` of a downloaded Release, open a Powershell terminal in the same directory that it saved to and then run the first line below of the following code:
```bash
Get-FileHash -Path "Lotus.7z" -Algorithm SHA256
Get-FileHash -Path "lotus.exe" -Algorithm SHA256
```

Verify the .exe in the extracted Lotus folder through the Powershell terminal with the second line above:
`1E7EC6034BF183312A4C6D67D64A28D38B9B295444DF8D7EBDBA3F7025517B24`
`89029E2F288E2C9B8AFBC4DE459A92731C097B7CED3553ECC225838AA25D45F8`

## Compilation From Source

Building `lotus.exe` locally requires an exact file structure. If the source file, icon, or assets are missing from the root, the compilation will fail.

### Prerequisites
Install the required dependencies defined in the 1.1.0 architecture:
```bash
pip install pyinstaller
pip install -r requirements.txt
```

### Required Directory Structure
You must have `lotus.py`, `icon.ico`, the template `mpcscrobbler_config.ini`, and the `assets/` folder in the same root directory before running the build command:
```text
Lotus_1.1.0_Source/
├── lotus.py
├── icon.ico
├── requirements.txt
├── mpcscrobbler_config.ini
└── assets/
    └── MPCLotus.png
```

### Build Command

Open your terminal in the root directory and execute:
```bash
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." --add-data "assets;assets" lotus.py
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
Lotus was developed to provide a reliable, aesthetically pleasing telemetry solution for Media Player Classic, specifically optimized for high-resolution displays like homelab television setups. It transforms a passive listening or viewing session into a curated data feed, ensuring your playback history is captured with precision while you focus entirely on the enjoyment of your media.

### Windows Compatibility
Lotus requires Windows 10 or Windows 11. The application relies on the Windows SDK to hook into the System Media Transport Controls for OS-level playback tracking. Older operating systems like Windows 7 and Windows 8 lack this native architecture; they will fail to execute the telemetry fallback. The graphical interface utilizes Desktop Window Manager injection for native dark mode rendering. Do not attempt to run this software on legacy systems.

### Platform Compatibility & Security Expectations
Lotus is currently built specifically for the Windows environment, leveraging native Windows APIs for universal media tracking. I made an attempt to have the Windows version as secure as possible before V1.1.0 hit GitHub. If you plan to release Linux and Apple versions, I ask that you please keep code contributions security-forward. Porting to Linux or macOS requires replacing the Windows-specific System Media Transport Controls (SMTC) module with platform-native alternatives (e.g., MPRIS for Linux). If you are a developer interested in contributing a security-focused tracking module for these platforms, pull requests are welcome.

## Requirements & Disclaimer

* **Requirements:** Python 3.11+
* **Disclaimer:** Background assets are fan-created artwork and belong to their respective copyright holders. This software is provided for personal, non-commercial use. Any skinning or theming is fully up to the end-user; Kahlua is not responsible for the skins and themes used by end-users, futhermore the only skin provided is the one that fits the matrix rain theme, you'll have to drop your own skins in.

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
