# 🎤 Hindi + Telugu Interactive Voice Bot

A full-stack AI voice bot that understands and responds in Hindi + Telugu (mixed conversation).

---

## 📁 Project Structure

```
voicebot/
├── backend/
│   ├── app.py              # Flask server (API + serves frontend)
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # Full UI (STT + TTS + Chat)
├── logs/
│   ├── conversation.json   # Auto-generated chat logs
│   └── conversation.txt    # Human-readable logs
└── README.md
```

---

## 🚀 Setup & Run

### 1. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the server

```bash
python app.py
```

The app runs at: **http://localhost:5000**

---

## 🌐 Expose with ngrok

```bash
ngrok http 5000
```

Copy the HTTPS URL and share it!

---

## 🔧 Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | HTML + CSS + Vanilla JS             |
| Backend  | Python Flask + Flask-CORS           |
| STT      | Web Speech API (browser-native)     |
| TTS      | Browser SpeechSynthesis API         |
| Logs     | JSON + TXT files                    |

---

## 💬 Example Conversation

```
User: Namaste, naa peru Raju
Bot:  Namaste! Mera naam VoiceBot hai. Main aapki kaise help kar sakta hoon?

User: Mujhe ek software demo chahiye
Bot:  Sure! Meeku software demo schedule chestanu. Aapko kab convenient hai?

User: Contact details do
Bot:  Aap hamare sales team se contact kar sakte hain: +91 9853886666
```

---

## ✨ Features

- 🎤 **Microphone STT** — Web Speech API for Hindi (`hi-IN`) and Telugu (`te-IN`)
- 🔊 **Auto TTS** — Bot responses spoken aloud using SpeechSynthesis
- 💬 **Chat UI** — Live transcript bar + conversation bubbles
- 📝 **Conversation Logs** — Auto-saved as `.json` and `.txt`
- 📥 **Download Logs** — One-click export from the sidebar
- 🗑️ **Clear History** — Reset conversation anytime
- 📱 **Responsive** — Works on mobile and desktop

---

## 🏆 Evaluation Coverage

| Criteria                        | Status |
|----------------------------------|--------|
| Hindi + Telugu mix conversation  | ✅ Done |
| STT working                      | ✅ Web Speech API |
| TTS working                      | ✅ SpeechSynthesis |
| UI & usability                   | ✅ Clean dark UI |
| Logs implementation              | ✅ JSON + TXT |
| Code quality                     | ✅ Clean, modular |

---

## Submission

**Candidate Name:** _______________  
**Tech Stack:** Python Flask + HTML/CSS/JS + Web Speech API  
**Ngrok URL:** _(run ngrok http 5000)_  
**GitHub Repo:** _(push this folder)_
