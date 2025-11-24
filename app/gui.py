import tkinter as tk
from tkinter import ttk
from orchestrator import Orchestrator, InterviewState
from llm_client import LLMClient

# Initialize LLM client and orchestrator
client = LLMClient(provider="ollama", model="mistral")
orc = Orchestrator(client)

def start_session():
    role = role_var.get()
    seniority = seniority_var.get()
    domain = domain_var.get()
    persona = persona_var.get()
    if not role or not seniority or not domain or not persona:
        chat_box.insert(tk.END, "Agent: Please select role, seniority, domain, and persona.\n")
        return
    orc.set_profile(role, seniority, domain, persona)
    chat_box.insert(tk.END, f"Agent: Starting {role} interview ({seniority}, {domain}) as {persona} persona.\n")
    ask_question()

def ask_question():
    q = orc.next_question()
    chat_box.insert(tk.END, f"Agent: {q}\n\n")

def send_answer():
    ans = entry.get().strip()
    if not ans:
        return
    chat_box.insert(tk.END, f"You: {ans}\n")
    entry.delete(0, tk.END)
    fu = orc.followup(ans)
    chat_box.insert(tk.END, f"Agent (follow-up): {fu}\n")
    fb = orc.feedback(ans)
    chat_box.insert(tk.END, format_feedback(fb) + "\n\n")

def format_feedback(fb):
    lines = []
    lines.append("Feedback:")
    if "scores" in fb and fb["scores"]:
        lines.append(
            f" - clarity: {fb['scores'].get('clarity','-')} | technical_depth: {fb['scores'].get('technical_depth','-')} | relevance: {fb['scores'].get('relevance','-')} | confidence: {fb['scores'].get('confidence','-')}"
        )
    if fb.get("strengths"):
        lines.append(" - strengths: " + "; ".join(fb["strengths"]))
    if fb.get("improvements"):
        lines.append(" - improvements: " + "; ".join(fb["improvements"]))
    if fb.get("raw"):
        lines.append(" - notes: " + fb["raw"])
    return "\n".join(lines)

def end_session():
    summary = orc.summary()
    chat_box.insert(tk.END, f"Agent (summary): {summary}\n")
    chat_box.insert(tk.END, "Agent: Interview ended.\n")

# Build GUI
root = tk.Tk()
root.title("Interview Practice Partner")

top_frame = ttk.Frame(root)
top_frame.pack(fill=tk.X, padx=8, pady=8)

role_var = tk.StringVar(value="software_engineer")
seniority_var = tk.StringVar(value="mid")
domain_var = tk.StringVar(value="backend")
persona_var = tk.StringVar(value="efficient")

ttk.Label(top_frame, text="Role").grid(row=0, column=0)
ttk.Combobox(top_frame, textvariable=role_var, values=["software_engineer","sales_ae","retail_associate"]).grid(row=0, column=1)
ttk.Label(top_frame, text="Seniority").grid(row=0, column=2)
ttk.Combobox(top_frame, textvariable=seniority_var, values=["junior","mid","senior"]).grid(row=0, column=3)
ttk.Label(top_frame, text="Domain").grid(row=0, column=4)
ttk.Combobox(top_frame, textvariable=domain_var, values=["backend","frontend","ml","devops"]).grid(row=0, column=5)
ttk.Label(top_frame, text="Persona").grid(row=0, column=6)
ttk.Combobox(top_frame, textvariable=persona_var, values=["efficient","chatty","confused","edge"]).grid(row=0, column=7)

start_btn = ttk.Button(top_frame, text="Start", command=start_session)
start_btn.grid(row=0, column=8, padx=6)
end_btn = ttk.Button(top_frame, text="End", command=end_session)
end_btn.grid(row=0, column=9, padx=6)

chat_box = tk.Text(root, height=24, width=100)
chat_box.pack(padx=8, pady=8)

entry_frame = ttk.Frame(root)
entry_frame.pack(fill=tk.X, padx=8, pady=8)
entry = ttk.Entry(entry_frame, width=80)
entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
send_button = ttk.Button(entry_frame, text="Send", command=send_answer)
send_button.pack(side=tk.RIGHT)

root.mainloop()
