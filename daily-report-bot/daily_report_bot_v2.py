import pyautogui
import pyperclip
import time
from datetime import datetime

def wait(seconds):
    """Helper function to pause execution and let apps load."""
    time.sleep(seconds)

def main():
    # 1. Generate today's date and time dynamically
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    
    filename = f"daily_report_{current_date}.xlsx"
    my_comment = "Looks like a great day!"

    print("Starting bot in 3 seconds. Do not touch the mouse or keyboard!")
    wait(3)

    # 2. Open Chrome and navigate to a website
    # Adjust this hotkey based on your OS ('win' for Windows, 'command' for Mac)
    pyautogui.hotkey('win') 
    wait(1)
    pyautogui.write('chrome')
    wait(1)
    pyautogui.press('enter')
    wait(3) # Wait for Chrome to load

    # Go to a weather website
    pyautogui.write('weather')
    pyautogui.press('enter')
    wait(6) # Wait for the page to fully load

    # 3. Copy information from the page
    # IMPORTANT: You must change these coordinates to where the temperature/data is on YOUR screen
    data_x, data_y = 500, 400 
    
    # Triple click usually highlights the whole word/number
    pyautogui.click(x=434, y=4692, clicks=3, interval=0.1) 
    pyautogui.hotkey('ctrl', 'c') # Use 'command', 'c' on Mac
    wait(1)
    
    fetched_data = pyperclip.paste()
    print(f"Data fetched: {fetched_data}")

    # 4. Open Microsoft Excel
    pyautogui.hotkey('win') # Use 'command' on Mac
    wait(1)
    pyautogui.write('excel')
    wait(1)
    pyautogui.press('enter')
    wait(5) # Wait for Excel to load

    # Press Enter to select "Blank Workbook" (default in newer Excel versions)
    pyautogui.press('enter')
    wait(2)

    # 5. Type the data into the row
    # Type Date & Time
    pyautogui.write(current_datetime)
    pyautogui.press('tab')
    wait(0.5)
    
    # Paste Fetched Data
    pyautogui.hotkey('ctrl', 'v') # Use 'command', 'v' on Mac
    pyautogui.press('tab')
    wait(0.5)
    
    # Type Comment
    pyautogui.write(my_comment)
    pyautogui.press('enter')
    wait(1)

    # 6. Save the Excel file
    pyautogui.hotkey('ctrl', 's') # Use 'command', 's' on Mac
    wait(2)
    pyautogui.write(filename)
    wait(1)
    pyautogui.press('enter')
    wait(2)

    # 7. Take a screenshot of the final Excel sheet and save it
    screenshot_name = f"screenshot_{current_date}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_name)
    print(f"Report saved as {filename} and screenshot saved as {screenshot_name}")

if __name__ == "__main__":
    main()