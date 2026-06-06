"""
Pro Fibonacci, Prime & Zeta Visualizer
======================================
This application is a mathematical tool designed to explore three distinct 
areas of number theory: 
1. Fibonacci Sequences (Growth and Golden Ratio)
2. Prime Number Distribution (Sieve of Eratosthenes and Prime Gap Analysis)
3. Riemann Zeta Function (Complex Analysis and the Critical Strip)

Architecture: 
- Backend: Pure Python with NumPy for numerical efficiency.
- Frontend: Tkinter for the GUI, Matplotlib for interactive visualization.
- Concurrency: Threading is used to prevent the UI from freezing during 
  heavy mathematical computations.
"""

import csv
import cmath
import math
import os
import threading
from datetime import datetime
from typing import List, Tuple, Optional, Union, Dict
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk

# =============================================================================
# 1. MATHEMATICAL CORE ENGINE
# =============================================================================

def complex_gamma(z: complex) -> complex:
    """
    The Gamma function extends the factorial function to complex numbers.
    We use the Lanczos Approximation, which provides high precision across 
    the complex plane by using a series of pre-calculated coefficients.
    """
    # Lanczos coefficients for precision
    p = [
        0.99999999999980993, 676.5203681218851, -1259.13921672240,
        771.3234287768164, -176.6150291621406, 12.50734024154800,
        -0.13857109526572012, 9.9843695780195716e-6, 1.5056327196869211e-7
    ]
    g = 7
    # Reflection formula for the left half-plane (where Re(z) < 0.5)
    if z.real < 0.5:
        return math.pi / (cmath.sin(math.pi * z) * complex_gamma(1 - z))

    z -= 1
    x = p[0]
    for i in range(1, len(p)):
        x += p[i] / (z + i)

    t = z + g + 0.5
    return math.sqrt(2 * math.pi) * t**(z + 0.5) * cmath.exp(-t) * x


def generate_fibonacci_list(n: int) -> List[int]:
    """
    Creates a list of Fibonacci numbers where each element is the sum of the 
    previous two. This illustrates exponential growth.
    """
    if n <= 0:
        return []
    seq = []
    a, b = 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq


def generate_primes_list(n: int) -> List[int]:
    """
    Sieve of Eratosthenes: An ancient, efficient algorithm to find all primes 
    up to limit N. It works by iteratively marking the multiples of each 
    prime as composite (not prime).
    """
    if n < 2:
        return []
    # Initialize a boolean array: assume all numbers are prime initially
    sieve = [True] * (n + 1)
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            # Mark all multiples of p starting from p*p as not prime
            for i in range(p * p, n + 1, p):
                sieve[i] = False
    return [p for p in range(2, n + 1) if sieve[p]]


