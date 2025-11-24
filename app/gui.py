import tkinter as tk
from tkinter import ttk, messagebox
import json
from orchestrator import Orchestrator, InterviewState
from llm_client import LLMClient
from voice_utils import VoiceController

# --- Colors & Fonts ---
BG_COLOR = "#12161E"          # App background
SURFACE_COLOR = "#1A2230"     # Panel/entry background
TEXT_COLOR = "#E6EAF0"        # Primary text
PRIMARY_COLOR = "#1F3A5F"     # Primary button/background
SECONDARY_COLOR = "#2E5A88"   # Hover/active
ACCENT_COLOR = "#F39C12"      # Accent (feedback)
FONT_NAME = "Segoe UI"
FONT_BOLD = (FONT_NAME, 11, "bold")
FONT_BODY = (FONT_NAME, 11)
FONT_LABEL = (FONT_NAME, 10)
FONT_TITLE = (FONT_NAME, 12, "bold")
FONT_ITALIC = (FONT_NAME, 12, "italic")

# --- LLM, Orchestrator and Voice Initialization ---
try:
    client = LLMClient(provider="ollama", model="mistral")
    orc = Orchestrator(client)
    voice = VoiceController()
except Exception as e:
    messagebox.showerror("Initialization Error", f"Failed To Initialize Components: {e}")
    raise SystemExit(1)

# --- Load roles.json (dynamic roles & domains) ---
try:
    with open("data/roles.json") as f:
        roles_config = json.load(f)["roles"]  # expects {"roles": {"software_engineer": {"domains": [...]}, ...}}
except Exception as e:
    messagebox.showerror("Configuration Error", f"Failed To Load data/roles.json: {e}")
    raise SystemExit(1)

# --- UI Helpers ---
def title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())

def display_message(msg, tag):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, msg, tag)
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

def clear_chat():
    chat_box.config(state=tk.NORMAL)
    chat_box.delete(1.0, tk.END)
    chat_box.config(state=tk.DISABLED)

def toggle_voice():
    voice.toggle_voice(voice_enabled_var.get())

# --- Session Flow ---
def start_session():
    role = role_var.get()
    seniority = seniority_var.get()
    domain = domain_var.get()
    persona = persona_var.get()

    if not all([role, seniority, domain, persona]):
        messagebox.showwarning("Missing Information", "Please Select A Value For All Fields.")
        return

    # Normalize values to match JSON keys and Orchestrator expectations
    role_key = role.lower().replace(" ", "_")       # "Software Engineer" → "software_engineer"
    seniority_key = seniority.lower()               # "Mid" → "mid"
    domain_key = domain.lower()                     # "Backend" → "backend"
    persona_key = persona.lower()                   # "Efficient" → "efficient"

    try:
        orc.set_profile(role_key, seniority_key, domain_key, persona_key)
    except Exception as e:
        messagebox.showerror("Profile Error", f"Failed To Set Profile: {e}")
        return

    clear_chat()
    display_message(
        f"Interviewer: Starting {title_case(role)} Interview ({title_case(seniority)}, {title_case(domain)}) As {title_case(persona)} Persona.\n",
        "Interviewer"
    )
    ask_question()

def ask_question():
    try:
        q = orc.next_question()
    except Exception as e:
        messagebox.showerror("Question Error", f"Failed To Generate Question: {e}")
        return
    display_message(f"Interviewer: {q}\n", "Interviewer")
    if voice_enabled_var.get():
        voice.speak(q)

def send_answer():
    ans = entry.get().strip()
    if not ans:
        return
    display_message(f"You: {ans}\n", "User")
    entry.delete(0, tk.END)
    root.after(100, process_response, ans)

def record_answer():
    record_button.config(text="Listening...")
    root.update()
    try:
        ans = voice.listen()
    except Exception as e:
        record_button.config(text="Record")
        messagebox.showerror("Voice Error", f"Failed To Capture Audio: {e}")
        return
    record_button.config(text="Record")
    if ans:
        entry.delete(0, tk.END)
        entry.insert(0, ans)
        send_answer()

