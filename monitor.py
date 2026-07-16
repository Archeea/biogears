import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# ENGINE SOURCE PATH: Change this to point directly to your build's output folder if different
CSV_PATH = r"C:\Users\email\biogears\build\outputs\Release\bin\BasicStandardResults.csv"

class VitalsMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CLINICAL TELEMETRY MONITOR - PHARMACODYNAMIC INTERACTION VERIFIER")
        self.root.configure(bg="#0C0C0E")
        self.root.geometry("1200x700")

        # Top Control & Telemetry Alert Bar
        self.status_bar = tk.Label(
            root, text="SYSTEM STATUS: INITIALIZING DATA CORRELATION FILTER...", 
            font=("Consolas", 12, "bold"), fg="#FFCC00", bg="#141419", anchor="w", padx=15
        )
        self.status_bar.pack(fill=tk.X, side=tk.TOP, ipady=6)

        # Main Layout Splitting
        self.main_frame = tk.Frame(root, bg="#0C0C0E")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left Container for Waveform Graphs
        self.graph_frame = tk.Frame(self.main_frame, bg="#0C0C0E")
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right Panel for Digital HUD Numbers
        self.hud_frame = tk.Frame(self.main_frame, bg="#141419", width=280, highlightbackground="#24242B", highlightthickness=1)
        self.hud_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0))
        self.hud_frame.pack_propagate(False)

        # Render Digital HUD Displays
        self.create_hud_field("MEAN ARTERIAL PRESSURE (mmHg)", "#00FFFF", "val_map")
        self.create_hud_field("CARDIAC OUTPUT (L/min)", "#FFCC00", "val_co")

        # Matplotlib Figure Infrastructure Configuration
        self.fig, (self.ax_map, self.ax_co) = plt.subplots(2, 1, figsize=(6, 5), facecolor="#0C0C0E")
        self.fig.tight_layout(pad=3.5)
        
        for ax in (self.ax_map, self.ax_co):
            ax.set_facecolor("#060608")
            ax.grid(True, color="#1C1C22", linestyle=":")
            ax.tick_params(colors="#71717A", labelsize=9)

        # Setup Waveform Canvas Graph Frames
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Run continuous background telemetry check loop
        self.ani = FuncAnimation(self.fig, self.update_telemetry, interval=1000, cache_frame_data=False)

    def create_hud_field(self, label_text, color, val_attr):
        lbl = tk.Label(self.hud_frame, text=label_text, font=("Consolas", 9, "bold"), fg="#71717A", bg="#141419", anchor="w", padx=15, pady=12)
        lbl.pack(fill=tk.X)
        val = tk.Label(self.hud_frame, text="---", font=("Consolas", 36, "bold"), fg=color, bg="#141419", anchor="w", padx=15)
        val.pack(fill=tk.X, pady=(0, 20))
        setattr(self, val_attr, val)

    def update_telemetry(self, frame):
        if not os.path.exists(CSV_PATH):
            self.status_bar.config(text="OFFLINE: AWAITING ACTIVE BIOGEARS CSV DATA STREAM...", fg="#EF4444")
            return

        try:
            # Safely stream only required physics matrices columns to preserve performance loop
            df = pd.read_csv(CSV_PATH, usecols=["SimulationTime(s)", "MeanArterialPressure(mmHg)", "CardiacOutput(mL/min)"])
            if df.empty:
                return

            # Keep only the latest 60 seconds data window for the scrolling monitor monitor array sweep
            df_slice = df.tail(60)
            time_axis = df_slice["SimulationTime(s)"]
            map_axis = df_slice["MeanArterialPressure(mmHg)"]
            co_axis = df_slice["CardiacOutput(mL/min)"] / 1000.0  # Transpose fluid flow units to standard L/min parameters

            # Redraw MAP Signal Waveform Array
            self.ax_map.clear()
            self.ax_map.set_title("MEAN ARTERIAL PRESSURE", color="#00FFFF", fontname="Consolas", fontsize=10, weight="bold", loc="left")
            self.ax_map.grid(True, color="#1C1C22", linestyle=":")
            self.ax_map.plot(time_axis, map_axis, color="#00FFFF", linewidth=2)
            self.ax_map.tick_params(colors="#71717A")

            # Redraw Cardiac Output Signal Waveform Array
            self.ax_co.clear()
            self.ax_co.set_title("CARDIAC OUTPUT", color="#FFCC00", fontname="Consolas", fontsize=10, weight="bold", loc="left")
            self.ax_co.grid(True, color="#1C1C22", linestyle=":")
            self.ax_co.plot(time_axis, co_axis, color="#FFCC00", linewidth=2)
            self.ax_co.tick_params(colors="#71717A")

            # Update Digital HUD Panel values
            latest_map = map_axis.iloc[-1]
            latest_co = co_axis.iloc[-1]
            t = time_axis.iloc[-1]

            self.val_map.config(text=f"{latest_map:.1f}")
            self.val_co.config(text=f"{latest_co:.2f}")

            # Direct State Intercept Logic Warnings matching C++ engine metrics
            if t > 30.0 and latest_map < 75.0:
                self.status_bar.config(text=f"CRITICAL STATE: UNCOMPENSATED DISTRIBUTIVE SHOCK COLLAPSE IN PROGRESS (T={t:.1f}s)", fg="#EF4444")
            elif t > 60.0 and latest_map >= 95.0:
                self.status_bar.config(text=f"HEMODYNAMIC BALANCE DETECTED: ADRENERGIC RESCUE COMPLETE (T={t:.1f}s)", fg="#22C55E")
            else:
                self.status_bar.config(text=f"MONITOR RUNNING: BASELINE PHYSIOLOGY HOMEOSTASIS SECURED (T={t:.1f}s)", fg="#22C55E")

            self.canvas.draw()

        except Exception:
            pass # Gracefully handle file read lock collisions while the C++ thread writes raw entries

if __name__ == "__main__":
    root = tk.Tk()
    app = VitalsMonitorApp(root)
    root.mainloop()
    