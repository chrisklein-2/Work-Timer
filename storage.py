import json
from pathlib import Path

DATA_FILE = Path("data/sessions.json")

def save_session(session):
    """Append a session to the JSON file."""
    DATA_FILE.parent.mkdir(exist_ok=True)  # Create data/ if missing

    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(session)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def print_sessions():
    """Print all saved sessions for debugging."""
    if not DATA_FILE.exists():
        print("No sessions saved yet.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    
    minutes = 0
    hours = 0
    daily_hours = 0
    daily_minutes = 0
    previous_date = ""
    for session in data:
        minutes += session['duration_minutes']
        hours += session['duration_hours']
        
        start_time = session['start_time'].split("T")
        rotate = start_time[0].split("-")
        start_time[0] = f"{rotate[1]}/{rotate[2]}/{rotate[0]}"
        if previous_date != start_time[0]:         
            print(f"Date: {start_time[0]}")
            previous_date = start_time[0]
            
        print(f"    Project: {session['project']}\n    {session['duration_hours']} hr : {session['duration_minutes']} min\n")

    total_hours = hours + minutes // 60
    total_minutes = minutes % 60
    
    print(f"Total Time: {total_hours} hr : {total_minutes} min")


if __name__ == "__main__":
    print_sessions()