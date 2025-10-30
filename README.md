# 📱 Telegram OTP Recovery Bot

This is a Python-based tool designed to help recover Telegram sessions by automating the process of receiving and handling One-Time Passwords (OTPs). It attempts to log into existing `.session` files, displays the account's phone number, captures the OTP sent to that number, and organizes sessions into 'recovered' or 'dead' folders based on the outcome.

---

## ⚙️ Features

* **Session Processing**: Iterates through all `.session` files located in the `sessions` directory.
* **Phone Number Display**: Automatically retrieves and **displays the phone number** associated with the session, so you know exactly where to send the login code.
* **OTP Handling**: Automatically listens for and extracts the 5 or 6-digit login code from Telegram's official service account (ID 777000).
* **2FA Check**: Can optionally skip sessions that have Two-Factor Authentication (2FA) enabled (configurable in `config.json`).
* **Session Organization**: Automatically moves sessions to `recovered_sessions` upon success or `dead_sessions` upon failure (e.g., 2FA enabled, banned account, invalid session).
* **Phone Number Logging**: Saves the phone numbers of all successfully recovered accounts to `recovered_numbers.txt`.
* **Interactive Controls**: Allows you to manually retry (R), mark as failed (F), or proceed to the next session (Enter) after an OTP is received.
---

## 🧩 Requirements

- **Python 3.8+**
- **Telegram API credentials** (from [my.telegram.org](https://my.telegram.org))

Install dependencies:

```bash
pip install -r requirements.txt
````

`requirements.txt`:

```txt
pyrogram==2.0.106
tgcrypto
colorama
```

---

## 📁 Project Structure

```
.
├── main.py
├── config.json
├── sessions/
├── recovered_sessions/
├── dead_sessions/
└── recovered_numbers.txt
```

---

## 🔧 Setup

1.  **Get API Credentials:**
    * Log in to your Telegram account at [https://my.telegram.org](https://my.telegram.org).
    * Go to "API development tools" and create a new application.
    * You will receive an **`api_id`** and **`api_hash`**.

2.  **Configure the Bot:**
    * Open the `config.json` file.
    * Paste your `api_id` and `api_hash` into the respective fields.
    * Set `SKIP_2FA_enabled` to `true` if you want to automatically skip accounts that have 2FA enabled. Otherwise, leave it as `false`.

    **Example `config.json`:**
    ```json
    {
      "api_id": 1234567,
      "api_hash": "0123456789abcdef0123456789abcdef",
      "SKIP_2FA_enabled": false
    }
    ```

3.  **Add Session Files:**
    * Place all your Telegram `.session` files (e.g., `my_account.session`) into the `sessions/` directory. The script creates this directory if it doesn't exist.

4.  **Run the Script:**
    * Execute the main script from your terminal:
    ```sh
    python main.py
    ```
5. The bot will:

  * The bot will start processing each session file one by one.
    * It will log in and **display the phone number** for the account (e.g., `📱 Phone Number: +1234567890`).
    * The script will then pause and ask you to **send an OTP to that number** (e.g., by logging in on another device) and press Enter to continue.

6.  **Handle the OTP:**
    * Once you've sent the code, the bot will detect the incoming OTP message from Telegram (ID 777000) and display the code.
    * You will then be prompted to:
    * Press **Enter** to confirm recovery (saves the number, moves the session) and move to the next session.
    * Type **`r`** and press Enter to retry waiting for an OTP for the *same* session.
    * Type **`f`** and press Enter to mark the session as failed and move it to `dead_sessions`.

## 🗂️ Output Explanation

* ✅ `recovered_sessions/` → Sessions successfully verified
* ❌ `dead_sessions/` → Banned, invalid, or 2FA-locked sessions
* 📝 `recovered_numbers.txt` → Log of recovered phone numbers

---

## ⚠️ Notes

* This script **requires valid Telegram sessions** created using Pyrogram or similar tools.
* The OTP capture depends on receiving messages from **@Telegram (777000)**.
* If `SKIP_2FA_enabled` is `true`, accounts with 2FA will be auto-skipped.
* Run the script responsibly — repeated login attempts may trigger Telegram’s floodwait limits.

---

## 🧠 Example Run

```
📱 Starting Telegram OTP Recovery Bot...
📁 Created directory: sessions
🟢 Found 5 session files.
Press Enter to start the recovery bot...

🔄 Processing session: user1.session
📱 Phone Number: +8801XXXXXXX
⏳ Waiting for OTP message...
🔐 OTP Code: 123456
✅ Session recovered!
📂 Moved user1.session to recovered_sessions
📝 Saved phone number to recovered_numbers.txt
```

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.
This project is licensed under the **MIT License**.
Use at your own risk. Not affiliated with Telegram.

## 👨‍💻 Author

- **Nabil** – [GitHub: xNabil](https://github.com/xNabil)

---

## Donate 💸
Love the bot? Wanna fuel more WAGMI vibes? Drop some crypto love to keep the charts lit! 🙌
- **SUI**: `0x8ffde56ce74ddd5fe0095edbabb054a63f33c807fa4f6d5dc982e30133c239e8`
- **USDT (TRC20)**: `TG8JGN59e8iqF3XzcD26WPL8Zd1R5So7hm`
- **BNB (BEP20)**: `0xe6bf8386077c04a9cc05aca44ee0fc2fe553eff1`
- **Binance UID**:`921100473`

Every bit helps me grind harder and keep this bot stacking bags! 😎

