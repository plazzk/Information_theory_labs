import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os

# ------------------------------------------------------------
# Математические алгоритмы
# ------------------------------------------------------------
def fast_exp(a, z, n):
    return pow(a, z, n)

def extended_gcd(a, b):
    if b == 0:
        return 1, 0, a
    x1, y1, g = extended_gcd(b, a % b)
    return y1, x1 - (a // b) * y1, g

def mod_inverse(a, m):
    x, y, g = extended_gcd(a, m)
    return x % m if g == 1 else None

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

# ------------------------------------------------------------
# Хеш-функция (регистрозависимая через ord)
# ------------------------------------------------------------
def char_code(ch):
    return ord(ch)

def compute_hash(text, n, H0=100):
    H = H0
    for ch in text:
        Mi = char_code(ch)
        H = (H + Mi) ** 2 % n
    return H % n   # важно!

# ------------------------------------------------------------
# RSA операции
# ------------------------------------------------------------
def compute_r_and_e(p, q, d):
    r = p * q
    phi = (p - 1) * (q - 1)
    e = mod_inverse(d, phi)
    return r, phi, e

def sign_message(hash_val, d, r):
    return fast_exp(hash_val, d, r)

def verify_signature(signature, e, r):
    return fast_exp(signature, e, r)

# ------------------------------------------------------------
# GUI
# ------------------------------------------------------------
DARK_BG   = "#0f1117"
PANEL_BG  = "#1a1d27"
ACCENT    = "#4f8ef7"
ACCENT2   = "#7c3aed"
SUCCESS   = "#22c55e"
DANGER    = "#ef4444"
TEXT_MAIN = "#e2e8f0"
TEXT_DIM  = "#64748b"
BORDER    = "#2a2d3e"
ENTRY_BG  = "#12151f"

FONT_MONO   = ("Courier New", 10)
FONT_LABEL  = ("Segoe UI", 10)
FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_FORMULA = ("Courier New", 9)

class RSAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЭЦП на основе RSA")
        self.geometry("980x880")
        self.configure(bg=DARK_BG)
        self.resizable(True, True)

        self._build_header()
        self._build_notebook()
        self._build_status()

        self._last_r = self._last_phi = self._last_e = None
        self._computed_r = self._computed_phi = self._computed_d = None
        self._signed_content = None

    # --------------------------------------------------------
    # Вспомогательные виджеты
    # --------------------------------------------------------
    def _build_header(self):
        hdr = tk.Frame(self, bg=PANEL_BG, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🔐", bg=PANEL_BG, fg=ACCENT, font=("Segoe UI", 20)).pack(side="left", padx=(20,8))
        tk.Label(hdr, text="ЭЦП на основе RSA", bg=PANEL_BG, fg=TEXT_MAIN, font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text="Лабораторная работа №4", bg=PANEL_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side="right", padx=20)
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

    def _build_notebook(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Dark.TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab", background=PANEL_BG, foreground=TEXT_DIM,
                        font=FONT_BTN, padding=[16,6], borderwidth=0)
        style.map("Dark.TNotebook.Tab", background=[("selected", ACCENT), ("active", BORDER)],
                  foreground=[("selected", "#fff"), ("active", TEXT_MAIN)])
        nb = ttk.Notebook(self, style="Dark.TNotebook")
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        self._sign_tab(nb)
        self._verify_tab(nb)

    def _section(self, parent, title, padx=15, pady=(10,2)):
        f = tk.Frame(parent, bg=DARK_BG)
        f.pack(fill="x", padx=padx, pady=pady)
        tk.Label(f, text=title, bg=DARK_BG, fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=8)

    def _lbl(self, parent, text, fg=TEXT_DIM, font=None):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=fg,
                        font=font or FONT_LABEL)

    def _entry(self, parent, width=12):
        e = tk.Entry(parent, width=width, bg=ENTRY_BG, fg=TEXT_MAIN,
                     insertbackground=ACCENT, relief="flat", font=FONT_MONO, bd=5)
        return e

    def _btn(self, parent, text, cmd, color, width=None):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white",
                         font=FONT_BTN, relief="flat", cursor="hand2", padx=12, pady=4,
                         activebackground=color, activeforeground="white", width=width)

    def _build_status(self):
        sf = tk.Frame(self, bg=PANEL_BG, height=26)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)
        self.status_lbl = tk.Label(sf, text="Готово.", bg=PANEL_BG, fg=TEXT_DIM, font=FONT_SMALL)
        self.status_lbl.pack(side="left", padx=12)

    def _status(self, msg, color=TEXT_DIM):
        self.status_lbl.configure(text=msg, fg=color)
        self.update_idletasks()

    # --------------------------------------------------------
    # Вкладка ПОДПИСАТЬ
    # --------------------------------------------------------
    def _sign_tab(self, nb):
        frame = tk.Frame(nb, bg=DARK_BG)
        nb.add(frame, text="  ✏  Подписать  ")

        canvas = tk.Canvas(frame, bg=DARK_BG, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=DARK_BG)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_resize)

        # ----- Ввод p, q, d -----
        self._section(inner, "Закрытый ключ (p, q, d)")
        pf = tk.Frame(inner, bg=DARK_BG)
        pf.pack(fill="x", padx=15, pady=4)
        self._lbl(pf, "p:").grid(row=0, column=0, padx=(0,4), sticky="e")
        self.p_entry = self._entry(pf, 8)
        self.p_entry.grid(row=0, column=1, padx=(0,15))
        self._lbl(pf, "q:").grid(row=0, column=2, padx=(0,4), sticky="e")
        self.q_entry = self._entry(pf, 8)
        self.q_entry.grid(row=0, column=3, padx=(0,15))
        self._lbl(pf, "d:").grid(row=0, column=4, padx=(0,4), sticky="e")
        self.d_entry = self._entry(pf, 8)
        self.d_entry.grid(row=0, column=5)
        self._btn(pf, "Вычислить ключи", self._compute_keys, ACCENT, width=14).grid(row=0, column=6, padx=(15,0))
        self._lbl(pf, "1 < d < φ(r), НОД(d,φ(r))=1", fg=TEXT_DIM, font=FONT_SMALL).grid(row=1, column=0, columnspan=7, pady=(2,0), sticky="w")

        # ----- Вычисленные ключи (с формулами) -----
        self._section(inner, "Вычисленные ключи")
        kf = tk.Frame(inner, bg=PANEL_BG)
        kf.pack(fill="x", padx=15, pady=4)
        # r
        row_r = tk.Frame(kf, bg=PANEL_BG)
        row_r.pack(fill="x", padx=8, pady=2)
        self.lbl_r_text = self._lbl(row_r, "r = p·q = ", fg=TEXT_DIM)
        self.lbl_r_text.pack(side="left")
        self.lbl_r = self._lbl(row_r, "—", fg=ACCENT, font=FONT_MONO)
        self.lbl_r.pack(side="left")
        # φ
        row_phi = tk.Frame(kf, bg=PANEL_BG)
        row_phi.pack(fill="x", padx=8, pady=2)
        self.lbl_phi_text = self._lbl(row_phi, "φ(r) = (p-1)(q-1) = ", fg=TEXT_DIM)
        self.lbl_phi_text.pack(side="left")
        self.lbl_phi = self._lbl(row_phi, "—", fg=ACCENT2, font=FONT_MONO)
        self.lbl_phi.pack(side="left")
        # e
        row_e = tk.Frame(kf, bg=PANEL_BG)
        row_e.pack(fill="x", padx=8, pady=2)
        self.lbl_e_text = self._lbl(row_e, "e = d⁻¹ mod φ(r) = ", fg=TEXT_DIM)
        self.lbl_e_text.pack(side="left")
        self.lbl_e = self._lbl(row_e, "—", fg=SUCCESS, font=FONT_MONO)
        self.lbl_e.pack(side="left")

        # ----- Сообщение -----
        self._section(inner, "Сообщение")
        msgf = tk.Frame(inner, bg=DARK_BG)
        msgf.pack(fill="x", padx=15, pady=4)
        btn_row = tk.Frame(msgf, bg=DARK_BG)
        btn_row.pack(fill="x", pady=(0,4))
        self._btn(btn_row, "Открыть файл", self._load_file_sign, ACCENT2).pack(side="left")
        self._lbl(btn_row, "  или введите текст:").pack(side="left")
        self.sign_file_label = self._lbl(btn_row, "", fg=ACCENT, font=FONT_SMALL)
        self.sign_file_label.pack(side="left", padx=(10,0))
        self.msg_text = scrolledtext.ScrolledText(msgf, height=5, wrap="word",
                                                  bg=ENTRY_BG, fg=TEXT_MAIN,
                                                  font=FONT_MONO, relief="flat", bd=4)
        self.msg_text.pack(fill="x")

        # ----- Результаты подписи -----
        self._section(inner, "Результаты подписи")
        resf = tk.Frame(inner, bg=PANEL_BG)
        resf.pack(fill="x", padx=15, pady=4)
        # Хеш
        row_h = tk.Frame(resf, bg=PANEL_BG)
        row_h.pack(fill="x", padx=8, pady=2)
        self._lbl(row_h, "h(M) = хеш (H₀=100, Hᵢ=(Hᵢ₋₁+ord(Mᵢ))² mod r) = ",
                  fg=TEXT_DIM).pack(side="left")
        self.hash_label = self._lbl(row_h, "—", fg=SUCCESS, font=FONT_MONO)
        self.hash_label.pack(side="left")
        # Подпись
        row_s = tk.Frame(resf, bg=PANEL_BG)
        row_s.pack(fill="x", padx=8, pady=2)
        self._lbl(row_s, "S = h(M)ᵈ mod r = ", fg=TEXT_DIM).pack(side="left")
        self.sig_label = self._lbl(row_s, "—", fg=ACCENT, font=FONT_MONO)
        self.sig_label.pack(side="left")

        self._btn(inner, "🔏 Подписать сообщение", self._do_sign, SUCCESS).pack(anchor="w", padx=15, pady=6)

        # ----- Подписанный файл -----
        self._section(inner, "Подписанный файл (сообщение\\nS)")
        self.signed_display = scrolledtext.ScrolledText(inner, height=3, wrap="word",
                                                        bg=ENTRY_BG, fg=TEXT_MAIN,
                                                        font=FONT_MONO, relief="flat", bd=4,
                                                        state="disabled")
        self.signed_display.pack(fill="x", padx=15, pady=4)
        self._btn(inner, "Сохранить подписанный файл", self._save_signed, ACCENT).pack(anchor="w", padx=15, pady=4)

    def _compute_keys(self):
        try:
            p = int(self.p_entry.get().strip())
            q = int(self.q_entry.get().strip())
            d = int(self.d_entry.get().strip())
            if not (is_prime(p) and is_prime(q)):
                raise ValueError("p и q должны быть простыми")
            if p == q:
                raise ValueError("p и q должны быть различными")
            if d <= 1:
                raise ValueError("d должно быть > 1")

            r, phi, e = compute_r_and_e(p, q, d)
            if e is None:
                raise ValueError(f"d и φ(r)={phi} не взаимно просты (НОД(d, φ(r)) != 1)")

            if d >= phi:
                raise ValueError(f"d должно быть меньше φ(r) = {phi} (получено d={d})")

            self._computed_r, self._computed_phi, self._computed_d = r, phi, d
            self._last_r, self._last_phi, self._last_e = r, phi, e
            self.lbl_r_text.config(text=f"r = {p}·{q} = ")
            self.lbl_r.config(text=str(r))
            self.lbl_phi_text.config(text=f"φ(r) = ({p}-1)({q}-1) = ")
            self.lbl_phi.config(text=str(phi))
            self.lbl_e_text.config(text=f"e = d⁻¹ mod φ(r) = ")
            self.lbl_e.config(text=str(e))
            self._status(f"Ключи: r={r}, φ={phi}, e={e}", SUCCESS)
        except Exception as ex:
            messagebox.showerror("Ошибка", str(ex))
            self._status("Ошибка", DANGER)

    def _load_file_sign(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.msg_text.delete("1.0", "end")
                    self.msg_text.insert("1.0", f.read())
                self.sign_file_label.config(text=os.path.basename(path))
                self._status(f"Загружен: {os.path.basename(path)}")
            except Exception as ex:
                messagebox.showerror("Ошибка", str(ex))

    def _do_sign(self):
        if self._computed_r is None:
            messagebox.showwarning("Нет ключей", "Сначала вычислите ключи.")
            return
        msg = self.msg_text.get("1.0", "end").rstrip("\n")
        try:
            h = compute_hash(msg, self._computed_r)
            S = sign_message(h, self._computed_d, self._computed_r)
            self.hash_label.config(text=str(h))
            self.sig_label.config(text=str(S))
            signed = msg + "\n" + str(S)
            self.signed_display.config(state="normal")
            self.signed_display.delete("1.0", "end")
            self.signed_display.insert("1.0", signed)
            self.signed_display.config(state="disabled")
            self._signed_content = signed
            self._status(f"Подписано. h={h}, S={S}", SUCCESS)
        except Exception as ex:
            messagebox.showerror("Ошибка", str(ex))

    def _save_signed(self):
        if not self._signed_content:
            messagebox.showwarning("Нет данных", "Сначала подпишите.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._signed_content)
            self._status(f"Сохранён: {os.path.basename(path)}", SUCCESS)

    # --------------------------------------------------------
    # Вкладка ПРОВЕРИТЬ
    # --------------------------------------------------------
    def _verify_tab(self, nb):
        frame = tk.Frame(nb, bg=DARK_BG)
        nb.add(frame, text="  🔍  Проверить  ")
        inner = tk.Frame(frame, bg=DARK_BG)
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        self._section(inner, "Открытый ключ (e, r)")
        kf = tk.Frame(inner, bg=DARK_BG)
        kf.pack(fill="x", pady=4)
        self._lbl(kf, "e:").pack(side="left", padx=(0,4))
        self.v_e = self._entry(kf, 10)
        self.v_e.pack(side="left", padx=(0,15))
        self._lbl(kf, "r:").pack(side="left", padx=(0,4))
        self.v_r = self._entry(kf, 14)
        self.v_r.pack(side="left")
        self._btn(kf, "Вставить из подписи", self._fill_e_r_phi, ACCENT2).pack(side="left", padx=15)
        self.v_phi_info = self._lbl(kf, "", fg=TEXT_DIM, font=FONT_SMALL)
        self.v_phi_info.pack(side="left", padx=(10,0))

        self._section(inner, "Файл с подписью")
        mf = tk.Frame(inner, bg=DARK_BG)
        mf.pack(fill="x", pady=4)
        self._btn(mf, "Выбрать файл", self._load_signed_file, ACCENT2).pack(side="left")
        self.v_file_lbl = self._lbl(mf, "  файл не выбран")
        self.v_file_lbl.pack(side="left")

        self._section(inner, "Содержимое файла")
        self.v_content = scrolledtext.ScrolledText(inner, height=5, wrap="word",
                                                   bg=ENTRY_BG, fg=TEXT_MAIN,
                                                   font=FONT_MONO, relief="flat", bd=4,
                                                   state="disabled")
        self.v_content.pack(fill="x", pady=4)

        self._section(inner, "Результат проверки")
        resf = tk.Frame(inner, bg=PANEL_BG)
        resf.pack(fill="x", pady=4)
        for txt, attr, color in [
            ("h(M') = хеш принятого сообщения = ", "v_hash_new", ACCENT),
            ("h' = хеш подписи = Sᵉ mod r = ", "v_hash_sig", ACCENT),
            ("S = подпись= ", "v_sig", TEXT_DIM)
        ]:
            row = tk.Frame(resf, bg=PANEL_BG)
            row.pack(fill="x", padx=8, pady=2)
            self._lbl(row, txt, fg=TEXT_DIM).pack(side="left")
            lbl = self._lbl(row, "—", fg=color, font=FONT_MONO)
            lbl.pack(side="left")
            setattr(self, attr, lbl)

        self.verdict_lbl = tk.Label(resf, text="", bg=PANEL_BG, font=("Segoe UI", 11, "bold"),
                                    wraplength=700, justify="left")
        self.verdict_lbl.pack(fill="x", padx=8, pady=8)

        self._btn(inner, "✅ Проверить подпись", self._do_verify, SUCCESS).pack(anchor="w")

        self._v_file_content = None

    def _fill_e_r_phi(self):
        if self._last_e is not None and self._last_r is not None:
            self.v_e.delete(0, tk.END); self.v_e.insert(0, str(self._last_e))
            self.v_r.delete(0, tk.END); self.v_r.insert(0, str(self._last_r))
            if self._last_phi is not None:
                self.v_phi_info.config(text=f"φ(r)={self._last_phi}")
            self._status("Поля e и r заполнены", SUCCESS)
        else:
            messagebox.showinfo("Нет данных", "Сначала вычислите ключи на вкладке «Подписать».")

    def _load_signed_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._v_file_content = f.read()
            self.v_file_lbl.config(text=f"  {os.path.basename(path)}", fg=ACCENT)
            self.v_content.config(state="normal")
            self.v_content.delete("1.0", "end")
            self.v_content.insert("1.0", self._v_file_content)
            self.v_content.config(state="disabled")
            self._status(f"Загружен: {os.path.basename(path)}")
        except Exception as ex:
            messagebox.showerror("Ошибка", str(ex))

    def _do_verify(self):
        try:
            e = int(self.v_e.get().strip())
            r = int(self.v_r.get().strip())
            if r <= 1 or e <= 0: raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите корректные e и r")
            return
        if not self._v_file_content:
            messagebox.showwarning("Нет файла", "Выберите файл.")
            return

        content = self._v_file_content.rstrip("\n")
        lines = content.split("\n")

        # Определяем сообщение и подпись
        if len(lines) == 0:
            messagebox.showerror("Формат", "Файл пуст.")
            return
        elif len(lines) == 1:
            # Только одна строка - считаем её подписью, сообщение пустое
            msg_part = ""
            sig_part = lines[0].strip()
        else:
            # Две и более строк: подпись в последней строке, всё остальное - сообщение
            sig_part = lines[-1].strip()
            msg_part = "\n".join(lines[:-1])

        if not sig_part:
            messagebox.showerror("Ошибка", "Подпись отсутствует.")
            return

        try:
            S = int(sig_part)
        except ValueError:
            messagebox.showerror("Ошибка", f"Подпись не число:\n{sig_part}")
            return

        h_new = compute_hash(msg_part, r)
        h_sig = verify_signature(S, e, r)

        self.v_hash_new.config(text=str(h_new))
        self.v_hash_sig.config(text=str(h_sig))
        self.v_sig.config(text=str(S))

        valid = (h_new == h_sig)
        if valid:
            detail = f"✓ ПОДПИСЬ ВЕРНА\nh(M') = h' = {h_new}\nСообщение не изменено."
        else:
            detail = (f"✗ ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА\n"
                      f"h(M') = {h_new}\nh' = {h_sig}\n"
                      f"Значения не совпадают. Изменены сообщение или подпись, либо неверен ключ.")
        self.verdict_lbl.config(text=detail, fg=SUCCESS if valid else DANGER)
        self._status("Проверка завершена", SUCCESS if valid else DANGER)

if __name__ == "__main__":
    app = RSAApp()
    app.mainloop()