from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
import os


class CryptoApp:
    def __init__(self, window):
        self.window = window
        self.window.title("LAB 1 - Шифрование текста")
        self.window.geometry("1000x800")
        self.window.resizable(False, False)

        self.setup_styles()

        self.russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        self.russian_alphabet_upper = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.russian_index = {char: i for i, char in enumerate(self.russian_alphabet_upper)}
        self.russian_chars = list(self.russian_alphabet_upper)

        self.english_alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.english_alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        self.selected_method = StringVar(value="Столбцовый (англ)")
        self.key_var = StringVar()
        self.input_mode = StringVar(value="keyboard")
        self.current_file_path = None
        self.last_result = None
        self.last_table_data = None
        self.last_vigenere_data = None
        self.last_vigenere_decrypt_data = None

        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.bg_color = "#2E7D32"
        self.fg_color = "#FFFFFF"
        self.entry_bg = "#FFFFFF"
        self.entry_fg = "#000000"
        self.button_bg = "#4CAF50"
        self.button_fg = "#FFFFFF"
        self.frame_bg = "#2E7D32"

        self.window.config(bg=self.bg_color)

        self.style.configure("TFrame", background=self.frame_bg)
        self.style.configure("TLabelframe", background=self.frame_bg)
        self.style.configure("TLabelframe.Label", background=self.frame_bg, foreground=self.fg_color)

        self.style.configure("Header.TLabel",
                             font=("Arial", 16, "bold"),
                             background=self.bg_color,
                             foreground=self.fg_color)

        self.style.configure("Normal.TLabel",
                             font=("Arial", 11),
                             background=self.bg_color,
                             foreground=self.fg_color)

        self.style.configure("Method.TRadiobutton",
                             font=("Arial", 11),
                             background=self.bg_color,
                             foreground=self.fg_color)

        self.style.configure("Action.TButton",
                             font=("Arial", 10, "bold"),
                             background=self.button_bg,
                             foreground=self.button_fg)

        self.style.map("Action.TButton",
                       background=[('active', '#45a049')])

        self.style.configure("TEntry",
                             fieldbackground=self.entry_bg,
                             foreground=self.entry_fg)

    def create_widgets(self):
        header = ttk.Label(self.window, text="Лабораторная работа №1: Шифрование текста",
                           style="Header.TLabel")
        header.pack(pady=10)

        top_frame = ttk.Frame(self.window)
        top_frame.pack(pady=5, padx=10, fill="x")

        method_frame = ttk.Frame(top_frame)
        method_frame.pack(side=LEFT, padx=5)

        ttk.Label(method_frame, text="Метод:", style="Normal.TLabel").pack(side=LEFT, padx=5)

        methods = ["Столбцовый (англ)", "Виженер (русский)"]

        for method in methods:
            rb = ttk.Radiobutton(method_frame, text=method,
                                 variable=self.selected_method,
                                 value=method, style="Method.TRadiobutton")
            rb.pack(side=LEFT, padx=5)

        key_frame = ttk.Frame(top_frame)
        key_frame.pack(side=LEFT, padx=10)

        ttk.Label(key_frame, text="Ключ:", style="Normal.TLabel").pack(side=LEFT, padx=5)

        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var,
                                   font=("Arial", 11), width=15)
        self.key_entry.pack(side=LEFT, padx=5)

        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side=LEFT, padx=10)

        ttk.Radiobutton(input_frame, text="Клавиатура",
                        variable=self.input_mode, value="keyboard",
                        style="Method.TRadiobutton").pack(side=LEFT, padx=2)
        ttk.Radiobutton(input_frame, text="Файл",
                        variable=self.input_mode, value="file",
                        style="Method.TRadiobutton").pack(side=LEFT, padx=2)

        ttk.Button(top_frame, text="Показать таблицу",
                   command=self.show_table_window, style="Action.TButton").pack(side=RIGHT, padx=10)

        self.text_frame = ttk.Frame(self.window)
        self.text_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.keyboard_frame = ttk.Frame(self.text_frame)

        ttk.Label(self.keyboard_frame, text="Исходный текст:",
                  style="Normal.TLabel").pack(anchor="w")

        self.input_text = scrolledtext.ScrolledText(self.keyboard_frame,
                                                    wrap=WORD, width=80, height=6,
                                                    font=("Arial", 10),
                                                    bg="#FFFFFF", fg="#000000")
        self.input_text.pack(pady=2, fill="both", expand=True)

        ttk.Label(self.keyboard_frame, text="Результат:",
                  style="Normal.TLabel").pack(anchor="w", pady=(5, 0))

        self.output_text = scrolledtext.ScrolledText(self.keyboard_frame,
                                                     wrap=WORD, width=80, height=6,
                                                     font=("Arial", 10),
                                                     bg="#FFFFFF", fg="#000000")
        self.output_text.pack(pady=2, fill="both", expand=True)

        keyboard_actions = ttk.Frame(self.keyboard_frame)
        keyboard_actions.pack(pady=10)

        ttk.Button(keyboard_actions, text="Зашифровать",
                   command=self.encrypt_text, style="Action.TButton").pack(side=LEFT, padx=5)
        ttk.Button(keyboard_actions, text="Расшифровать",
                   command=self.decrypt_text, style="Action.TButton").pack(side=LEFT, padx=5)
        ttk.Button(keyboard_actions, text="Очистить",
                   command=self.clear_fields, style="Action.TButton").pack(side=LEFT, padx=5)
        ttk.Button(keyboard_actions, text="Сохранить результат",
                   command=self.save_result, style="Action.TButton").pack(side=LEFT, padx=5)

        self.file_frame = ttk.Frame(self.text_frame)

        file_top = ttk.Frame(self.file_frame)
        file_top.pack(fill="x", pady=5)

        ttk.Label(file_top, text="Файл для чтения:", style="Normal.TLabel").pack(side=LEFT, padx=5)

        self.file_path_var = StringVar()
        self.file_entry = ttk.Entry(file_top, textvariable=self.file_path_var,
                                    font=("Arial", 10), width=40, state="readonly")
        self.file_entry.pack(side=LEFT, padx=5, fill="x", expand=True)

        ttk.Button(file_top, text="Обзор...",
                   command=self.select_input_file, style="Action.TButton").pack(side=LEFT, padx=5)

        ttk.Label(self.file_frame, text="Содержимое файла:",
                  style="Normal.TLabel").pack(anchor="w", pady=(10, 0))

        self.file_content = scrolledtext.ScrolledText(self.file_frame,
                                                      wrap=WORD, width=80, height=6,
                                                      font=("Arial", 10),
                                                      bg="#FFFFFF", fg="#000000")
        self.file_content.pack(pady=2, fill="both", expand=True)

        ttk.Label(self.file_frame, text="Результат:",
                  style="Normal.TLabel").pack(anchor="w", pady=(5, 0))

        self.file_result_text = scrolledtext.ScrolledText(self.file_frame,
                                                          wrap=WORD, width=80, height=6,
                                                          font=("Arial", 10),
                                                          bg="#FFFFFF", fg="#000000")
        self.file_result_text.pack(pady=2, fill="both", expand=True)

        file_actions = ttk.Frame(self.file_frame)
        file_actions.pack(pady=10)

        ttk.Button(file_actions, text="Зашифровать файл",
                   command=self.encrypt_file, style="Action.TButton").pack(side=LEFT, padx=10)
        ttk.Button(file_actions, text="Расшифровать файл",
                   command=self.decrypt_file, style="Action.TButton").pack(side=LEFT, padx=10)

        ttk.Button(file_actions, text="Сохранить результат",
                   command=self.save_file_result, style="Action.TButton").pack(side=LEFT, padx=10)

        ttk.Button(file_actions, text="Очистить",
                   command=self.clear_file_fields, style="Action.TButton").pack(side=LEFT, padx=10)

        self.show_input_frame()

        self.input_mode.trace('w', self.on_input_mode_change)

    def show_input_frame(self):
        if self.input_mode.get() == "keyboard":
            self.keyboard_frame.pack(fill="both", expand=True)
            self.file_frame.pack_forget()
        else:
            self.keyboard_frame.pack_forget()
            self.file_frame.pack(fill="both", expand=True)

    def on_input_mode_change(self, *args):
        self.show_input_frame()

    def select_input_file(self):
        # Только текстовые файлы
        filename = filedialog.askopenfilename(
            title="Выберите текстовый файл для чтения",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        if filename:
            self.file_path_var.set(filename)
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.file_content.delete(1.0, END)
                self.file_content.insert(1.0, content)
                messagebox.showinfo("Успех", f"Файл загружен: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")

    def save_result(self):
        if not hasattr(self, 'last_result') or not self.last_result:
            messagebox.showwarning("Предупреждение", "Нет результата для сохранения")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить результат как текстовый файл",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt")
            ]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.last_result)
                messagebox.showinfo("Успех", f"Результат сохранен в файл:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def save_file_result(self):
        result_text = self.file_result_text.get(1.0, END).strip()
        if not result_text:
            messagebox.showwarning("Предупреждение", "Нет результата для сохранения")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить результат как текстовый файл",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt")
            ]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result_text)
                messagebox.showinfo("Успех", f"Результат сохранен в файл:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def clear_fields(self):
        self.input_text.delete(1.0, END)
        self.output_text.delete(1.0, END)
        self.last_result = None
        self.last_table_data = None
        self.last_vigenere_data = None
        self.last_vigenere_decrypt_data = None

    def clear_file_fields(self):
        self.file_path_var.set("")
        self.file_content.delete(1.0, END)
        self.file_result_text.delete(1.0, END)
        self.last_result = None
        self.last_table_data = None
        self.last_vigenere_data = None
        self.last_vigenere_decrypt_data = None

    def show_table_window(self):
        if self.selected_method.get() == "Столбцовый (англ)":
            if not self.last_table_data:
                messagebox.showwarning("Предупреждение",
                                       "Сначала выполните шифрование или дешифрование столбцовым методом")
                return
            self.show_column_table()
        else:
            if not self.last_vigenere_data and not self.last_vigenere_decrypt_data:
                messagebox.showwarning("Предупреждение", "Сначала выполните шифрование или дешифрование Виженера")
                return
            self.show_vigenere_tables()

    def show_column_table(self):
        table_window = Toplevel(self.window)
        table_window.title("Таблица распределения символов (улучшенный столбцовый метод)")
        table_window.geometry("900x700")
        table_window.resizable(True, True)
        table_window.configure(bg=self.bg_color)

        table_data = self.last_table_data
        table = table_data['table']
        key = table_data['key']
        original_key = table_data.get('original_key', key)
        column_order = table_data['column_order']
        filtered_text = table_data['filtered_text']
        result = table_data['result']
        mode = table_data.get('mode', 'encrypt')

        mode_text = "шифрования" if mode == 'encrypt' else "дешифрования"
        header = ttk.Label(table_window, text=f"Таблица {mode_text} (улучшенный столбцовый метод)",
                           font=("Arial", 14, "bold"),
                           background=self.bg_color, foreground=self.fg_color)
        header.pack(pady=10)

        info_frame = ttk.Frame(table_window)
        info_frame.pack(pady=5, padx=10, fill="x")

        input_text_label = "Исходный текст" if mode == 'encrypt' else "Шифротекст"
        ttk.Label(info_frame, text=f"{input_text_label}: {filtered_text}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text=f"Исходный ключ: {original_key}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text=f"Повторенный ключ: {key}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text=f"Порядок столбцов: {column_order}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")

        result_text_label = "Зашифрованный текст" if mode == 'encrypt' else "Расшифрованный текст"
        ttk.Label(info_frame, text=f"{result_text_label}: {result}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")

        table_frame = ttk.Frame(table_window)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        canvas = Canvas(table_frame, bg=self.bg_color, highlightbackground=self.bg_color)
        scrollbar_y = Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        rows = len(table)
        cols = len(table[0]) if rows > 0 else 0

        key_label = ttk.Label(inner_frame, text="Ключ:",
                              font=("Arial", 10, "bold"),
                              relief="solid", borderwidth=1,
                              width=8, anchor="center")
        key_label.grid(row=0, column=0, padx=1, pady=1)

        for j in range(cols):
            key_cell = ttk.Label(inner_frame, text=f"{key[j]}",
                                 font=("Arial", 12, "bold"),
                                 relief="solid", borderwidth=1,
                                 width=5, anchor="center",
                                 background="#E3F2FD")
            key_cell.grid(row=0, column=j + 1, padx=1, pady=1)

        order_label = ttk.Label(inner_frame, text="Порядок:",
                                font=("Arial", 10, "bold"),
                                relief="solid", borderwidth=1,
                                width=8, anchor="center")
        order_label.grid(row=1, column=0, padx=1, pady=1)

        for j in range(cols):
            order_cell = ttk.Label(inner_frame, text=f"{column_order[j]}",
                                   font=("Arial", 10),
                                   relief="solid", borderwidth=1,
                                   width=5, anchor="center",
                                   background="#FFF9C4")
            order_cell.grid(row=1, column=j + 1, padx=1, pady=1)

        for i in range(rows):
            row_label = ttk.Label(inner_frame, text=f"Строка {i + 1}",
                                  font=("Arial", 10, "bold"),
                                  relief="solid", borderwidth=1,
                                  width=8, anchor="center")
            row_label.grid(row=i + 2, column=0, padx=1, pady=1)

            for j in range(cols):
                cell_value = table[i][j]
                if cell_value and cell_value != '':
                    bg_color = "#E8F5E8"
                    cell = ttk.Label(inner_frame, text=cell_value,
                                     font=("Arial", 12, "bold"),
                                     relief="solid", borderwidth=1,
                                     width=5, anchor="center",
                                     background=bg_color)
                else:
                    cell = ttk.Label(inner_frame, text="—",
                                     font=("Arial", 10),
                                     relief="solid", borderwidth=1,
                                     width=5, anchor="center",
                                     foreground="gray")
                cell.grid(row=i + 2, column=j + 1, padx=1, pady=1)

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        info_text = "Особенности заполнения:\n"
        for i in range(rows):
            stop_value = (i % cols) + 1
            stop_index = column_order.index(stop_value)
            info_text += f"• Строка {i + 1} заполнена до столбца с порядком {stop_value} (столбец {stop_index + 1})\n"

        info_label = ttk.Label(table_window, text=info_text,
                               font=("Arial", 10),
                               background=self.bg_color, foreground=self.fg_color,
                               justify=LEFT)
        info_label.pack(pady=5, padx=10, anchor="w")

        ttk.Button(table_window, text="Закрыть",
                   command=table_window.destroy,
                   style="Action.TButton").pack(pady=10)

    def show_vigenere_tables(self):
        table_window = Toplevel(self.window)
        table_window.title("Таблицы Виженера")
        table_window.geometry("1400x900")
        table_window.resizable(True, True)
        table_window.configure(bg=self.bg_color)

        notebook = ttk.Notebook(table_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        full_table_frame = ttk.Frame(notebook)
        notebook.add(full_table_frame, text="Полная таблица Виженера")

        if self.last_vigenere_data:
            encrypt_frame = ttk.Frame(notebook)
            notebook.add(encrypt_frame, text="Шифрование (шаги)")
            self.create_vigenere_steps_table(encrypt_frame, self.last_vigenere_data, "шифрование")

        if self.last_vigenere_decrypt_data:
            decrypt_frame = ttk.Frame(notebook)
            notebook.add(decrypt_frame, text="Дешифрование (шаги)")
            self.create_vigenere_steps_table(decrypt_frame, self.last_vigenere_decrypt_data, "дешифрование")

        self.create_full_vigenere_table(full_table_frame)

        ttk.Button(table_window, text="Закрыть",
                   command=table_window.destroy,
                   style="Action.TButton").pack(pady=10)

    def create_vigenere_steps_table(self, parent, data, mode):
        text = data['text']
        key = data['key']
        result = data['result']
        steps = data['steps']
        generated_key = data['generated_key']

        header = ttk.Label(parent, text=f"Алгоритм Виженера ({mode}) с самогенерирующимся ключом",
                           font=("Arial", 14, "bold"),
                           background=self.bg_color, foreground=self.fg_color)
        header.pack(pady=10)

        info_frame = ttk.Frame(parent)
        info_frame.pack(pady=5, padx=10, fill="x")

        ttk.Label(info_frame, text=f"{'Исходный' if mode == 'шифрование' else 'Зашифрованный'} текст: {text}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text=f"Исходный ключ: {key}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text=f"Сгенерированный ключ: {generated_key}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text=f"{'Зашифрованный' if mode == 'шифрование' else 'Расшифрованный'} текст: {result}",
                  font=("Arial", 10), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")

        table_frame = ttk.Frame(parent)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        canvas = Canvas(table_frame, bg=self.bg_color, highlightbackground=self.bg_color)
        scrollbar_y = Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        if mode == "шифрование":
            columns = ["№", "Буква текста", "Индекс", "Буква ключа", "Индекс", "Сумма", "Результат"]
        else:
            columns = ["№", "Буква шифра", "Индекс", "Буква ключа", "Индекс", "Разность", "Результат"]

        for j, col in enumerate(columns):
            ttk.Label(inner_frame, text=col,
                      font=("Arial", 10, "bold"),
                      relief="solid", borderwidth=1,
                      width=12 if j > 0 else 5,
                      anchor="center").grid(row=0, column=j, padx=1, pady=1)

        for i, step in enumerate(steps):
            ttk.Label(inner_frame, text=str(i + 1),
                      font=("Arial", 10),
                      relief="solid", borderwidth=1,
                      width=5, anchor="center").grid(row=i + 1, column=0, padx=1, pady=1)

            ttk.Label(inner_frame, text=step['text_char'],
                      font=("Arial", 12, "bold"),
                      relief="solid", borderwidth=1,
                      width=12, anchor="center",
                      background="#E8F5E8").grid(row=i + 1, column=1, padx=1, pady=1)

            ttk.Label(inner_frame, text=str(step['text_idx']),
                      font=("Arial", 10),
                      relief="solid", borderwidth=1,
                      width=12, anchor="center").grid(row=i + 1, column=2, padx=1, pady=1)

            bg_color = "#FFF3E0" if i < len(key) else "#FFE0B2"
            ttk.Label(inner_frame, text=step['key_char'],
                      font=("Arial", 12, "bold"),
                      relief="solid", borderwidth=1,
                      width=12, anchor="center",
                      background=bg_color).grid(row=i + 1, column=3, padx=1, pady=1)

            ttk.Label(inner_frame, text=str(step['key_idx']),
                      font=("Arial", 10),
                      relief="solid", borderwidth=1,
                      width=12, anchor="center").grid(row=i + 1, column=4, padx=1, pady=1)

            if mode == "шифрование":
                operation = f"{step['text_idx']} + {step['key_idx']} = {step['sum']}"
            else:
                operation = f"{step['text_idx']} - {step['key_idx']} = {step['diff']}"
            ttk.Label(inner_frame, text=operation,
                      font=("Arial", 10),
                      relief="solid", borderwidth=1,
                      width=15, anchor="center").grid(row=i + 1, column=5, padx=1, pady=1)

            ttk.Label(inner_frame, text=f"{step['result_char']} ({step['result_idx']})",
                      font=("Arial", 12, "bold"),
                      relief="solid", borderwidth=1,
                      width=12, anchor="center",
                      background="#E0F2F1").grid(row=i + 1, column=6, padx=1, pady=1)

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def create_full_vigenere_table(self, parent):
        header = ttk.Label(parent, text="Полная таблица Виженера (русский алфавит)",
                           font=("Arial", 14, "bold"),
                           background=self.bg_color, foreground=self.fg_color)
        header.pack(pady=10)

        info_frame = ttk.Frame(parent)
        info_frame.pack(pady=5, padx=10, fill="x")

        alphabet_str = "А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я"
        ttk.Label(info_frame, text=f"Алфавит: {alphabet_str}",
                  font=("Arial", 9), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")
        ttk.Label(info_frame, text="Индексы: 0-32 (А=0, Б=1, ..., Я=32)",
                  font=("Arial", 9), background=self.bg_color, foreground=self.fg_color).pack(anchor="w")

        table_frame = ttk.Frame(parent)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        canvas = Canvas(table_frame, bg=self.bg_color, highlightbackground=self.bg_color)
        scrollbar_y = Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        alphabet = list(self.russian_alphabet_upper)

        for j, letter in enumerate(alphabet):
            ttk.Label(inner_frame, text=letter,
                      font=("Arial", 9, "bold"),
                      relief="solid", borderwidth=1,
                      width=3, anchor="center",
                      background="#E3F2FD").grid(row=0, column=j + 1, padx=1, pady=1)

        for i, letter in enumerate(alphabet):
            ttk.Label(inner_frame, text=letter,
                      font=("Arial", 9, "bold"),
                      relief="solid", borderwidth=1,
                      width=3, anchor="center",
                      background="#E3F2FD").grid(row=i + 1, column=0, padx=1, pady=1)

        for i in range(33):
            for j in range(33):
                result_idx = (i + j) % 33
                result_char = alphabet[result_idx]

                bg_color = "#FFFFFF"
                if i == j:
                    bg_color = "#FFF9C4"
                elif result_idx == 0:
                    bg_color = "#C8E6C9"

                ttk.Label(inner_frame, text=result_char,
                          font=("Arial", 9),
                          relief="solid", borderwidth=1,
                          width=3, anchor="center",
                          background=bg_color).grid(row=i + 1, column=j + 1, padx=1, pady=1)

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def filter_english_text(self, text):
        filtered = []
        for char in text:
            upper_char = char.upper()
            if upper_char in self.english_alphabet_upper:
                filtered.append(upper_char)
        return ''.join(filtered)

    def filter_russian_text_only(self, text):
        filtered = []
        for char in text:
            upper_char = char.upper()
            if upper_char in self.russian_alphabet_upper:
                filtered.append(upper_char)
        return ''.join(filtered)

    def filter_russian_with_spaces(self, text):
        filtered = []
        for char in text:
            upper_char = char.upper()
            if upper_char in self.russian_alphabet_upper:
                filtered.append(upper_char)
            elif char == ' ':
                filtered.append(' ')
        return ''.join(filtered)

    def prepare_english_key(self, key):
        filtered = []
        for char in key:
            upper_char = char.upper()
            if upper_char in self.english_alphabet_upper:
                filtered.append(upper_char)

        if not filtered:
            raise ValueError("Ключ должен содержать хотя бы одну английскую букву")

        return ''.join(filtered)

    def prepare_russian_key(self, key):
        filtered = []
        for char in key:
            upper_char = char.upper()
            if upper_char in self.russian_alphabet_upper:
                filtered.append(upper_char)

        if not filtered:
            raise ValueError("Ключ должен содержать хотя бы одну русскую букву")

        return ''.join(filtered)

    def calculate_column_order(self, key):
        pairs = [(key[i], i) for i in range(len(key))]
        sorted_pairs = sorted(pairs, key=lambda x: (x[0], x[1]))

        order = [0] * len(key)
        for i, (_, idx) in enumerate(sorted_pairs):
            order[idx] = i + 1

        return order

    def column_encrypt(self, text, key):
        if not text:
            return ""

        clean_text = self.filter_english_text(text)
        if not clean_text:
            raise ValueError("Текст не содержит английских букв")

        clean_key = self.prepare_english_key(key)

        text_length = len(clean_text)
        total_capacity = 0
        row = 0
        repeats = 1
        current_key = clean_key
        column_order = self.calculate_column_order(current_key)
        cols = len(column_order)

        while total_capacity < text_length:
            stop_value = (row % cols) + 1
            stop_index = column_order.index(stop_value)
            total_capacity += stop_index + 1
            row += 1

            if row >= cols and total_capacity < text_length:
                repeats += 1
                current_key = clean_key * repeats
                column_order = self.calculate_column_order(current_key)
                cols = len(column_order)

        repeated_key = clean_key * repeats
        column_order = self.calculate_column_order(repeated_key)
        cols = len(column_order)

        table = []
        text_index = 0
        current_row = 0

        while text_index < len(clean_text):
            row_data = [''] * cols
            stop_value = (current_row % cols) + 1
            stop_index = column_order.index(stop_value)

            found_stop = False
            for col in range(cols):
                if not found_stop:
                    if text_index < len(clean_text):
                        row_data[col] = clean_text[text_index]
                        text_index += 1
                    else:
                        row_data[col] = ''

                    if col == stop_index:
                        found_stop = True
                else:
                    row_data[col] = ''

            table.append(row_data)
            current_row += 1

        result = []
        for order_num in range(1, cols + 1):
            col_idx = column_order.index(order_num)
            for row in table:
                if col_idx < len(row) and row[col_idx]:
                    result.append(row[col_idx])

        result_str = ''.join(result)

        self.last_table_data = {
            'table': table,
            'key': repeated_key,
            'original_key': clean_key,
            'column_order': column_order,
            'filtered_text': clean_text,
            'result': result_str,
            'mode': 'encrypt',
            'repeats': repeats
        }

        return result_str

    def column_decrypt(self, text, key):
        if not text:
            return ""

        clean_text = self.filter_english_text(text)
        if not clean_text:
            raise ValueError("Текст не содержит английских букв")

        clean_key = self.prepare_english_key(key)

        text_length = len(clean_text)
        total_capacity = 0
        row = 0
        repeats = 1
        current_key = clean_key
        column_order = self.calculate_column_order(current_key)
        cols = len(column_order)

        while total_capacity < text_length:
            stop_value = (row % cols) + 1
            stop_index = column_order.index(stop_value)
            total_capacity += stop_index + 1
            row += 1

            if row >= cols and total_capacity < text_length:
                repeats += 1
                current_key = clean_key * repeats
                column_order = self.calculate_column_order(current_key)
                cols = len(column_order)

        repeated_key = clean_key * repeats
        column_order = self.calculate_column_order(repeated_key)
        cols = len(column_order)

        row_structure = []
        filled = 0
        row_num = 0

        while filled < text_length:
            stop_value = (row_num % cols) + 1
            stop_index = column_order.index(stop_value)
            row_cols = []

            for c in range(stop_index + 1):
                if filled < text_length:
                    row_cols.append(c)
                    filled += 1

            row_structure.append(row_cols)
            row_num += 1

        rows = len(row_structure)

        table = [[''] * cols for _ in range(rows)]

        text_index = 0
        for order_num in range(1, cols + 1):
            col_idx = column_order.index(order_num)
            for r in range(rows):
                if col_idx in row_structure[r]:
                    if text_index < len(clean_text):
                        table[r][col_idx] = clean_text[text_index]
                        text_index += 1

        result = []
        for r in range(rows):
            for col in row_structure[r]:
                if table[r][col]:
                    result.append(table[r][col])

        result_str = ''.join(result)

        self.last_table_data = {
            'table': table,
            'key': repeated_key,
            'original_key': clean_key,
            'column_order': column_order,
            'filtered_text': clean_text,
            'result': result_str,
            'mode': 'decrypt',
            'repeats': repeats,
            'row_structure': row_structure
        }

        return result_str

    def vigenere_encrypt(self, text, key):
        if not text:
            return ""

        text_with_spaces = self.filter_russian_with_spaces(text)

        letters_only = self.filter_russian_text_only(text_with_spaces)
        if not letters_only:
            raise ValueError("Текст не содержит русских букв")

        clean_key = self.prepare_russian_key(key)
        alphabet = self.russian_alphabet_upper
        alphabet_len = len(alphabet)

        encrypted_letters = []
        key_index = 0
        steps = []
        generated_key = list(clean_key)

        for i, char in enumerate(letters_only):
            text_idx = alphabet.index(char)

            if i < len(clean_key):
                key_char = clean_key[i]
            else:
                key_char = letters_only[i - len(clean_key)]
                generated_key.append(key_char)

            key_idx = alphabet.index(key_char)
            result_idx = (text_idx + key_idx) % alphabet_len
            result_char = alphabet[result_idx]

            step = {
                'text_char': char,
                'text_idx': text_idx,
                'key_char': key_char,
                'key_idx': key_idx,
                'sum': text_idx + key_idx,
                'result_idx': result_idx,
                'result_char': result_char
            }
            steps.append(step)
            encrypted_letters.append(result_char)
            key_index += 1

        result_chars = []
        letter_pos = 0
        for char in text_with_spaces:
            if char == ' ':
                result_chars.append(' ')
            else:
                result_chars.append(encrypted_letters[letter_pos])
                letter_pos += 1

        result_str = ''.join(result_chars)

        self.last_vigenere_data = {
            'text': letters_only,
            'key': clean_key,
            'result': ''.join(encrypted_letters),
            'steps': steps,
            'generated_key': ''.join(generated_key)
        }

        return result_str

    def vigenere_decrypt(self, text, key):
        if not text:
            return ""

        text_with_spaces = self.filter_russian_with_spaces(text)

        letters_only = self.filter_russian_text_only(text_with_spaces)
        if not letters_only:
            raise ValueError("Текст не содержит русских букв")

        clean_key = self.prepare_russian_key(key)
        alphabet = self.russian_alphabet_upper
        alphabet_len = len(alphabet)

        decrypted_letters = []
        key_index = 0
        steps = []
        generated_key = list(clean_key)

        for i, char in enumerate(letters_only):
            text_idx = alphabet.index(char)

            if i < len(clean_key):
                key_char = clean_key[i]
            else:
                key_char = decrypted_letters[i - len(clean_key)]
                generated_key.append(key_char)

            key_idx = alphabet.index(key_char)
            result_idx = (text_idx - key_idx) % alphabet_len
            result_char = alphabet[result_idx]

            step = {
                'text_char': char,
                'text_idx': text_idx,
                'key_char': key_char,
                'key_idx': key_idx,
                'diff': (text_idx - key_idx) % alphabet_len,
                'result_idx': result_idx,
                'result_char': result_char
            }
            steps.append(step)
            decrypted_letters.append(result_char)
            key_index += 1

        result_chars = []
        letter_pos = 0
        for char in text_with_spaces:
            if char == ' ':
                result_chars.append(' ')
            else:
                result_chars.append(decrypted_letters[letter_pos])
                letter_pos += 1

        result_str = ''.join(result_chars)

        self.last_vigenere_decrypt_data = {
            'text': letters_only,
            'key': clean_key,
            'result': ''.join(decrypted_letters),
            'steps': steps,
            'generated_key': ''.join(generated_key)
        }

        return result_str

    def encrypt_text(self):
        try:
            text = self.input_text.get(1.0, END).rstrip('\n')
            key = self.key_var.get().strip()

            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
                return
            if not key:
                messagebox.showwarning("Предупреждение", "Введите ключ")
                return

            if self.selected_method.get() == "Столбцовый (англ)":
                space_positions = [i for i, char in enumerate(text) if char == ' ']
                text_without_spaces = text.replace(' ', '')

                filtered_text = self.filter_english_text(text_without_spaces)
                if not filtered_text:
                    messagebox.showwarning("Предупреждение", "Текст не содержит английских букв")
                    return

                encrypted_without_spaces = self.column_encrypt(filtered_text, key)

                result = list(encrypted_without_spaces)
                for pos in space_positions:
                    if pos < len(result):
                        result.insert(pos, ' ')
                    else:
                        result.append(' ')
                result = ''.join(result)

                messagebox.showinfo("Информация",
                                    f"Столбцовый метод:\n"
                                    f"Исходный текст: {text}\n"
                                    f"Пробелы на позициях: {space_positions}")

            else:
                result = self.vigenere_encrypt(text, key)

            self.last_result = result
            self.output_text.delete(1.0, END)
            self.output_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def decrypt_text(self):
        try:
            text = self.input_text.get(1.0, END).rstrip('\n')
            key = self.key_var.get().strip()

            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для дешифрования")
                return
            if not key:
                messagebox.showwarning("Предупреждение", "Введите ключ")
                return

            if self.selected_method.get() == "Столбцовый (англ)":
                space_positions = [i for i, char in enumerate(text) if char == ' ']
                text_without_spaces = text.replace(' ', '')

                filtered_text = self.filter_english_text(text_without_spaces)
                if not filtered_text:
                    messagebox.showwarning("Предупреждение", "Текст не содержит английских букв")
                    return

                decrypted_without_spaces = self.column_decrypt(filtered_text, key)

                result = list(decrypted_without_spaces)
                for pos in space_positions:
                    if pos < len(result):
                        result.insert(pos, ' ')
                    else:
                        result.append(' ')
                result = ''.join(result)

                messagebox.showinfo("Информация",
                                    f"Столбцовый метод:\n"
                                    f"Исходный текст: {text}\n"
                                    f"Пробелы на позициях: {space_positions}")

            else:
                result = self.vigenere_decrypt(text, key)

            self.last_result = result
            self.output_text.delete(1.0, END)
            self.output_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def encrypt_file(self):
        try:
            input_file = self.file_path_var.get()
            if not input_file:
                messagebox.showwarning("Предупреждение", "Выберите файл для чтения")
                return

            key = self.key_var.get().strip()
            if not key:
                messagebox.showwarning("Предупреждение", "Введите ключ")
                return

            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            if self.selected_method.get() == "Столбцовый (англ)":
                space_positions = [i for i, char in enumerate(text) if char == ' ']
                text_without_spaces = text.replace(' ', '')

                filtered_text = self.filter_english_text(text_without_spaces)
                if not filtered_text:
                    messagebox.showwarning("Предупреждение", "Файл не содержит английских букв")
                    return

                encrypted_without_spaces = self.column_encrypt(filtered_text, key)

                result = list(encrypted_without_spaces)
                for pos in space_positions:
                    if pos < len(result):
                        result.insert(pos, ' ')
                    else:
                        result.append(' ')
                result = ''.join(result)
            else:
                result = self.vigenere_encrypt(text, key)

            self.last_result = result

            self.file_result_text.delete(1.0, END)
            self.file_result_text.insert(1.0, result)

            messagebox.showinfo("Успех",
                                f"Файл зашифрован.\n\n"
                                f"Результат отображен в поле 'Результат'.\n"
                                f"Теперь вы можете сохранить его в файл, нажав кнопку 'Сохранить результат'.")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def decrypt_file(self):
        try:
            input_file = self.file_path_var.get()
            if not input_file:
                messagebox.showwarning("Предупреждение", "Выберите файл для чтения")
                return

            key = self.key_var.get().strip()
            if not key:
                messagebox.showwarning("Предупреждение", "Введите ключ")
                return

            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            if self.selected_method.get() == "Столбцовый (англ)":
                space_positions = [i for i, char in enumerate(text) if char == ' ']
                text_without_spaces = text.replace(' ', '')

                filtered_text = self.filter_english_text(text_without_spaces)
                if not filtered_text:
                    messagebox.showwarning("Предупреждение", "Файл не содержит английских букв")
                    return

                decrypted_without_spaces = self.column_decrypt(filtered_text, key)

                result = list(decrypted_without_spaces)
                for pos in space_positions:
                    if pos < len(result):
                        result.insert(pos, ' ')
                    else:
                        result.append(' ')
                result = ''.join(result)
            else:
                result = self.vigenere_decrypt(text, key)

            self.last_result = result

            self.file_result_text.delete(1.0, END)
            self.file_result_text.insert(1.0, result)

            messagebox.showinfo("Успех",
                                f"Файл расшифрован.\n\n"
                                f"Результат отображен в поле 'Результат'.\n"
                                f"Теперь вы можете сохранить его в файл, нажав кнопку 'Сохранить результат'.")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


def main():
    window = Tk()
    app = CryptoApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()