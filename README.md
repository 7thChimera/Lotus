Lotus // Universal Media Scrobbler
A high-precision, lightweight, standalone utility for casting media playback metadata to Last.fm and ListenBrainz. Built for power users who demand reliability, security, and zero bloat. Includes a HD-skinnable GUI with a matrix visualizer and live track marquee.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ CORE FEATURES
MPC-HC Precision
Directly interfaces with your MPC-HC web server for perfect, sub-second metadata accuracy. This does not use WSMT, opting for full MPC integration.

Universal SMTC Fallback
When your player is not MPC, Lotus pivots to the native Windows System Media Transport Controls. It automatically scrobbles from browsers, Spotify, foobar2000, and any other media source without additional plugins or configuration.

Automated Cache Resilience
If your internet connection drops, Lotus caches all playback data locally in a secure SQLite database and automatically syncs it once the connection is restored.

Dynamic Visualizer
The UI features a real-time, matrix-style visualizer that reacts to playback state and theme shifts.

Low-Impact Design
Operates as a transparent background process with zero registry footprint, no startup folders, and minimal CPU/RAM overhead.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ SECURITY & PRIVACY ARCHITECTURE
Lotus is engineered for maximum security through strict isolation and local-only processing.

Local-Only Interception
All communication with your local media player is strictly restricted to the 127.0.0.1 loopback interface. No external network traffic ever touches your media player’s internal interface.

Zero-Exposed Ports
The application does not broadcast to your local network. It binds exclusively to the loopback address, ensuring no malicious scripts or local-network actors can hijack your session or poll your playback status.

Encrypted Transmission
Every payload sent to external APIs (Last.fm and ListenBrainz) is processed via TLS/HTTPS. Your API tokens and session keys remain encrypted in transit.

Zero Registry Footprint
Lotus is fully portable. It does not write to the Windows Registry, install background services, or hide processes in your startup folder. It lives only in the directory where you place it. It has a one running instance rule.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ QUICK SETUP
1. MPC-HC Configuration

Open MPC-HC -> View -> Options -> Player -> Web Interface.

Enable "Listen on port 13579" and check "Allow access from localhost only".

2. Authentication

Run Lotus.exe.

Input your API credentials. Use the provided UI tools to link your accounts securely via browser handshake.

Click [ COMM_SAVE ] to store your configuration locally.

3. Operation

The background monitor starts immediately. It will detect your media playback automatically.

If you switch to a browser or other media player, Lotus seamlessly pivots to OS-level tracking.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ SECURITY VERIFICATION
To verify the integrity of the downloaded Lotus.exe, run the following in PowerShell:

Get-FileHash -Path "Lotus.exe" -Algorithm SHA256

The result must match:
D12CB23730319C2208B35E9266CEABA7064D1503806F7F202DFBDEE0CADD270B

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ CUSTOMIZATION
Modular Assets: Place any .png file in the assets folder to customize the interface. For best results, use HD dimensions.

Dynamic Scaling: Assets are rendered to match your display resolution automatically.

Theme Shuffle: Cycle through skins in-app via the UI.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ ROADMAP & PLATFORM COMPATIBILITY
Roadmap

Multi-Format Caching: Expand SQL storage to handle high-volume offline session logging.

Auto-Update Mechanism: Implementation of a silent check-for-updates service.

Extended Player Support: Direct API integration for additional local media players.

Why Lotus?
Lotus was developed to provide a reliable, aesthetically pleasing scrobbling solution for Media Player Classic, specifically optimized for high-resolution displays like homelab television setups. Rather than functioning as a standard administrative tool, Lotus enhances your media consumption by automating the social metadata casting process. It transforms a passive listening session into a curated data feed, ensuring your playback history is captured with precision while you focus entirely on the enjoyment of your media.

