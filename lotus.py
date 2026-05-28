# ==============================================================================
# APPLICATION: Lotus, Standalone Universal Media Telemetry Core
# CORE AUTHOR: Kahlua Dingo
# SYSTEM ARCHITECT: Kahlua Dingo
# INITIAL RELEASE: May 2026
# BUILD VERSION: 1.1.0
# ARCHITECTURE: Triple-Stream Sync Engine [LastFM/ListenBrainz/Trakt]
# ==============================================================================

import os
import sys
import shutil
import traceback
import time
import re
import hashlib
import threading
import random
import math
import base64
import configparser
import json
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
import socket
import asyncio
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
from mutagen import File as MutagenFile
import pystray

try:
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
except ImportError:
    GlobalSystemMediaTransportControlsSessionManager = None

BUILD_VERSION = "1.1.0"

if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(sys.executable)
    MEIPASS_DIR = sys._MEIPASS
else:
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))
    MEIPASS_DIR = EXE_DIR

ROOT_FOLDER = EXE_DIR
ASSETS_FOLDER = os.path.join(ROOT_FOLDER, "assets")

os.makedirs(ASSETS_FOLDER, exist_ok=True)

CONFIG_FILE = os.path.join(ROOT_FOLDER, "mpcscrobbler_config.ini")
DB_FILE = os.path.join(ROOT_FOLDER, "scrobble_cache.db")
ICON_FILE = os.path.join(ROOT_FOLDER, "icon.ico")

def get_log_path():
    return os.path.join(ROOT_FOLDER, "debug_log.txt")

LOG_FILE = get_log_path()

if sys.stdout is None or getattr(sys, 'frozen', False):
    try:
        log_stream = open(LOG_FILE, "a", encoding="utf-8", buffering=0)
        sys.stdout = log_stream
        sys.stderr = log_stream
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [BUILD: {BUILD_VERSION}] LOGGER: System initialized.")
    except Exception:
        pass

def write_debug_log(error_context, exception_obj):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    raw_error = str(exception_obj)
    raw_error = re.sub(r'([a-zA-Z0-9]{32,})', '[REDACTED_TOKEN]', raw_error)
    
    error_msg = f"[{timestamp}] [BUILD: {BUILD_VERSION}] [{error_context}]\n"
    error_msg += f"EXCEPTION: {raw_error}\n"
    error_msg += f"{traceback.format_exc()}\n"
    error_msg += "="*80 + "\n"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_msg)
            f.flush()
    except Exception:
        pass

def extract_bundled_assets():
    if not getattr(sys, 'frozen', False):
        return
        
    search_dirs = [MEIPASS_DIR, os.path.join(MEIPASS_DIR, "assets")]
    
    for s_dir in search_dirs:
        if os.path.exists(s_dir):
            for filename in os.listdir(s_dir):
                source_path = os.path.join(s_dir, filename)
                if os.path.isfile(source_path):
                    if filename.lower().endswith('.png'):
                        target_path = os.path.join(ASSETS_FOLDER, filename)
                        if not os.path.exists(target_path):
                            try:
                                shutil.copy(source_path, target_path)
                            except Exception as e:
                                write_debug_log(f"PNG_EXTRACTION_ERROR_{filename}", e)
                    elif filename.lower() == "icon.ico":
                        target_path = os.path.join(ROOT_FOLDER, filename)
                        if not os.path.exists(target_path):
                            try:
                                shutil.copy(source_path, target_path)
                            except Exception as e:
                                write_debug_log("ICON_EXTRACTION_ERROR", e)

extract_bundled_assets()
DARK_TITLE_COLOR = "#0A0A0A"

class LotusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lotus // Universal Media Scrobbler")
        
        write_debug_log("SESSION_START", "Application initialized.")
        
        if os.path.exists(ICON_FILE):
            try:
                self.root.iconbitmap(ICON_FILE)
            except Exception as icon_err:
                write_debug_log("WINDOW_ICON_INITIALIZATION", icon_err)
        
        self.matrix_theme = "green" 
        self.color_green_neon = "#00FF33"
        self.color_blue_neon = "#00B4FF"
        self.color_red_neon = "#FF3333"
        self.color_yellow_neon = "#FFFF33"
        
        self.bg_color = "#000000"       
        self.text_color = self.color_green_neon     
        self.entry_bg = "#0A0A0A"       
        self.font_main = ("Consolas", 10, "bold")
        
        self.is_running = False
        self.monitor_thread = None
        self.auth_token = None
        self.tray_instance = None
        
        self.tray_command_queue = None 
        self.is_minimizing = False 
        
        self.raw_artist = ""
        self.raw_track = ""
        self.stream_active = False
        self.diagnostic_mode = False
        self.last_parsed_media = "AWAITING..."
        
        self.current_track_uid = None
        self.track_start_time = 0
        self.scrobble_submitted = False
        self.current_active_weight = 0
        
        self.marquee_text = ""
        self.marquee_display_width = 30  
        self.marquee_index = 0
        self.current_display_track = ""

        self.last_w = 0
        self.last_h = 0
        self.is_resizing = False
        self.resize_after_id = None
        self.win_width = 700
        self.win_height = 450
        
        self.matrix_speed_multiplier = 1.0
        self.matrix_mutation_rate = 0.10

        self.chars = (
            "0123456789"
            "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎ"
            "ﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "ｦｧｨｩｪｫｬｭｮｯｰ"
            "!@#$%^&*()_+{}[]:;<>?/"
        )
        
        self.matrix_streams = []
        for i in range(150):
            self.matrix_streams.append({
                "base_x": random.randint(0, self.win_width),
                "y": random.randint(-self.win_height, 0),
                "speed": random.uniform(2.0, 6.0),
                "chars": [random.choice(self.chars) for _ in range(random.randint(15, 30))]
            })

        self.init_database()
        self.cleanup_old_cache()
        
        self.config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
        
        self.verify_config_sections()

        self.skin_active = False
        self.current_bg_name = self.config.get("Theme", "current_background", fallback="shuffle").strip()
        bg_path = ""

        png_images = []
        if os.path.exists(ASSETS_FOLDER):
            all_files = os.listdir(ASSETS_FOLDER)
            png_images = sorted([f for f in all_files if f.lower().endswith('.png')])

        if self.current_bg_name.lower() == "shuffle" and png_images:
            self.current_bg_name = random.choice(png_images)
            bg_path = os.path.join(ASSETS_FOLDER, self.current_bg_name)
        elif self.current_bg_name.lower() != "shuffle":
            explicit_path = os.path.join(ASSETS_FOLDER, self.current_bg_name)
            if os.path.exists(explicit_path):
                bg_path = explicit_path
            elif png_images:
                self.current_bg_name = png_images[0]
                bg_path = os.path.join(ASSETS_FOLDER, self.current_bg_name)
        
        if bg_path and os.path.exists(bg_path) and os.path.getsize(bg_path) > 0:
            try:
                self.pil_source_image = Image.open(bg_path).convert("RGBA")
                orig_w, orig_h = self.pil_source_image.size
                if orig_w > 0 and orig_h > 0:
                    self.skin_active = True
            except Exception as e:
                write_debug_log("PIL_IMAGE_OPEN_FAIL", e)
                self.skin_active = False

        self.matrix_font = None
        if self.skin_active:
            font_paths = [
                "C:\\Windows\\Fonts\\arialuni.ttf",
                "C:\\Windows\\Fonts\\msgothic.ttc",
                "C:\\Windows\\Fonts\\msmincho.ttc"
            ]
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        self.matrix_font = ImageFont.truetype(path, 12)
                        break
                    except Exception as font_err:
                        write_debug_log("FONT_LOAD_EXCEPTION", font_err)
            if not self.matrix_font:
                self.matrix_font = ImageFont.load_default()

        self.root.geometry(f"{self.win_width}x{self.win_height}")
        self.root.resizable(True, True)
        self.root.configure(bg=DARK_TITLE_COLOR)

        self.canvas_elements = []
        self.text_ids_array = []    
        self.button_widgets_array = [] 
        self.entry_widgets_array = []  
        
        self.create_layout()
        self.load_settings()
        
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_system_tray)
        
        self.root.bind("<Control-Key-g>", lambda e: self.trigger_explicit_theme_shift("green"))
        self.root.bind("<Control-Key-b>", lambda e: self.trigger_explicit_theme_shift("blue"))
        self.root.bind("<Control-Key-r>", lambda e: self.trigger_explicit_theme_shift("red"))
        self.root.bind("<Control-Key-y>", lambda e: self.trigger_explicit_theme_shift("yellow"))
        
        self.root.bind("<Control-Up>", lambda e: self.adjust_matrix_speed(0.2))
        self.root.bind("<Control-Down>", lambda e: self.adjust_matrix_speed(-0.2))
        self.root.bind("<Control-Left>", lambda e: self.adjust_matrix_mutation(-0.02))
        self.root.bind("<Control-Right>", lambda e: self.adjust_matrix_mutation(0.02))
        self.root.bind("<Control-d>", lambda e: self.toggle_diagnostic_mode())
        
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import windll, byref, sizeof, c_int
                self.root.update()
                self.hwnd = windll.user32.GetParent(self.root.winfo_id())
                
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                windll.dwmapi.DwmSetWindowAttribute(self.hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(c_int(1)), sizeof(c_int))
                
                self.setup_native_window_proc()
            except Exception as e:
                try:
                    DWMWA_USE_IMMERSIVE_DARK_MODE_FALLBACK = 19
                    windll.dwmapi.DwmSetWindowAttribute(self.hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_FALLBACK, byref(c_int(1)), sizeof(c_int))
                    self.setup_native_window_proc()
                except Exception as ex:
                    write_debug_log("DWM_DARK_MODE_INJECTION", ex)
        
        if self.skin_active:
            self.init_matrix_streams()
            self.root.bind("<Configure>", self.on_window_configure)
            self.initial_layout_draw()
            self.update_visualizer()
            
        self.update_marquee()
        self.refresh_cache_counter()
        self.poll_tray_commands()
        
        threading.Thread(target=self.run_silent_update_check, daemon=True).start()

    def obfuscate_string(self, raw_str):
        if not raw_str or raw_str.startswith("enc://"):
            return raw_str
        if "paste" in raw_str.lower():
            return raw_str
            
        key = "LOTUS_SYSTEM_ARCHITECT_KAHLUA"
        xored = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(raw_str))
        encoded = base64.b64encode(xored.encode('utf-8')).decode('utf-8')
        return f"enc://{encoded}"

    def deobfuscate_string(self, enc_str):
        if not enc_str or not enc_str.startswith("enc://"):
            return enc_str
        try:
            raw_b64 = enc_str[6:]
            xored = base64.b64decode(raw_b64).decode('utf-8')
            key = "LOTUS_SYSTEM_ARCHITECT_KAHLUA"
            raw_str = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(xored))
            return raw_str
        except Exception as e:
            write_debug_log("DEOBFUSCATION_ERROR", e)
            return enc_str

    def get_conf(self, section, key, default=""):
        try:
            val = self.config.get(section, key, fallback=default).strip()
            return self.deobfuscate_string(val)
        except Exception:
            return default

    def verify_config_sections(self):
        updated = False
        if "LastFM" not in self.config:
            self.config["LastFM"] = {"api_key": "paste last.fm api here", "secret": "", "session_key": ""}
            updated = True
        if "ListenBrainz" not in self.config:
            self.config["ListenBrainz"] = {"user_token": ""}
            updated = True
        if "Trakt" not in self.config:
            self.config["Trakt"] = {
                "client_id": "paste trakt client id here",
                "client_secret": "paste trakt secret here",
                "access_token": "",
                "refresh_token": ""
            }
            updated = True
        if "MPC" not in self.config:
            self.config["MPC"] = {"port": "13579"}
            updated = True
        if "Theme" not in self.config:
            self.config["Theme"] = {"current_background": "shuffle"}
            updated = True
            
        for section in ["LastFM", "ListenBrainz", "Trakt"]:
            if section in self.config:
                for option in self.config[section]:
                    val = self.config.get(section, option).strip()
                    if val and not val.startswith("enc://") and not val.lower().startswith("paste") and option != "port" and option != "current_background":
                        self.config[section][option] = self.obfuscate_string(val)
                        updated = True
                        
        if updated:
            try:
                with open(CONFIG_FILE, "w") as f:
                    self.config.write(f)
            except Exception as e:
                write_debug_log("CONFIG_INIT_WRITE_ERROR", e)

    def init_database(self):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        artist TEXT,
                        track TEXT,
                        timestamp INTEGER,
                        target TEXT,
                        media_type TEXT DEFAULT 'music',
                        status INTEGER DEFAULT 0
                    )
                """)
                conn.commit()
                
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("ALTER TABLE cache ADD COLUMN media_type TEXT DEFAULT 'music'")
                except sqlite3.OperationalError:
                    pass
                try:
                    cursor.execute("ALTER TABLE cache ADD COLUMN status INTEGER DEFAULT 0")
                except sqlite3.OperationalError:
                    pass
                conn.commit()
        except Exception as e:
            write_debug_log("SQLITE_INIT_EXCEPTION", e)

    def cleanup_old_cache(self):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                thirty_days_ago = int(time.time()) - (30 * 24 * 60 * 60)
                conn.execute("DELETE FROM cache WHERE status = 1 AND timestamp < ?", (thirty_days_ago,))
                conn.commit()
        except Exception as e:
            write_debug_log("CACHE_CLEANUP_ERROR", e)

    def setup_native_window_proc(self):
        return

    def run_silent_update_check(self):
        try:
            url = "https://raw.githubusercontent.com/KahluaDingo/Lotus/main/version.json"
            req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': f'LotusScrobbler/{BUILD_VERSION}'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode('utf-8'))
                remote_ver = data.get("version", BUILD_VERSION)
                if remote_ver != BUILD_VERSION:
                    write_debug_log("UPDATER", f"Update verified. Current local build: {BUILD_VERSION}, Remote upstream: {remote_ver}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass
            else:
                write_debug_log("SILENT_UPDATE_CHECK_FAILED", e)
        except Exception as e:
            pass

    def toggle_diagnostic_mode(self):
        self.diagnostic_mode = not self.diagnostic_mode

    def adjust_matrix_speed(self, delta):
        self.matrix_speed_multiplier = max(0.1, min(5.0, self.matrix_speed_multiplier + delta))

    def adjust_matrix_mutation(self, delta):
        self.matrix_mutation_rate = max(0.01, min(1.0, self.matrix_mutation_rate + delta))

    def create_layout(self):
        if self.skin_active:
            self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.bg_image_id = self.canvas.create_image(0, 0, anchor=tk.NW)
            
            self.ent_key = tk.Entry(self.canvas, width=32, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, bd=1, relief=tk.SOLID, show="*")
            self.ent_secret = tk.Entry(self.canvas, width=32, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, bd=1, relief=tk.SOLID, show="*")
            self.ent_sk = tk.Entry(self.canvas, width=32, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, bd=1, relief=tk.SOLID, show="*")
            self.ent_lb = tk.Entry(self.canvas, width=32, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, bd=1, relief=tk.SOLID, show="*")
            self.ent_port = tk.Entry(self.canvas, width=32, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, bd=1, relief=tk.SOLID)
            
            self.entry_widgets_array.extend([self.ent_key, self.ent_secret, self.ent_sk, self.ent_lb, self.ent_port])

            self.btn_link1 = tk.Button(self.canvas, text="[ 1. LFM_LINK ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=self.start_authorization)
            self.btn_link2 = tk.Button(self.canvas, text="[ 2. LFM_CONFIRM ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=self.fetch_session_key)
            self.btn_link3 = tk.Button(self.canvas, text="[ 3. TRAKT_AUTH ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=self.start_trakt_auth)

            self.btn_toggle = tk.Button(self.canvas, text="[ INITIALIZE_LINK ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=self.toggle_service, cursor="hand2")
            self.btn_save = tk.Button(self.canvas, text="[ COMM_SAVE ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=self.save_settings, cursor="hand2")
            self.btn_cycle = tk.Button(self.canvas, text="[ CYCLE_SKIN ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=self.cycle_background, cursor="hand2")

            self.button_widgets_array.extend([self.btn_link1, self.btn_link2, self.btn_link3, self.btn_toggle, self.btn_save, self.btn_cycle])

            self.cache_label_id = self.canvas.create_text(0, 0, text="CACHE_PENDING: //0_TRACKS", font=self.font_main, fill=self.text_color, anchor=tk.NW)
            self.text_ids_array.append(self.cache_label_id)

            self.canvas_blueprint = [
                ("LABEL://API KEY:", -220, -145, "text"),         (self.ent_key, -45, -145, "window"),
                ("LABEL://SHARED SECRET:", -220, -115, "text"),   (self.ent_secret, -45, -115, "window"),
                ("LABEL://SESSION KEY (sk):", -220, -65, "text"), (self.ent_sk, -45, -65, "window"),
                ("LABEL://LISTENBRAINZ TOK:", -220, -35, "text"), (self.ent_lb, -45, -35, "window"),
                ("LABEL://MPC-HC PORT:", -220, -5, "text"),       (self.ent_port, -45, -5, "window"),
                (self.btn_link1, -220, 35, "window"),             (self.btn_link2, -100, 35, "window"),
                (self.btn_link3, 35, 35, "window"),
                ("STATUS://SYSTEM_STATUS: //OFFLINE", -220, 75, "text"),
                ("RAW_ID://" + str(self.cache_label_id), -220, 105, "text"),
                (self.btn_toggle, -220, 140, "window"),           (self.btn_save, -35, 140, "window"),
                (self.btn_cycle, 110, 140, "window")
            ]
            
            for item, off_x, off_y, type_tag in self.canvas_blueprint:
                if type_tag == "text":
                    if item.startswith("LABEL://"):
                        txt = item.replace("LABEL://", "")
                        i_id = self.canvas.create_text(0, 0, text=txt, font=self.font_main, fill=self.text_color, anchor=tk.NW)
                        self.text_ids_array.append(i_id)
                    elif item.startswith("RAW_ID://"):
                        i_id = int(item.replace("RAW_ID://", ""))
                    else:
                        txt = item.replace("STATUS://", "")
                        i_id = self.canvas.create_text(0, 0, text=txt, font=self.font_main, fill=self.text_color, anchor=tk.NW)
                        self.status_text_id = i_id
                    self.canvas_elements.append((i_id, off_x, off_y, "text"))
                else:
                    i_id = self.canvas.create_window(0, 0, window=item, anchor=tk.NW)
                    self.canvas_elements.append((i_id, off_x, off_y, "window"))
        else:
            self.main_frame = tk.Frame(self.root, bg=self.bg_color, bd=0)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
            fields = [("API KEY:", "ent_key"), ("SHARED SECRET:", "ent_secret"), ("SESSION KEY (sk):", "ent_sk"), ("LISTENBRAINZ TOK:", "ent_lb"), ("MPC-HC PORT:", "ent_port")]
            for idx, (lbl_txt, attr) in enumerate(fields):
                tk.Label(self.main_frame, text=lbl_txt, font=self.font_main, bg=self.bg_color, fg=self.text_color, anchor="w").grid(row=idx, column=0, sticky=tk.W, pady=3)
                entry = tk.Entry(self.main_frame, width=32, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, bd=1, relief=tk.SOLID, show="*")
                entry.grid(row=idx, column=1, pady=3, padx=10)
                setattr(self, attr, entry)
            
            auth_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            auth_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)
            tk.Button(auth_frame, text="[ 1. LFM_LINK ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, command=self.start_authorization, bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=2)
            tk.Button(auth_frame, text="[ 2. LFM_CONFIRM ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, command=self.fetch_session_key, bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=5)
            tk.Button(auth_frame, text="[ 3. TRAKT_AUTH ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, command=self.start_trakt_auth, bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=5)
            
            self.lbl_status = tk.Label(self.main_frame, text="SYSTEM_STATUS: //OFFLINE", font=self.font_main, bg=self.bg_color, fg=self.text_color)
            self.lbl_status.grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.W)
            
            self.lbl_cache = tk.Label(self.main_frame, text="CACHE_PENDING: //0_TRACKS", font=self.font_main, bg=self.bg_color, fg=self.text_color)
            self.lbl_cache.grid(row=7, column=0, columnspan=2, pady=2, sticky=tk.W)

            btn_frame = tk.Frame(self.main_frame, bg=self.bg_color)
            btn_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky=tk.W)
            self.btn_toggle = tk.Button(btn_frame, text="[ INITIALIZE_LINK ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, command=self.toggle_service, bd=1, relief=tk.SOLID)
            self.btn_toggle.pack(side=tk.LEFT, padx=2)
            self.btn_save = tk.Button(btn_frame, text="[ COMM_SAVE ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, command=self.save_settings, bd=1, relief=tk.SOLID)
            self.btn_save.pack(side=tk.LEFT, padx=5)
            self.btn_cycle = tk.Button(btn_frame, text="[ CYCLE_SKIN ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, command=self.cycle_background, bd=1, relief=tk.SOLID)
            self.btn_cycle.pack(side=tk.LEFT, padx=5)

    def trigger_explicit_theme_shift(self, target_theme):
        if not self.skin_active or self.matrix_theme == target_theme:
            return
            
        self.matrix_theme = target_theme
        if target_theme == "blue":
            self.text_color = self.color_blue_neon
        elif target_theme == "red":
            self.text_color = self.color_red_neon
        elif target_theme == "yellow":
            self.text_color = self.color_yellow_neon
        else:
            self.text_color = self.color_green_neon
            
        for t_id in self.text_ids_array:
            self.canvas.itemconfig(t_id, fill=self.text_color)
            
        self.canvas.itemconfig(self.status_text_id, fill=self.text_color)
            
        for btn in self.button_widgets_array:
            btn.config(fg=self.text_color, activebackground=self.text_color)
            
        for ent in self.entry_widgets_array:
            ent.config(fg=self.text_color, insertbackground=self.text_color)

    def minimize_to_system_tray(self):
        if not os.path.exists(ICON_FILE):
            self.complete_application_shutdown()
            return
            
        self.is_minimizing = True 
        self.root.withdraw()
        
        if self.tray_instance:
            self.is_minimizing = False
            return
            
        try:
            tray_img = Image.open(ICON_FILE)
            menu_blueprint = (
                pystray.MenuItem('[ Restore Console ]', lambda: setattr(self, 'tray_command_queue', 'restore')),
                pystray.MenuItem('[ Shutdown Link ]', lambda: setattr(self, 'tray_command_queue', 'shutdown'))
            )
            
            restore_action = pystray.MenuItem('default', lambda: setattr(self, 'tray_command_queue', 'restore'), visible=False)
            
            self.tray_instance = pystray.Icon("Lotus", tray_img, "Lotus // Active Media Cast", menu_blueprint, default_action=restore_action)
            self.tray_instance.run_detached()
        except Exception as e:
            write_debug_log("SYSTEM_TRAY_MINIMIZATION_EXCEPTION", e)
            self.root.destroy()
        finally:
            self.is_minimizing = False 

    def poll_tray_commands(self):
        if self.tray_command_queue == 'restore':
            self.tray_command_queue = None
            self.is_minimizing = True 
            if self.tray_instance:
                self.tray_instance.stop()
                self.tray_instance = None
            self.root.deiconify()
            self.is_minimizing = False 
        elif self.tray_command_queue == 'shutdown':
            self.tray_command_queue = None
            self.complete_application_shutdown()
            return

        self.root.after(100, self.poll_tray_commands)

    def complete_application_shutdown(self):
        self.is_running = False
        if self.tray_instance:
            self.tray_instance.stop()
            self.tray_instance = None
        self.root.destroy()
        os._exit(0)

    def update_shadow_text_color(self, text, color=None):
        if not color:
            color = self.text_color
        try:
            if self.skin_active:
                self.canvas.itemconfig(self.status_text_id, text=text, fill=color)
            else:
                self.lbl_status.config(text=text, fg=color)
        except Exception as e:
            write_debug_log("TKINTER_STATUS_DISPLAY_ERROR", e)

    def refresh_cache_counter(self):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache WHERE status = 0")
                count = cursor.fetchone()[0]
                text = f"CACHE_PENDING: //{count}_TRACKS"
                if self.skin_active:
                    self.canvas.itemconfig(self.cache_label_id, text=text)
                else:
                    self.lbl_cache.config(text=text)
        except Exception as e:
            write_debug_log("REFRESH_CACHE_COUNTER_DB_ERROR", e)

    def sanitize_track_metadata(self, text_raw):
        if not text_raw:
            return ""
        text = text_raw
        patterns = [
            r'\s*[\(\]][⧿\s]*Official\s*(?:Video|Audio|Music\s*Video|Lyrics?\s*Video)?\s*[\)\]]',
            r'\s*[\(\]][⧿\s]*(?:199\d|20[0-2]\d)\s*Remaster(?:ed)?\s*[\)\]]',
            r'\s*[\(\]][⧿\s]*Remaster(?:ed)?\s*[\)\]]',
            r'\s*[\(\]][⧿\s]*HD\s*[\)\]]',
            r'\s*[\(\]][⧿\s]*(?:4K|UHD)\s*[\)\]]',
            r'\s*[\(\]][⧿\s]*FLAC[⧿\s]*(?:24bit|16bit)?\s*[\)\]]',
            r'\s*[\(\]][⧿\s]*HQ\s*[\)\]]'
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    def init_matrix_streams(self):
        col_width = 15
        num_cols = 3840 // col_width
        self.matrix_streams = []
        for i_val in range(num_cols):
            self.matrix_streams.append({
                "base_x": i_val * col_width,
                "y": random.randint(-800, 0),
                "speed": random.randint(4, 9),
                "chars": [random.choice(self.chars) for _ in range(random.randint(12, 28))]
            })

    def initial_layout_draw(self):
        w = self.win_width
        h = self.win_height
        self.last_w = w
        self.last_h = h
        try:
            self.resized_base = self.pil_source_image.resize((w, h), Image.Resampling.BILINEAR)
            mid_x, mid_y = w // 2, h // 2
            for item_id, offset_x, offset_y, _ in self.canvas_elements:
                self.canvas.coords(item_id, mid_x + offset_x, mid_y + offset_y)
        except Exception as e:
            write_debug_log("INITIAL_LAYOUT_DRAW_PIL_FAIL", e)

    def on_window_configure(self, event):
        if event.widget != self.root:
            return
            
        w = min(event.width, 3840)
        h = min(event.height, 2160)
        
        if w < 430 or h < 270:
            return

        mid_x, mid_y = w // 2, h // 2
        for item_id, offset_x, offset_y, _ in self.canvas_elements:
            self.canvas.coords(item_id, mid_x + offset_x, mid_y + offset_y)

        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
            
        if w != self.last_w or h != self.last_h:
            self.win_width = w
            self.win_height = h
            self.resize_after_id = self.root.after(300, self.execute_background_resample)

    def execute_background_resample(self):
        if self.is_resizing:
            return
        self.is_resizing = True
        try:
            self.resized_base = self.pil_source_image.resize((self.win_width, self.win_height), Image.Resampling.BILINEAR)
            self.last_w = self.win_width
            self.last_h = self.win_height
        except Exception as e:
            write_debug_log("EXECUTE_BACKGROUND_RESAMPLE_PIL_FAIL", e)
        finally:
            self.is_resizing = False
            self.resize_after_id = None

    def update_visualizer(self):
        if self.is_resizing or not hasattr(self, 'resized_base'):
            self.root.after(40, self.update_visualizer)
            return

        try:
            tgt_w, tgt_h = self.resized_base.size
            overlay = Image.new("RGBA", (tgt_w, tgt_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            mid_x, mid_y = tgt_w // 2, tgt_h // 2
            box_w, box_h = 470, 340
            bx1, by1 = mid_x - (box_w // 2), mid_y - (box_h // 2)
            bx2, by2 = mid_x + (box_w // 2), mid_y + (box_h // 2)
            
            speed_mult = 0.5
            if self.stream_active:
                pulse = (math.sin(time.time() * 6.28) + 1.0) / 2.0
                speed_mult = 0.8 + (pulse * 2.2)
            
            wind_drift = int(math.cos(time.time() * 1.5) * 12)
            
            for stream in self.matrix_streams:
                current_x = stream["base_x"] + wind_drift
                
                if -20 < current_x < tgt_w + 20:
                    stream["y"] += int(stream["speed"] * speed_mult * self.matrix_speed_multiplier * random.uniform(0.9, 1.1))
                    
                    for idx in range(len(stream["chars"])):
                        if random.random() < self.matrix_mutation_rate:
                            stream["chars"][idx] = random.choice(self.chars)
                    
                    if stream["y"] > tgt_h + len(stream["chars"]) * 14:
                        stream["y"] = random.randint(-200, 0)
                        stream["chars"] = [random.choice(self.chars) for _ in range(random.randint(12, 28))]
                    
                    for idx, char in enumerate(stream["chars"]):
                        char_y = stream["y"] - (idx * 14)
                        
                        if 0 <= char_y < tgt_h:
                            pos_ratio = idx / len(stream["chars"])
                            
                            if idx == 0:
                                if self.matrix_theme == "blue": color_rgb = (220, 245, 255)
                                elif self.matrix_theme == "red": color_rgb = (255, 220, 220)
                                elif self.matrix_theme == "yellow": color_rgb = (255, 255, 220)
                                else: color_rgb = (215, 255, 225)
                                alpha = 255
                            elif pos_ratio < 0.25:
                                if self.matrix_theme == "blue": color_rgb = (0, 180, 255)
                                elif self.matrix_theme == "red": color_rgb = (255, 51, 51)
                                elif self.matrix_theme == "yellow": color_rgb = (255, 255, 51)
                                else: color_rgb = (0, 255, 51)
                                alpha = int(240 * (1.0 - pos_ratio))
                            elif pos_ratio < 0.70:
                                if self.matrix_theme == "blue": color_rgb = (0, 90, 220)
                                elif self.matrix_theme == "red": color_rgb = (180, 30, 30)
                                elif self.matrix_theme == "yellow": color_rgb = (180, 180, 30)
                                else: color_rgb = (0, 180, 40)
                                alpha = int(180 * (1.0 - pos_ratio))
                            else:
                                if self.matrix_theme == "blue": color_rgb = (0, 25, 100)
                                elif self.matrix_theme == "red": color_rgb = (90, 10, 10)
                                elif self.matrix_theme == "yellow": color_rgb = (90, 90, 10)
                                else: color_rgb = (0, 65, 10)
                                alpha = int(90 * (1.0 - pos_ratio))
                                
                            if bx1 <= current_x <= bx2 and by1 <= char_y <= by2:
                                alpha = max(5, int(alpha * 0.2))
                            else:
                                alpha = max(10, alpha)
                                
                            draw.text((current_x, char_y), char, fill=(color_rgb[0], color_rgb[1], color_rgb[2], alpha), font=self.matrix_font)

            draw.rectangle([bx1, by1, bx2, by2], fill=(0, 0, 0, 175))
            final_render = Image.alpha_composite(self.resized_base, overlay)
            self.tk_image_render = ImageTk.PhotoImage(final_render)
            self.canvas.itemconfig(self.bg_image_id, image=self.tk_image_render)
            
        except Exception as e:
            write_debug_log("UPDATE_VISUALIZER_CANVAS_EXCEPTION", e)
            
        self.root.after(40, self.update_visualizer)

    def load_settings(self):
        self.ent_key.insert(0, self.get_conf("LastFM", "api_key"))
        self.ent_secret.insert(0, self.get_conf("LastFM", "secret"))
        self.ent_sk.insert(0, self.get_conf("LastFM", "session_key"))
        self.ent_lb.insert(0, self.get_conf("ListenBrainz", "user_token"))
        self.ent_port.insert(0, self.config.get("MPC", "port", fallback="13579").strip())

    def save_settings(self):
        try:
            self.config["LastFM"]["api_key"] = self.obfuscate_string(self.ent_key.get().strip())
            self.config["LastFM"]["secret"] = self.obfuscate_string(self.ent_secret.get().strip())
            self.config["LastFM"]["session_key"] = self.obfuscate_string(self.ent_sk.get().strip())
            self.config["ListenBrainz"]["user_token"] = self.obfuscate_string(self.ent_lb.get().strip())
            self.config["MPC"]["port"] = self.ent_port.get().strip()
            
            for k in ["client_id", "client_secret", "access_token", "refresh_token"]:
                if k in self.config["Trakt"]:
                    raw_t = self.get_conf("Trakt", k)
                    if raw_t and not raw_t.lower().startswith("paste"):
                        self.config["Trakt"][k] = self.obfuscate_string(raw_t)
                        
            with open(CONFIG_FILE, "w") as f:
                self.config.write(f)
            messagebox.showinfo("SYSTEM LOG", "Configuration matrices synchronized.")
        except Exception as e:
            write_debug_log("SAVE_SETTINGS_INI_ERROR", e)

    def cycle_background(self):
        if not os.path.exists(ASSETS_FOLDER):
            return
        all_files = os.listdir(ASSETS_FOLDER)
        png_images = sorted([f for f in all_files if f.lower().endswith('.png')])
        if not png_images:
            return

        if self.current_bg_name not in png_images:
            next_bg = png_images[0]
        else:
            current_index = png_images.index(self.current_bg_name)
            next_index = (current_index + 1) % len(png_images)
            next_bg = png_images[next_index]

        bg_path = os.path.join(ASSETS_FOLDER, next_bg)
        try:
            self.pil_source_image = Image.open(bg_path).convert("RGBA")
            self.current_bg_name = next_bg
            self.config["Theme"]["current_background"] = next_bg
            with open(CONFIG_FILE, "w") as f:
                self.config.write(f)
            
            if self.skin_active:
                self.execute_background_resample()
        except Exception as e:
            write_debug_log("CYCLE_BACKGROUND_EXCEPTION", e)

    def generate_signature(self, params, secret):
        sorted_keys = sorted(params.keys())
        sig_string = "".join(f"{k}{params[k]}" for k in sorted_keys) + secret
        return hashlib.md5(sig_string.encode('utf-8')).hexdigest()

    def start_authorization(self):
        api_key = self.get_conf("LastFM", "api_key")
        secret = self.get_conf("LastFM", "secret")
        if not api_key or not secret:
            messagebox.showerror("ERROR", "Populate API Key and Shared Secret fields in configuration.")
            return
        params = {"method": "auth.getToken", "api_key": api_key}
        params["api_sig"] = self.generate_signature(params, secret)
        url = "https://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                res_text = r.read().decode('utf-8')
                token = re.search(r'<token>(.*?)</token>', res_text).group(1)
                self.auth_token = token
                auth_url = f"https://www.last.fm/api/auth/?api_key={api_key}&token={self.auth_token}"
                webbrowser.open(auth_url)
                self.stream_active = False
                self.update_shadow_text_color("AUTH: //AWAITING_BROWSER_CONFIRMATION...", "#FFFF33")
        except Exception as e:
            write_debug_log("LASTFM_START_AUTH_HTTP_EXCEPTION", e)
            messagebox.showerror("ERROR", f"Token generation failure: {e}")

    def fetch_session_key(self):
        api_key = self.get_conf("LastFM", "api_key")
        secret = self.get_conf("LastFM", "secret")
        if not self.auth_token:
            messagebox.showerror("ERROR", "Generate token parameters via Step 1 first.")
            return
        params = {"method": "auth.getSession", "api_key": api_key, "token": self.auth_token}
        params["api_sig"] = self.generate_signature(params, secret)
        url = "https://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                res_text = r.read().decode('utf-8')
                sk = re.search(r'<key>(.*?)</key>', res_text).group(1)
                self.ent_sk.delete(0, tk.END)
                self.ent_sk.insert(0, sk)
                self.save_settings()
                self.update_shadow_text_color("AUTH: //HANDSHAKE_COMPLETE_SESSION_LOCKED", self.text_color)
        except Exception as e:
            write_debug_log("LASTFM_FETCH_SESSION_KEY_HTTP_EXCEPTION", e)
            messagebox.showerror("ERROR", f"Authorization extraction failure: {e}")

    def spawn_matrix_pin_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("TRAKT // PIN_OVERRIDE")
        dialog.configure(bg=self.bg_color)
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import windll, byref, sizeof, c_int
                dialog.update()
                hwnd = windll.user32.GetParent(dialog.winfo_id())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(c_int(1)), sizeof(c_int))
            except Exception:
                try:
                    DWMWA_USE_IMMERSIVE_DARK_MODE_FALLBACK = 19
                    windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_FALLBACK, byref(c_int(1)), sizeof(c_int))
                except:
                    pass
        
        try:
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
            dialog.geometry(f"+{x}+{y}")
        except:
            pass

        tk.Label(dialog, text="INPUT TRAKT PIN SEQUENCE:", font=self.font_main, bg=self.bg_color, fg=self.text_color).pack(pady=15)
        
        entry = tk.Entry(dialog, font=self.font_main, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color, justify="center", bd=1, relief=tk.SOLID)
        entry.pack(pady=5, padx=40, fill=tk.X)
        entry.focus_set()
        
        result = [None]
        
        def submit(event=None):
            result[0] = entry.get().strip()
            dialog.destroy()
            
        btn = tk.Button(dialog, text="[ EXECUTE ]", font=self.font_main, bg=self.bg_color, fg=self.text_color, activebackground=self.text_color, activeforeground=self.bg_color, bd=1, relief=tk.SOLID, command=submit)
        btn.pack(pady=10)
        
        dialog.bind('<Return>', submit)
        self.root.wait_window(dialog)
        return result[0]

    def start_trakt_auth(self):
        client_id = self.get_conf("Trakt", "client_id")
        if not client_id or client_id.lower().startswith("paste"):
            messagebox.showerror("ERROR", "Provide Trakt client_id in configuration INI before proceeding.")
            return

        auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        webbrowser.open(auth_url)
        
        pin = self.spawn_matrix_pin_dialog()
        
        if not pin:
            self.update_shadow_text_color("TRAKT: //AUTHORIZATION_ABORTED", "#FF3333")
            return

        client_secret = self.get_conf("Trakt", "client_secret")
        req = urllib.request.Request("https://api.trakt.tv/oauth/token",
            data=json.dumps({
                "code": pin,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "grant_type": "authorization_code"
            }).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"LotusScrobbler/{BUILD_VERSION} (https://github.com/KahluaDingo)"
            }, method="POST")

        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
                if "access_token" in data:
                    self.config["Trakt"]["access_token"] = self.obfuscate_string(data["access_token"])
                    self.config["Trakt"]["refresh_token"] = self.obfuscate_string(data["refresh_token"])
                    with open(CONFIG_FILE, "w") as f:
                        self.config.write(f)
                    self.update_shadow_text_color("TRAKT: //AUTHORIZATION_LOCKED", self.text_color)
                    messagebox.showinfo("SYSTEM LOG", "Trakt authorization matrices synchronized.")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            write_debug_log("TRAKT_PIN_EXCHANGE_ERROR", f"HTTP {e.code}: {err_body}")
            messagebox.showerror("ERROR", "Failed to verify PIN. Inspect debug log.")
            self.update_shadow_text_color("TRAKT: //AUTHORIZATION_FAILED", "#FF3333")
        except Exception as e:
            write_debug_log("TRAKT_PIN_EXCHANGE_EXCEPTION", e)
            messagebox.showerror("ERROR", "Unexpected network disruption.")

    def normalize_metadata(self, filename):
        clean = re.sub(r'(\[.*?\]|\(.*?\)|-|\.)', ' ', filename)
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', clean)
        year = year_match.group(1) if year_match else ""
        
        title = re.sub(r'\b(19\d{2}|20\d{2})\b', '', clean).strip()
        title = re.sub(r'\s+', ' ', title)
        return title, year

    def send_to_trakt(self, action, filename, progress=0.0):
        token = self.get_conf("Trakt", "access_token")
        client_id = self.get_conf("Trakt", "client_id")
        if not token or not client_id:
            return False

        title, year = self.normalize_metadata(filename)
        search_query = f"{title} {year}".strip()

        search_url = f"https://api.trakt.tv/search/movie?query={urllib.parse.quote(search_query)}"
        req = urllib.request.Request(search_url, headers={
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": client_id,
            "Authorization": f"Bearer {token}",
            "User-Agent": f"LotusScrobbler/{BUILD_VERSION} (https://github.com/KahluaDingo)"
        })
        
        try:
            with urllib.request.urlopen(req) as r:
                results = json.loads(r.read())
                if not results:
                    return False
                movie_obj = results[0].get('movie')
                if not movie_obj:
                    return False

            scrobble_url = f"https://api.trakt.tv/scrobble/{action}"
            payload = {
                "movie": {
                    "title": movie_obj.get("title"),
                    "year": movie_obj.get("year"),
                    "ids": movie_obj.get("ids")
                },
                "progress": round(float(progress), 2), 
                "app_version": BUILD_VERSION,
                "app_date": time.strftime("%Y-%m-%d")
            }
            
            scrobble_req = urllib.request.Request(scrobble_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "trakt-api-version": "2",
                    "trakt-api-key": client_id,
                    "Authorization": f"Bearer {token}",
                    "User-Agent": f"LotusScrobbler/{BUILD_VERSION} (https://github.com/KahluaDingo)"
                }, method="POST")
                
            with urllib.request.urlopen(scrobble_req) as r2:
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            write_debug_log(f"TRAKT_API_SCROBBLE_HTTP_{e.code}_{action}", err_body)
            if e.code == 429:
                retry_after = int(e.headers.get('Retry-After', 5))
                time.sleep(retry_after)
            return False
        except Exception as e:
            write_debug_log(f"TRAKT_API_SCROBBLE_ERROR_{action}", e)
            return False

    def send_to_lastfm(self, method, artist, track, timestamp=None):
            api_key = self.get_conf("LastFM", "api_key")
            sk = self.get_conf("LastFM", "session_key")
            secret = self.get_conf("LastFM", "secret")
            params = {"method": method, "api_key": api_key, "sk": sk, "artist": artist, "track": track}
            if timestamp:
                params["timestamp"] = str(timestamp)
            params["api_sig"] = self.generate_signature(params, secret)
            data = urllib.parse.urlencode(params).encode('utf-8')
            req = urllib.request.Request("https://ws.audioscrobbler.com/2.0/", data=data, method="POST")
            req.add_header("User-Agent", f"LotusScrobbler/{BUILD_VERSION} (https://github.com/KahluaDingo)")
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    return True
            except Exception as e:
                write_debug_log(f"LASTFM_POST_PAYLOAD_FAILED_METHOD_{method}", e)
                return False

    def send_to_listenbrainz(self, listen_type, artist, track, timestamp=None):
        token = self.get_conf("ListenBrainz", "user_token")
        if not token:
            return False
            
        url = "https://api.listenbrainz.org/1/submit-listens"
        payload = {
            "listen_type": listen_type,
            "payload": [{
                "track_metadata": {
                    "artist_name": artist,
                    "track_name": track
                }
            }]
        }
        if timestamp and listen_type == "single":
            payload["payload"][0]["listened_at"] = int(timestamp)
            
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Authorization", f"Token {token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", f"LotusScrobbler/{BUILD_VERSION} (https://github.com/KahluaDingo)")
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return True
        except Exception as e:
                write_debug_log(f"LISTENBRAINZ_POST_PAYLOAD_FAILED_TYPE_{listen_type}", e)
                return False

    def process_cached_scrobbling(self):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, artist, track, timestamp, target, media_type FROM cache WHERE status = 0 LIMIT 10")
                rows = cursor.fetchall()
                
                for row in rows:
                    row_id, artist, track, ts, target, m_type = row
                    success = False
                    
                    if m_type == "video" and target == "trakt":
                        success = self.send_to_trakt("stop", track, progress=100.0)
                    elif m_type == "music":
                        if target == "lastfm":
                            success = self.send_to_lastfm("track.scrobble", artist, track, timestamp=ts)
                        elif target == "listenbrainz":
                            success = self.send_to_listenbrainz("single", artist, track, timestamp=ts)
                            
                    if success:
                        cursor.execute("UPDATE cache SET status = 1 WHERE id = ?", (row_id,))
                    else:
                        cursor.execute("UPDATE cache SET status = 2 WHERE id = ?", (row_id,))
                conn.commit()
            self.refresh_cache_counter()
        except Exception as e:
            write_debug_log("SQLITE_CACHE_CLEAR_LOOP_EXCEPTION", e)

    def parse_mpc_playing(self):
        current_port = self.config.get("MPC", "port", fallback="13579").strip()
        url = f"http://localhost:{current_port}/variables.html"
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                html = response.read().decode('utf-8')
                filename_match = re.search(r'<p id="file">(.*?)</p>', html)
                filepath_match = re.search(r'<p id="filepath">(.*?)</p>', html)
                state_match = re.search(r'<p id="statestring">(.*?)</p>', html)
                
                position_match = re.search(r'<p id="position">(.*?)</p>', html)
                duration_match = re.search(r'<p id="duration">(.*?)</p>', html)
                
                if filename_match and state_match:
                    filename = filename_match.group(1).strip()
                    state = state_match.group(1).strip().lower()
                    
                    pos = int(position_match.group(1).strip()) if position_match else 0
                    dur = int(duration_match.group(1).strip()) if duration_match else 0
                    
                    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
                    media_type = 'music'
                    if any(filename.lower().endswith(ext) for ext in video_extensions):
                        media_type = 'video'
                    
                    if filename and "playing" in state:
                        clean_name = filename.rsplit(".", 1)[0].strip()
                        clean_name = re.sub(r'^\d{1,3}([.\s\-–—]+|\s)', '', clean_name).strip()
                        clean_name = self.sanitize_track_metadata(clean_name)
                        
                        if filepath_match:
                            local_path = urllib.parse.unquote(filepath_match.group(1).strip())
                            if os.path.exists(local_path) and media_type == 'music':
                                try:
                                    audio = MutagenFile(local_path)
                                    if audio is not None:
                                        artist_key = 'artist' if 'artist' in audio else 'TPE1'
                                        title_key = 'title' if 'title' in audio else 'TIT2'
                                        
                                        meta_artist = audio.get(artist_key)
                                        meta_title = audio.get(title_key)
                                        
                                        if meta_artist and meta_title:
                                            r_artist = meta_artist[0].strip() if isinstance(meta_artist, list) else meta_artist.text[0].strip()
                                            r_track = meta_title[0].strip() if isinstance(meta_title, list) else meta_title.text[0].strip()
                                            
                                            r_artist = self.sanitize_track_metadata(r_artist)
                                            r_track = self.sanitize_track_metadata(r_track)
                                            return r_artist, r_track, pos, dur, media_type
                                except Exception as meta_err:
                                    write_debug_log("MUTAGEN_FILE_PARSING_METADATA_ERROR", meta_err)

                        if " - " in clean_name:
                            parts = clean_name.split(" - ", 1)
                            return parts[0].strip(), parts[1].strip(), pos, dur, media_type
                        
                        if filepath_match:
                            raw_filepath = urllib.parse.unquote(filepath_match.group(1).strip())
                            normalized_path = raw_filepath.replace('/', '\\')
                            segments = [seg.strip() for seg in normalized_path.split('\\') if seg.strip()]
                            
                            clean_segments = []
                            for seg in segments:
                                if re.match(r'^[A-Za-z]:$', seg):
                                    continue
                                if re.match(r'^(music|curation|flac|mp3|new folder|downloads|audio|tracks|movies|video)$', seg, re.IGNORECASE):
                                    continue
                                clean_segments.append(seg)
                            
                            if len(clean_segments) >= 2:
                                return clean_segments[-2], clean_name, pos, dur, media_type
                            elif len(clean_segments) == 1:
                                return clean_segments[0], clean_name, pos, dur, media_type
                        
                        return "Unknown Artist", clean_name, pos, dur, media_type
        except Exception:
            pass
        return None, None, 0, 0, "music"

    def parse_smtc_playing(self):
        if GlobalSystemMediaTransportControlsSessionManager is None:
            return None, None, 0, 0, None

        async def get_smtc_metadata():
            try:
                manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
                session = manager.get_current_session()
                if not session or session.get_playback_info().playback_status != 4:
                    return None, None, 0, 0, None
                    
                props = await session.try_get_media_properties_async()
                artist = self.sanitize_track_metadata(props.artist)
                title = self.sanitize_track_metadata(props.title)
                
                app_id = session.source_app_user_model_id if hasattr(session, 'source_app_user_model_id') else ""
                
                if not artist or not title:
                    return None, None, 0, 0, app_id
                    
                try:
                    timeline = session.get_timeline_properties()
                    pos = int(timeline.position.total_seconds() * 1000)
                    dur = int(timeline.end_time.total_seconds() * 1000)
                except Exception:
                    pos = 0
                    dur = 0
                    
                return artist, title, pos, dur, app_id
            except Exception as e:
                write_debug_log("SMTC_QUERY_FAILURE", e)
                return None, None, 0, 0, None

        try:
            return asyncio.run(asyncio.wait_for(get_smtc_metadata(), timeout=2.0))
        except Exception:
            return None, None, 0, 0, None

    def update_marquee(self):
        if not self.is_running:
            self.update_shadow_text_color("SYSTEM_STATUS: //OFFLINE", "#FF3333")
            self.root.after(150, self.update_marquee)
            return

        if self.stream_active:
            current_string = f"{self.raw_artist} - {self.raw_track}"
            
            if current_string != self.current_display_track:
                self.current_display_track = current_string
                raw_payload = f" {self.raw_artist.upper()} - {self.raw_track.upper()} "
                padding = " " * self.marquee_display_width
                self.marquee_text = padding + raw_payload + padding
                self.marquee_index = 0

            if self.marquee_text:
                display = self.marquee_text[self.marquee_index : self.marquee_index + self.marquee_display_width]
                
                if self.diagnostic_mode:
                    self.update_shadow_text_color(f"DIAG://{self.last_parsed_media}", "#FFFF33")
                else:
                    self.update_shadow_text_color(f"BROADCASTING://{display}", self.text_color)
                    
                self.marquee_index += 1
                if self.marquee_index > len(self.marquee_text) - self.marquee_display_width:
                    self.marquee_index = 0
        else:
            self.current_display_track = ""
            self.marquee_text = ""
            
            pulse_val = (math.sin(time.time() * 3.0) + 1.0) / 2.0
            r = int(100 + (155 * pulse_val))
            g = int(100 + (155 * pulse_val))
            b = int(20 + (31 * pulse_val))
            pulse_color = f"#{r:02x}{g:02x}{b:02x}"
            
            if self.diagnostic_mode:
                self.update_shadow_text_color(f"DIAG://{self.last_parsed_media}", pulse_color)
            else:
                self.update_shadow_text_color("LINK_ACTIVE://AWAITING_MEDIA_STREAM...", pulse_color)
        
        self.root.after(150, self.update_marquee)

    def monitor_loop(self):
        while self.is_running:
            try:
                events = []
                
                m_artist, m_track, m_pos, m_dur, m_type = self.parse_mpc_playing()
                events.append({'artist': m_artist, 'track': m_track, 'pos': m_pos, 'dur': m_dur, 'type': m_type, 'weight': 10})

                s_artist, s_track, s_pos, s_dur, s_app = self.parse_smtc_playing()
                s_weight = 1 if s_app and any(b in s_app.lower() for b in ["chrome", "msedge", "firefox", "brave", "opera"]) else 5
                events.append({'artist': s_artist, 'track': s_track, 'pos': s_pos, 'dur': s_dur, 'type': 'music', 'weight': s_weight})

                active_event = None
                for ev in events:
                    if ev['artist']:
                        if ev['weight'] >= self.current_active_weight:
                            self.current_active_weight = ev['weight']
                            active_event = ev
                    else:
                        if ev['weight'] == self.current_active_weight:
                            self.current_active_weight = 0

                if active_event:
                    artist = active_event['artist']
                    track = active_event['track']
                    media_type = active_event['type']
                    dur = active_event['dur']
                    pos = active_event['pos']
                    
                    track_uid = f"{artist} - {track}"
                    
                    if media_type == "video":
                        diag_title, diag_year = self.normalize_metadata(track)
                        self.last_parsed_media = f"V://{diag_title} {diag_year}"
                    else:
                        self.last_parsed_media = f"M://{artist} - {track}"
                    
                    if track_uid != self.current_track_uid:
                        self.raw_artist = artist
                        self.raw_track = track
                        self.current_track_uid = track_uid
                        self.track_start_time = int(time.time())
                        self.scrobble_submitted = False
                        self.stream_active = True
                        
                        if media_type == "video":
                            if self.get_conf("Trakt", "access_token"):
                                self.send_to_trakt("start", track, progress=0.0)
                        else:
                            if self.get_conf("LastFM", "session_key"):
                                self.send_to_lastfm("track.updateNowPlaying", artist, track)
                            if self.get_conf("ListenBrainz", "user_token"):
                                self.send_to_listenbrainz("playing_now", artist, track)
                    
                    if not self.scrobble_submitted:
                        elapsed = int(time.time()) - self.track_start_time
                        
                        target_seconds = 240
                        if dur > 0:
                            target_seconds = min((dur / 1000) / 2, 240)
                            
                        if elapsed >= target_seconds:
                            if media_type == "video":
                                if self.get_conf("Trakt", "access_token"):
                                    t_ok = self.send_to_trakt("stop", track, progress=100.0)
                                    if not t_ok:
                                        with sqlite3.connect(DB_FILE) as conn:
                                            conn.execute("INSERT INTO cache (artist, track, timestamp, target, media_type, status) VALUES (?, ?, ?, 'trakt', 'video', 0)", (artist, track, self.track_start_time))
                            else:
                                if self.get_conf("LastFM", "session_key"):
                                    lf_ok = self.send_to_lastfm("track.scrobble", artist, track, timestamp=self.track_start_time)
                                    if not lf_ok:
                                        with sqlite3.connect(DB_FILE) as conn:
                                            conn.execute("INSERT INTO cache (artist, track, timestamp, target, media_type, status) VALUES (?, ?, ?, 'lastfm', 'music', 0)", (artist, track, self.track_start_time))
                                
                                if self.get_conf("ListenBrainz", "user_token"):
                                    lb_ok = self.send_to_listenbrainz("single", artist, track, timestamp=self.track_start_time)
                                    if not lb_ok:
                                        with sqlite3.connect(DB_FILE) as conn:
                                            conn.execute("INSERT INTO cache (artist, track, timestamp, target, media_type, status) VALUES (?, ?, ?, 'listenbrainz', 'music', 0)", (artist, track, self.track_start_time))
                                            
                            self.scrobble_submitted = True
                else:
                    self.stream_active = False
                    self.current_track_uid = None
                    self.last_parsed_media = "AWAITING..."
                    
                self.process_cached_scrobbling()
            except Exception as loop_err:
                write_debug_log("MONITOR_THREAD_LOOP_CRITICAL_FAILURE", loop_err)
            time.sleep(4)

    def toggle_service(self):
        if not self.is_running:
            self.is_running = True
            self.btn_toggle.config(text="[ DISCONNECT_LINK ]")
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.is_running = False
            self.stream_active = False
            self.raw_artist = ""
            self.raw_track = ""
            self.current_track_uid = None
            self.current_active_weight = 0
            self.btn_toggle.config(text="[ INITIALIZE_LINK ]")

if __name__ == "__main__":
    try:
        instance_lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        instance_lock_socket.bind(('127.0.0.1', 14224))
        instance_lock_socket.listen(1)
    except socket.error:
        sys.exit(0)

    root = tk.Tk()
    app = LotusApp(root)
    root.mainloop()
