import asyncio
import json
import os
import random
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURATION & CONSTANTS ---
EXCEL_INPUT_FILE = "contacts.xlsx"
USER_DATA_DIR = "./chrome_wa_profile"  # Stores persistent login session
SCREENSHOT_DIR = "./screenshots"
DEFAULT_MESSAGE_TEMPLATE = "Hello {name}, this is an automated message to stay in touch!"

# Ensure directories exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)

async def human_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    """Pauses execution for a randomized duration to simulate human behavior and avoid rate limits."""
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

async def wait_for_login(page: Page):
    """Waits for the user to log in via QR code on the first run, or loads existing session."""
    print("⏳ Checking WhatsApp Web login status...")
    await page.goto("https://web.whatsapp.com", timeout=60000)
    
    try:
        await page.wait_for_selector("#pane-side, #side, [role='navigation']", timeout=15000)
        print("✅ Session restored! Already logged in.")
    except PlaywrightTimeoutError:
        print("⚠️ Session not found or expired. Please scan the QR code in the browser window!")
        await page.wait_for_selector("#pane-side, #side, [role='navigation']", timeout=120000)
        print("✅ QR Code scanned successfully! Logged in.")

async def search_and_open_contact(page: Page, identifier: str) -> bool:
    """
    Searches for a contact by Name or Phone Number using WhatsApp's search bar.
    Returns True if chat is successfully opened, False if contact is not found.
    """
    try:
        await page.wait_for_selector('#pane-side, #side, [role="navigation"]', timeout=30000)
        await human_delay(1.0, 2.0)
        
        search_box = page.locator(
            'input[type="text"], '
            'input[role="textbox"], '
            '[role="textbox"][aria-label*="Search"], '
            '[title*="Search"], '
            '[placeholder*="Search"], '
            '[contenteditable="true"]'
        ).first
        
        await search_box.wait_for(state="visible", timeout=15000)
        await search_box.click()
        await human_delay(1.0, 2.0)
        
        await search_box.fill("")
        await page.keyboard.type(str(identifier), delay=random.randint(50, 120))
        await human_delay(2.0, 3.0)
        
        no_results = await page.locator('span:has-text("No results found"), span:has-text("No chats, contacts or messages found")').count()
        if no_results > 0:
            print(f"   ⚠️ No results found for '{identifier}'. Clearing search bar...")
            await page.keyboard.press("Escape")
            await page.keyboard.press("Escape")
            return False
            
        await page.keyboard.press("Enter")
        
        await page.wait_for_selector(
            '[contenteditable="true"][data-tab="10"], '
            '[title="Type a message"], '
            '[role="textbox"][aria-label*="Type a message"], '
            '#main', 
            timeout=10000
        )
        await human_delay(1.5, 2.5)
        return True
        
    except Exception as e:
        print(f"   [Error] Search failed for '{identifier}': {str(e)}")
        await page.keyboard.press("Escape")
        return False

async def send_message_and_screenshot(page: Page, message_text: str, contact_name: str) -> tuple[bool, str]:
    """
    Types and sends the personalized message and captures a screenshot.
    """
    screenshot_path = ""
    try:
        msg_box = page.locator(
            '[contenteditable="true"][data-tab="10"], '
            '[title="Type a message"], '
            '[role="textbox"][aria-label*="Type a message"], '
            '#main [contenteditable="true"], '
            'footer [role="textbox"]'
        ).first
        
        await msg_box.wait_for(state="visible", timeout=10000)
        await msg_box.click()
        await human_delay(1.0, 2.0)
        
        await page.keyboard.type(message_text, delay=random.randint(30, 80))
        await human_delay(1.0, 2.0)
        
        # Press Enter to send message
        await page.keyboard.press("Enter")
        
        # Wait a few seconds for the message to transmit
        print("   ⏳ Waiting for message transmission...")
        await human_delay(3.0, 4.0)
        
        # Capture proof screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in contact_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{safe_name}_{timestamp}.png")
        
        main_panel = page.locator('#main, [role="main"]').first
        if await main_panel.count() > 0:
            await main_panel.screenshot(path=screenshot_path)
        else:
            await page.screenshot(path=screenshot_path)
            
        return True, screenshot_path
        
    except Exception as e:
        print(f"   [Error] Failed to send message: {str(e)}")
        return False, screenshot_path