def process_response(ans):
    try:
        fu = orc.followup(ans)
    except Exception as e:
        messagebox.showerror("Follow-up Error", f"Failed To Generate Follow-up: {e}")
        return
    display_message(f"Interviewer: {fu}\n", "Interviewer")
    if voice_enabled_var.get():
        voice.speak(fu)

def format_feedback(fb):
    lines = ["Feedback:"]
    if "scores" in fb and fb["scores"]:
        scores = " | ".join([f"{title_case(k.replace('_', ' '))}: {v}" for k, v in fb['scores'].items()])
        lines.append(f"Scores: {scores}")
    if fb.get("strengths"):
        lines.append("Strengths: " + "; ".join(fb["strengths"]))
    if fb.get("improvements"):
        lines.append("Improvements: " + "; ".join(fb["improvements"]))
    return "\n".join(lines)

def end_session():
    # Aggregate feedback for all answers only at end
    try:
        if orc.ctx.get("answers"):
            all_feedback = [orc.feedback(ans) for ans in orc.ctx["answers"]]
            for fb in all_feedback:
                display_message(format_feedback(fb) + "\n", "Feedback")

        summary = orc.summary()
    except Exception as e:
        messagebox.showerror("Summary Error", f"Failed To Generate Summary/Feedback: {e}")
        summary = "Summary unavailable due to an error."

    display_message(f"Interviewer (Summary): {summary}\n", "Summary")
    display_message("Interviewer: Interview Ended.\n", "Interviewer")
    if voice_enabled_var.get():
        voice.speak("Interview Ended.")

# --- GUI Setup ---
root = tk.Tk()
root.title("Interview Practice Partner")
root.configure(bg=BG_COLOR)
root.geometry("900x700")

# --- Style Configuration ---
style = ttk.Style()
style.theme_use("clam")

# Frames & Labels
style.configure("TFrame", background=BG_COLOR)
style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=FONT_LABEL)

# Buttons
style.configure(
    "TButton",
    background=PRIMARY_COLOR,
    foreground=TEXT_COLOR,
    font=FONT_BOLD,
    borderwidth=0,
    padding=6
)
style.map("TButton", background=[("active", SECONDARY_COLOR)], foreground=[("active", TEXT_COLOR)])

# Combobox
style.configure(
    "TCombobox",
    fieldbackground=SURFACE_COLOR,
    background=PRIMARY_COLOR,
    foreground=TEXT_COLOR,
    font=FONT_BODY
)
style.map("TCombobox", fieldbackground=[("readonly", SURFACE_COLOR)])

# Entry
style.configure(
    "TEntry",
    fieldbackground=SURFACE_COLOR,
    foreground=TEXT_COLOR,
    insertcolor=TEXT_COLOR,
    font=FONT_BODY
)

# Checkbutton
style.configure("TCheckbutton", background=BG_COLOR, foreground=TEXT_COLOR, font=FONT_BODY)
style.map("TCheckbutton", background=[("active", BG_COLOR)])

# --- Top Frame for Controls ---
top_frame = ttk.Frame(root, padding="10")
top_frame.pack(fill=tk.X)

# Role dropdown (from roles.json)
ttk.Label(top_frame, text="Role").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
role_var = tk.StringVar()
role_combo = ttk.Combobox(
    top_frame,
    textvariable=role_var,
    values=[title_case(r.replace("_", " ")) for r in roles_config.keys()],
    state="readonly",
    width=20
)
role_combo.grid(row=0, column=1, padx=(0, 10), pady=5)

# Seniority dropdown
ttk.Label(top_frame, text="Seniority").grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
seniority_var = tk.StringVar()
seniority_combo = ttk.Combobox(
    top_frame,
    textvariable=seniority_var,
    values=["Junior", "Mid", "Senior"],
    state="readonly",
    width=15
)
seniority_combo.grid(row=0, column=3, padx=(0, 10), pady=5)

