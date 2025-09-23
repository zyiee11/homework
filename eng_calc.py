#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import math

# ---------- Безопасная среда вычислений ----------
# Глобальные флаги/память для режима углов и памяти калькулятора
class Runtime:
    angle_mode = "DEG"  # или "RAD"
    memory = 0.0

RT = Runtime()

# Обёртки триг-функций, уважающие DEG/RAD
def _to_rad(x):
    return x * math.pi / 180.0

def _from_rad(x):
    return x * 180.0 / math.pi

def sin(x):  return math.sin(_to_rad(x) if RT.angle_mode == "DEG" else x)
def cos(x):  return math.cos(_to_rad(x) if RT.angle_mode == "DEG" else x)
def tan(x):  return math.tan(_to_rad(x) if RT.angle_mode == "DEG" else x)

def asin(x): 
    r = math.asin(x)
    return _from_rad(r) if RT.angle_mode == "DEG" else r

def acos(x):
    r = math.acos(x)
    return _from_rad(r) if RT.angle_mode == "DEG" else r

def atan(x):
    r = math.atan(x)
    return _from_rad(r) if RT.angle_mode == "DEG" else r

# Прочие удобные функции
def ln(x): return math.log(x)
def log10(x): return math.log10(x)
def log2(x): return math.log2(x)
def sqrt(x): return math.sqrt(x)
def exp(x): return math.exp(x)
def fact(x):
    if x < 0 or int(x) != x:
        raise ValueError("factorial() только для целых ≥ 0")
    return math.factorial(int(x))
def inv(x):
    if x == 0:
        raise ZeroDivisionError("деление на ноль")
    return 1.0 / x
def pow10(x): return 10 ** x
def sqr(x): return x * x

SAFE_ENV = {
    # константы
    "pi": math.pi, "π": math.pi,
    "e": math.e,
    # функции
    "sin": sin, "cos": cos, "tan": tan,
    "asin": asin, "acos": acos, "atan": atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "ln": ln, "log": log10, "log10": log10, "log2": log2,
    "sqrt": sqrt, "exp": exp, "fact": fact, "factorial": fact,
    "inv": inv, "pow": pow, "pow10": pow10, "sqr": sqr,
    "abs": abs,
    # базовые
    "__builtins__": {}
}

