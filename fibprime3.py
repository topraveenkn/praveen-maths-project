import tkinter as tk
from tkinter import messagebox, ttk
import threading
import matplotlib.pyplot as plt
import numpy as np
import csv
import os  # Added to handle directory paths
from datetime import datetime

# =============================================================================
# CORE MATHEMATICAL LOGIC
# =============================================================================

def generate_fibonacci_list(n):
    """Iterative approach to generate Fibonacci sequence. Time: O(n)"""
    if n <= 0: return []
    seq = []
    a, b = 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq

def generate_primes_list(n):
    """Sieve of Eratosthenes for efficient prime generation. Time: O(n log log n)"""
    if n < 2: return []
    sieve = [True] * (n + 1)
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            for i in range(p * p, n + 1, p):
                sieve[i] = False
    return [p for p in range(2, n + 1) if sieve[p]]

# =============================================================================
# MAIN APPLICATION FRAMEWORK
# =============================================================================

class FibPrimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Fibonacci & Prime Visualizer")
        self.root.geometry("650x600")
        self.root.configure(bg="#f5f6fa")
        
        self.current_data = [] 
        
        self.colors = {
            "primary": "#2c3e50",     # Dark Navy (Header)
            "secondary": "#3498db",   # Bright Blue (Visualize)
            "save_accent": "#2980b9", # Steel Blue (Save to CSV)
            "fib_accent": "#e67e22",  # Carrot Orange (Fib Generate)
            "prime_accent": "#27ae60",# Nephritis Green (Prime Generate)
            "danger": "#e74c3c",      # Alizarin Red (Exit)
            "text_dark": "#2f3640",   # Deep Grey
            "bg_light": "#ffffff"     # Pure White
        }

        self.center_window()

        # --- NAVIGATION BAR SETUP ---
        self.nav_bar = tk.Frame(self.root, bg=self.colors["primary"], pady=15)
        self.nav_bar.pack(fill="x")

        self.btn_fib_menu = tk.Button(self.nav_bar, text="Fibonacci", command=self.show_fib_screen, 
                                      bg=self.colors["primary"], fg="white", relief="flat", 
                                      font=("Segoe UI", 10, "bold"), padx=15, cursor="hand2")
        self.btn_fib_menu.pack(side="left", padx=15)

        self.btn_prime_menu = tk.Button(self.nav_bar, text="Primes", command=self.show_prime_screen, 
                                        bg=self.colors["primary"], fg="white", relief="flat", 
                                        font=("Segoe UI", 10, "bold"), padx=15, cursor="hand2")
        self.btn_prime_menu.pack(side="left", padx=15)

        self.btn_about = tk.Button(self.nav_bar, text="About", command=self.show_about, 
                                   bg=self.colors["primary"], fg="#bdc3c7", relief="flat", 
                                   font=("Segoe UI", 10), padx=15, cursor="hand2")
        self.btn_about.pack(side="right", padx=15)

        self.btn_exit = tk.Button(self.nav_bar, text="Exit", command=self.root.destroy, 
                                  bg=self.colors["danger"], fg="white", relief="flat", 
                                  font=("Segoe UI", 10, "bold"), padx=15, cursor="hand2")
        self.btn_exit.pack(side="right", padx=15)

        self.content_frame = tk.Frame(self.root, bg=self.colors["bg_light"], 
                                      padx=30, pady=30, highlightthickness=1, 
                                      highlightbackground="#dcdde1")
        self.content_frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.show_fib_screen()

    def center_window(self):
        self.root.update_idletasks()
        width, height = 650, 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def clear_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_input_field(self, label_text):
        tk.Label(self.content_frame, text=label_text, font=("Segoe UI", 11), 
                 bg=self.colors["bg_light"], fg=self.colors["text_dark"]).pack(pady=(10, 5))
        entry = ttk.Entry(self.content_frame, justify='center', font=("Segoe UI", 12))
        entry.pack(pady=5)
        return entry

    # =========================================================================
    # SCREEN MANAGEMENT
    # =========================================================================

    def show_fib_screen(self):
        self.clear_frame()
        tk.Label(self.content_frame, text="Fibonacci Sequence", font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["bg_light"], fg=self.colors["primary"]).pack(pady=(0, 20))
        self.entry_n = self.create_input_field("Enter number of elements (N):")
        
        btn_frame = tk.Frame(self.content_frame, bg=self.colors["bg_light"])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Generate", bg=self.colors["fib_accent"], fg="white", 
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=15, cursor="hand2",
                  command=lambda: self.start_thread(self.exec_fib)).pack(side="left", padx=5)
        
        self.btn_plot = tk.Button(btn_frame, text="Visualize", bg=self.colors["secondary"], 
                                  fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
                                  padx=15, cursor="hand2", state="disabled",
                                  command=lambda: self.plot_data("Fibonacci"))
        self.btn_plot.pack(side="left", padx=5)

        self.btn_save = tk.Button(btn_frame, text="Save to CSV", bg=self.colors["save_accent"], 
                                  fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
                                  padx=15, cursor="hand2", state="disabled",
                                  command=lambda: self.export_to_csv("Fib", ["Index N", "Fibonacci Number"]))
        self.btn_save.pack(side="left", padx=5)

        self.result_label = tk.Text(self.content_frame, height=10, width=45, wrap="word", 
                                    state="disabled", font=("Consolas", 11), bg="#f9f9f9",
                                    relief="flat", padx=10, pady=10)
        self.result_label.pack(pady=10)

    def show_prime_screen(self):
        self.clear_frame()
        tk.Label(self.content_frame, text="Prime Number Generator", font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["bg_light"], fg=self.colors["primary"]).pack(pady=(0, 20))
        self.entry_n = self.create_input_field("Enter limit (N):")
        
        btn_frame = tk.Frame(self.content_frame, bg=self.colors["bg_light"])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Generate", bg=self.colors["prime_accent"], fg="white", 
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=15, cursor="hand2",
                  command=lambda: self.start_thread(self.exec_prime)).pack(side="left", padx=5)
        
        self.btn_plot = tk.Button(btn_frame, text="Visualize", bg=self.colors["secondary"], 
                                  fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
                                  padx=15, cursor="hand2", state="disabled",
                                  command=lambda: self.plot_data("Prime"))
        self.btn_plot.pack(side="left", padx=5)

        self.btn_save = tk.Button(btn_frame, text="Save to CSV", bg=self.colors["save_accent"], 
                                  fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
                                  padx=15, cursor="hand2", state="disabled",
                                  command=lambda: self.export_to_csv("prime", ["Index N", "Prime Number"]))
        self.btn_save.pack(side="left", padx=5)

        self.result_label = tk.Text(self.content_frame, height=10, width=45, wrap="word", 
                                    state="disabled", font=("Consolas", 11), bg="#f9f9f9",
                                    relief="flat", padx=10, pady=10)
        self.result_label.pack(pady=10)

    # =========================================================================
    # DATA OPERATIONS & EXPORT
    # =========================================================================

    def export_to_csv(self, prefix, headers):
        """
        Saves generated data to the Windows Downloads folder.
        Logic: Uses os.path.expanduser('~') to ensure the path is correct 
        across different Windows user profiles.
        """
        if not self.current_data:
            return

        # 1. Target the Downloads folder dynamically
        # expanduser("~") gets 'C:\Users\UserName'
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # 2. Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"
        
        # 3. Combine folder and filename for absolute path
        full_path = os.path.join(downloads_folder, filename)
        
        try:
            with open(full_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers) 
                for i, value in enumerate(self.current_data, start=1):
                    writer.writerow([i, value])
            
            messagebox.showinfo("Export Successful", f"File saved to Downloads folder:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not save file: {e}")

    def start_thread(self, target_func):
        threading.Thread(target=target_func, daemon=True).start()

    def exec_fib(self):
        try:
            n = int(self.entry_n.get())
            if n > 10000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000.")
                return
            self.current_data = generate_fibonacci_list(n)
            result_text = ", ".join(map(str, self.current_data))
            self.root.after(0, self.display_result, result_text)
            self.root.after(0, lambda: self.btn_plot.config(state="normal"))
            self.root.after(0, lambda: self.btn_save.config(state="normal"))
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def exec_prime(self):
        try:
            n = int(self.entry_n.get())
            if n > 10000000:
                messagebox.showwarning("Limit", "Please enter N ≤ 10,000,000.")
                return
            self.current_data = generate_primes_list(n)
            result_text = ", ".join(map(str, self.current_data))
            self.root.after(0, self.display_result, result_text)
            self.root.after(0, lambda: self.btn_plot.config(state="normal"))
            self.root.after(0, lambda: self.btn_save.config(state="normal"))
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Error", "Invalid integer."))

    def display_result(self, text):
        self.result_label.config(state="normal")
        self.result_label.delete("1.0", tk.END)
        self.result_label.insert(tk.END, text)
        self.result_label.config(state="disabled")

    # =========================================================================
    # VISUALIZATION ENGINE
    # =========================================================================

    def plot_data(self, mode):
        if not self.current_data: return
        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(11, 7))
        x = np.arange(1, len(self.current_data) + 1)
        y = np.array(self.current_data)

        if len(x) > 5000:
            indices = np.linspace(0, len(x)-1, 5000, dtype=int)
            x_plot, y_plot = x[indices], y[indices]
        else:
            x_plot, y_plot = x, y

        color = self.colors["fib_accent"] if mode == "Fibonacci" else self.colors["prime_accent"]
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

    def show_about(self):
        messagebox.showinfo("About", "Pro Fibonacci & Prime Visualizer\n\n"
                            "Interactive data analysis and export tool.\n"
                            "Author: Praveen KN")

if __name__ == "__main__":
    root = tk.Tk()
    app = FibPrimeApp(root)
    root.mainloop()