# Domain dropdown (updates dynamically)
ttk.Label(top_frame, text="Domain").grid(row=0, column=4, padx=(0, 5), pady=5, sticky="w")
domain_var = tk.StringVar()
domain_combo = ttk.Combobox(top_frame, textvariable=domain_var, state="readonly", width=15)
domain_combo.grid(row=0, column=5, padx=(0, 10), pady=5)

# Persona dropdown
ttk.Label(top_frame, text="Persona").grid(row=0, column=6, padx=(0, 5), pady=5, sticky="w")
persona_var = tk.StringVar()
persona_combo = ttk.Combobox(
    top_frame,
    textvariable=persona_var,
    values=["Efficient", "Chatty", "Confused", "Edge"],
    state="readonly",
    width=15
)
persona_combo.grid(row=0, column=7, padx=(0, 10), pady=5)

# Update domains when role changes
def update_domains(event=None):
    role_key = role_var.get().lower().replace(" ", "_")
    try:
        domains = roles_config[role_key]["domains"]
    except KeyError:
        domains = []
    domain_combo["values"] = [title_case(d) for d in domains] if domains else []
    if domains:
        domain_var.set(title_case(domains[0]))
    else:
        domain_var.set("")

role_combo.bind("<<ComboboxSelected>>", update_domains)

# --- Action Buttons ---
action_frame = ttk.Frame(top_frame)
action_frame.grid(row=0, column=8, columnspan=3, padx=(10, 0))

start_btn = ttk.Button(action_frame, text="Start", command=start_session)
start_btn.pack(side=tk.LEFT, padx=5)

end_btn = ttk.Button(action_frame, text="End", command=end_session)
end_btn.pack(side=tk.LEFT, padx=5)

voice_enabled_var = tk.BooleanVar(value=True)
voice_toggle = ttk.Checkbutton(action_frame, text="Voice", variable=voice_enabled_var, command=toggle_voice)
voice_toggle.pack(side=tk.LEFT, padx=5)

# --- Chat Box ---
chat_frame = ttk.Frame(root, padding="10")
chat_frame.pack(fill=tk.BOTH, expand=True)

chat_box = tk.Text(
    chat_frame,
    height=20,
    width=100,
    wrap=tk.WORD,
    state=tk.DISABLED,
    bg=SURFACE_COLOR,
    fg=TEXT_COLOR,
    font=FONT_BODY,
    padx=10,
    pady=10
)
chat_box.pack(fill=tk.BOTH, expand=True)

# Tag configurations for message types
chat_box.tag_configure("User", foreground="#2ECC71", font=FONT_BOLD)
chat_box.tag_configure("Interviewer", foreground=SECONDARY_COLOR, font=FONT_BOLD)
chat_box.tag_configure("Feedback", foreground=ACCENT_COLOR, lmargin1=20, lmargin2=20, font=FONT_BODY)
chat_box.tag_configure("Summary", foreground="#E74C3C", font=FONT_ITALIC)

# --- Entry Frame ---
entry_frame = ttk.Frame(root, padding="10")
entry_frame.pack(fill=tk.X)

entry = ttk.Entry(entry_frame)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
entry.bind("<Return>", lambda event: send_answer())

record_button = ttk.Button(entry_frame, text="Record", command=record_answer)
record_button.pack(side=tk.LEFT, padx=(10, 0))

send_button = ttk.Button(entry_frame, text="Send", command=send_answer)
send_button.pack(side=tk.RIGHT, padx=(10, 0))

# --- Initialize domain dropdown with first role's domains ---
try:
    first_role_key = list(roles_config.keys())[0]
    role_var.set(title_case(first_role_key.replace("_", " ")))
    update_domains()  # sets domain values and default selection
    seniority_var.set("Junior")
    persona_var.set("Efficient")
except Exception:
    # If roles_config is empty or malformed, leave combos blank
    role_var.set("")
    domain_var.set("")
    seniority_var.set("")
    persona_var.set("")

# --- Main Loop ---
if __name__ == "__main__":
    root.mainloop()