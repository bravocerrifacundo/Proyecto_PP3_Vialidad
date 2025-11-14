import os
import sqlite3
import hashlib
import csv
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry

# Google APIs
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaInMemoryUpload

import sys, os

def resource_path(relative_path):
    """Devuelve la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        base_path = sys._MEIPASS  # Carpeta temporal usada por PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -----------------------------
# CONFIG
# -----------------------------
DB_PATH = "users.db"                  # BD local de usuarios (SQLite)
LOCAL_CSV = "datos_locales.csv"       # Copia local de registros

# ⚠️ PONÉ EL ID DE TU HOJA DE GOOGLE SHEETS:
SHEET_ID = ""

# Carpeta de Drive para backups (ya está configurada)
DRIVE_FOLDER_ID = ""

# Alcances Google APIs
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

HEADERS = [
    "Estado","ID_Expediente","Clasificacion_Norma","Fecha_Inicio","Caratula","Estado_Actual",
    "Prioridad_Expediente","Riesgo_Financiero","Abogado_Asignado","Instancia_Actual",
    "Audiencia_Prevista","Resultado_Final","Cantidad_de_Partes","Monto_Reclamado",
    "Monto_Resuelto","Tipo_Demandante","Dias_en_Etapa","Juzgado","Caratula.1","Abogado_Contraparte",
    "Cargado_por","FechaHora"
]

# -----------------------------
# Google Sheets / Drive
# -----------------------------
def get_gspread_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(resource_path("credentials.json"), SCOPE)
    return gspread.authorize(creds)

def get_drive_service():
    creds = Credentials.from_service_account_file(resource_path("credentials.json"))
    return build("drive", "v3", credentials=creds)

def ensure_headers(sheet):
    try:
        first_row = sheet.row_values(1)
    except Exception:
        first_row = []
    if first_row != HEADERS:
        sheet.clear()
        sheet.update("A1", [HEADERS])

def append_row_to_sheet(row):
    client = get_gspread_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    ensure_headers(sheet)
    sheet.append_row(row, value_input_option="USER_ENTERED")

def read_sheet_as_df():
    import pandas as pd
    client = get_gspread_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    ensure_headers(sheet)
    records = sheet.get_all_records()
    df = pd.DataFrame(records, columns=HEADERS)
    return df

def backup_sheet_to_drive():
    service = get_drive_service()
    data = service.files().export_media(fileId=SHEET_ID, mimeType="text/csv").execute()
    nombre = f"Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_metadata = {"name": nombre, "parents": [DRIVE_FOLDER_ID]}
    media = MediaInMemoryUpload(data, mimetype="text/csv")
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return nombre

# -----------------------------
# CSV local
# -----------------------------
def ensure_local_csv():
    if not os.path.exists(LOCAL_CSV):
        with open(LOCAL_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)

def append_row_local_csv(row):
    ensure_local_csv()
    with open(LOCAL_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

# -----------------------------
# Usuarios (SQLite)
# -----------------------------
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    );
    """)
    con.commit()
    con.close()

def hash_password(pw): return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def verify_user(username, password):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT password_hash, is_admin FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    con.close()
    if not row: return False, False
    return hash_password(password) == row[0], bool(row[1])

def user_exists(username):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    con.close()
    return row is not None

def create_user(username, password, is_admin):
    if user_exists(username):
        raise ValueError("El usuario ya existe.")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?,?,?)",
                (username, hash_password(password), 1 if is_admin else 0))
    con.commit()
    con.close()

def any_admin_exists():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE is_admin=1 LIMIT 1;")
    row = cur.fetchone()
    con.close()
    return row is not None

