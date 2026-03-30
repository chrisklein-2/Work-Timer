import win32gui
import time
def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

blacklist = ["YouTube", "Facebook", "Reddit", "New Tab", "Google Search"]

if __name__ == "__main__":
    not_found = True
    while not_found:
        not_found = False
        time.sleep(2)
        active_window= get_active_window_title()
        if "Google Chrome" not in active_window:
            not_found = True
            continue

        for word in blacklist:
            if word in active_window:
                not_found = True
                break
        if not not_found: 
            print(f"Active window:{active_window}")
        else:
            print("Incorrect active window.")
