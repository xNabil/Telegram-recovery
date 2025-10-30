# 📱 Telegram OTP Recovery Bot

A Python tool built with **Pyrogram** to automatically process and recover Telegram session files, detect OTP messages from **@Telegram (777000)**, and log recovered phone numbers.

---

## ⚙️ Features

- Auto-detects and processes all `.session` files in the `sessions/` folder  
- Handles 2FA-locked accounts (optional skip)  
- Logs recovered phone numbers to `recovered_numbers.txt`  
- Moves processed sessions into:
  - `recovered_sessions/` → Successfully recovered  
  - `dead_sessions/` → Failed or banned  
- Colored console output with timestamps  
- Manual OTP confirmation and control

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

1. **Create `config.json`** in the same directory as `main.py`:

```config.json
{
  "api_id": "YOUR_API_ID",
  "api_hash": "YOUR_API_HASH",
  "SKIP_2FA_enabled": true
}
```

2. **Place your `.session` files** inside the `sessions/` folder.

3. **Run the script:**

   ```bash
   python main.py
   ```

4. The bot will:

   * Connect each session.
   * Prompt you to send OTP to the number.
   * Wait for the OTP from @Telegram (777000).
   * Ask what to do next (Retry / Fail / Next).

---

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

## 📜 License

This project is licensed under the **MIT License**.
Use at your own risk. Not affiliated with Telegram.

```
```
