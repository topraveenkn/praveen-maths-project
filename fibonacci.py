"""
Number Functions Generator Application

A comprehensive GUI application that computes and visualizes:
- Fibonacci numbers up to a specified limit
- Prime numbers using the Sieve of Eratosthenes algorithm
- Reimann Zeta function values for a range of inputs with mathematical series expansions

Author: Praveen KN with help from coPilot
Date: May 9, 2026
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import math
import sys
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import ctypes
try:
    from ctypes import windll
except (ImportError, AttributeError):
    windll = None

# Import matplotlib for visualization; 
try:
    import matplotlib.pyplot as plt
    # Suppress matplotlib warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
except ImportError:
    plt = None


def compute_fibonacci(n):
    """Compute Fibonacci numbers up to the provided limit n."""
    if n < 1:
        return []

    # Start the sequence with the first two Fibonacci numbers.
    sequence = [1, 1]

    # Continue generating numbers until the next one would exceed n.
    while sequence[-1] + sequence[-2] <= n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence


def compute_primes(n):
    """Return all prime numbers from 2 through n using the Sieve of Eratosthenes."""
    if n < 2:
        return []

    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False

    # Only test divisors up to the integer square root of n.
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False

    return [i for i, prime in enumerate(sieve) if prime]


def compute_zeta(s, terms=200000):
    """Approximate the Reimann zeta function ζ(s) by summing the series 1/k^s."""
    if isinstance(s, complex):
        if s.real <= 1:
            raise ValueError("The Reimann zeta function converges only for Re(s) > 1.")
    else:
        if s <= 1:
            raise ValueError("The Reimann zeta function is undefined for s <= 1.")
    
    if s == 1 or (isinstance(s, complex) and s == 1+0j):
        # Harmonic series diverges, return None to indicate divergence
        return None

    total = 0
    for k in range(1, terms + 1):
        total += 1 / (k ** s)
    return total


def get_integer_input(title, prompt):
    """Ask the user for an integer value via a simple dialog box."""
    value = simpledialog.askstring(title, prompt)
    if value is None:
        return None

    try:
        n = int(value)
        return n
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid integer.")
        return None


def get_float_input(title, prompt):
    """Ask the user for a floating-point value via a simple dialog box."""
    value = simpledialog.askstring(title, prompt)
    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number.")
        return None


def plot_values(values, title, xlabel="Index", ylabel="Value"):
    """Plot a list of values using matplotlib if it is available."""
    if plt is None:
        messagebox.showerror(
            "Plot Error",
            "Matplotlib is not installed. Install it with `pip install matplotlib` to view graphs."
        )
        return

    if not values:
        messagebox.showinfo("Plot", "No values available to plot.")
        return

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plt.style.use('dark_background')
    
    plt.figure(figsize=(8, 4))
    plt.plot(values, marker='o', linestyle='-', color='#4da6ff')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


def show_result(title, text):
    """Display the result text in the read-only scrolling text box."""
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, f"{title}\n\n{text}")
    output_box.config(state="disabled")


def handle_fibonacci():
    """Handle the Fibonacci menu action and show the result plus a plot."""
    n = get_integer_input("Fibonacci", "Enter the upper bound n for Fibonacci numbers:")
    if n is None:
        return

    sequence = compute_fibonacci(n)
    if sequence:
        show_result("Fibonacci Numbers", ", ".join(str(x) for x in sequence))
        plot_values(sequence, "Fibonacci Numbers", xlabel="Sequence Index", ylabel="Fibonacci Value")
    else:
        show_result("Fibonacci Numbers", "No Fibonacci numbers found for the given input.")


def handle_primes():
    """Handle the prime number menu action and show the result plus a plot."""
    n = get_integer_input("Prime Numbers", "Enter n to list prime numbers up to n:")
    if n is None:
        return

    primes = compute_primes(n)
    if primes:
        show_result("Prime Numbers", ", ".join(str(x) for x in primes))
        plot_values(primes, "Prime Numbers", xlabel="Prime Index", ylabel="Prime Value")
    else:
        show_result("Prime Numbers", "No prime numbers found for the given input.")


def format_zeta_series(s, terms=10):
    """Create a short string representation of the zeta function series."""
    parts = []
    for k in range(1, terms + 1):
        if k == 1:
            parts.append("1")
        else:
            parts.append(f"1/{k}^{s}")
    return " + ".join(parts) + " + ..."


def show_series_popup(n1, n2, zeta_values):
    """Display series expansions for zeta function values in a separate popup window."""
    popup = tk.Toplevel(root)
    popup.title("Reimann Zeta Function - Series Expansions")
    popup.geometry("700x500")
    apply_glassy_style(popup)
    
    # Create a scrolled text widget for the series expansions
    text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD, state="normal", font=("Courier", 10), bg="#2d2d2d", fg="#ffffff", insertbackground="#ffffff")
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add series expansions for each value
    for idx, s in enumerate(range(n1, n2 + 1)):
        zeta_val = zeta_values[idx]
        
        text_widget.insert(tk.END, f"\nζ({s}):\n")
        
        if s == 1:
            text_widget.insert(tk.END, "Series: 1 + 1/2 + 1/3 + 1/4 + ... (Harmonic Series - DIVERGES)\n")
            text_widget.insert(tk.END, "Value: Undefined (diverges to infinity)\n")
        else:
            series = format_zeta_series(s, terms=8)
            text_widget.insert(tk.END, f"Series: {series}\n")
            text_widget.insert(tk.END, f"Value: {zeta_val:.12f}\n")
        
        text_widget.insert(tk.END, "-" * 70 + "\n")
    
    text_widget.config(state="disabled")
    
    # Add a close button
    close_button = tk.Button(popup, text="Close", command=popup.destroy, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    close_button.pack(pady=10)


def get_zeta_type():
    """Show a dialog to choose between Real and Complex zeta function."""
    choice_window = tk.Toplevel(root)
    choice_window.title("Reimann Zeta Function - Choose Type")
    choice_window.geometry("300x150")
    choice_window.resizable(False, False)
    apply_glassy_style(choice_window)
    choice_window.transient(root)
    choice_window.grab_set()

    result = {"type": None, "cancelled": True}

    label = tk.Label(choice_window, text="Choose the type of Reimann Zeta function:", font=("Segoe UI", 10), bg="#1e1e1e", fg="#ffffff")
    label.pack(pady=(20, 10))

    button_frame = tk.Frame(choice_window, bg="#1e1e1e")
    button_frame.pack(pady=(0, 20))

    def choose_real():
        result["type"] = "real"
        result["cancelled"] = False
        choice_window.destroy()

    def choose_complex():
        result["type"] = "complex"
        result["cancelled"] = False
        choice_window.destroy()

    real_button = tk.Button(button_frame, text="Real", width=10, command=choose_real, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    real_button.pack(side=tk.LEFT, padx=10)

    complex_button = tk.Button(button_frame, text="Complex", width=10, command=choose_complex, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    complex_button.pack(side=tk.LEFT, padx=10)

    choice_window.wait_window()
    return result


def handle_zeta_choice():
    """Handle the zeta button by first choosing the type."""
    choice = get_zeta_type()
    if choice["cancelled"]:
        return
    if choice["type"] == "real":
        handle_zeta()
    elif choice["type"] == "complex":
        handle_zeta_complex()


def get_zeta_inputs():
    """Show a dialog to get N1 and N2 values in a single popup window."""
    input_window = tk.Toplevel(root)
    input_window.title("Reimann Zeta Function - Input")
    input_window.geometry("380x200")
    input_window.resizable(False, False)
    apply_glassy_style(input_window)
    input_window.transient(root)
    input_window.grab_set()

    result = {"n1": None, "n2": None, "cancelled": True}

    # N1 Label and Entry
    n1_label = tk.Label(input_window, text="N1 (starting value, must be >= 1):", font=("Segoe UI", 10), bg="#1e1e1e", fg="#ffffff")
    n1_label.pack(padx=20, pady=(20, 5), anchor="w")

    n1_entry = tk.Entry(input_window, font=("Segoe UI", 10), width=25, bg="#3d3d3d", fg="#ffffff", insertbackground="#ffffff")
    n1_entry.pack(padx=20, pady=(0, 15))
    n1_entry.focus()

    # N2 Label and Entry
    n2_label = tk.Label(input_window, text="N2 (ending value):", font=("Segoe UI", 10), bg="#1e1e1e", fg="#ffffff")
    n2_label.pack(padx=20, pady=(0, 5), anchor="w")

    n2_entry = tk.Entry(input_window, font=("Segoe UI", 10), width=25, bg="#3d3d3d", fg="#ffffff", insertbackground="#ffffff")
    n2_entry.pack(padx=20, pady=(0, 20))

    # Button Frame
    button_frame = tk.Frame(input_window, bg="#1e1e1e")
    button_frame.pack(pady=(0, 15))

    def submit_inputs():
        try:
            n1 = int(n1_entry.get())
            n2 = int(n2_entry.get())
            result["n1"] = n1
            result["n2"] = n2
            result["cancelled"] = False
            input_window.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for both fields.")

    submit_button = tk.Button(button_frame, text="OK", width=10, command=submit_inputs, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    submit_button.pack(side=tk.LEFT, padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", width=10, command=input_window.destroy, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    cancel_button.pack(side=tk.LEFT, padx=5)

    input_window.wait_window()
    return result


def handle_zeta():
    """Handle the Reimann zeta function menu action and display values from N1 to N2."""
    # Get N1 and N2 from combined input dialog
    input_result = get_zeta_inputs()
    if input_result["cancelled"]:
        return

    n1 = input_result["n1"]
    n2 = input_result["n2"]

    # Validate inputs
    if n1 < 1:
        messagebox.showerror("Zeta Error", "N1 must be greater than or equal to 1.")
        return

    if n2 <= n1:
        messagebox.showerror("Zeta Error", "N2 must be greater than N1.")
        return

    if n2 - n1 > 50:
        messagebox.showerror("Zeta Error", "The range (N2 - N1) must not exceed 50.")
        return
    
    try:
        # Compute zeta values for the range
        zeta_values = []
        indices = []
        
        for s in range(n1, n2 + 1):
            zeta_val = compute_zeta(s)
            zeta_values.append(zeta_val)
            indices.append(s)
        
        # Create table output
        table_output = "Reimann Zeta Function Values\n"
        table_output += "=" * 50 + "\n"
        table_output += f"{'Index':<10} | {'ζ(n)':<35}\n"
        table_output += "-" * 50 + "\n"
        
        for idx, zeta_val in zip(indices, zeta_values):
            if zeta_val is None:
                table_output += f"{idx:<10} | {'Diverges (Harmonic Series)':<35}\n"
            else:
                table_output += f"{idx:<10} | {zeta_val:.12f}\n"
        
        show_result("Reimann Zeta Function", table_output)
        
        # Show series expansions in popup
        show_series_popup(n1, n2, zeta_values)
        
        # Filter out None values for plotting
        valid_zeta_values = [z if z is not None else 0 for z in zeta_values]
        valid_indices = [i for i, z in zip(indices, zeta_values) if z is not None]
        
        # Plot the zeta values (excluding s=1 if present)
        if valid_indices:
            plot_values(valid_zeta_values, "Reimann Zeta Function Values", xlabel="n", ylabel="ζ(n)")
        
    except ValueError as exc:
        messagebox.showerror("Zeta Error", str(exc))


def handle_zeta_complex():
    """Handle the complex Reimann zeta function menu action."""
    s_str = simpledialog.askstring("Reimann Zeta (complex)", "Enter complex number s as a+bj (e.g., 0.5+1j):")
    if s_str is None:
        return

    try:
        s = complex(s_str)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid complex number.")
        return

    try:
        zeta_val = compute_zeta(s)
        # Show result
        if zeta_val is None:
            show_result("Reimann Zeta (complex)", f"ζ({s}) diverges.")
        else:
            show_result("Reimann Zeta (complex)", f"ζ({s}) = {zeta_val}")
        # Show series popup
        show_complex_series_popup(s, zeta_val)
    except ValueError as exc:
        messagebox.showerror("Zeta Error", str(exc))


def show_complex_series_popup(s, zeta_val):
    """Display series expansion for complex zeta function in a separate popup window."""
    popup = tk.Toplevel(root)
    popup.title("Reimann Zeta Function - Complex Series Expansion")
    popup.geometry("700x500")
    apply_glassy_style(popup)
    
    # Create a scrolled text widget for the series expansion
    text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD, state="normal", font=("Courier", 10), bg="#2d2d2d", fg="#ffffff", insertbackground="#ffffff")
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    text_widget.insert(tk.END, f"ζ({s}):\n")
    if zeta_val is None:
        text_widget.insert(tk.END, "Series: 1 + 1/2 + 1/3 + 1/4 + ... (Harmonic Series - DIVERGES)\n")
        text_widget.insert(tk.END, "Value: Undefined (diverges to infinity)\n")
    else:
        series = format_zeta_series(s, terms=8)
        text_widget.insert(tk.END, f"Series: {series}\n")
        text_widget.insert(tk.END, f"Value: {zeta_val}\n")
    
    text_widget.config(state="disabled")
    
    # Add a close button
    close_button = tk.Button(popup, text="Close", command=popup.destroy, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    close_button.pack(pady=10)


def get_help_text(topic):
    """Return a short theoretical description for a selected topic."""
    help_texts = {
        "Fibonacci": (
            "The Fibonacci sequence is defined by the recurrence F(n)=F(n-1)+F(n-2), "
            "starting with F(1)=1 and F(2)=1. It appears in nature, combinatorics, and "
            "has connections to the golden ratio as the ratio of successive terms converges."
        ),
        "Prime Numbers": (
            "A prime number is an integer greater than 1 that has no positive divisors "
            "other than 1 and itself. Primes are the building blocks of number theory "
            "and are fundamental in cryptography, factorization, and arithmetic structure."
        ),
        "Reimann Zeta Function": (
            "The Reimann zeta function ζ(s) is defined for complex values of s by the series "
            "ζ(s)=∑_{k=1}^∞ 1/k^s when Re(s)>1. It extends analytically to other values and is "
            "central to the distribution of prime numbers through its non-trivial zeros."
        ),
    }
    return help_texts.get(topic, "")


def handle_help():
    """Show a help popup with a dropdown menu for theoretical details."""
    popup = tk.Toplevel(root)
    popup.title("Help")
    popup.geometry("540x320")
    popup.resizable(False, False)
    apply_glassy_style(popup)

    instruction_label = tk.Label(
        popup,
        text="Select a topic from the dropdown to view a brief theoretical explanation.",
        font=("Segoe UI", 10),
        bg="#1e1e1e",
        fg="#ffffff"
    )
    instruction_label.pack(padx=12, pady=(12, 6))

    selected_topic = tk.StringVar(value="Fibonacci")
    dropdown = tk.OptionMenu(popup, selected_topic, "Fibonacci", "Prime Numbers", "Reimann Zeta Function")
    dropdown.config(width=28, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff")
    dropdown.pack(padx=12, pady=(0, 12))

    help_text_box = scrolledtext.ScrolledText(popup, wrap=tk.WORD, state="disabled", width=62, height=10, bg="#2d2d2d", fg="#ffffff", insertbackground="#ffffff")
    help_text_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

    def update_help_text(*args):
        help_text_box.config(state="normal")
        help_text_box.delete("1.0", tk.END)
        help_text_box.insert(tk.END, get_help_text(selected_topic.get()))
        help_text_box.config(state="disabled")

    selected_topic.trace_add("write", update_help_text)
    update_help_text()

    close_button = tk.Button(popup, text="Close", width=10, command=popup.destroy, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    close_button.pack(pady=(0, 10))


def apply_glassy_style(window):
    """Apply a glassy Windows 11 style to the window."""
    try:
        # For Windows 10/11, apply dark theme colors
        if sys.platform == "win32" and windll is not None:
            # Try to enable dark title bar for Windows 11
            try:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                set_window_attribute = windll.dwmapi.DwmSetWindowAttribute
                get_parent = windll.user32.GetParent
                hwnd = get_parent(window.winfo_id())
                render_target = windll.user32.FindWindowExW(hwnd, None, "TKinterEmbedding", None)
                if render_target:
                    set_window_attribute(render_target, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
            except Exception:
                pass

        # Set modern colors
        bg_color = "#1e1e1e"
        fg_color = "#ffffff"
        window.configure(bg=bg_color)

        # Update all child widgets with modern styling
        for child in window.winfo_children():
            apply_widget_style(child, bg_color, fg_color)
    except Exception:
        pass


def apply_widget_style(widget, bg_color, fg_color):
    """Recursively apply glassy styling to widgets."""
    try:
        if isinstance(widget, tk.Label):
            widget.configure(bg=bg_color, fg=fg_color)
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=bg_color)
        elif isinstance(widget, tk.Button):
            widget.configure(bg="#3d3d3d", fg=fg_color, activebackground="#404040", activeforeground=fg_color, relief="flat", bd=0)
        elif isinstance(widget, (scrolledtext.ScrolledText, tk.Text)):
            widget.configure(bg="#2d2d2d", fg=fg_color, insertbackground=fg_color)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg="#3d3d3d", fg=fg_color, insertbackground=fg_color)
        elif isinstance(widget, tk.OptionMenu):
            widget.configure(bg="#3d3d3d", fg=fg_color, activebackground="#404040", activeforeground=fg_color)

        # Recursively style child widgets
        for child in widget.winfo_children():
            apply_widget_style(child, bg_color, fg_color)
    except Exception:
        pass


def handle_exit():
    """Exit the GUI application cleanly."""
    if root is not None:
        root.destroy()


def main():
    """Create and display the main Tkinter window with buttons and menus."""
    global root, output_box

    root = tk.Tk()
    root.title("Number Functions GUI")
    root.geometry("640x420")
    root.resizable(False, False)
    apply_glassy_style(root)

    # Create the top menu with function choices.
    menu_bar = tk.Menu(root, bg="#2d2d2d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff")
    functions_menu = tk.Menu(menu_bar, tearoff=0, bg="#2d2d2d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff")
    functions_menu.add_command(label="Fibonacci", command=handle_fibonacci)
    functions_menu.add_command(label="Prime Numbers", command=handle_primes)
    zeta_menu = tk.Menu(functions_menu, tearoff=0, bg="#2d2d2d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff")
    functions_menu.add_cascade(label="Reimann Zeta Function", menu=zeta_menu)
    zeta_menu.add_command(label="Reimann Zeta function (Real)", command=handle_zeta)
    zeta_menu.add_command(label="Reimann Zeta function (complex)", command=handle_zeta_complex)
    functions_menu.add_separator()
    functions_menu.add_command(label="Exit", command=handle_exit)
    menu_bar.add_cascade(label="Functions", menu=functions_menu)

    # Add a simple About menu with an About dialog.
    help_menu = tk.Menu(menu_bar, tearoff=0, bg="#2d2d2d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff")
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
        "About", "This GUI computes Fibonacci numbers, prime numbers up to n, and the Reimann zeta function for a given value. The software is for educational purpose only.\n\nAuthor: Praveen KN with help from coPilot"))
    menu_bar.add_cascade(label="About", menu=help_menu)
    root.config(menu=menu_bar)

    frame = tk.Frame(root, padx=12, pady=12, bg="#1e1e1e")
    frame.pack(fill=tk.BOTH, expand=True)

    instruction = tk.Label(frame, text="Choose a function from the top menu or use the buttons below.", font=("Segoe UI", 11), bg="#1e1e1e", fg="#ffffff")
    instruction.pack(pady=(0, 8))

    button_frame = tk.Frame(frame, bg="#1e1e1e")
    button_frame.pack(fill=tk.X, pady=(0, 10))

    fibonacci_button = tk.Button(button_frame, text="Fibonacci", width=16, command=handle_fibonacci, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    fibonacci_button.pack(side=tk.LEFT, padx=4)

    primes_button = tk.Button(button_frame, text="Prime Numbers", width=16, command=handle_primes, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    primes_button.pack(side=tk.LEFT, padx=4)

    zeta_button = tk.Button(button_frame, text="Reimann Zeta function", width=16, command=handle_zeta_choice, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    zeta_button.pack(side=tk.LEFT, padx=4)

    help_button = tk.Button(button_frame, text="Help", width=10, command=handle_help, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    help_button.pack(side=tk.LEFT, padx=4)

    exit_button = tk.Button(button_frame, text="Exit", width=10, command=handle_exit, bg="#3d3d3d", fg="#ffffff", activebackground="#404040", activeforeground="#ffffff", relief="flat", bd=0)
    exit_button.pack(side=tk.RIGHT, padx=4)

    output_box = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=72, height=18, state="disabled", bg="#2d2d2d", fg="#ffffff", insertbackground="#ffffff")
    output_box.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