async def extract_last_incoming_messages(page: Page, limit: int = 3) -> list[str]:
    """
    Scrapes the active chat DOM to extract the last N incoming messages from the contact.
    """
    extracted = []
    try:
        incoming_locators = page.locator('#main div[data-id^="false_"], #main div.message-in')
        count = await incoming_locators.count()
        if count == 0:
            return ["No previous incoming messages found."]
            
        start_index = max(0, count - limit)
        for i in range(start_index, count):
            element = incoming_locators.nth(i)
            text_content = await element.inner_text()
            clean_lines = [line.strip() for line in text_content.split('\n') if line.strip() and not line.strip().endswith(('AM', 'PM', 'am', 'pm'))]
            if clean_lines:
                extracted.append(" | ".join(clean_lines))
                
        return extracted if extracted else ["Messages found but text was unreadable/media only."]
        
    except Exception as e:
        return [f"Extraction error: {str(e)}"]

async def main():
    if not os.path.exists(EXCEL_INPUT_FILE):
        print(f"❌ Critical Error: Input spreadsheet '{EXCEL_INPUT_FILE}' not found!")
        return

    df = pd.read_excel(EXCEL_INPUT_FILE)
    
    rename_map = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if c in ['name', 'contact_name', 'contact']:
            rename_map[col] = 'Name'
        elif c in ['phone', 'phone number', 'phone_number', 'mobile', 'number']:
            rename_map[col] = 'Phone'
        elif c in ['message', 'msg', 'template']:
            rename_map[col] = 'Message'
            
    df = df.rename(columns=rename_map)

    required_cols = {'Name', 'Phone'}
    if not required_cols.issubset(set(df.columns)):
        print(f"❌ Critical Error: Excel file must contain columns: {required_cols}")
        return

    report_data = []
    run_date = datetime.now().strftime("%Y-%m-%d")

    async with async_playwright() as p:
        print("🚀 Starting Chromium Browser in Persistent Context...")
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await browser.new_page()
        await wait_for_login(page)
        await human_delay(3.0, 5.0)

        print(f"\n📋 Processing {len(df)} contacts from '{EXCEL_INPUT_FILE}'...\n" + "="*50)

        for index, row in df.iterrows():
            name = str(row.get('Name', 'Friend')).strip()
            phone = str(row.get('Phone', '')).strip()
            raw_message = str(row.get('Message', '')) if pd.notna(row.get('Message')) else DEFAULT_MESSAGE_TEMPLATE
            
            message_to_send = raw_message.replace("{name}", name)
            search_target = name if name and str(name).lower() != 'nan' else phone
            print(f"\n[{index+1}/{len(df)}] Target: {name} (Searching: {search_target})")

            contact_record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": name,
                "Phone": phone,
                "Message_Sent": message_to_send,
                "Status": "Pending",
                "Screenshot_Path": "N/A",
                "Last_3_Incoming_Messages": []
            }

            print(f"   🔍 Searching for contact...")
            chat_opened = await search_and_open_contact(page, search_target)
            
            if not chat_opened:
                print(f"   ❌ Contact not found or unreachable: {search_target}")
                contact_record["Status"] = "Failed - Contact Not Found"
                report_data.append(contact_record)
                await human_delay(2.0, 4.0)
                continue

            print(f"   📥 Extracting last 3 incoming messages...")
            incoming_msgs = await extract_last_incoming_messages(page, limit=3)
            contact_record["Last_3_Incoming_Messages"] = incoming_msgs
            for idx, msg in enumerate(incoming_msgs, 1):
                print(f"      [Msg {idx}]: {msg[:60]}..." if len(msg) > 60 else f"      [Msg {idx}]: {msg}")

            print(f"   💬 Sending message...")
            sent_success, screenshot_file = await send_message_and_screenshot(page, message_to_send, name)

            if sent_success:
                print(f"   ✅ Message sent successfully! Screenshot saved.")
                contact_record["Status"] = "Success - Sent"
                contact_record["Screenshot_Path"] = screenshot_file
            else:
                print(f"   ❌ Failed to send message.")
                contact_record["Status"] = "Failed - Send Error"

            report_data.append(contact_record)

            print("   ⏳ Taking a short break before next contact...")
            await human_delay(3.0, 6.0)

        print("\n" + "="*50)
        print("🛑 All contacts processed. Saving reports...")
        await browser.close()

    json_filename = f"whatsapp_report_{run_date}.json"
    xlsx_filename = f"whatsapp_report_{run_date}.xlsx"

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)
    print(f"📁 Full JSON report saved to: {json_filename}")

    summary_data = []
    for item in report_data:
        summary_data.append({
            "Timestamp": item["Timestamp"],
            "Name": item["Name"],
            "Phone": item["Phone"],
            "Status": item["Status"],
            "Screenshot": item["Screenshot_Path"],
            "Recent_Messages_Count": len(item["Last_3_Incoming_Messages"])
        })
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_excel(xlsx_filename, index=False)
    print(f"📊 Excel summary report saved to: {xlsx_filename}")
    print("✨ Automation run completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())