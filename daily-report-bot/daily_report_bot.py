import os
import sys
import time
import subprocess
import datetime as dt

import pyautogui
import pyperclip

CITY = "Coimbatore"
WEATHER_URL = f"https://wttr.in/{CITY}?format=3"
COMMENT = "Good for outdoor activities"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

WAIT_APP_LAUNCH = 3.0
WAIT_PAGE_LOAD = 4.0
WAIT_SHORT = 1.0
WAIT_UI_SETTLE = 1.5

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def today_stamp():
    now = dt.datetime.now()
    date_for_filename = now.strftime("%Y-%m-%d")
    date_time_for_sheet = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_for_filename, date_time_for_sheet


def wait(seconds):
    time.sleep(seconds)


def focus_window_by_title_hint(title_hint):
    try:
        ps_command = (
            f"$w = Get-Process | Where-Object "
            f"{{$_.MainWindowTitle -like '*{title_hint}*'}} | Select-Object -First 1; "
            f"if ($w) {{ (New-Object -ComObject WScript.Shell)"
            f".AppActivate($w.Id) }}"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            timeout=5,
            capture_output=True,
        )
        wait(WAIT_SHORT)
    except Exception as e:
        print(f"    (window focus helper skipped: {e})")


def clean_weather_text(raw_text):
    if not raw_text:
        return "Weather data unavailable"
    for line in raw_text.splitlines():
        line = line.strip()
        if line:
            return line
    return "Weather data unavailable"


def open_chrome_and_get_weather():
    print("[1/6] Launching Chrome...")
    subprocess.Popen(["cmd", "/c", "start", "chrome", WEATHER_URL])
    wait(WAIT_APP_LAUNCH)
    wait(WAIT_PAGE_LOAD)

    focus_window_by_title_hint("Chrome")

    print("[2/6] Selecting and copying weather data from the page...")
    screen_w, screen_h = pyautogui.size()
    pyautogui.click(screen_w // 2, screen_h // 2)
    wait(WAIT_SHORT)

    pyautogui.hotkey("ctrl", "a")
    wait(WAIT_SHORT)
    pyautogui.hotkey("ctrl", "c")
    wait(WAIT_SHORT)

    raw_text = pyperclip.paste()
    weather_line = clean_weather_text(raw_text)
    print(f"    -> Captured: {weather_line}")
    return weather_line


def dismiss_office_activation_wizard():
    print("    Checking for / dismissing Office activation wizard...")
    for _ in range(3):
        pyautogui.press("esc")
        wait(0.8)


def open_excel():
    print("[3/6] Launching Microsoft Excel...")
    subprocess.Popen(["cmd", "/c", "start", "excel"])
    wait(WAIT_APP_LAUNCH)
    wait(WAIT_UI_SETTLE)
    focus_window_by_title_hint("Excel")
    wait(WAIT_SHORT)
    dismiss_office_activation_wizard()


def type_report_row(date_time_str, weather_data, comment):
    print("[4/6] Typing the daily report row into Excel...")

    pyautogui.hotkey("ctrl", "Home")
    wait(WAIT_SHORT)

    pyautogui.typewrite("Date & Time", interval=0.02)
    pyautogui.press("tab")
    pyautogui.typewrite("Weather Data", interval=0.02)
    pyautogui.press("tab")
    pyautogui.typewrite("Comment", interval=0.02)
    pyautogui.press("enter")

    pyautogui.typewrite(date_time_str, interval=0.02)
    pyautogui.press("tab")
    pyautogui.typewrite(weather_data, interval=0.02)
    pyautogui.press("tab")
    pyautogui.typewrite(comment, interval=0.02)
    pyautogui.press("enter")

    wait(WAIT_SHORT)

    pyautogui.hotkey("ctrl", "a")
    wait(0.3)
    pyautogui.hotkey("alt", "h")
    wait(0.3)
    pyautogui.press("o")
    wait(0.3)
    pyautogui.press("i")
    wait(WAIT_SHORT)
    pyautogui.hotkey("ctrl", "Home")
    wait(WAIT_SHORT)


def save_excel_as(filepath_no_ext):
    print("[5/6] Saving the Excel file...")
    pyautogui.press("f12")
    wait(WAIT_UI_SETTLE)

    pyautogui.hotkey("ctrl", "a")
    wait(0.3)
    pyautogui.typewrite(filepath_no_ext, interval=0.01)
    wait(0.3)

    pyautogui.press("enter")
    wait(WAIT_UI_SETTLE)

    pyautogui.press("enter")
    wait(WAIT_SHORT)


def take_screenshot(filepath_png):
    print("[6/6] Taking a screenshot of the final sheet...")
    wait(WAIT_SHORT)
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath_png)
    print(f"    -> Screenshot saved: {filepath_png}")


def main():
    if sys.platform != "win32":
        print("WARNING: This script was written and tested for Windows.")

    output_dir = ensure_output_dir()
    date_for_filename, date_time_for_sheet = today_stamp()

    xlsx_path_no_ext = os.path.join(output_dir, f"daily_report_{date_for_filename}")
    xlsx_path = xlsx_path_no_ext + ".xlsx"
    png_path = os.path.join(output_dir, f"daily_report_{date_for_filename}.png")

    print("=" * 60)
    print("Daily Status Report Bot - starting run")
    print(f"Output folder: {output_dir}")
    print("Do NOT touch the mouse/keyboard until this finishes.")
    print("=" * 60)
    wait(2)

    weather_data = open_chrome_and_get_weather()
    open_excel()
    type_report_row(date_time_for_sheet, weather_data, COMMENT)
    save_excel_as(xlsx_path_no_ext)
    take_screenshot(png_path)

    print("=" * 60)
    print("DONE.")
    print(f"Excel file : {xlsx_path}")
    print(f"Screenshot : {png_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()