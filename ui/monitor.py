import os
import sys
import pandas as pd
import tkinter as tk

# Calculate the path dynamically from the repo root
UI_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(UI_DIR)
CSV_PATH = os.path.join(REPO_ROOT, "build", "outputs", "Release", "bin", "BasicStandardResults.csv")

def update_metrics():
    if not os.path.exists(CSV_PATH):
        status_label.config(text="OFFLINE: AWAITING SIMULATOR STREAM...", fg="#ff4444")
        root.after(1000, update_metrics)
        return

    try:
        df = pd.read_csv(CSV_PATH)
        if not df.empty and len(df) >= 2:
            latest = df.iloc[-1]
            time_val = latest.get("SimulationTime(s)", latest.get("Time(s)", 0))
            map_val = latest.get("MeanArterialPressure(mmHg)", 0)
            co_val = latest.get("CardiacOutput(L/min)", latest.get("CardiacOutput(mL/min)", 0))
            
            if co_val > 100:
                co_val = co_val / 1000.0
            
            status_label.config(text="ONLINE: CAPTURING LIVE PHYSIOLOGICAL DATA", fg="#00ff66")
            map_display.config(text=f"{map_val:.1f} mmHg")
            co_display.config(text=f"{co_val:.2f} L/min")
            time_display.config(text=f"Sim Time: {time_val:.1f}s")
    except Exception as e:
        print(f"[UI WARNING] Data parse gap: {e}")
        
    root.after(1000, update_metrics)

root = tk.Tk()
root.title("CLINICAL TELEMETRY MONITOR - PRODUCTION BUILD")
root.geometry("550x320")
root.configure(bg="#111116")

status_label = tk.Label(root, text="OFFLINE: AWAITING SIMULATOR STREAM...", bg="#111116", fg="#ff4444", font=("Arial", 11, "bold"))
status_label.pack(pady=15)

map_display = tk.Label(root, text="-- mmHg", bg="#111116", fg="#00d8ff", font=("Arial", 24, "bold"))
map_display.pack(pady=10)

co_display = tk.Label(root, text="-- L/min", bg="#111116", fg="#ffcc00", font=("Arial", 24, "bold"))
co_display.pack(pady=10)

time_display = tk.Label(root, text="Sim Time: 0.0s", bg="#111116", fg="#666677", font=("Arial", 10))
time_display.pack(side="bottom", pady=15)

root.after(1000, update_metrics)
root.mainloop()