def calculate_riemann_zeta(
    s: complex, 
    terms: int = 1000
) -> Tuple[Optional[complex], Optional[str], bool]:
    """
    Computes the Riemann Zeta function ζ(s). This is a critical function in 
    number theory that relates to the distribution of prime numbers.
    
    The logic is split into three mathematical regions:
    1. Re(s) > 1: Convergent Dirichlet series.
    2. 0 < Re(s) < 1: Alternating Eta series (used to analyze the critical strip).
    3. Re(s) <= 0: Functional Equation (mirrors values from the right plane).
    """
    # The pole at s = 1 causes the function to diverge (infinity)
    if s == 1 + 0j:
        return None, None, False

    # Trivial Zeros: Occur at negative even integers (-2, -4, -6...)
    if s.imag == 0 and s.real < 0 and s.real == float(int(s.real)) \
            and int(s.real) % 2 == 0:
        return 0 + 0j, "Trivial Zero", True

    if s.real > 1:
        # Dirichlet Series: ζ(s) = Σ (1 / n^s)
        zeta_sum = 0 + 0j
        series_parts = []
        for n in range(1, terms + 1):
            term = n**(-s)
            zeta_sum += term
            if n <= 5:
                series_parts.append(f"{n}^(-{s})")
        series_str = "Σ " + " + ".join(series_parts) + "... (Dirichlet Series)"
        return zeta_sum, series_str, True

    elif s.real > 0:
        # Dirichlet Eta function: used to compute Zeta in the critical strip (0 < Re(s) < 1)
        eta_sum = 0 + 0j
        series_parts = []
        for n in range(1, terms + 1):
            term = ((-1)**(n-1)) * (n**(-s))
            eta_sum += term
            if n <= 5:
                series_parts.append(f"((-1)^{n-1}) * {n}^(-{s})")
        denominator = 1 - (2**(1-s))
        zeta_sum = eta_sum / denominator
        series_str = (f"1/(1-2^(1-{s})) * [Σ " 
                      f"{' + '.join(series_parts)}... (Eta Series)]")
        return zeta_sum, series_str, True

    else:
        # Functional Equation: Maps the zeta function to the left plane using Gamma
        s_reflected = 1 - s
        zeta_reflected, _, _ = calculate_riemann_zeta(s_reflected, terms)
        term1 = 2**s
        term2 = (complex(math.pi)**(s-1))
        term3 = cmath.sin((math.pi * s) / 2)
        gamma_val = complex_gamma(1 - s)
        zeta_sum = term1 * term2 * term3 * gamma_val * zeta_reflected
        series_str = f"Functional Equation Mapping: ζ({s}) ⮕ ζ({s_reflected})"
        return zeta_sum, series_str, True

# =============================================================================
# 2. USER INTERFACE & APPLICATION ARCHITECTURE
# =============================================================================

