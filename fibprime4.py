"""
Pro Fibonacci, Prime & Zeta Visualizer.
This module provides a GUI application to calculate and visualize 
Fibonacci sequences, Prime numbers, and the Riemann Zeta function.
"""

import csv
import cmath
import math
import os
import threading
from datetime import datetime
from typing import List, Tuple, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk

# =============================================================================
# 1. CORE MATHEMATICAL LOGIC
# =============================================================================

def complex_gamma(z: complex) -> complex:
    """
    Compute the Gamma function for complex numbers using Lanczos approximation.
    """
    # Lanczos coefficients
    p = [
        0.99999999999980993, 676.5203681218851, -1259.13921672240,
        771.3234287768164, -176.6150291621406, 12.50734024154800,
        -0.13857109526572012, 9.9843695780195716e-6, 1.5056327196869211e-7
    ]
    g = 7
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
    Generate a list of Fibonacci numbers up to n elements.
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
    Generate prime numbers up to a given limit using the Sieve of Eratosthenes.
    """
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            for i in range(p * p, n + 1, p):
                sieve[i] = False
    return [p for p in range(2, n + 1) if sieve[p]]


def calculate_riemann_zeta(
    s: complex, 
    terms: int = 1000
) -> Tuple[Optional[complex], Optional[str], bool]:
    """
    Compute the Riemann Zeta function ζ(s) for complex numbers.
    """
    if s == 1 + 0j:
        return None, None, False

    # Trivial Zeros check
    if s.imag == 0 and s.real < 0 and s.real == float(int(s.real)) \
            and int(s.real) % 2 == 0:
        return 0 + 0j, "Trivial Zero", True

    if s.real > 1:
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
        # Functional Equation
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
# 2. MAIN APPLICATION CLASS
# =============================================================================

class FibPrimeApp:
    """
    Main application class for the Pro Fibonacci, Prime & Zeta Visualizer.
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
        "bg_light": "#ffffff"
    }

    def __init__(self, root: tk.Tk):
        """Initialize the application window and layout."""
        self.root = root
        self.root.title("Pro Fibonacci, Prime & Zeta Visualizer")
        self.root.geometry("800x700")
        self.root.configure(bg="#f5f6fa")

        self.current_data: List[Union[int, float]] = []
        self.zeta_pairs: List[Tuple[complex, complex]] = []

        self.center_window()
        self.setup_navigation()

        self.content_frame = tk.Frame(
            self.root, bg=self.COLORS["bg_light"],
            padx=30, pady=30, highlightthickness=1,
            highlightbackground="#dcdde1"
        )
        self.content_frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.show_fib_screen()

    def setup_navigation(self) -> None:
        """Initializes the top navigation bar and its buttons."""
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
        """Centers the main application window on the screen."""
        self.root.update_idletasks()
        width, height = 800, 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def clear_frame(self) -> None:
        """Removes all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_input_field(self, label_text: str) -> ttk.Entry:
        """Helper to create a label and an entry field."""
        tk.Label(
            self.content_frame, text=label_text, font=("Segoe UI", 11),
            bg=self.COLORS["bg_light"], fg=self.COLORS["text_dark"]
        ).pack(pady=(10, 5))
        entry = ttk.Entry(self.content_frame, justify='center', font=("Segoe UI", 12))
        entry.pack(pady=5)
        return entry

    def create_result_display(self) -> tk.Text:
        """Creates a scrollable text area for results."""
        container = tk.Frame(self.content_frame, bg=self.COLORS["bg_light"])
        container.pack(pady=20, expand=True, fill="both")
        
        v_scroll = tk.Scrollbar(container, orient="vertical")
        v_scroll.pack(side="right", fill="y")
        
        text_area = tk.Text(
            container, wrap="word", font=("Consolas", 11),
            bg="#f9f9f9", relief="flat", padx=10, pady=10
        )
        text_area.pack(side="left", expand=True, fill="both")
        text_area.config(yscrollcommand=v_scroll.set)
        v_scroll.config(command=text_area.yview)
        text_area.config(state="disabled")
        return text_area

    def format_indexed_data(self, data: List[Union[int, float]]) -> str:
        """Formats a list of numbers into indexed strings arranged in rows of 10."""
        indexed_list = [f"{i+1}) {val}" for i, val in enumerate(data)]
        rows = []
        for i in range(0, len(indexed_list), 10):
            chunk = indexed_list[i : i + 10]
            rows.append(", ".join(chunk))
        return "\n".join(rows)

    def format_prime_gaps(self, gap_strings: List[str]) -> str:
        """Formats prime gap strings arranged in rows of 5."""
        rows = []
        for i in range(0, len(gap_strings), 5):
            chunk = gap_strings[i : i + 5]
            rows.append(", ".join(chunk))
        return "\n".join(rows)

    def show_fib_screen(self) -> None:
        """Sets up the UI for the Fibonacci generator."""
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
        """Sets up the UI for the Prime number generator."""
        self.clear_frame()
        tk.Label(
            self.content_frame, text="Prime Number Generator", 
            font=("Segoe UI", 16, "bold"), bg=self.COLORS["bg_light"], 
            fg=self.COLORS["primary"]
        ).pack(pady=(0, 20))
        
        self.entry_n = self.create_input_field("Enter limit (N):")
        
        btn_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg_light"])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame, text="Generate", bg=self.COLORS["prime_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_prime)
        ).pack(side="left", padx=5)

        # New Prime Gap Button
        tk.Button(
            btn_frame, text="Prime Gap", bg=self.COLORS["primary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat", 
            padx=15, cursor="hand2", command=lambda: self.start_thread(self.exec_prime_gap)
        ).pack(side="left", padx=5)
        
        self.btn_plot = tk.Button(
            btn_frame, text="Visualize", bg=self.COLORS["secondary"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.plot_data("Prime")
        )
        self.btn_plot.pack(side="left", padx=5)
        
        self.btn_save = tk.Button(
            btn_frame, text="Save to CSV", bg=self.COLORS["save_accent"], 
            fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, cursor="hand2", state="disabled",
            command=lambda: self.export_to_csv("prime", ["Index N", "Prime Number"])
        )
        self.btn_save.pack(side="left", padx=5)
        self.result_label = self.create_result_display()

    def show_zeta_screen(self) -> None:
        """Sets up the UI for the Riemann Zeta calculator."""
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
        """Exports sequence data to a CSV file in the Downloads folder."""
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
        """Executes computations in a separate daemon thread."""
        threading.Thread(target=target_func, daemon=True).start()

    def exec_fib(self) -> None:
        """Validates input and generates Fibonacci sequence."""
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
        """Validates input and generates Prime numbers."""
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
        """Calculates and displays the gaps between consecutive primes."""
        try:
            n = int(self.entry_n.get())
            if n > 10000000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000,000.")
                return
            
            primes = generate_primes_list(n)
            if len(primes) < 2:
                self.root.after(0, lambda: messagebox.showinfo("Info", "Not enough primes found to calculate gaps."))
                return

            gap_strings = []
            for i in range(len(primes) - 1):
                pn = primes[i]
                pn_plus_1 = primes[i+1]
                gap = pn_plus_1 - pn
                # Format: 1) 3-2=1
                gap_strings.append(f"{i+1}){pn_plus_1}-{pn}={gap}")

            result_text = self.format_prime_gaps(gap_strings)
            self.root.after(0, self.display_result, result_text)
            
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def exec_zeta(self) -> None:
        """Processes Riemann Zeta calculations for multiple complex inputs."""
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
        """Updates the text area with the final calculated result."""
        self.result_label.config(state="normal")
        self.result_label.delete("1.0", tk.END)
        self.result_label.insert(tk.END, text)
        self.result_label.config(state="disabled")

    def plot_data(self, mode: str) -> None:
        """Plots Fibonacci or Prime distributions."""
        if not self.current_data:
            return
        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(11, 7))
        x = np.arange(1, len(self.current_data) + 1)
        y = np.array(self.current_data)

        if len(x) > 5000:
            indices = np.linspace(0, len(x)-1, 5000, dtype=int)
            x_plot, y_plot = x[indices], y[indices]
        else:
            x_plot, y_plot = x, y

        color = self.COLORS["fib_accent"] if mode == "Fibonacci" \
                else self.COLORS["prime_accent"]
        ax.plot(x_plot, y_plot, color=color, linewidth=2, alpha=0.8)
        
        if mode == "Fibonacci":
            ax.set_yscale('log')
            ax.set_title(f"{mode} Distribution (Log Scale)", fontsize=14, fontweight='bold')
        else:
            ax.set_title(f"{mode} Distribution", fontsize=14, fontweight='bold')

        ax.set_xlabel("Index (N)", fontsize=12)
        ax.set_ylabel("Value", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)

        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", color='k'))
        annot.set_visible(False)
        cursor_marker = ax.plot(0, 0, 'ro', markersize=6)[0]
        cursor_marker.set_visible(False)

        def update_annot(ind):
            idx = int(round(ind[0])) - 1
            idx = max(0, min(idx, len(self.current_data)-1))
            pos = (x[idx], y[idx])
            annot.xy = pos
            annot.set_text(f"Index: {x[idx]}\nValue: {y[idx]}")
            cursor_marker.set_data([x[idx]], [y[idx]])
            annot.set_visible(True)
            cursor_marker.set_visible(True)

        def hover(event):
            if event.inaxes == ax:
                update_annot((event.xdata, event.ydata))
                fig.canvas.draw_idle()
            else:
                annot.set_visible(False)
                cursor_marker.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)
        plt.tight_layout()
        plt.show()

    def plot_zeta_complex(self) -> None:
        """Plots s and zeta(s) on the complex plane."""
        if not self.zeta_pairs:
            return
        
        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(10, 8))
        
        s_reals = [p[0].real for p in self.zeta_pairs]
        s_imags = [p[0].imag for p in self.zeta_pairs]
        z_reals = [p[1].real for p in self.zeta_pairs]
        z_imags = [p[1].imag for p in self.zeta_pairs]
        
        ax.scatter(s_reals, s_imags, color=self.COLORS["secondary"], 
                  label='Input $s$', zorder=3, s=60, edgecolors='k')
        ax.scatter(z_reals, z_imags, color=self.COLORS["zeta_accent"], 
                  label=r'$\zeta(s)$', zorder=3, s=60, edgecolors='k')
        
        for i in range(len(self.zeta_pairs)):
            ax.plot([s_reals[i], z_reals[i]], [s_imags[i], z_imags[i]], 
                    color='gray', linestyle='--', alpha=0.4, zorder=2)

        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        ax.set_title("Riemann Zeta Mapping in the Complex Plane", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("Real Part (Re)", fontsize=12)
        ax.set_ylabel("Imaginary Part (Im)", fontsize=12)
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_aspect('equal')

        annot = ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", color='k'))
        annot.set_visible(False)

        def format_complex(c: complex) -> str:
            real = round(c.real, 4)
            imag = round(abs(c.imag), 4)
            sign = "+" if c.imag >= 0 else "-"
            return f"{real} {sign} {imag}j"

        def hover(event):
            if event.inaxes == ax:
                best_dist, best_type, best_idx = float('inf'), None, -1
                for i in range(len(self.zeta_pairs)):
                    ds = np.hypot(event.xdata - s_reals[i], event.ydata - s_imags[i])
                    if ds < best_dist:
                        best_dist, best_type, best_idx = ds, 's', i
                    dz = np.hypot(event.xdata - z_reals[i], event.ydata - z_imags[i])
                    if dz < best_dist:
                        best_dist, best_type, best_idx = dz, 'z', i

                if best_dist < 0.2:
                    s_val, z_val = self.zeta_pairs[best_idx]
                    if best_type == 's':
                        annot.xy = (s_reals[best_idx], s_imags[best_idx])
                        annot.set_text(f"s = {format_complex(s_val)}")
                    else:
                        annot.xy = (z_reals[best_idx], z_imags[best_idx])
                        annot.set_text(f"ζ({format_complex(s_val)}) = {format_complex(z_val)}")
                    annot.set_visible(True)
                else:
                    annot.set_visible(False)
                fig.canvas.draw_idle()
            else:
                annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)
        plt.tight_layout()
        plt.show()

    def plot_zeta_3d(self) -> None:
        """Plots the Magnitude of the Zeta function in 3D Space."""
        if not self.zeta_pairs:
            return
        
        plt.style.use('seaborn-v0_8-muted')
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        s_reals = [p[0].real for p in self.zeta_pairs]
        s_imags = [p[0].imag for p in self.zeta_pairs]
        z_mags = [abs(p[1]) for p in self.zeta_pairs]
        
        scatter = ax.scatter(s_reals, s_imags, z_mags, 
                            c=z_mags, cmap='viridis', 
                            s=60, edgecolors='k', alpha=0.8)
        
        fig.colorbar(scatter, ax=ax, label=r'Magnitude $|\zeta(s)|$')
        ax.set_title("3D Visualization: Magnitude of Riemann Zeta Function", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("Real Part (Re s)", fontsize=12)
        ax.set_ylabel("Imaginary Part (Im s)", fontsize=12)
        ax.set_zlabel(r"$|\zeta(s)|$", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.view_init(elev=30, azim=45)
        
        plt.tight_layout()
        plt.show()

    def show_about(self) -> None:
        """Displays the information dialog about the application."""
        about_text = (
            "Pro Fibonacci, Prime & Zeta Visualizer\n"
            "--------------------------------------------------\n\n"
            "Fibonacci: Generates the sequence where each number is\n"
            "the sum of the two preceding ones (0, 1, 1, 2, 3, 5...).\n\n"
            "Primes: Generates a list of prime numbers using the Sieve\n"
            "of Eratosthenes, which is efficient for large limits.\n\n"
            "Riemann Zeta: Computes ζ(s) for any complex number s.\n"
            "- Re(s) > 1: Calculated via standard Dirichlet series.\n"
            "- 0 < Re(s) < 1: Calculated via Dirichlet Eta function.\n"
            "- Re(s) <= 0: Calculated via the Functional Equation using\n"
            "  a complex Lanczos approximation for the Gamma function.\n"
            "- Trivial Zeros: Occur at s = -2, -4, -6... (Symmetry).\n"
            "- Note: Only diverges at s = 1 (the simple pole).\n\n"
            "--------------------------------------------------\n"
            "Author: Praveen KN\n"
            "This software is for education purpose only."
        )
        messagebox.showinfo("About", about_text)


if __name__ == "__main__":
    root_window = tk.Tk()
    app = FibPrimeApp(root_window)
    root_window.mainloop()