Platform Compatibility & Security Expectations
Lotus is currently built specifically for the Windows environment, leveraging native Windows APIs for universal media tracking. I made an attempt to have the Windows version as secure as possible before V1 hit GitHub. If you plan to release Linux and Apple versions, I ask that you please keep code contributions security-forward. Porting to Linux or macOS requires replacing the Windows-specific System Media Transport Controls (SMTC) module with platform-native alternatives (e.g., MPRIS for Linux). If you are a developer interested in contributing a security-focused tracking module for these platforms, pull requests are welcome.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ REQUIREMENTS & DISCLAIMER
Requirements: Python 3.11+ | pip install -r requirements.txt

Disclaimer: Background assets are fan-created artwork and belong to their respective copyright holders. This software is provided for personal, non-commercial use. Any skinning or theming is fully up to the end-user; I am not responsible for the skins and themes used by end-users.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◈ SUPPORT & CONTACT
Inquiries & Security:
For bug reports or security disclosures, contact: cannibox.bsky@gmail.com

Donations:
Donations are appreciated but never required. They go directly towards development costs and maintaining equipment for event setups. If you make core contributions to the project, such as porting to Linux or macOS, please contact me via email to discuss donation sharing.

https://ko-fi.com/k4hlu4

I'll also accept cryptocurrency donations, but send an e-mail regarding that.

░█▓▓▓███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░   Kahlua                ░    ▓█     
                            ▓▓▓░  █▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░                              ░█▒     
                                ░▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░                              █▓     
                               ▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                              ▓█     
                             ░█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░                             ▓█░   
                            ▓█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒▒▒▒▒▒▒▒▒▒▒▒▒                             ▒█░   
                              ▓█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   ░▒▒▒▒▒▒▒▒▒▒                             ░█░   
                               ▒█▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒     ░▒▒▒▒▒▒▒▒░                            ░█▒   
 ▒                               ▓█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░▒░░      ░▒▒▒▒▒▒░                 ░█▓        ░█▓   
▓                                 ▒██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░        ▒▒▒▒▒▒                 ▒▒ ▓▒      ░██▓   
░                                   ██▓▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░         ░▒▒▒▒                 ▓▒  ░▓     ░█▒▒▓▒▓
                      ▒▓▓▓▓▓▓░        ██▓▒▒▒▒▒▒▒▒▒▒▒▒░ ░░░         ░▒▒▒                 ▓▒    ▓    ░▓  ▓▒ 
                ░▓▓▓▓▒▒▒▒▒▒▒▓         ██▓▒▒▒▒▒▒▒▒▒▒▒░   ░          ░▒▒                 █░     ▒   ▒▓   ▓ 
             ░▓▓▓▒▒▒▒▒▒▒▒▒▒▒▓░         ██▒▒▒▒▒▒▒▒▒▒▒░   ░░          ▒░                ▒█░      ▓  ▓░    ▓
           ▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒         ░█▓▒▒▒▒▒▒▒▒▒▒    ░▒                            ▓█▓▓      ▓▓▓     
         ▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓          ▓█▓▒▒▒▒▒▒▒▒░    ░▒                           ▒█▓▒▒▓▓     ▓▒     
        ▓▒▒▒▒▒▒▓▓▓▓▓███████▓▓▓           █▓▒▒▒▒▒▒▒░     ▒▒                          ░██▓▒▒▒▒▓▓   ▒       
      ▒▒▒▒▓▓▓███▓▒░░       ░░▒           ▒█▓▒▒▒▒▒░     ░▒▓                          ▓█████▓▒▒▒▓░         
     ▓▓▓▓██▓░                             █▓▒▒▒▒▒░     ▒▓█░                        ▓█▒   ▒▓██▓▓▓▒       
   ░███▓░                                 ▓█▓▒▒▒▒     ▒▒▓█▓                       ▓█▒        ▒▓██▓       
  ▒▓▒                                     ▒█▓▒▒▒▒    ▒▒▒▓██▒                     ▓█▒            ░▒▓     
                                          ░█▓▒▒▒░   ▒▒▒▒▓██▓                    ▓█▒                     
                                           █▓▒▒▒   ▒▒▒▒▒█▓░█                  ░▓█                       
                                           ▓█▒▒   ▒▒▒▒▒▓▓  █░                ▓█▓                         
        ░▓███████▓▓░                       ▓▓▓  ░▒▒▒▒▒▓█▒  █░              ▒█▓░  ░▒▓████████▒░           
     ▓████████████████▓░                   ▓█▒ ▒▒▒▒▒▒▒██   █░            ░▓█▒ ░█████████████████▒       
  ░▓█████████████████████▒                 ▓█▒▒▒▒▒▒▒▒▓█    █           ░▓█▒▒▓█████████████████████▓     