class FibPrimeApp:
    """
    The main Controller class for the GUI. 
    It handles window management, user input, and the bridge between 
    mathematical logic and the visual display.
    """

    COLORS = {
        "primary": "#2c3e50",
        "secondary": "#3498db",
        "save_accent": "#2980b9",
        "fib_accent": "#e67e22",
        "prime_accent": "#27ae60",
        "zeta_accent": "#8e44ad",
        "danger": "#e74c3c",
        "text_dark": "#2f3640",
        "bg_light": "#ffffff",
        "table_header": "#ecf0f1"
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Pro Fibonacci, Prime & Zeta Visualizer")
        self.root.geometry("900x750")
        self.root.configure(bg="#f5f6fa")

        # Shared data storage for plotting and exporting
        self.current_data: List[Union[int, float]] = []
        self.zeta_pairs: List[Tuple[complex, complex]] = []

        self.center_window()
        self.setup_navigation()

        # Central content area where all screens are loaded
        self.content_frame = tk.Frame(
            self.root, bg=self.COLORS["bg_light"],
            padx=30, pady=30, highlightthickness=1,
            highlightbackground="#dcdde1"
        )
        self.content_frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.show_fib_screen()

    def setup_navigation(self) -> None:
        """Creates the top navigation bar for switching between tool modules."""
        self.nav_bar = tk.Frame(self.root, bg=self.COLORS["primary"], pady=15)
        self.nav_bar.pack(fill="x")

        nav_buttons = [
            ("Fibonacci", self.show_fib_screen, "left"),
            ("Primes", self.show_prime_screen, "left"),
            ("Zeta Function", self.show_zeta_screen, "left"),
        ]

        for text, cmd, side in nav_buttons:
            btn = tk.Button(
                self.nav_bar, text=text, command=cmd,
                bg=self.COLORS["primary"], fg="white", relief="flat",
                font=("Segoe UI", 10, "bold"), padx=15, cursor="hand2"
            )
            btn.pack(side=side, padx=15)

        self.btn_about = tk.Button(
            self.nav_bar, text="About", command=self.show_about,
            bg=self.COLORS["primary"], fg="#bdc3c7", relief="flat",
            font=("Segoe UI", 10), padx=15, cursor="hand2"
        )
        self.btn_about.pack(side="right", padx=15)

        self.btn_exit = tk.Button(
            self.nav_bar, text="Exit", command=self.root.destroy,
            bg=self.COLORS["danger"], fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=15, cursor="hand2"
        )
        self.btn_exit.pack(side="right", padx=15)

    def center_window(self) -> None:
        """Calculates the screen center to position the app window."""
        self.root.update_idletasks()
        width, height = 900, 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def clear_frame(self) -> None:
        """Wipes the content frame clean before loading a new screen."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_input_field(self, label_text: str) -> ttk.Entry:
        """Standardized input field creator for a consistent UI look."""
        tk.Label(
            self.content_frame, text=label_text, font=("Segoe UI", 11),
            bg=self.COLORS["bg_light"], fg=self.COLORS["text_dark"]
        ).pack(pady=(10, 5))
        entry = ttk.Entry(self.content_frame, justify='center', font=("Segoe UI", 12))
        entry.pack(pady=5)
        return entry

    def create_result_display(self) -> tk.Text:
        """Creates the result window with a vertical scrollbar for large datasets."""
        container = tk.Frame(self.content_frame, bg=self.COLORS["bg_light"])
        container.pack(pady=20, expand=True, fill="both")
        
        v_scroll = tk.Scrollbar(container, orient="vertical")
        v_scroll.pack(side="right", fill="y")
        
        # 'wrap=none' is used specifically for the Prime Gap Summary table to ensure
        # the columns align vertically like a spreadsheet.
        text_area = tk.Text(
            container, wrap="none", font=("Consolas", 11),
            bg="#f9f9f9", relief="flat", padx=10, pady=10
        )
        text_area.pack(side="left", expand=True, fill="both")
        text_area.config(yscrollcommand=v_scroll.set)
        v_scroll.config(command=text_area.yview)
        text_area.config(state="disabled")
        return text_area

    def format_indexed_data(self, data: List[Union[int, float]]) -> str:
        """Wraps data into rows of 10 to avoid excessive vertical scrolling."""
        indexed_list = [f"{i+1}) {val}" for i, val in enumerate(data)]
        rows = []
        for i in range(0, len(indexed_list), 10):
            chunk = indexed_list[i : i + 10]
            rows.append(", ".join(chunk))
        return "\n".join(rows)

    def format_prime_gaps(self, gap_strings: List[str]) -> str:
        """Wraps prime gap calculations into rows of 5 for better readability."""
        rows = []
        for i in range(0, len(gap_strings), 5):
            chunk = gap_strings[i : i + 5]
            rows.append(", ".join(chunk))
        return "\n".join(rows)

    def show_fib_screen(self) -> None:
        """UI Setup for the Fibonacci module."""
        self.clear_frame()
        tk.Label(
            self.content_frame, text="Fibonacci Sequence", 
            font=("Segoe UI", 16, "bold"), bg=self.COLORS["bg_light"], 
            fg=self.COLORS["primary"]
        ).pack(pady=(0, 20))
        
        self.entry_n = self.create_input_field("Enter number of elements (N):")
        
        btn_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg_light"])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame, text="Generate", bg=self.COLORS["fib_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_fib)
        ).pack(side="left", padx=5)
        
        self.btn_plot = tk.Button(
            btn_frame, text="Visualize", bg=self.COLORS["secondary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.plot_data("Fibonacci")
        )
        self.btn_plot.pack(side="left", padx=5)
        
        self.btn_save = tk.Button(
            btn_frame, text="Save to CSV", bg=self.COLORS["save_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.export_to_csv("Fib", ["Index N", "Fibonacci Number"])
        )
        self.btn_save.pack(side="left", padx=5)
        self.result_label = self.create_result_display()

    def show_prime_screen(self) -> None:
        """UI Setup for the Prime Distribution module."""
        self.clear_frame()
        tk.Label(
            self.content_frame, text="Prime Number Distribution Analysis", 
            font=("Segoe UI", 16, "bold"), bg=self.COLORS["bg_light"], 
            fg=self.COLORS["primary"]
        ).pack(pady=(0, 20))
        
        self.entry_n = self.create_input_field("Enter upper limit (N):")
        
        main_btn_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg_light"])
        main_btn_frame.pack(pady=20)

        # Command Group: Actions related to generating data
        gen_group = tk.Frame(main_btn_frame, bg=self.COLORS["bg_light"])
        gen_group.pack(side="left", padx=10)

        tk.Button(
            gen_group, text="Generate Primes", bg=self.COLORS["prime_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_prime)
        ).pack(side="left", padx=5)

        tk.Button(
            gen_group, text="Prime Gap", bg=self.COLORS["primary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_prime_gap)
        ).pack(side="left", padx=5)

        tk.Button(
            gen_group, text="Gap Summary", bg=self.COLORS["primary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_prime_gap_summary)
        ).pack(side="left", padx=5)

        # Action Group: Actions related to data manipulation (plotting/saving)
        action_group = tk.Frame(main_btn_frame, bg=self.COLORS["bg_light"])
        action_group.pack(side="left", padx=10)

        self.btn_plot = tk.Button(
            action_group, text="Visualize", bg=self.COLORS["secondary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.plot_data("Prime")
        )
        self.btn_plot.pack(side="left", padx=5)
        
        self.btn_save = tk.Button(
            action_group, text="Save to CSV", bg=self.COLORS["save_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.export_to_csv("prime", ["Index N", "Prime Number"])
        )
        self.btn_save.pack(side="left", padx=5)
        
        self.result_label = self.create_result_display()

    def show_zeta_screen(self) -> None:
        """UI Setup for the Riemann Zeta module."""
        self.clear_frame()
        tk.Label(
            self.content_frame, text="Riemann Zeta Function", 
            font=("Segoe UI", 16, "bold"), bg=self.COLORS["bg_light"], 
            fg=self.COLORS["primary"]
        ).pack(pady=(0, 20))
        
        self.entry_n = self.create_input_field(
            "Enter complex numbers s (separated by , or ; e.g., 2, -2, 0.5+14.13j, 2+2j):"
        )
        
        btn_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg_light"])
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, text="Calculate Zeta", bg=self.COLORS["zeta_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_zeta)
        ).pack(side="left", padx=5)

        self.btn_zeta_plot_2d = tk.Button(
            btn_frame, text="Visualize 2D", bg=self.COLORS["secondary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.plot_zeta_complex()
        )
        self.btn_zeta_plot_2d.pack(side="left", padx=5)

        self.btn_zeta_plot_3d = tk.Button(
            btn_frame, text="Visualize 3D", bg=self.COLORS["secondary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.plot_zeta_3d()
        )
        self.btn_zeta_plot_3d.pack(side="left", padx=5)
        
        self.result_label = self.create_result_display()

    def export_to_csv(self, prefix: str, headers: List[str]) -> None:
        """Saves current data to a CSV file in the User's Downloads folder."""
        if not self.current_data:
            return
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"
        full_path = os.path.join(downloads_folder, filename)
        try:
            with open(full_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                for i, value in enumerate(self.current_data, start=1):
                    writer.writerow([i, value])
            messagebox.showinfo("Export Successful", f"File saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not save file: {e}")

    def start_thread(self, target_func) -> None:
        """Run calculations in a background thread to keep the UI responsive."""
        threading.Thread(target=target_func, daemon=True).start()

    def exec_fib(self) -> None:
        """Validates input and computes Fibonacci sequence."""
        try:
            n = int(self.entry_n.get())
            if n > 10000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000.")
                return
            self.current_data = generate_fibonacci_list(n)
            result_text = self.format_indexed_data(self.current_data)
            self.root.after(0, self.display_result, result_text)
            self.root.after(0, lambda: self.btn_plot.config(state="normal"))
            self.root.after(0, lambda: self.btn_save.config(state="normal"))
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def exec_prime(self) -> None:
        """Validates input and computes Prime numbers."""
        try:
            n = int(self.entry_n.get())
            if n > 10000000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000,000.")
                return
            self.current_data = generate_primes_list(n)
            result_text = self.format_indexed_data(self.current_data)
            self.root.after(0, self.display_result, result_text)
            self.root.after(0, lambda: self.btn_plot.config(state="normal"))
            self.root.after(0, lambda: self.btn_save.config(state="normal"))
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def exec_prime_gap(self) -> None:
        """Calculates the gap between consecutive primes for the given range."""
        try:
            n = int(self.entry_n.get())
            if n > 10000000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000,000.")
                return
            primes = generate_primes_list(n)
            if len(primes) < 2:
                self.root.after(0, lambda: messagebox.showinfo("Info", "Not enough primes to calculate gaps."))
                return

            gap_strings = []
            for i in range(len(primes) - 1):
                pn, pn_plus_1 = primes[i], primes[i+1]
                gap_strings.append(f"{i+1}){pn_plus_1}-{pn}={pn_plus_1 - pn}")

            result_text = self.format_prime_gaps(gap_strings)
            self.root.after(0, self.display_result, result_text)
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def exec_prime_gap_summary(self) -> None:
        """
        Analyzes prime gap frequencies.
        Groups primes by the size of the gap between them and formats 
        the output into a professional, Excel-style table.
        """
        try:
            n = int(self.entry_n.get())
            if n > 10000000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000,000.")
                return
            
            primes = generate_primes_list(n)
            if len(primes) < 2:
                self.root.after(0, lambda: messagebox.showinfo("Info", "Not enough primes to generate a summary."))
                return

            # Mathematical grouping: {Gap_Size: [ (P1, P2), (P3, P4)... ]}
            gap_map = defaultdict(list)
            for i in range(len(primes) - 1):
                p1, p2 = primes[i], primes[i+1]
                gap = p2 - p1
                gap_map[gap].append(f"({p1}, {p2})")

            sorted_gaps = sorted(gap_map.keys())
            
            # Formatting constants for "Excel" alignment
            COL_GAP = 12
            COL_PAIRS = 60
            COL_TOTAL = 15
            
            header = f" {'Gap Size':<{COL_GAP}} | {'Prime Pairs (Pn, Pn+1)':<{COL_PAIRS}} | {'Total':<{COL_TOTAL}} "
            separator = "—" * (COL_GAP + COL_PAIRS + COL_TOTAL + 6) + "\n"
            
            table_rows = []
            for gap in sorted_gaps:
                pairs = gap_map[gap]
                pairs_str = ", ".join(pairs)
                total_count = len(pairs)
                
                # Text Wrapping Logic: 
                # Since we use 'wrap=none' for the text widget, we must manually split
                # the strings to ensure the 'Total' column remains aligned on the right.
                row_lines = [pairs_str[i : i + COL_PAIRS] for i in range(0, len(pairs_str), COL_PAIRS)]

                # Primary row line: Contains Gap and Total
                first_line = f" {gap:<{COL_GAP}} | {row_lines[0]:<{COL_PAIRS}} | Total: {total_count:<{COL_TOTAL-7}} "
                table_rows.append(first_line)
                
                # Overflow lines: Contains only the continuation of the prime pairs
                for j in range(1, len(row_lines)):
                    line = f" {' ' * COL_GAP} | {row_lines[j]:<{COL_PAIRS}} | {' ' * (COL_TOTAL-1)} "
                    table_rows.append(line)
                
                # Visual divider between different gap sizes
                table_rows.append(" " * (COL_GAP + 3) + "┈" * (COL_PAIRS + COL_TOTAL + 2))

            final_summary = header + "\n" + separator + "\n" + "\n".join(table_rows)
            self.root.after(0, self.display_result, final_summary)

        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def exec_zeta(self) -> None:
        """Calculates Riemann Zeta values and handles the complex number mapping."""
        try:
            raw_input = self.entry_n.get()
            s_strings = [x.strip() for x in raw_input.replace(';', ',').split(',')]
            self.zeta_pairs = []
            all_results = []
            zeta_symbol = "ζ"

            for idx, s_str in enumerate(s_strings, 1):
                try:
                    s_val = complex(s_str)
                    val, series, converges = calculate_riemann_zeta(s_val)
                    if converges:
                        if series == "Trivial Zero":
                            line = (f"{idx}. {zeta_symbol}({s_str}) = Trivial Zero\n"
                                   f"   {zeta_symbol}({s_str}) = 0 (Negative Even Integer)\n")
                        else:
                            line = (f"{idx}. {zeta_symbol}({s_str}) = {val}\n"
                                   f"   {zeta_symbol}({s_str}) = {series}\n")
                        if val is not None:
                            self.zeta_pairs.append((s_val, val))
                    else:
                        line = (f"{idx}. {zeta_symbol}({s_str}) = Diverges\n"
                                f"   {zeta_symbol}({s_str}) = Pole at s=1\n")
                    all_results.append(line)
                except ValueError:
                    all_results.append(f"{idx}. Error: '{s_str}' is invalid.\n")

            final_text = "\n".join(all_results)
            self.root.after(0, self.display_result, final_text)
            status = "normal" if self.zeta_pairs else "disabled"
            self.root.after(0, lambda: self.btn_zeta_plot_2d.config(state=status))
            self.root.after(0, lambda: self.btn_zeta_plot_3d.config(state=status))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))

    def display_result(self, text: str) -> None:
        """Safe update of the text area from a background thread."""
        self.result_label.config(state="normal")
        self.result_label.delete("1.0", tk.END)
        self.result_label.insert(tk.END, text)
        self.result_label.config(state="disabled")

    def plot_data(self, mode: str) -> None:
        """
        Interactive visualizer for sequence growth.
        Fix: We synchronize the data plotted with the data used for tooltips 
        to ensure the hover index is always accurate.
        """
        if not self.current_data:
            return
        
        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(11, 7))
        
        # Data Downsampling logic: 
        # If we have too many points (e.g. 1M primes), the plot becomes a solid wall 
        # and tooltips break. We slice the data to exactly 5,000 points if necessary.
        all_x = np.arange(1, len(self.current_data) + 1)
        all_y = np.array(self.current_data)

        if len(all_x) > 5000:
            indices = np.linspace(0, len(all_x)-1, 5000, dtype=int)
            x_plot = all_x[indices]
            y_plot = all_y[indices]
        else:
            x_plot, y_plot = all_x, all_y

        color = self.COLORS["fib_accent"] if mode == "Fibonacci" else self.COLORS["prime_accent"]
        ax.plot(x_plot, y_plot, color=color, linewidth=2, alpha=0.8)
        
        if mode == "Fibonacci":
            ax.set_yscale('log')
            ax.set_title(f"{mode} Distribution (Log Scale)", fontsize=14, fontweight='bold')
        else:
            ax.set_title(f"{mode} Distribution", fontsize=14, fontweight='bold')

        ax.set_xlabel("Index (N)", fontsize=12)
        ax.set_ylabel("Value", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)

        # Create Annotation object (the tooltip box)
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", color='k'))
        annot.set_visible(False)
        
        # Create a red dot that follows the mouse cursor
        cursor_marker = ax.plot(0, 0, 'ro', markersize=6)[0]
        cursor_marker.set_visible(False)

        def update_annot(ind):
            """Updates the position and text of the tooltip."""
            # Get the index of the nearest plotted point
            idx = int(round(ind[0])) - 1
            idx = max(0, min(idx, len(x_plot)-1))
            
            pos = (x_plot[idx], y_plot[idx])
            annot.xy = pos
            annot.set_text(f"Index: {x_plot[idx]}\nValue: {y_plot[idx]}")
            cursor_marker.set_data([x_plot[idx]], [y_plot[idx]])
            annot.set_visible(True)
            cursor_marker.set_visible(True)

        def hover(event):
            """Triggers when the mouse moves over the plot area."""
            if event.inaxes == ax:
                # Search for the nearest point to the mouse cursor
                # We use a simple distance check for the current plotted indices
                dist = np.abs(x_plot - event.xdata)
                nearest_idx = np.argmin(dist)
                
                # Move the annotation to that point
                pos = (x_plot[nearest_idx], y_plot[nearest_idx])
                annot.xy = pos
                annot.set_text(f"Index: {x_plot[nearest_idx]}\nValue: {y_plot[nearest_idx]}")
                cursor_marker.set_data([x_plot[nearest_idx]], [y_plot[nearest_idx]])
                
                annot.set_visible(True)
                cursor_marker.set_visible(True)
                fig.canvas.draw_idle()
            else:
                annot.set_visible(False)
                cursor_marker.set_visible(False)
                fig.canvas.draw_idle()

        # Connect the hover function to the Matplotlib event loop
        fig.canvas.mpl_connect("motion_notify_event", hover)
        plt.tight_layout()
        plt.show()

    def plot_zeta_complex(self) -> None:
        """Plots the input 's' and the resulting 'zeta(s)' on the complex plane."""
        if not self.zeta_pairs:
            return
        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(10, 8))
        s_reals = [p[0].real for p in self.zeta_pairs]
        s_imags = [p[0].imag for p in self.zeta_pairs]
        z_reals = [p[1].real for p in self.zeta_pairs]
        z_imags = [p[1].imag for p in self.zeta_pairs]
        ax.scatter(s_reals, s_imags, color=self.COLORS["secondary"], label='Input $s$', zorder=3, s=60, edgecolors='k')
        ax.scatter(z_reals, z_imags, color=self.COLORS["zeta_accent"], label=r'$\zeta(s)$', zorder=3, s=60, edgecolors='k')
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        ax.set_title("Riemann Zeta Mapping in the Complex Plane", fontsize=14, fontweight='bold')
        ax.set_xlabel("Real Part (Re)", fontsize=12)
        ax.set_ylabel("Imaginary Part (Im)", fontsize=12)
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_aspect('equal')
        plt.tight_layout()
        plt.show()

    def plot_zeta_3d(self) -> None:
        """Plots the magnitude of the Zeta function in a 3D coordinate system."""
        if not self.zeta_pairs:
            return
        plt.style.use('seaborn-v0_8-muted')
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        s_reals = [p[0].real for p in self.zeta_pairs]
        s_imags = [p[0].imag for p in self.zeta_pairs]
        z_mags = [abs(p[1]) for p in self.zeta_pairs]
        scatter = ax.scatter(s_reals, s_imags, z_mags, c=z_mags, cmap='viridis', s=60, edgecolors='k', alpha=0.8)
        fig.colorbar(scatter, ax=ax, label=r'Magnitude $|\zeta(s)|$')
        ax.set_title("3D Visualization: Magnitude of Riemann Zeta Function", fontsize=14, fontweight='bold')
        ax.set_xlabel("Real Part (Re s)", fontsize=12)
        ax.set_ylabel("Imaginary Part (Im s)", fontsize=12)
        ax.set_zlabel(r"$|\zeta(s)|$", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.view_init(elev=30, azim=45)
        plt.tight_layout()
        plt.show()

    def show_about(self) -> None:
        """Displays a summary of the tool's mathematical capabilities."""
        about_text = (
            "Pro Fibonacci, Prime & Zeta Visualizer\n"
            "--------------------------------------------------\n\n"
            "Fibonacci: Generates sequence growth analysis.\n\n"
            "Primes: Sieve of Eratosthenes with Gap Analysis.\n"
            "- Prime Gap: Sequential difference between primes.\n"
            "- Gap Summary: professional analysis of gap frequency.\n\n"
            "Riemann Zeta: Computes ζ(s) for complex values.\n"
            "- Re(s) > 1: Dirichlet series convergence.\n"
            "- 0 < Re(s) < 1: Analyzes the critical strip via Eta.\n"
            "- Re(s) <= 0: Functional Equation symmetry mapping.\n\n"
            "--------------------------------------------------\n"
            "Author: Praveen KN\n"
            "This software is for educational purpose only."
        )
        messagebox.showinfo("About", about_text)


if __name__ == "__main__":
    root_window = tk.Tk()
    app = FibPrimeApp(root_window)
    root_window.mainloop()

