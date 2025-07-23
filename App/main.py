import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import threading
import time
import platform
import json
import os

CONFIG_FILE = "config.json"

settings = {
    "theme": "light",
    "system_prompt": "You are a helpful assistant."
}

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def load_settings():
    global settings
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                settings.update(loaded)
        except Exception as e:
            print(f"Failed to load config file: {e}")

def save_settings():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Failed to save config file: {e}")

def is_ollama_running():
    try:
        r = requests.get("http://127.0.0.1:11434")
        return r.status_code == 200
    except:
        return False

def start_ollama_serve():
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pull_model():
    try:
        subprocess.run(["ollama", "pull", "gemma3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        status_label.config(text=f"[Pull Error] {str(e)}")

def stop_ollama():
    confirm = messagebox.askyesno("End Ollama", "Stop Ollama server and close the app?")
    if not confirm:
        return
    status_label.config(text="🛑 Stopping Ollama...")
    root.update()
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["pkill", "-f", "ollama serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        status_label.config(text=f"[Error stopping Ollama] {str(e)}")
    root.after(1000, root.destroy)

def query_model(prompt, callback):
    full_prompt = f"{settings['system_prompt'].strip()}\n\nUser: {prompt}"
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "gemma3",
            "prompt": full_prompt,
            "stream": False
        })
        if response.status_code == 200:
            result = response.json()["response"]
            callback(result)
        else:
            callback(f"[Error] Status {response.status_code}:\n{response.text}")
    except Exception as e:
        callback(f"[Exception] {str(e)}")

def on_submit():
    prompt = input_box.get("1.0", tk.END).strip()
    if not prompt:
        return
    input_box.delete("1.0", tk.END)
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"User: {prompt}\n\n")
    chat_box.see(tk.END)
    chat_box.config(state="disabled")

    def run_query():
        query_model(prompt, lambda response: chat_box.after(0, lambda: show_response(response)))

    threading.Thread(target=run_query).start()

def show_response(response):
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"AI: {response}\n\n")
    chat_box.see(tk.END)
    chat_box.config(state="disabled")

def initialize_ollama():
    status_label.config(text="🔧 Checking Ollama...")
    root.update()
    if not is_ollama_running():
        status_label.config(text="🚀 Starting Ollama server...")
        start_ollama_serve()
        time.sleep(3)
    try:
        requests.get("http://127.0.0.1:11434")
        status_label.config(text="✅ Ollama Ready — Model: gemma3")
        threading.Thread(target=pull_model).start()
    except:
        status_label.config(text="❌ Failed to connect to Ollama.")