# -----------------------------
# INTERFAZ: Login
# -----------------------------
class LoginWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Login - Gestión de Expedientes")
        self.geometry("360x260")
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Usuario").grid(row=0, column=0, sticky="w", pady=6)
        self.ent_user = ttk.Entry(frm, width=28)
        self.ent_user.grid(row=0, column=1, pady=6)

        ttk.Label(frm, text="Contraseña").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_pass = ttk.Entry(frm, show="*", width=28)
        self.ent_pass.grid(row=1, column=1, pady=6)

        ttk.Button(frm, text="Ingresar", command=self.login).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        if not any_admin_exists():
            ttk.Separator(frm).grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)
            ttk.Label(frm, text="No hay administrador. Crear uno:").grid(row=4, column=0, columnspan=2, sticky="w")
            ttk.Button(frm, text="Crear Admin", command=self.create_admin_dialog).grid(row=5, column=0, columnspan=2, sticky="ew", pady=4)

    def create_admin_dialog(self):
        u = simpledialog.askstring("Crear Admin", "Usuario admin:", parent=self)
        if not u: return
        p = simpledialog.askstring("Crear Admin", "Contraseña:", parent=self, show="*")
        if not p: return
        try:
            create_user(u, p, True)
            messagebox.showinfo("OK", "Administrador creado con éxito.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def login(self):
        username, password = self.ent_user.get().strip(), self.ent_pass.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Ingresá usuario y contraseña.")
            return
        ok, is_admin = verify_user(username, password)
        if ok:
            self.destroy()
            self.master.open_main(username, is_admin)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# -----------------------------
# INTERFAZ: Registros
# -----------------------------
class RecordsWindow(tk.Toplevel):
    def __init__(self, master, df):
        super().__init__(master)
        self.title("Registros - Google Sheets")
        self.geometry("1200x500")

        cols = HEADERS
        tree = ttk.Treeview(self, columns=cols, show="headings")
        vsb = ttk.Scrollbar(self, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, stretch=True)

        for _, row in df.iterrows():
            tree.insert("", "end", values=[row.get(c, "") for c in cols])

# -----------------------------
# INTERFAZ: Principal
# -----------------------------
import sys, os

def resource_path(relative_path):
    """Devuelve la ruta absoluta, compatible con .exe empaquetado."""
    try:
        base_path = sys._MEIPASS  # Carpeta temporal usada por PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Expedientes")
        self.geometry("980x640")
        self.resizable(True, True)
        self.iconbitmap(resource_path("icono.ico"))
        self.current_user, self.is_admin = None, False
        init_db()
        self.after(100, self.show_login)

    def show_login(self): LoginWindow(self)

    def open_main(self, username, is_admin):
        self.current_user, self.is_admin = username, is_admin
        self.build_ui()

    def build_ui(self):
        for w in self.winfo_children():
            if isinstance(w, ttk.Frame): w.destroy()

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="📋 Gestión de Expedientes", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Label(top, text=f"Usuario: {self.current_user}  |  Rol: {'Admin' if self.is_admin else 'Usuario'}").pack(side="right")
        ttk.Separator(self).pack(fill="x", pady=5)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=False)
        self.inputs = {}

        fields = [
            ("Estado", ttk.Combobox, {"values": ["Activo","Cerrado","Pendiente"]}),
            ("ID_Expediente", ttk.Entry, {}),
            ("Clasificacion_Norma", ttk.Entry, {}),
            ("Fecha_Inicio", DateEntry, {"date_pattern": "yyyy-mm-dd"}),
            ("Caratula", ttk.Entry, {}),
            ("Estado_Actual", ttk.Entry, {}),
            ("Prioridad_Expediente", ttk.Combobox, {"values": ["Alta","Media","Baja"]}),
            ("Riesgo_Financiero", ttk.Combobox, {"values": ["Alto","Medio","Bajo"]}),
            ("Abogado_Asignado", ttk.Entry, {}),
            ("Instancia_Actual", ttk.Entry, {}),
            ("Audiencia_Prevista", ttk.Entry, {}),
            ("Resultado_Final", ttk.Entry, {}),
            ("Cantidad_de_Partes", ttk.Entry, {}),
            ("Monto_Reclamado", ttk.Entry, {}),
            ("Monto_Resuelto", ttk.Entry, {}),
            ("Tipo_Demandante", ttk.Entry, {}),
            ("Dias_en_Etapa", ttk.Entry, {}),
            ("Juzgado", ttk.Entry, {}),
            ("Caratula.1", ttk.Entry, {}),
            ("Abogado_Contraparte", ttk.Entry, {}),
        ]

        for i, (label, widget_cls, opts) in enumerate(fields):
            r, c = divmod(i, 3)
            c *= 2
            ttk.Label(form, text=label).grid(row=r, column=c, sticky="w", padx=4, pady=6)
            w = widget_cls(form, **opts)
            w.grid(row=r, column=c+1, sticky="ew", padx=4, pady=6)
            self.inputs[label] = w
        for i in range(6): form.grid_columnconfigure(i, weight=1)

        btns = ttk.Frame(self, padding=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="💾 Guardar", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(btns, text="📑 Ver registros", command=self.on_view).pack(side="left", padx=5)
        ttk.Button(btns, text="☁️ Backup manual", command=self.on_backup).pack(side="left", padx=5)
        if self.is_admin:
            ttk.Button(btns, text="👤 Agregar usuario (Admin)", command=self.on_add_user).pack(side="right", padx=5)

    def on_save(self):
        try:
            vals = {k: v.get().strip() if hasattr(v, "get") else "" for k, v in self.inputs.items()}
            if not vals["ID_Expediente"]:
                messagebox.showerror("Error", "ID_Expediente es obligatorio.")
                return
            cant = int(vals["Cantidad_de_Partes"] or 0)
            monto_rec = float(vals["Monto_Reclamado"] or 0)
            monto_res = float(vals["Monto_Resuelto"] or 0)
            dias = int(vals["Dias_en_Etapa"] or 0)
            fecha = vals["Fecha_Inicio"] or str(date.today())

            row = [
                vals["Estado"], vals["ID_Expediente"], vals["Clasificacion_Norma"], fecha,
                vals["Caratula"], vals["Estado_Actual"], vals["Prioridad_Expediente"],
                vals["Riesgo_Financiero"], vals["Abogado_Asignado"], vals["Instancia_Actual"],
                vals["Audiencia_Prevista"], vals["Resultado_Final"], cant, monto_rec, monto_res,
                vals["Tipo_Demandante"], dias, vals["Juzgado"], vals["Caratula.1"],
                vals["Abogado_Contraparte"], self.current_user, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            append_row_to_sheet(row)
            append_row_local_csv(row)
            messagebox.showinfo("OK", "Registro guardado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_view(self):
        try:
            import pandas as pd
            df = read_sheet_as_df()
            if df.empty:
                messagebox.showinfo("Info", "No hay datos en la hoja.")
                return
            RecordsWindow(self, df)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_backup(self):
        try:
            nombre = backup_sheet_to_drive()
            messagebox.showinfo("OK", f"Backup creado: {nombre}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_add_user(self):
        if not self.is_admin:
            messagebox.showerror("Error", "Solo el administrador puede crear usuarios.")
            return
        u = simpledialog.askstring("Nuevo usuario", "Nombre de usuario:", parent=self)
        if not u: return
        p = simpledialog.askstring("Nuevo usuario", "Contraseña:", parent=self, show="*")
        if not p: return
        is_admin = messagebox.askyesno("Rol", "¿Hacerlo administrador?")
        try:
            create_user(u, p, is_admin)
            messagebox.showinfo("OK", "Usuario creado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