░▓███████▓▒░░░░▒▒▓█████████▓               ▓█▒▒▒▒▒▒▒██     █         ░▓█▒▒██████████▓▒▒░░░░▒▓███████▓   
████▒  ▓▒        ▒██▓████████▓             ▓█▒▒▒▒▒▓██      ▓       ▒█▓▒▒█████████▓██░        ▓   ▓████▒ 
██░    ▓░       ░▓█▓▓█▓▓▓██████░           █▓▒▒▒▒▓██      ▒▒     ▒█▒  ▒█████▓▓▓▓▓▓▓█▒        ▒░    ▓████░
░      ▓        ░██▓▓▓▓▓░     ░█▓          █▓▒▒▒██▒       ▓░  ░▓▓░  ░█████▓▓█▓░              ▒▒      ████
       ▓        ▒██▓▓▓▓        ▒█▓        ░█▓▒▓█▓         ▒ ▒▓▓    ▒▓███▓▓▓▓▓                ▒▒       ██▓
       ▓        ░██▓▓▓         █          ▒▓▓██░         ▓█▓         ▒██▓▓▓▓▒                ▒▒      ▒██ 
▓      ▓        ░███▓▓▒      ▒▓█▓         ▓▓█░                       ██▓▓▓▒▓▓      ▓▓        ░▒      ██ 
█      ▓         ▓    ▒▓▓▓▓▓▓▓▓██         ▒                         ░██▓     ▓▓▓▓▓██▒        ▒▒     ▓█ 
 ▓     ▓░        ░    ▒▓▓▓▓▓▓▓▓██                                   ▓█▓▓░   ▒▓▓▓▓▓██         ▓     ░▓   
  ▒    ░▒         ▓██▓▓▓▓▓▓▓▓▓▓██▒                                  ██▓▓▓▓▓▓▓▓▓▓▓██▒         █     ▒   
   ░    ▓         ░██▓▓▓▓▓▓▓▓▓▓██▓                                  ██▓▓▓▓▓▓▓▓▓▓▓█▓         ░▓         
    ░   ░▒         ░██▓▓▓▓▓▓▓▓▓██▓                                 ░███▓▓▓▓▓▓▓▓▓█▓          ▓           
     ░   ▓           ▓█▓▓▓▓▓▓██░░▓                                 ░▒░▓█▓▓▓▓▓▓▓█▒          ▒░  ░       
       ░  ▓            ▓█████▒   ▓                                 ▒▒   ▓█████▒           ░▓  ░         
        ▒░▒▓                     ░                                 ░░                    ░▓░░           
          ▒█▓                                                                           ░█▓░           
             ▒▓░               ░░                                   ░░░              ░▒▒░               
                  ░▒▒▒▒▒░░                                                  ░░▒▒▒▒░                     
                                                                  ░                                     
                                  ▒                                                                     
                                                                   ░                                     
                                                                                                       
                                 ░ ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒ ▒                                   
                                ▒██▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓██                                   
                                ▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█                                   
                                ▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█                                   
                                 ▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒                                   
    ████▓                        ░▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓                        ░▓███▓       
     ▓████▓                       ▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓░                       █████░       
       ███▓                        ▒█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓                        ░███▓