def open_settings():
    def save_and_close():
        settings["theme"] = theme_var.get()
        settings["system_prompt"] = system_prompt_text.get("1.0", tk.END).strip()
        save_settings()
        apply_theme()
        system_prompt_label.config(text=f"System Prompt: {settings['system_prompt'][:50]}{'...' if len(settings['system_prompt']) > 50 else ''}")
        settings_window.destroy()

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x350")
    settings_window.resizable(False, False)

    padding_x = 20
    padding_y = 10

    ttk.Label(settings_window, text="Theme:", font=("Segoe UI", 11, "bold")).pack(pady=(padding_y, 5), anchor=tk.W, padx=padding_x)
    theme_var = tk.StringVar(value=settings["theme"])
    ttk.Radiobutton(settings_window, text="Light", variable=theme_var, value="light").pack(anchor=tk.W, padx=padding_x)
    ttk.Radiobutton(settings_window, text="Dark", variable=theme_var, value="dark").pack(anchor=tk.W, padx=padding_x)

    ttk.Label(settings_window, text="System Prompt (Instructions to AI):", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5), anchor=tk.W, padx=padding_x)
    system_prompt_text = tk.Text(settings_window, height=8, font=("Segoe UI", 10), wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
    system_prompt_text.pack(fill=tk.BOTH, padx=padding_x, pady=(0, 15))
    system_prompt_text.insert("1.0", settings["system_prompt"])

    ttk.Button(settings_window, text="Save", command=save_and_close).pack(pady=10)

# --- Test Drive Window ---
def open_test_drive():
    test_drive_window = tk.Toplevel(root)
    test_drive_window.title("Test Drive AI Prompts")
    test_drive_window.geometry("400x300")
    test_drive_window.resizable(False, False)

    ttk.Label(test_drive_window, text="Select a prompt to test:", font=("Segoe UI", 12, "bold")).pack(pady=10)

    prompts = [
        "Tell me a joke.",
        "Explain quantum computing in simple terms.",
        "What's the weather like today?",
        "Write a short poem about the mountains.",
        "Give me advice on starting a small business.",
        "Summarize the importance of traditional values.",
        "Describe how AI can help in everyday life."
    ]

    prompt_var = tk.StringVar(value=prompts)

    listbox = tk.Listbox(test_drive_window, listvariable=prompt_var, height=10, font=("Segoe UI", 11))
    listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    def run_selected_prompt():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No selection", "Please select a prompt to run.")
            return
        prompt = listbox.get(selected_indices[0])
        test_drive_window.destroy()
        input_box.delete("1.0", tk.END)
        input_box.insert(tk.END, prompt)
        on_submit()

    run_button = ttk.Button(test_drive_window, text="▶ Run Selected Prompt", command=run_selected_prompt)
    run_button.pack(pady=10, ipadx=10, ipady=6)

def apply_theme():
    if settings["theme"] == "dark":
        bg = "#1e1e1e"
        fg = "#eeeeee"
        text_bg = "#2e2e2e"
        btn_bg = "#3c3c3c"
        btn_fg = "#eeeeee"
        status_fg = "#a9a9a9"
    else:
        bg = "#f4f4f4"
        fg = "#000000"
        text_bg = "#ffffff"
        btn_bg = "#e1e1e1"
        btn_fg = "#000000"
        status_fg = "#555555"

    root.configure(bg=bg)

    main_frame.configure(style="Main.TFrame")
    style.configure("Main.TFrame", background=bg)

    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("Status.TLabel", background=bg, foreground=status_fg, font=("Segoe UI", 10, "italic"))

    style.configure("TButton",
                    background=btn_bg,
                    foreground=btn_fg,
                    font=("Segoe UI", 10, "bold"))
    style.map("TButton",
              background=[('active', '#5a5a5a' if settings["theme"] == "dark" else '#cfcfcf')],
              foreground=[('active', btn_fg)])

    chat_frame.configure(style="Main.TFrame")
    right_frame.configure(style="Main.TFrame")

    for widget in main_frame.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.configure(style="Main.TFrame")
            for child in widget.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(background=bg, foreground=fg)

    for widget in [chat_box, input_box]:
        widget.configure(bg=text_bg, fg=fg, insertbackground=fg)

    system_prompt_label.configure(background=bg, foreground=fg)

    for widget in right_frame.winfo_children():
        if isinstance(widget, ttk.Button):
            widget.configure(style="TButton")

# --- UI Setup ---
load_settings()

root = tk.Tk()
root.title("Gemma3 Desktop AI (via Ollama)")
root.geometry("900x600")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

main_frame = ttk.Frame(root, padding=15, style="Main.TFrame")
main_frame.pack(fill=tk.BOTH, expand=True)

# Left side: Chat box
chat_frame = ttk.Frame(main_frame)
chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

chat_label = ttk.Label(chat_frame, text="Chat History", font=("Segoe UI", 14, "bold"))
chat_label.pack(anchor=tk.W, pady=(0,5))

chat_box = tk.Text(chat_frame, state="disabled", wrap=tk.WORD, font=("Segoe UI", 11), relief=tk.SOLID, borderwidth=1)
chat_box.pack(fill=tk.BOTH, expand=True)

# Right side: Input, system prompt, buttons
right_frame = ttk.Frame(main_frame, width=300)
right_frame.pack(side=tk.RIGHT, fill=tk.Y)

input_label = ttk.Label(right_frame, text="Enter Prompt:", font=("Segoe UI", 12, "bold"))
input_label.pack(anchor=tk.W, pady=(0,5))

input_box = tk.Text(right_frame, height=6, wrap=tk.WORD, font=("Segoe UI", 11), relief=tk.SOLID, borderwidth=1)
input_box.pack(fill=tk.X, pady=(0, 15))

system_prompt_label = ttk.Label(right_frame, text=f"System Prompt: {settings['system_prompt'][:50]}{'...' if len(settings['system_prompt']) > 50 else ''}", wraplength=280, font=("Segoe UI", 10, "italic"))
system_prompt_label.pack(anchor=tk.W, pady=(0,15))

submit_button = ttk.Button(right_frame, text="▶ Run Prompt", command=on_submit)
submit_button.pack(fill=tk.X, pady=(0,5), ipadx=10, ipady=8)

settings_button = ttk.Button(right_frame, text="⚙️ Settings", command=open_settings)
settings_button.pack(fill=tk.X, pady=(0,5), ipadx=10, ipady=8)

test_drive_button = ttk.Button(right_frame, text="🚗 Test Drive", command=open_test_drive)
test_drive_button.pack(fill=tk.X, pady=(0,5), ipadx=10, ipady=8)

end_button = ttk.Button(right_frame, text="🛑 End Ollama and Close App", command=stop_ollama)
end_button.pack(fill=tk.X, pady=(0,15), ipadx=10, ipady=8)

status_label = ttk.Label(main_frame, text="Starting...", style="Status.TLabel")
status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

apply_theme()
initialize_ollama()
root.mainloop()
