"""
Interfaz gráfica para la conciliación bancaria.
Requiere: conciliar_v3.py en la misma carpeta.
Las rutas se guardan automáticamente en conciliar_config.json.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import json
import sys
import os
import io
from pathlib import Path

# ── Ubicación del script (robusto en Windows con doble clic) ─────────────────
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except Exception:
    SCRIPT_DIR = Path(os.path.abspath(sys.argv[0])).parent

CONFIG_FILE  = SCRIPT_DIR / "conciliar_config.json"
MOTOR_ERROR  = None

# ── Importar el motor de conciliación ────────────────────────────────────────
sys.path.insert(0, str(SCRIPT_DIR))
try:
    import conciliar_v3 as motor
    MOTOR_OK = True
except Exception as _e:
    MOTOR_OK    = False
    MOTOR_ERROR = str(_e)



def verificar_dependencias():
    """Devuelve lista de paquetes faltantes."""
    faltantes = []
    for pkg, install_name in [
        ("pandas",     "pandas"),
        ("openpyxl",   "openpyxl"),
        ("pdfplumber", "pdfplumber"),
    ]:
        try:
            __import__(pkg)
        except ImportError:
            faltantes.append(install_name)
    return faltantes


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
def cargar_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def guardar_config(data):
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conciliación Bancaria – DPT")
        self.resizable(False, False)
        self._config = cargar_config()
        self._build_ui()
        self._restore_paths()
        self._after(100, self._check_deps)

    # ── Verificación de dependencias ─────────────────────────────────────────
    def _after(self, ms, fn):
        self.after(ms, fn)

    def _check_deps(self):
        faltantes = verificar_dependencias()
        if faltantes:
            pkgs = " ".join(faltantes)
            msg  = (f"Faltan los siguientes paquetes de Python:\n\n"
                    f"  {', '.join(faltantes)}\n\n"
                    f"Abrí una terminal (cmd) y ejecutá:\n\n"
                    f"  pip install {pkgs}\n\n"
                    f"Después reiniciá la aplicación.")
            messagebox.showwarning("Dependencias faltantes", msg)
            self._log(f"⚠  Instalar: pip install {pkgs}", "warn")
        elif not MOTOR_OK:
            self._log(f"⚠  No se pudo cargar conciliar_v3.py: {MOTOR_ERROR}", "error")
            self._log(f"   Carpeta buscada: {SCRIPT_DIR}", "warn")

    # ── Construcción de la UI ─────────────────────────────────────────────────
    def _build_ui(self):
        AZUL     = "#1F4E79"
        AZUL_CLR = "#2E75B6"
        BG       = "#F5F7FA"
        FONT     = ("Segoe UI", 10)
        FONT_B   = ("Segoe UI", 10, "bold")
        FONT_T   = ("Segoe UI", 13, "bold")

        self.configure(bg=BG)

        # ── Título ────────────────────────────────────────────────────────────
        frm_title = tk.Frame(self, bg=AZUL, pady=14)
        frm_title.pack(fill="x")
        tk.Label(frm_title, text="Conciliación Bancaria",
                 bg=AZUL, fg="white", font=FONT_T).pack()
        tk.Label(frm_title, text="Fundación DPT",
                 bg=AZUL, fg="#BDD7EE", font=("Segoe UI", 9)).pack()

        # ── Formulario ────────────────────────────────────────────────────────
        frm = tk.Frame(self, bg=BG, padx=24, pady=18)
        frm.pack(fill="x")

        def fila_ruta(parent, label, row, key, es_guardar=False):
            tk.Label(parent, text=label, bg=BG, font=FONT_B,
                     anchor="w").grid(row=row, column=0, sticky="w", pady=(8,0))
            var = tk.StringVar()
            entry = tk.Entry(parent, textvariable=var, width=52, font=FONT,
                             relief="solid", bd=1)
            entry.grid(row=row+1, column=0, sticky="ew", padx=(0,8))

            def browse():
                if es_guardar:
                    p = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        filetypes=[("Excel", "*.xlsx")],
                        title="Guardar conciliación como…"
                    )
                else:
                    p = filedialog.askopenfilename(
                        filetypes=[("Excel", "*.xlsx *.xls")],
                        title=f"Seleccionar {label}"
                    )
                if p:
                    var.set(p)
                    self._save_field(key, p)

            btn = tk.Button(parent, text="Examinar…", command=browse,
                            bg=AZUL_CLR, fg="white", font=FONT,
                            relief="flat", padx=10, cursor="hand2")
            btn.grid(row=row+1, column=1, sticky="w")
            parent.columnconfigure(0, weight=1)

            # Guardar al escribir a mano
            var.trace_add("write", lambda *_: self._save_field(key, var.get()))
            return var

        self.var_banco_archivo = fila_ruta(frm, "Archivo Santander (.xlsx)", 0, "banco_archivo")
        self.var_mp_archivo    = fila_ruta(frm, "Archivo MP (.xlsx)  — opcional", 2, "mp_archivo")
        self.var_gastos        = fila_ruta(frm, "Detalle de gastos (.xlsx)", 4, "gastos_archivo")
        self.var_salida        = fila_ruta(frm, "Guardar resultado en…",     6, "salida_archivo",
                                           es_guardar=True)

        # ── Botón ejecutar ────────────────────────────────────────────────────
        frm_btn = tk.Frame(self, bg=BG, pady=4)
        frm_btn.pack(fill="x", padx=24)
        self.btn_run = tk.Button(
            frm_btn, text="▶  Ejecutar conciliación",
            command=self._ejecutar,
            bg=AZUL, fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=20, pady=8, cursor="hand2",
            activebackground="#163B5C", activeforeground="white"
        )
        self.btn_run.pack(fill="x")

        # ── Log / resultado ───────────────────────────────────────────────────
        tk.Label(self, text="Resultado", bg=BG,
                 font=FONT_B, anchor="w").pack(anchor="w", padx=24, pady=(14, 2))
        self.log = scrolledtext.ScrolledText(
            self, width=72, height=12, font=("Consolas", 9),
            bg="#1E1E2E", fg="#CDD6F4", insertbackground="white",
            relief="flat", padx=8, pady=8, state="disabled"
        )
        self.log.pack(padx=24, pady=(0, 20))

        # Colores para el log
        self.log.tag_config("ok",    foreground="#A6E3A1")
        self.log.tag_config("error", foreground="#F38BA8")
        self.log.tag_config("info",  foreground="#89DCEB")
        self.log.tag_config("warn",  foreground="#FAB387")

    # ── Persistencia ─────────────────────────────────────────────────────────
    def _restore_paths(self):
        self.var_banco_archivo.set(self._config.get("banco_archivo", ""))
        self.var_mp_archivo.set(self._config.get("mp_archivo", ""))
        self.var_gastos.set(self._config.get("gastos_archivo", ""))
        self.var_salida.set(self._config.get("salida_archivo", ""))

    def _save_field(self, key, value):
        self._config[key] = value
        guardar_config(self._config)

    # ── Log helpers ───────────────────────────────────────────────────────────
    def _log(self, text, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _log_clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    # ── Ejecución ─────────────────────────────────────────────────────────────
    def _ejecutar(self):
        if not MOTOR_OK:
            detail = f"\n\nDetalle técnico:\n{MOTOR_ERROR}" if MOTOR_ERROR else ""
            messagebox.showerror("Error al cargar el motor",
                f"No se pudo cargar conciliar_v3.py.\n"
                f"Carpeta buscada: {SCRIPT_DIR}\n"
                f"Asegurate de tener ambos archivos juntos "
                f"e instalar las dependencias (pandas, openpyxl, pdfplumber).{detail}")
            return

        santander = self.var_banco_archivo.get().strip()
        mp_archivo = self.var_mp_archivo.get().strip()
        gastos     = self.var_gastos.get().strip()
        salida     = self.var_salida.get().strip()

        errores = []
        if not santander or not Path(santander).exists():
            errores.append("• El archivo Santander no existe o no fue seleccionado.")
        if mp_archivo and not Path(mp_archivo).exists():
            errores.append("• El archivo MP fue ingresado pero no existe.")
        if not gastos or not Path(gastos).exists():
            errores.append("• El detalle de gastos no existe o no fue seleccionado.")
        if not salida:
            errores.append("• Falta indicar dónde guardar el resultado.")

        if errores:
            messagebox.showwarning("Datos incompletos", "\n".join(errores))
            return

        self.btn_run.configure(state="disabled", text="⏳  Procesando…")
        self._log_clear()
        modo = "Santander + MP" if mp_archivo else "solo Santander"
        self._log(f"Iniciando conciliación ({modo})…", "info")

        def run():
            old_stdout = sys.stdout
            sys.stdout = buf = io.StringIO()
            try:
                if mp_archivo:
                    motor.main(santander, gastos, "Santander", salida, mp_archivo, "MP")
                else:
                    motor.main(santander, gastos, "Santander", salida)
                output = buf.getvalue()
                for line in output.strip().splitlines():
                    tag = "ok" if "OK" in line or "Guardado" in line else \
                          "warn" if "Sin" in line or "Revisar" in line else "info"
                    self.after(0, lambda l=line, t=tag: self._log(l, t))
                self.after(0, lambda: self._log("\n✅  Archivo guardado correctamente.", "ok"))
                self.after(0, lambda: messagebox.showinfo("Listo",
                    f"Conciliación completada.\n\nArchivo guardado en:\n{salida}"))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda m=err_msg: self._log(f"\n❌  Error: {m}", "error"))
                self.after(0, lambda m=err_msg: messagebox.showerror("Error al ejecutar", m))
            finally:
                sys.stdout = old_stdout
                self.after(0, lambda: self.btn_run.configure(
                    state="normal", text="▶  Ejecutar conciliación"))

        threading.Thread(target=run, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
