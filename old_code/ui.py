from old_code.timer import Timer
import tkinter as tk
import time
from datetime import datetime
from storage import save_session

UPDATE_INTERVAL = 200  # ms

background_color = "#270DBD"
light_blue = "#ADC3DB"

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Timer")
        self.root.configure(bg=background_color)
        self.timer = Timer()
        self.project_label = tk.Label(root, text="Project:", bg=background_color, fg="white", font=("Helvetica", 12))
        self.project_label.pack()

        self.project_entry = tk.Entry(root, width=30, bg=light_blue, font=("Helvetica", 12))
        self.project_entry.pack(pady=5)
        self.curr_session = None


        # Time display
        self.time_label = tk.Label(
            root,
            text="00:00:00",
            font=("Helvetica", 32),
            bg=light_blue,
            fg="black"
        )
        self.time_label.pack(pady=20)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        btn_frame.configure(bg=background_color)
        self.start_btn = tk.Button(
            btn_frame, text="Start", width=10, command=self.start, bg="green", font=("Helvetica", 10, "bold")
        )
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.stop_btn = tk.Button(
            btn_frame, text="Stop", width=10, command=self.stop, bg="red", font=("Helvetica", 10, "bold")
        )
        self.stop_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = tk.Button(
            btn_frame, text="Save", width=10, command=self.reset, font=("Helvetica", 10, "bold")
        )
        self.reset_btn.grid(row=0, column=2, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_display()

    def on_close(self):

        # if no session and timer not running, just exit
        if not self.curr_session and not self.timer.running:
            self.root.destroy()
            print("Exiting...")
            return
        
        # else, save session before exiting
        self.update_session()
        save_session(self.curr_session)
        print(f"Session saved for {self.curr_session["project"]}")
        self.root.destroy()

    def update_session(self):

        # gets elapsed time
        elapsed = self.timer.stop()
        project_name = self.project_entry.get() or "Untitled"
        hours, minutes = int(elapsed) // 3600, (int(elapsed) % 3600) // 60


        self.curr_session = {
            "project": project_name,
            "start_time": datetime.fromtimestamp(self.timer.start_time or time.time()).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_minutes": minutes,
            "duration_hours": hours
        }


    def start(self):
        project_name = self.project_entry.get() or "Untitled"

        if not self.curr_session:
            self.session_start = datetime.now()  # Keep a reference
        
        self.timer.start()

    def stop(self):
        if not self.timer.running:
            return False
        self.update_session()
        

    def reset(self):
        if self.timer.running:
            self.update_session()
            
        self.timer.reset()
        self.time_label.config(text="00:00:00")
        if self.curr_session:
            save_session(self.curr_session)
            print(f"Session saved for {self.curr_session['project']}")
        self.curr_session = None

    def update_display(self):
        elapsed = int(self.timer.get_elapsed())

        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60

        self.time_label.config(
            text=f"{hours:02}:{minutes:02}:{seconds:02}"
        )

        self.root.after(UPDATE_INTERVAL, self.update_display)