# ---------- Калькулятор ----------
class CalcApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Инженерный калькулятор (Python)")
        self.geometry("420x560")
        self.minsize(400, 520)

        # стиль
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.expr_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value=RT.angle_mode)

        # Поле ввода/отображения
        self.entry = ttk.Entry(self, textvariable=self.expr_var, font=("Consolas", 18))
        self.entry.grid(row=0, column=0, columnspan=8, sticky="nsew", ipady=12, padx=8, pady=(8, 2))
        self.entry.focus_set()

        # Строка режима и памяти
        bar = ttk.Frame(self)
        bar.grid(row=1, column=0, columnspan=8, sticky="ew", padx=8, pady=(0, 6))
        self.mode_btn = ttk.Button(bar, text="DEG", width=6, command=self.toggle_mode)
        self.mode_btn.pack(side="left")
        self.mem_label = ttk.Label(bar, text="МП: 0")
        self.mem_label.pack(side="right")

        # сетка
        for r in range(2, 12):
            self.rowconfigure(r, weight=1)
        for c in range(8):
            self.columnconfigure(c, weight=1)

        # Кнопки
        self._build_buttons()

        # биндинги клавиатуры
        self.bind("<Return>", lambda e: self.equals())
        self.bind("<KP_Enter>", lambda e: self.equals())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>", lambda e: self.clear_all())
        self.bind("<Key>", self.on_key)

        # начальный рендер памяти
        self._update_mem_label()

    # ---------- Построение кнопок ----------
    def _btn(self, r, c, text, cmd, cs=1):
        b = ttk.Button(self, text=text, command=cmd)
        b.grid(row=r, column=c, columnspan=cs, sticky="nsew", padx=4, pady=4)
        return b

    def ins(self, s):
        self.entry.icursor(tk.END)
        self.entry.insert(tk.INSERT, s)

    def _build_buttons(self):
        # Ряд функций
        self._btn(2,0,"MC", self.mem_clear);   self._btn(2,1,"MR", self.mem_recall)
        self._btn(2,2,"M+", self.mem_add);     self._btn(2,3,"M-", self.mem_sub)
        self._btn(2,4,"(",  lambda: self.ins("("));    self._btn(2,5,")",  lambda: self.ins(")"))
        self._btn(2,6,"DEL", self.backspace);  self._btn(2,7,"AC", self.clear_all)

        # Тригонометрия и пр.
        self._btn(3,0,"sin", lambda: self.ins("sin(")); self._btn(3,1,"cos", lambda: self.ins("cos("))
        self._btn(3,2,"tan", lambda: self.ins("tan(")); self._btn(3,3,"ln",  lambda: self.ins("ln("))
        self._btn(3,4,"log", lambda: self.ins("log(")); self._btn(3,5,"log2",lambda: self.ins("log2("))
        self._btn(3,6,"x²",  lambda: self.ins("sqr(")); self._btn(3,7,"√",   lambda: self.ins("sqrt("))

        self._btn(4,0,"asin",lambda: self.ins("asin(")); self._btn(4,1,"acos",lambda: self.ins("acos("))
        self._btn(4,2,"atan",lambda: self.ins("atan(")); self._btn(4,3,"exp", lambda: self.ins("exp("))
        self._btn(4,4,"10^x",lambda: self.ins("pow10("));self._btn(4,5,"x^y", lambda: self.ins("pow("))
        self._btn(4,6,"1/x", lambda: self.ins("inv("));  self._btn(4,7,"n!",  lambda: self.ins("fact("))

        # Числовой блок
        self._btn(5,0,"7", lambda: self.ins("7")); self._btn(5,1,"8", lambda: self.ins("8"))
        self._btn(5,2,"9", lambda: self.ins("9")); self._btn(5,3,"/", lambda: self.ins("/"))
        self._btn(5,4,"π", lambda: self.ins("pi"));self._btn(5,5,"e",  lambda: self.ins("e"))
        self._btn(5,6,"%", lambda: self.ins("/100")); self._btn(5,7,"±", self.negate)

        self._btn(6,0,"4", lambda: self.ins("4")); self._btn(6,1,"5", lambda: self.ins("5"))
        self._btn(6,2,"6", lambda: self.ins("6")); self._btn(6,3,"*", lambda: self.ins("*"))
        self._btn(6,4,"sinh", lambda: self.ins("sinh(")); self._btn(6,5,"cosh", lambda: self.ins("cosh("))
        self._btn(6,6,"tanh", lambda: self.ins("tanh(")); self._btn(6,7,"^",    lambda: self.ins("**"))

        self._btn(7,0,"1", lambda: self.ins("1")); self._btn(7,1,"2", lambda: self.ins("2"))
        self._btn(7,2,"3", lambda: self.ins("3")); self._btn(7,3,"-", lambda: self.ins("-"))
        self._btn(7,4,"←", self.backspace);       self._btn(7,5,"C", self.clear_entry)
        self._btn(7,6,"ANS", self.insert_last_ans);self._btn(7,7,"=", self.equals)

        self._btn(8,0,"0", lambda: self.ins("0")); self._btn(8,1,"00", lambda: self.ins("00"))
        self._btn(8,2,".", lambda: self.ins(".")); self._btn(8,3,"+", lambda: self.ins("+"))
        # пустые для ровной сетки — увеличим "="
        eq = ttk.Button(self, text="=", command=self.equals)
        eq.grid(row=8, column=4, columnspan=4, sticky="nsew", padx=4, pady=4)

    # ---------- Память ----------
    def _update_mem_label(self):
        self.mem_label.config(text=f"МП: {RT.memory:g}")

    def mem_clear(self): RT.memory=0.0; self._update_mem_label()
    def mem_recall(self): self.ins(self._fmt(RT.memory))
    def mem_add(self):    RT.memory += self._eval_safe(self.expr_var.get() or "0"); self._update_mem_label()
    def mem_sub(self):    RT.memory -= self._eval_safe(self.expr_var.get() or "0"); self._update_mem_label()

    # ---------- Режим углов ----------
    def toggle_mode(self):
        RT.angle_mode = "RAD" if RT.angle_mode == "DEG" else "DEG"
        self.mode_btn.config(text=RT.angle_mode)

    # ---------- Редактирование ----------
    def backspace(self):
        s = self.expr_var.get()
        if s:
            self.expr_var.set(s[:-1])

    def clear_all(self): self.expr_var.set("")
    def clear_entry(self):
        # стирает последний "токен" после оператора
        s = self.expr_var.get()
        i = max(s.rfind('+'), s.rfind('-'), s.rfind('*'), s.rfind('/'), s.rfind('('), s.rfind(')'))
        self.expr_var.set(s[:i+1] if i >= 0 else "")

    def negate(self):
        s = self.expr_var.get()
        if not s:
            self.expr_var.set("-")
            return
        # если последним был оператор — просто вставим минус
        if s[-1] in "+-*/(":
            self.ins("-")
            return
        # обернём последний числовой фрагмент в -( ... )
        j = len(s)-1
        while j>=0 and (s[j].isalnum() or s[j] in "._"):
            j -= 1
        self.expr_var.set(s[:j+1] + "-(" + s[j+1:] + ")")

    def insert_last_ans(self):
        if hasattr(self, "_last_ans"):
            self.ins(self._fmt(self._last_ans))

    # ---------- Вычисления ----------
    def _fmt(self, x):
        # компактное форматирование
        return f"{x:.12g}"

    def _eval_safe(self, expr: str) -> float:
        # косметика: ^ как степень
        expr = expr.replace("^", "**")
        # заменить «×» и «÷», если вдруг вставили
        expr = expr.replace("×", "*").replace("÷", "/")
        # удалить пробелы
        expr = expr.strip()

        # вычисляем в ограниченной среде
        val = eval(expr, SAFE_ENV, {})
        if isinstance(val, (int, float)):
            return float(val)
        raise ValueError("выражение не вернуло число")

    def equals(self):
        expr = self.expr_var.get()
        if not expr:
            return
        try:
            val = self._eval_safe(expr)
            self._last_ans = val
            self.expr_var.set(self._fmt(val))
        except Exception as e:
            self.expr_var.set("Error")
            # через небольшую задержку вернуть исходное
            self.after(900, lambda: self.expr_var.set(""))

    # ---------- Клавиатура ----------
    def on_key(self, event: tk.Event):
        # Разрешим безопасные символы — остальное игнор
        allowed = "0123456789.+-*/()^"
        letters = "sincotaehlgprwx"  # для sin, cos, tan, ln, log, pow, exp, sqrt, pi, pow10, sqr, inv
        if event.char and (event.char in allowed or event.char.isalpha() and event.char.lower() in letters):
            return  # обычная вставка пройдёт в Entry
        # запретим прочие
        if event.keysym in ("Return","KP_Enter","BackSpace","Escape"):
            return
        return "break"

if __name__ == "__main__":
    app = CalcApp()
    app.mainloop()

