import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import random
import struct
from pathlib import Path


# ============== КРИПТОГРАФИЧЕСКИЕ ФУНКЦИИ ==============

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def fast_exp(a, z, n):
    a1 = a
    z1 = z
    x = 1
    while z1 != 0:
        while (z1 % 2) == 0:
            z1 = z1 // 2
            a1 = (a1 * a1) % n
        z1 = z1 - 1
        x = (x * a1) % n
    return x


def is_prime(n, k=5):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = fast_exp(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n):
    if n < 2:
        return 2
    candidate = n + 1 if n % 2 == 0 else n
    while not is_prime(candidate):
        candidate += 2
    return candidate


def prime_factors(n):
    factors = []
    i = 2
    temp = n
    while i * i <= temp:
        if temp % i == 0:
            factors.append(i)
            while temp % i == 0:
                temp //= i
        i += 1
    if temp > 1:
        factors.append(temp)
    return factors


def find_one_primitive_root(p, q_factors):
    phi = p - 1
    while True:
        g = random.randint(2, p - 1)
        is_primitive = True
        for q in q_factors:
            if fast_exp(g, phi // q, p) == 1:
                is_primitive = False
                break
        if is_primitive:
            return g


def find_all_primitive_roots(p):
    if not is_prime(p):
        raise ValueError(f"Число {p} не является простым")

    phi = p - 1
    q_factors = prime_factors(phi)
    g0 = find_one_primitive_root(p, q_factors)

    coprime_numbers = []
    for k in range(1, phi):
        if gcd(k, phi) == 1:
            coprime_numbers.append(k)

    roots = []
    for k in coprime_numbers:
        root = fast_exp(g0, k, p)
        if root not in roots:
            roots.append(root)

    roots.sort()
    return roots


def validate_prime(p):
    if p < 2:
        raise ValueError("p > 1")
    if not is_prime(p):
        raise ValueError(f"{p} не простое")
    return True


def validate_private_key(x, p):
    if x <= 1:
        raise ValueError("x > 1")
    if x >= p - 1:
        raise ValueError(f"x < {p - 1}")
    return True


def validate_k(k, p):
    if k <= 1:
        raise ValueError("k > 1")
    if k >= p - 1:
        raise ValueError(f"k < {p - 1}")
    if gcd(k, p - 1) != 1:
        raise ValueError(f"НОД(k,{p - 1}) = 1")
    return True


def read_file_bytes(filepath):
    with open(filepath, 'rb') as f:
        return list(f.read())


def write_bytes_to_file(filepath, data):
    with open(filepath, 'wb') as f:
        f.write(bytes(data))


def read_encrypted_file(filepath):
    pairs = []
    with open(filepath, 'rb') as f:
        data = f.read()
        for i in range(0, len(data), 8):
            if i + 7 < len(data):
                a = struct.unpack('I', data[i:i + 4])[0]
                b = struct.unpack('I', data[i + 4:i + 8])[0]
                pairs.append((a, b))
    return pairs


def write_encrypted_file(filepath, encrypted_pairs):
    with open(filepath, 'wb') as f:
        for a, b in encrypted_pairs:
            f.write(struct.pack('I', a))
            f.write(struct.pack('I', b))


# ============== ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ==============

class ElGamalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Эль-Гамаль")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)

        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.encrypted_file_path = tk.StringVar()
        self.decrypted_file_path = tk.StringVar()
        self.p_value = tk.StringVar()
        self.g_value = tk.StringVar()
        self.x_value = tk.StringVar()
        self.y_value = tk.StringVar()
        self.k_value = tk.StringVar()
        self.primitive_roots = []

        self.encryption_cancelled = False
        self.decryption_cancelled = False
        self.BATCH_SIZE = 500

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.create_keys_tab()
        self.create_encrypt_tab()
        self.create_decrypt_tab()
        self.create_view_tab()

        self.status_bar = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def create_keys_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Ключи")

        frame_p = ttk.LabelFrame(tab, text="Параметр p (простое число)", padding=10)
        frame_p.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_p, text="p > максимального байта файла (0-255), p > 1").grid(row=0, column=0, columnspan=3,
                                                                                     sticky=tk.W, padx=5, pady=2)

        ttk.Label(frame_p, text="p:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        p_entry = ttk.Entry(frame_p, textvariable=self.p_value, width=15)
        p_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_p, text="Найти корни", command=self.find_primitive_roots).grid(row=1, column=2, padx=10,
                                                                                        pady=5)

        ttk.Label(frame_p, text="Первообразные корни (выберите g):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.g_combobox = ttk.Combobox(frame_p, textvariable=self.g_value, width=40, state='readonly')
        self.g_combobox.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.roots_text = scrolledtext.ScrolledText(frame_p, height=8, width=85, font=('Courier', 9))
        self.roots_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        frame_x = ttk.LabelFrame(tab, text="Закрытый ключ x", padding=10)
        frame_x.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_x, text="1 < x < p-1").grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(frame_x, text="x:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        x_entry = ttk.Entry(frame_x, textvariable=self.x_value, width=15)
        x_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_x, text="Вычислить y", command=self.compute_public_key).grid(row=1, column=2, padx=10, pady=5)

        frame_y = ttk.LabelFrame(tab, text="Открытый ключ y", padding=10)
        frame_y.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_y, text="y = g^x mod p").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        y_display = ttk.Entry(frame_y, textvariable=self.y_value, width=40, state='readonly', font=('Courier', 10))
        y_display.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

    def find_primitive_roots(self):
        try:
            p = int(self.p_value.get())
            self.update_status(f"Поиск корней для p={p}...")
            self.root.update()

            roots = find_all_primitive_roots(p)
            self.primitive_roots = roots

            self.roots_text.delete(1.0, tk.END)
            self.roots_text.insert(tk.END, f"p = {p}\n")
            self.roots_text.insert(tk.END, f"p-1 = {p - 1}\n")
            self.roots_text.insert(tk.END, f"Простые делители p-1: {prime_factors(p - 1)}\n")
            self.roots_text.insert(tk.END, f"Количество первообразных корней: {len(roots)}\n")
            self.roots_text.insert(tk.END, "=" * 60 + "\n")
            self.roots_text.insert(tk.END, "ВСЕ ПЕРВООБРАЗНЫЕ КОРНИ:\n")
            self.roots_text.insert(tk.END, "=" * 60 + "\n")

            line = ""
            for i, r in enumerate(roots):
                line += f"{r:6d} "
                if (i + 1) % 10 == 0:
                    self.roots_text.insert(tk.END, line + "\n")
                    line = ""
            if line:
                self.roots_text.insert(tk.END, line + "\n")

            self.roots_text.insert(tk.END, "=" * 60 + "\n")

            self.g_combobox['values'] = [str(r) for r in roots]
            if roots:
                self.g_combobox.set(str(roots[0]))

            self.update_status(f"Найдено {len(roots)} первообразных корней")

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def compute_public_key(self):
        try:
            p = int(self.p_value.get())
            g = int(self.g_value.get())
            x = int(self.x_value.get())

            validate_prime(p)
            validate_private_key(x, p)

            if not self.primitive_roots:
                roots = find_all_primitive_roots(p)
                self.primitive_roots = roots

            if g not in self.primitive_roots:
                phi = p - 1
                factors = prime_factors(phi)
                for q in factors:
                    if fast_exp(g, phi // q, p) == 1:
                        raise ValueError(f"{g} не первообразный корень")

            y = fast_exp(g, x, p)
            self.y_value.set(str(y))
            self.update_status(f"y = {y}")
            messagebox.showinfo("Успех", f"y = {y}\n\np={p}, g={g}, x={x}")

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def create_encrypt_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Шифрование")

        frame_files = ttk.LabelFrame(tab, text="Файлы", padding=10)
        frame_files.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_files, text="Исходный:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame_files, textvariable=self.input_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_files, text="Обзор", command=self.select_input_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame_files, text="Выходной:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame_files, textvariable=self.output_file_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_files, text="Обзор", command=self.select_output_file).grid(row=1, column=2, padx=5, pady=5)

        frame_params = ttk.LabelFrame(tab, text="Параметры (ограничения)", padding=10)
        frame_params.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_params, text="p: простое, p > 255").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        p_entry = ttk.Entry(frame_params, textvariable=self.p_value, width=15)
        p_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Button(frame_params, text="Найти корни", command=self.find_primitive_roots_for_encrypt).grid(row=0,
                                                                                                         column=2,
                                                                                                         padx=10,
                                                                                                         pady=2)

        ttk.Label(frame_params, text="g: первообразный корень по mod p").grid(row=1, column=0, sticky=tk.W, padx=5,
                                                                              pady=2)
        self.encrypt_g_combo = ttk.Combobox(frame_params, textvariable=self.g_value, width=20, state='readonly')
        self.encrypt_g_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame_params, text="y: открытый ключ (y = g^x mod p)").grid(row=2, column=0, sticky=tk.W, padx=5,
                                                                              pady=2)
        y_entry = ttk.Entry(frame_params, textvariable=self.y_value, width=20)
        y_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame_params, text="k: 1 < k < p-1, НОД(k, p-1)=1 (первый k)").grid(row=3, column=0, sticky=tk.W,
                                                                                      padx=5, pady=2)
        k_entry = ttk.Entry(frame_params, textvariable=self.k_value, width=15)
        k_entry.grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame_params, text="Для КАЖДОГО байта используется СВОЁ уникальное k!", foreground="red",
                  font=('Arial', 10, 'bold')).grid(
            row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        encrypt_btn = ttk.Button(tab, text="ЗАШИФРОВАТЬ", command=self.start_encryption)
        encrypt_btn.pack(pady=10)

        self.encrypt_progress = ttk.Progressbar(tab, mode='determinate')
        self.encrypt_progress.pack(fill=tk.X, padx=10, pady=5)

        self.encrypt_result = scrolledtext.ScrolledText(tab, height=12, font=('Courier', 10))
        self.encrypt_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def find_primitive_roots_for_encrypt(self):
        try:
            p = int(self.p_value.get())
            self.update_status(f"Поиск корней для p={p}...")
            self.root.update()

            roots = find_all_primitive_roots(p)
            self.primitive_roots = roots
            self.encrypt_g_combo['values'] = [str(r) for r in roots]
            if roots:
                self.encrypt_g_combo.set(str(roots[0]))
            self.update_status(f"Найдено {len(roots)} корней")

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def select_input_file(self):
        filepath = filedialog.askopenfilename(title="Выберите файл")
        if filepath:
            self.input_file_path.set(filepath)
            size = Path(filepath).stat().st_size
            self.update_status(f"{Path(filepath).name}, {size} байт")

    def select_output_file(self):
        filepath = filedialog.asksaveasfilename(title="Сохранить как")
        if filepath:
            self.output_file_path.set(filepath)

    def check_file_against_p(self, filepath, p):
        try:
            bytes_data = read_file_bytes(filepath)
            if not bytes_data:
                return True, 0, p
            max_byte = max(bytes_data)
            if max_byte >= p:
                recommended_p = next_prime(max_byte)
                return False, max_byte, recommended_p
            return True, max_byte, p
        except Exception as e:
            raise e

    def start_encryption(self):
        if not self.input_file_path.get():
            messagebox.showwarning("Ошибка", "Выберите исходный файл")
            return
        if not self.output_file_path.get():
            messagebox.showwarning("Ошибка", "Укажите выходной файл")
            return

        try:
            p = int(self.p_value.get())
            g = int(self.g_value.get())
            y = int(self.y_value.get())
            first_k = int(self.k_value.get())

            validate_prime(p)
            validate_k(first_k, p)

            ok, max_byte, recommended_p = self.check_file_against_p(self.input_file_path.get(), p)

            if not ok:
                messagebox.showerror("Ошибка", f"Байт {max_byte} >= p={p}\nРекомендуется p={recommended_p}")
                return

            if not self.primitive_roots:
                roots = find_all_primitive_roots(p)
                self.primitive_roots = roots

            if g not in self.primitive_roots:
                raise ValueError(f"{g} не первообразный корень")

            self.plain_bytes = read_file_bytes(self.input_file_path.get())
            self.total_bytes = len(self.plain_bytes)

            if self.total_bytes == 0:
                messagebox.showwarning("Ошибка", "Файл пуст")
                return

            phi = p - 1
            all_possible_k = [k_val for k_val in range(2, phi) if gcd(k_val, phi) == 1]

            if first_k in all_possible_k:
                all_possible_k.remove(first_k)

            if len(all_possible_k) < self.total_bytes - 1:
                messagebox.showerror("Ошибка", f"Нужно {self.total_bytes - 1} значений k, есть {len(all_possible_k)}")
                return

            if not messagebox.askyesno("Подтверждение",
                                       f"Файл: {Path(self.input_file_path.get()).name}\nРазмер: {self.total_bytes} байт\np={p}\n\nДля КАЖДОГО байта будет своё k!\nПродолжить?"):
                return

            random.shuffle(all_possible_k)
            auto_k_values = all_possible_k[:self.total_bytes - 1]

            self.encrypt_params = {
                'p': p,
                'g': g,
                'y': y,
                'first_k': first_k,
                'auto_k_values': auto_k_values,
                'encrypted_pairs': [],
                'k_list': [first_k]
            }

            self.encryption_cancelled = False
            self.encrypt_result.delete(1.0, tk.END)
            self.encrypt_progress['value'] = 0

            self.encrypt_all_bytes()

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def encrypt_all_bytes(self):
        p = self.encrypt_params['p']
        g = self.encrypt_params['g']
        y = self.encrypt_params['y']
        first_k = self.encrypt_params['first_k']
        auto_k_values = self.encrypt_params['auto_k_values']

        encrypted_pairs = []
        k_list = [first_k]

        self.encrypt_result.insert(tk.END, "=" * 80 + "\n")
        self.encrypt_result.insert(tk.END, "ШИФРОВАНИЕ ФАЙЛА\n")
        self.encrypt_result.insert(tk.END, "=" * 80 + "\n")
        self.encrypt_result.insert(tk.END, f"p = {p}\n")
        self.encrypt_result.insert(tk.END, f"g = {g}\n")
        self.encrypt_result.insert(tk.END, f"y = {y}\n")
        self.encrypt_result.insert(tk.END, f"Всего байт: {self.total_bytes}\n")
        self.encrypt_result.insert(tk.END, f"Первый k = {first_k}\n")
        self.encrypt_result.insert(tk.END, f"Для каждого следующего байта генерируется СВОЁ уникальное k!\n")
        self.encrypt_result.insert(tk.END, "-" * 80 + "\n")

        # Заголовки таблицы с фиксированной шириной
        self.encrypt_result.insert(tk.END, f"{'#':>4}  {'m(dec)':>6}  {'m(char)':>7}  {'k':>8}  {'a':>10}  {'b':>10}\n")
        self.encrypt_result.insert(tk.END, "-" * 80 + "\n")
        self.root.update_idletasks()

        # Первый байт
        m0 = self.plain_bytes[0]
        a0 = fast_exp(g, first_k, p)
        yk0 = fast_exp(y, first_k, p)
        b0 = (yk0 * m0) % p
        encrypted_pairs.append((a0, b0))

        m0_char = chr(m0) if 32 <= m0 < 127 else '.'
        self.encrypt_result.insert(tk.END, f"{0:4d}  {m0:6d}  {m0_char:>7}  {first_k:8d}  {a0:10d}  {b0:10d}\n")
        self.encrypt_progress['value'] = 1 / self.total_bytes * 100
        self.root.update_idletasks()

        # Остальные байты
        for i in range(1, self.total_bytes):
            if self.encryption_cancelled:
                return

            m = self.plain_bytes[i]
            k = auto_k_values[i - 1]
            k_list.append(k)

            a = fast_exp(g, k, p)
            yk = fast_exp(y, k, p)
            b = (yk * m) % p
            encrypted_pairs.append((a, b))

            # Выводим первые 50 байт
            if i <= 50:
                m_char = chr(m) if 32 <= m < 127 else '.'
                self.encrypt_result.insert(tk.END, f"{i:4d}  {m:6d}  {m_char:>7}  {k:8d}  {a:10d}  {b:10d}\n")
                self.encrypt_result.see(tk.END)

            # Обновляем прогресс
            if i % self.BATCH_SIZE == 0 or i == self.total_bytes - 1:
                progress = (i + 1) / self.total_bytes * 100
                self.encrypt_progress['value'] = progress
                self.update_status(f"Шифрование: {i + 1}/{self.total_bytes} ({progress:.1f}%)")
                self.root.update_idletasks()

        if self.total_bytes > 50:
            self.encrypt_result.insert(tk.END,
                                       f"\n... и еще {self.total_bytes - 50} байт (все k сохранены в лог-файл)\n")

        self.encrypt_params['encrypted_pairs'] = encrypted_pairs
        self.encrypt_params['k_list'] = k_list
        self.finish_encryption()

    def finish_encryption(self):
        write_encrypted_file(self.output_file_path.get(), self.encrypt_params['encrypted_pairs'])

        k_log_file = self.output_file_path.get() + ".k_log.txt"
        with open(k_log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ЛОГ ЗНАЧЕНИЙ K ДЛЯ КАЖДОГО БАЙТА\n")
            f.write("=" * 80 + "\n")
            f.write(f"{'#':>4}  {'m(dec)':>6}  {'m(char)':>7}  {'k':>8}  {'a':>10}  {'b':>10}\n")
            f.write("-" * 80 + "\n")
            for idx, (k_val, (a, b)) in enumerate(
                    zip(self.encrypt_params['k_list'], self.encrypt_params['encrypted_pairs'])):
                m = self.plain_bytes[idx] if idx < len(self.plain_bytes) else 0
                m_char = chr(m) if 32 <= m < 127 else '.'
                f.write(f"{idx:4d}  {m:6d}  {m_char:>7}  {k_val:8d}  {a:10d}  {b:10d}\n")
            f.write("=" * 80 + "\n")

        self.encrypt_progress['value'] = 100
        self.update_status("Шифрование завершено")

        self.encrypt_result.insert(tk.END, "\n" + "=" * 80 + "\n")
        self.encrypt_result.insert(tk.END, f"ШИФРОВАНИЕ ЗАВЕРШЕНО!\n")
        self.encrypt_result.insert(tk.END, f"Зашифровано байт: {len(self.encrypt_params['encrypted_pairs'])}\n")
        self.encrypt_result.insert(tk.END, f"Лог ВСЕХ k (для каждого байта): {Path(k_log_file).name}\n")
        self.encrypt_result.insert(tk.END, "=" * 80 + "\n")

        messagebox.showinfo("Успех", f"Файл зашифрован!\n\n"
                                     f"Для каждого из {self.total_bytes} байтов использовано СВОЁ значение k.\n"
                                     f"Лог всех k сохранён в: {Path(k_log_file).name}")

    def create_decrypt_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Дешифрование")

        frame_files = ttk.LabelFrame(tab, text="Файлы", padding=10)
        frame_files.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_files, text="Зашифрованный:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame_files, textvariable=self.encrypted_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_files, text="Обзор", command=self.select_encrypted_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame_files, text="Выходной:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame_files, textvariable=self.decrypted_file_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_files, text="Обзор", command=self.select_decrypted_file).grid(row=1, column=2, padx=5, pady=5)

        frame_params = ttk.LabelFrame(tab, text="Параметры (ограничения)", padding=10)
        frame_params.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_params, text="p: простое число (то же, что при шифровании)").grid(row=0, column=0, sticky=tk.W,
                                                                                          padx=5, pady=2)
        p_entry = ttk.Entry(frame_params, textvariable=self.p_value, width=15)
        p_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame_params, text="x: закрытый ключ (1 < x < p-1)").grid(row=1, column=0, sticky=tk.W, padx=5,
                                                                            pady=2)
        x_entry = ttk.Entry(frame_params, textvariable=self.x_value, width=15)
        x_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        decrypt_btn = ttk.Button(tab, text="РАСШИФРОВАТЬ", command=self.decrypt_file)
        decrypt_btn.pack(pady=10)

        self.decrypt_progress = ttk.Progressbar(tab, mode='determinate')
        self.decrypt_progress.pack(fill=tk.X, padx=10, pady=5)

        self.decrypt_result = scrolledtext.ScrolledText(tab, height=12, font=('Courier', 10))
        self.decrypt_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def select_encrypted_file(self):
        filepath = filedialog.askopenfilename(title="Выберите зашифрованный файл")
        if filepath:
            self.encrypted_file_path.set(filepath)

    def select_decrypted_file(self):
        filepath = filedialog.asksaveasfilename(title="Сохранить как")
        if filepath:
            self.decrypted_file_path.set(filepath)

    def decrypt_file(self):
        if not self.encrypted_file_path.get():
            messagebox.showwarning("Ошибка", "Выберите зашифрованный файл")
            return
        if not self.decrypted_file_path.get():
            messagebox.showwarning("Ошибка", "Укажите выходной файл")
            return

        try:
            p = int(self.p_value.get())
            x = int(self.x_value.get())

            validate_prime(p)
            validate_private_key(x, p)

            self.decrypt_result.delete(1.0, tk.END)
            self.decrypt_progress['value'] = 0

            encrypted_pairs = read_encrypted_file(self.encrypted_file_path.get())
            total = len(encrypted_pairs)

            self.decrypt_result.insert(tk.END, "=" * 80 + "\n")
            self.decrypt_result.insert(tk.END, "ДЕШИФРОВАНИЕ ФАЙЛА\n")
            self.decrypt_result.insert(tk.END, "=" * 80 + "\n")
            self.decrypt_result.insert(tk.END, f"p = {p}\n")
            self.decrypt_result.insert(tk.END, f"x = {x}\n")
            self.decrypt_result.insert(tk.END, "-" * 80 + "\n")
            self.decrypt_result.insert(tk.END, f"{'#':>4}  {'a':>10}  {'b':>10}  {'m(dec)':>6}  {'m(char)':>7}\n")
            self.decrypt_result.insert(tk.END, "-" * 80 + "\n")
            self.root.update_idletasks()

            decrypted_bytes = []
            exponent = p - 1 - x

            for i, (a, b) in enumerate(encrypted_pairs):
                a_pow = fast_exp(a, exponent, p)
                m = (b * a_pow) % p
                decrypted_bytes.append(m)

                if i < 50:
                    m_char = chr(m) if 32 <= m < 127 else '.'
                    self.decrypt_result.insert(tk.END, f"{i:4d}  {a:10d}  {b:10d}  {m:6d}  {m_char:>7}\n")
                    self.decrypt_result.see(tk.END)
                elif i % self.BATCH_SIZE == 0 or i == total - 1:
                    progress = (i + 1) / total * 100
                    self.decrypt_progress['value'] = progress
                    self.update_status(f"Дешифрование: {i + 1}/{total} ({progress:.1f}%)")
                    self.root.update_idletasks()

            write_bytes_to_file(self.decrypted_file_path.get(), decrypted_bytes)

            self.decrypt_progress['value'] = 100
            self.update_status("Дешифрование завершено")

            if total > 50:
                self.decrypt_result.insert(tk.END, f"\n... и еще {total - 50} байт\n")
            self.decrypt_result.insert(tk.END, "\n" + "=" * 80 + "\n")
            self.decrypt_result.insert(tk.END, f"ДЕШИФРОВАНИЕ ЗАВЕРШЕНО!\n")
            self.decrypt_result.insert(tk.END, f"Расшифровано байт: {len(decrypted_bytes)}\n")
            self.decrypt_result.insert(tk.END, "=" * 80 + "\n")
            messagebox.showinfo("Успех", "Файл расшифрован!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def create_view_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Просмотр")

        frame_file = ttk.Frame(tab)
        frame_file.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_file, text="Файл:").pack(side=tk.LEFT, padx=5)
        self.view_file_path = tk.StringVar()
        ttk.Entry(frame_file, textvariable=self.view_file_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_file, text="Обзор", command=self.select_view_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_file, text="Показать", command=self.show_encrypted_content).pack(side=tk.LEFT, padx=5)

        self.view_text = scrolledtext.ScrolledText(tab, font=('Courier', 10))
        self.view_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def select_view_file(self):
        filepath = filedialog.askopenfilename(title="Выберите файл")
        if filepath:
            self.view_file_path.set(filepath)

    def show_encrypted_content(self):
        filepath = self.view_file_path.get()
        if not filepath:
            messagebox.showwarning("Ошибка", "Выберите файл")
            return

        try:
            pairs = read_encrypted_file(filepath)
            self.view_text.delete(1.0, tk.END)
            self.view_text.insert(tk.END, f"Файл: {filepath}\n")
            self.view_text.insert(tk.END, f"Размер: {Path(filepath).stat().st_size} байт\n")
            self.view_text.insert(tk.END, f"Пар (a,b): {len(pairs)}\n")
            self.view_text.insert(tk.END, "-" * 60 + "\n")
            self.view_text.insert(tk.END, f"{'#':>4}  {'a':>10}  {'b':>10}\n")
            self.view_text.insert(tk.END, "-" * 60 + "\n")

            for i, (a, b) in enumerate(pairs[:100]):
                self.view_text.insert(tk.END, f"{i:4d}  {a:10d}  {b:10d}\n")

            if len(pairs) > 100:
                self.view_text.insert(tk.END, f"\n... и еще {len(pairs) - 100} пар\n")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


def main():
    root = tk.Tk()
    app = ElGamalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()