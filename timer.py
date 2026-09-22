import tkinter as tk
from tkinter import messagebox
import json
import os
import time
from datetime import datetime

# ─── File where saved tasks are stored ────────────────────────────
DATA_FILE = "time_tracker_data.json"

# ─── Dark mode colour palette (Catppuccin Mocha) ─────────────────
C = {
    "base":     "#1e1e2e",
    "mantle":   "#181825",
    "surface0": "#313244",
    "surface1": "#45475a",
    "text":     "#cdd6f4",
    "subtext":  "#a6adc8",
    "blue":     "#89b4fa",
    "green":    "#a6e3a1",
    "red":      "#f38ba8",
    "yellow":   "#f9e2af",
    "lavender": "#b4befe",
}


class TimeTrackerApp:
    """Main application – one window, three actions: start, stop, save."""

    # ── initialisation ────────────────────────────────────────────
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Task Time Tracker")
        self.root.geometry("540x700")
        self.root.resizable(False, False)
        self.root.configure(bg=C["base"])

        # timer state
        self.running = False
        self.start_time: float = 0
        self.elapsed: float = 0.0

        # persistent task list
        self.tasks: list[dict] = self._load_data()

        self._build_ui()
        self._refresh_task_list()
        self._tick()  # start the display loop

    # ── helpers ────────────────────────────────────────────────────
    @staticmethod
    def _fmt(seconds: float) -> str:
        """Return seconds as HH:MM:SS."""
        h = int(seconds // 3600)
        m = int(seconds % 3600 // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def _total(tasks: list[dict]) -> float:
        return sum(t["duration"] for t in tasks)

    # ── data persistence ──────────────────────────────────────────
    def _load_data(self) -> list[dict]:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_data(self) -> None:
        with open(DATA_FILE, "w") as fh:
            json.dump(self.tasks, fh, indent=2)

    # ── UI construction ───────────────────────────────────────────
    def _build_ui(self) -> None:
        # --- header ---
        tk.Label(
            self.root, text="⏱  Task Time Tracker",
            font=("Segoe UI", 20, "bold"),
            bg=C["base"], fg=C["lavender"],
        ).pack(pady=(18, 6))

        # --- task name entry ---
        entry_frame = tk.Frame(self.root, bg=C["base"])
        entry_frame.pack(padx=35, fill="x")

        tk.Label(
            entry_frame, text="Task name",
            font=("Segoe UI", 10), bg=C["base"], fg=C["subtext"],
        ).pack(anchor="w")

        self.task_entry = tk.Entry(
            entry_frame, font=("Segoe UI", 13),
            bg=C["surface1"], fg=C["text"],
            insertbackground=C["text"], relief="flat",
            highlightthickness=2,
            highlightbackground=C["surface0"],
            highlightcolor=C["blue"],
        )
        self.task_entry.pack(fill="x", ipady=6, pady=(2, 0))

        # --- big timer display ---
        self.timer_label = tk.Label(
            self.root, text="00:00:00",
            font=("Consolas", 48, "bold"),
            bg=C["base"], fg=C["text"],
        )
        self.timer_label.pack(pady=(18, 12))

        # --- start / stop / save buttons ---
        btn_frame = tk.Frame(self.root, bg=C["base"])
        btn_frame.pack()

        btn_cfg = dict(font=("Segoe UI", 12, "bold"), relief="flat",
                       width=10, cursor="hand2", bd=0)

        self.start_btn = tk.Button(
            btn_frame, text="▶  Start", bg=C["green"], fg=C["mantle"],
            activebackground="#77d590", activeforeground=C["mantle"],
            command=self.start_timer, **btn_cfg,
        )
        self.start_btn.grid(row=0, column=0, padx=4)

        self.stop_btn = tk.Button(
            btn_frame, text="⏹  Stop", bg=C["red"], fg=C["mantle"],
            activebackground="#e07090", activeforeground=C["mantle"],
            command=self.stop_timer, state=tk.DISABLED, **btn_cfg,
        )
        self.stop_btn.grid(row=0, column=1, padx=4)

        self.save_btn = tk.Button(
            btn_frame, text="💾  Save", bg=C["blue"], fg=C["mantle"],
            activebackground="#6a9ae8", activeforeground=C["mantle"],
            command=self.save_task, **btn_cfg,
        )
        self.save_btn.grid(row=0, column=2, padx=4)

        # --- reset link ---
        tk.Button(
            self.root, text="↺  Reset timer",
            font=("Segoe UI", 10), bg=C["base"], fg=C["subtext"],
            activebackground=C["base"], activeforeground=C["text"],
            relief="flat", bd=0, cursor="hand2",
            command=self.reset_timer,
        ).pack(pady=(6, 12))

        # --- divider ---
        tk.Frame(self.root, bg=C["surface0"], height=2).pack(fill="x", padx=35)

        # --- saved-tasks header row ---
        hdr = tk.Frame(self.root, bg=C["base"])
        hdr.pack(fill="x", padx=35, pady=(12, 2))

        tk.Label(
            hdr, text="Saved Tasks", font=("Segoe UI", 13, "bold"),
            bg=C["base"], fg=C["lavender"],
        ).pack(side="left")

        self.total_label = tk.Label(
            hdr, text="", font=("Segoe UI", 10),
            bg=C["base"], fg=C["subtext"],
        )
        self.total_label.pack(side="left", padx=10)

        tk.Button(
            hdr, text="🗑 Clear all", font=("Segoe UI", 9),
            bg=C["surface0"], fg=C["red"],
            activebackground=C["surface1"], activeforeground=C["red"],
            relief="flat", cursor="hand2", command=self._clear_all,
        ).pack(side="right")

        # --- scrollable task list ---
        list_wrap = tk.Frame(self.root, bg=C["mantle"])
        list_wrap.pack(fill="both", expand=True, padx=35, pady=(4, 18))

        self.canvas = tk.Canvas(list_wrap, bg=C["mantle"],
                                highlightthickness=0, bd=0)
        sb = tk.Scrollbar(list_wrap, orient="vertical",
                          command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=C["mantle"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self._canvas_win = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw",
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self._canvas_win, width=e.width),
        )
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # mousewheel scroll
        self.canvas.bind("<Enter>",
                         lambda e: self.canvas.bind_all(
                             "<MouseWheel>", self._on_wheel))
        self.canvas.bind("<Leave>",
                         lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_wheel(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # ── timer actions ─────────────────────────────────────────────
    def start_timer(self) -> None:
        if self.running:
            return
        self.running = True
        self.start_time = time.time() - self.elapsed
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.timer_label.config(fg=C["green"])

    def stop_timer(self) -> None:
        if not self.running:
            return
        self.running = False
        self.elapsed = time.time() - self.start_time
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.timer_label.config(fg=C["yellow"])

    def reset_timer(self) -> None:
        self.running = False
        self.elapsed = 0.0
        self.start_time = 0
        self.timer_label.config(text="00:00:00", fg=C["text"])
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def save_task(self) -> None:
        name = self.task_entry.get().strip()
        if not name:
            messagebox.showwarning("No name", "Enter a task name first.")
            return
        if self.elapsed < 1:
            messagebox.showwarning("No time",
                                   "Run the timer for at least 1 second.")
            return

        if self.running:
            self.stop_timer()

        self.tasks.append({
            "name":     name,
            "duration": round(self.elapsed, 2),
            "date":     datetime.now().strftime("%Y-%m-%d  %H:%M"),
        })
        self._save_data()
        self._refresh_task_list()
        self.reset_timer()
        self.task_entry.delete(0, tk.END)

    # ── task-list management ──────────────────────────────────────
    def _delete_task(self, idx: int) -> None:
        if 0 <= idx < len(self.tasks):
            self.tasks.pop(idx)
            self._save_data()
            self._refresh_task_list()

    def _clear_all(self) -> None:
        if self.tasks and messagebox.askyesno("Confirm",
                                              "Delete every saved task?"):
            self.tasks.clear()
            self._save_data()
            self._refresh_task_list()

    def _refresh_task_list(self) -> None:
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        # total time label
        self.total_label.config(
            text=f"(total {self._fmt(self._total(self.tasks))})"
            if self.tasks else "",
        )

        if not self.tasks:
            tk.Label(
                self.scroll_frame, text="No saved tasks yet.",
                font=("Segoe UI", 11), bg=C["mantle"], fg=C["subtext"],
            ).pack(pady=30)
            return

        # newest first
        for display_i, task in enumerate(reversed(self.tasks)):
            real_idx = len(self.tasks) - 1 - display_i

            row = tk.Frame(self.scroll_frame, bg=C["surface0"])
            row.pack(fill="x", pady=2, padx=4)

            info = tk.Frame(row, bg=C["surface0"])
            info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            tk.Label(
                info, text=task["name"],
                font=("Segoe UI", 11, "bold"),
                bg=C["surface0"], fg=C["text"], anchor="w",
            ).pack(anchor="w")

            tk.Label(
                info,
                text=f"{self._fmt(task['duration'])}   •   {task['date']}",
                font=("Segoe UI", 9),
                bg=C["surface0"], fg=C["subtext"], anchor="w",
            ).pack(anchor="w")

            tk.Button(
                row, text="✕", font=("Segoe UI", 10, "bold"),
                bg=C["surface0"], fg=C["red"],
                activebackground=C["surface1"], activeforeground=C["red"],
                relief="flat", bd=0, cursor="hand2",
                command=lambda i=real_idx: self._delete_task(i),
            ).pack(side="right", padx=8)

    # ── clock tick (runs every 100 ms) ────────────────────────────
    def _tick(self) -> None:
        if self.running:
            self.elapsed = time.time() - self.start_time
        self.timer_label.config(text=self._fmt(self.elapsed))
        self.root.after(100, self._tick)


# ── entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()