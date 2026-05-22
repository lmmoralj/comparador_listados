import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from .reader import read_fallecidos, read_citas, ReaderError
from .comparator import compare_data
from .report_writer import write_report
from .utils import VALID_EXTENSIONS, ensure_dirs, ts_name

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Comparador Fallecidos vs Citas')
        self.geometry('920x620')
        self.a1 = tk.StringVar(); self.a2 = tk.StringVar()
        self.solo = tk.BooleanVar(value=True)
        self.umbral = tk.StringVar(value='90')
        self._ui()

    def _ui(self):
        f = ttk.Frame(self, padding=12); f.pack(fill='both', expand=True)
        ttk.Button(f, text='Seleccionar Archivo1 — Fallecidos', command=lambda: self._pick(self.a1)).pack(fill='x')
        ttk.Label(f, textvariable=self.a1).pack(fill='x')
        ttk.Button(f, text='Seleccionar Archivo2 — Citas', command=lambda: self._pick(self.a2)).pack(fill='x', pady=(8,0))
        ttk.Label(f, textvariable=self.a2).pack(fill='x')
        ttk.Checkbutton(f, text='Analizar solo citas pendientes', variable=self.solo).pack(anchor='w', pady=8)
        ttk.Label(f, text='Umbral similitud (%)').pack(anchor='w')
        ttk.Entry(f, textvariable=self.umbral).pack(anchor='w')
        ttk.Button(f, text='Ejecutar comparación', command=self.run).pack(fill='x', pady=8)
        self.pb = ttk.Progressbar(f, maximum=100, mode='determinate'); self.pb.pack(fill='x')
        self.log = tk.Text(f, height=18); self.log.pack(fill='both', expand=True, pady=8)
        ttk.Button(f, text='Abrir carpeta de reportes', command=self.open_reports).pack(fill='x')

    def _pick(self, var):
        p = filedialog.askopenfilename(filetypes=[('Excel','*.xlsx *.xls *.xlsm')])
        if p: var.set(p)

    def run(self):
        try:
            self.pb['value']=5
            p1,p2 = self.a1.get().strip(), self.a2.get().strip()
            for p in [p1,p2]:
                if not p or not Path(p).exists() or Path(p).suffix.lower() not in VALID_EXTENSIONS:
                    raise ValueError('Seleccione ambos archivos Excel válidos.')
            um = int(self.umbral.get())
            if not (0 <= um <= 100):
                raise ValueError('Umbral entre 0 y 100.')
            d1,l1 = read_fallecidos(p1); self.pb['value']=30
            d2,l2 = read_citas(p2); self.pb['value']=55
            res = compare_data(d1,d2,threshold=um,solo_pendientes=self.solo.get()); self.pb['value']=80
            root = Path(__file__).resolve().parents[1]; ensure_dirs(root)
            out = root/'reportes_generados'/f'Reporte_Fallecidos_vs_Citas_{ts_name()}.xlsx'
            meta = {
                'archivo1': Path(p1).name, 'archivo2': Path(p2).name, 'total_fallecidos': len(d1), 'total_citas': len(d2),
                'total_citas_analizadas': len(res['citas']), 'solo_pendientes': self.solo.get(),
                'dup_cedula_a1': int(res['fallecidos']['cedula_norm'].duplicated().sum()),
                'dup_cedula_a2': int(res['citas']['cedula_norm'].duplicated().sum()),
                'cedulas_invalidas': int((~res['fallecidos']['cedula_ok']).sum() + (~res['citas']['cedula_ok']).sum()),
                'revision': len(res['cedula_nombre_diff']) + len(res['nombre_exacto']) + len(res['posible_nombre'])
            }
            write_report(out, res, meta, l1+l2+res['logs']); self.pb['value']=100
            self._log(f'Reporte generado: {out}')
            messagebox.showinfo('Éxito', f'Reporte generado:\n{out}')
        except (ValueError, ReaderError) as e:
            self._log(f'ERROR: {e}')
            messagebox.showerror('Error', str(e))

    def _log(self,m):
        self.log.insert('end', m+'\n'); self.log.see('end')

    def open_reports(self):
        root = Path(__file__).resolve().parents[1]; ensure_dirs(root)
        folder = root/'reportes_generados'
        if os.name=='nt':
            os.startfile(folder)
