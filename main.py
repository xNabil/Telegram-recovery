import os
import json
import re
import asyncio
import logging
from datetime import datetime
from colorama import Fore, Style, init
from pyrogram import Client, filters
from pyrogram.raw.functions.account import GetPassword
from pyrogram.errors import FloodWait, SessionPasswordNeeded, PhoneNumberBanned, AuthKeyUnregistered, UserDeactivated

# Initialize colorama for colored output
init(autoreset=True)

# Suppress Pyrogram's verbose logs
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Configure custom logging with timestamps for specific events
logger = logging.getLogger("RecoveryBot")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s,%(msecs)03d - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(handler)

# Custom logging function for colored output
def log(message, color=Fore.WHITE, emoji="", timestamp=False):
    if timestamp:
        logger.info(f"{emoji} {color}{message}{Style.RESET_ALL}")
    else:
        print(f"{emoji} {color}{message}{Style.RESET_ALL}")

# Check and create directories if they don't exist
def setup_directories():
    for folder in ["sessions", "recovered_sessions", "dead_sessions"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            log(f"Created directory: {folder}", Fore.WHITE, "📁")

# Load API credentials and 2FA skip setting from config.json
def load_config():
    if not os.path.exists("config.json"):
        log("config.json not found.", Fore.RED, "❌")
        exit(1)
    try:
        with open("config.json") as f:
            config = json.load(f)
        api_id = config.get("api_id")
        api_hash = config.get("api_hash")
        skip_2fa_enabled = config.get("SKIP_2FA_enabled", False)
        if not api_id or not api_hash:
            log("api_id or api_hash missing in config.json.", Fore.RED, "❌")
            exit(1)
        return api_id, api_hash, bool(skip_2fa_enabled)
    except json.JSONDecodeError:
        log("Invalid JSON in config.json.", Fore.RED, "❌")
        exit(1)

# Get all session files
def get_session_files():
    session_files = [f for f in os.listdir("sessions") if f.endswith(".session")]
    if not session_files:
        log("No session files found in 'sessions/'.", Fore.RED, "❌")
        exit(1)
    return session_files

# Move session file to specified folder
def move_session_file(session_file, target_folder):
    src = os.path.join("sessions", session_file)
    dst = os.path.join(target_folder, session_file)
    try:
        os.rename(src, dst)
        log(f"Moved {session_file} to {target_folder}", Fore.WHITE, "📂", timestamp=True)
    except Exception as e:
        log(f"Error moving {session_file}: {e}", Fore.RED, "❌", timestamp=True)

# Append phone number to recovered_numbers.txt
def append_phone_number(session_file, phone_number):
    try:
        # Check if file exists to decide whether to write header
        file_exists = os.path.exists("recovered_numbers.txt")
        with open("recovered_numbers.txt", "a") as f:
            if not file_exists:
                f.write("Recovered Accounts\n======================================\n")
            f.write(f"Session: {session_file} | Phone: {phone_number} | \n")
        log(f"Saved phone number to recovered_numbers.txt", Fore.WHITE, "📝", timestamp=True)
    except Exception as e:
        log(f"Error writing to recovered_numbers.txt: {e}", Fore.RED, "❌", timestamp=True)

# Check if 2FA is enabled for the session
async def is_2fa_enabled(app):
    try:
        pwd = await app.invoke(GetPassword())
        return pwd.has_password
    except Exception:
        return False  # Assume 2FA is not enabled if the check fails

async def process_session(session_file, api_id, api_hash, skip_2fa_enabled):
    session_name = os.path.splitext(session_file)[0]
    log(f"Processing session: {session_file}", Fore.CYAN, "🔄")

    # Initialize Pyrogram client
    app = Client(name=os.path.join("sessions", session_name), api_id=api_id, api_hash=api_hash)

    try:
        # Connect to Telegram
        await app.start()

        # Check for 2FA if skip_2fa_enabled is True
        if skip_2fa_enabled:
            if await is_2fa_enabled(app):
                log("Session failed: 2FA enabled", Fore.RED, "🔴")
                if app.is_connected:
                    try:
                        await app.stop()
                    except Exception as e:
                        log(f"Error stopping client: {e}", Fore.RED, "❌", timestamp=True)
                move_session_file(session_file, "dead_sessions")
                return  # Skip to next session

        # Get account info
        me = await app.get_me()

        phone_number = getattr(me, "phone_number", None)
        if phone_number:
            formatted_phone = (
                 f"\n{Fore.CYAN}{'=' * 30}\n"
                 f"{Fore.BLUE}📱 Phone Number: {phone_number}\n"
                 f"{Fore.CYAN}{'=' * 30}"
            )
            log(formatted_phone, "", timestamp=True)

        # Prompt user to send OTP
        input(f"{Fore.YELLOW}Please send an OTP to {phone_number} and press Enter...{Style.RESET_ALL}")

        # Set up message handler
        otp_received = asyncio.Event()
        otp_code = None

        @app.on_message(filters.private & filters.user([777000]))
        async def handle_otp(client, message):
            nonlocal otp_code
            log(f"Message received from {message.from_user.id}", Fore.BLUE, "📩")
    
            match = re.search(r"(?:Login code|Code|Your code)[:\s]+(\d{5,6})\b", message.text, re.IGNORECASE)
            if match:
                  otp_code = match.group(1)
                  formatted_otp = (
                  f"\n{Fore.CYAN}{'=' * 30}\n"
                  f"{Fore.MAGENTA}🔐 OTP Code: {otp_code}\n"
                  f"{Fore.CYAN}{'=' * 30}"
                  )
                  log(formatted_otp, "", timestamp=True)
                  otp_received.set()


        while True:
            # Wait for OTP (up to 10 seconds)
            log("Waiting for OTP message...", Fore.YELLOW, "⏳")
            try:
                await asyncio.wait_for(otp_received.wait(), timeout=10)
            except asyncio.TimeoutError:
                log("No OTP received within 10 seconds.", Fore.RED, "⏰")
                # Ask to retry
                retry = input(f"{Fore.YELLOW}Try again for this session? (y/n): {Style.RESET_ALL}").strip().lower()
                if retry == "y":
                    log("Retrying OTP wait...", Fore.YELLOW, "🔄")
                    continue
                else:
                    log("Skipping session.", Fore.YELLOW, "⏭️")
                    if app.is_connected:
                        try:
                            await app.stop()
                        except Exception as e:
                            log(f"Error stopping client: {e}", Fore.RED, "❌", timestamp=True)
                    break

            # OTP received, ask user what to do
            choice = input(f"{Fore.YELLOW}R/F/Enter? (Retry/Failed/Next Session): {Style.RESET_ALL}").strip().lower()
            if choice == "r":
                log("Retrying OTP wait...", Fore.YELLOW, "🔄")
                otp_received.clear()  # Reset event to wait for new OTP
                continue
            elif choice == "f":
                log("Marked as failed.", Fore.RED, "🔴")
                # Disconnect client before moving file
                if app.is_connected:
                    try:
                        await app.stop()
                    except Exception as e:
                        log(f"Error stopping client: {e}", Fore.RED, "❌", timestamp=True)
                move_session_file(session_file, "dead_sessions")
                break
            elif choice == "":
                log("Session recovered!", Fore.GREEN, "✅")
                # Disconnect client before moving file
                if app.is_connected:
                    try:
                        await app.stop()
                    except Exception as e:
                        log(f"Error stopping client: {e}", Fore.RED, "❌", timestamp=True)
                move_session_file(session_file, "recovered_sessions")
                append_phone_number(session_file, phone_number)
                input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                break
            else:
                log("Invalid choice. Please enter R, F, or N.", Fore.RED, "❌")

    except (FloodWait, SessionPasswordNeeded, PhoneNumberBanned, AuthKeyUnregistered, UserDeactivated) as e:
        log(f"Session failed: {str(e)}", Fore.RED, "🔴")
        move_session_file(session_file, "dead_sessions")
    except Exception as e:
        log(f"Unexpected error: {str(e)}", Fore.RED, "❌")
        move_session_file(session_file, "dead_sessions")
    finally:
        # Ensure client is disconnected, but only if connected
        if app.is_connected:
            try:
                await app.stop()
            except:
                pass

async def main():
    # Setup directories
    setup_directories()
    # Load API credentials and 2FA skip setting
    api_id, api_hash, skip_2fa_enabled = load_config()
    # Get session files
    session_files = get_session_files()
    log(f"Found {len(session_files)} session files.", Fore.GREEN, "🟢")

    # Prompt to start
    input(f"{Fore.GREEN}Press Enter to start the recovery bot...{Style.RESET_ALL}")

    # Process each session
    for session_file in session_files:
        await process_session(session_file, api_id, api_hash, skip_2fa_enabled)

    log("All sessions processed.", Fore.GREEN, "✅")

if __name__ == "__main__":
    log("Starting Telegram OTP Recovery Bot...", Fore.GREEN, "🟢")
    asyncio.run(main())