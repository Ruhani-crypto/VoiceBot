from flask import Flask, request, jsonify, send_from_directory, after_this_request
import json
import os
import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Conversation history (in-memory for demo; persisted to JSON)
conversation_history = []

def load_logs():
    global conversation_history
    log_file = os.path.join(LOGS_DIR, 'conversation.json')
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                conversation_history = json.load(f)
            except:
                conversation_history = []

def save_logs():
    log_file = os.path.join(LOGS_DIR, 'conversation.json')
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=2)
    
    # Also save as .txt
    txt_file = os.path.join(LOGS_DIR, 'conversation.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        for entry in conversation_history:
            f.write(f"{entry['role']}: {entry['message']}\n")

# Rule-based response engine for Hindi + Telugu mixed conversation
# Each category has Latin romanized keywords AND Devanagari/Telugu script keywords
RESPONSES = {
    "greet": {
        "keywords": [
            # Latin
            "namaste", "hello", "hi", "namaskar", "vanakkam", "namas", "hey", "helo",
            # Devanagari Hindi
            "नमस्ते", "नमस्कार", "हेलो", "हाय",
            # Telugu
            "నమస్తే", "నమస్కారం", "హలో"
        ],
        "response": "Namaste! Mera naam VoiceBot hai. Main aapki kaise help kar sakta hoon? / Meeru ela untaro?"
    },
    "name": {
        "keywords": [
            # Latin
            "peru", "naam", "name", "mera naam", "naa peru", "naaku", "mera", "aapka naam", "my name",
            # Devanagari Hindi
            "नाम", "मेरा नाम", "मेरा", "आपका नाम", "राजू", "रaju",
            # Telugu
            "నా పేరు", "పేరు", "నా", "మీ పేరు"
        ],
        "response": "Bahut accha! Aapka naam sunke khushi hui. Aap kya help chahte hain? / Meeru cheppindi vinataniki santhosham aindi!"
    },
    "demo": {
        "keywords": [
            # Latin
            "demo", "kavali", "chahiye", "software demo", "product demo", "show", "dikhao", "dekhna",
            # Devanagari Hindi
            "डेमो", "चाहिए", "दिखाओ", "देखना",
            # Telugu
            "డెమో", "కావాలి", "చూపించు"
        ],
        "response": "Sure! Meeku software demo schedule chestanu. Aapko kab convenient hai? Monday ya Tuesday? / Aapko kaunsa time suit karega?"
    },
    "help": {
        "keywords": [
            # Latin
            "help", "madad", "sahayam", "assist", "support", "problem", "issue", "chahiye help", "help karo",
            # Devanagari Hindi
            "मदद", "सहायता", "समस्या", "मदद करो", "हेल्प",
            # Telugu
            "సహాయం", "సహాయపడు", "సమస్య", "హెల్ప్"
        ],
        "response": "Main aapki help karne ke liye hoon! Aap kya jaanna chahte hain? / Meeru ela help cheyyali?"
    },
    "pricing": {
        "keywords": [
            # Latin
            "price", "cost", "kitna", "rate", "fees", "charges", "amount", "rupee", "paisa", "kitne", "pricing",
            # Devanagari Hindi
            "कीमत", "कितना", "दाम", "पैसे", "रुपये", "मूल्य",
            # Telugu
            "ధర", "ఎంత", "రేటు", "పైసలు", "ధరలు"
        ],
        "response": "Hamari pricing plans bahut flexible hain. Demo ke baad aapko exact pricing batayenge. / Meeku demo tarvatha pricing discuss chestamu."
    },
    "contact": {
        "keywords": [
            # Latin
            "contact", "call", "phone", "email", "reach", "connect", "sampark", "number do", "number dena",
            # Devanagari Hindi
            "संपर्क", "फोन", "नंबर", "कॉल", "ईमेल",
            # Telugu
            "సంప్రదించు", "ఫోన్", "నంబర్", "కాల్", "ఇమెయిల్"
        ],
        "response": "Aap hamare sales team se contact kar sakte hain: +91 9853886666. / Mee details lekunte meeru call back chestamu!"
    },
    "thanks": {
        "keywords": [
            # Latin
            "thank", "thanks", "shukriya", "dhanyawad", "dhanyavaadalu", "theek", "badhiya", "shukriyaa", "tq", "ty",
            # Devanagari Hindi
            "धन्यवाद", "शुक्रिया", "थैंक्स", "ठीक",
            # Telugu
            "ధన్యవాదాలు", "థాంక్స్", "బాగుంది"
        ],
        "response": "Aapka shukriya! Koi aur help chahiye ho toh batayein. / Meeru ela untaro, always here for you!"
    },
    "bye": {
        "keywords": [
            # Latin
            "bye", "goodbye", "alvida", "tata", "baad mein", "later", "chal", "chalte", "phir milenge",
            # Devanagari Hindi
            "अलविदा", "बाय", "चलते", "फिर मिलेंगे",
            # Telugu
            "వెళ్తాను", "బై", "వీడ్కోలు", "మళ్ళీ కలుద్దాం"
        ],
        "response": "Alvida! Milte hain phir. Aapka din shubh ho! / Meeru tarvaata kalisthamu, subhakaankshalu!"
    },
    "schedule": {
        "keywords": [
            # Latin
            "schedule", "appointment", "meeting", "book", "time", "slot", "milna", "fix karo", "book karo",
            # Devanagari Hindi
            "शेड्यूल", "अपॉइंटमेंट", "मीटिंग", "बुक", "समय",
            # Telugu
            "షెడ్యూల్", "అపాయింట్మెంట్", "మీటింగ్", "బుక్", "సమయం"
        ],
        "response": "Zaroor! Meeku appointment book kar deta hoon. Aapka naam aur contact number denge? / Meeting ke liye convenient time batayein."
    },
    "features": {
        "keywords": [
            # Latin
            "features", "kya kya", "kya hai", "functionality", "options", "capabilities", "kya milega", "kya karta",
            # Devanagari Hindi
            "फीचर्स", "क्या है", "क्या क्या", "सुविधाएं",
            # Telugu
            "ఫీచర్లు", "ఏమేమి", "ఏమి ఉంది", "సౌకర్యాలు"
        ],
        "response": "Hamare software mein bahut saare features hain: AI-powered analytics, multi-language support, real-time dashboards aur bahut kuch! / Detailed demo mein sab dikhayenge."
    },
    "software": {
        "keywords": [
            # Latin
            "software", "product", "app", "application", "tool", "system", "platform",
            # Devanagari Hindi
            "सॉफ्टवेयर", "एप्लिकेशन", "प्रोडक्ट",
            # Telugu
            "సాఫ్ట్‌వేర్", "అప్లికేషన్", "ప్రొడక్ట్"
        ],
        "response": "Haan! Hamara software bahut powerful hai. Aapko demo dekhna hai? / Meeku demo chupinchali ante cheppandi!"
    }
}

# Name extraction — greet user by name if detected
import re

def extract_name(text):
    """Try to extract a name from common Hindi/Telugu name patterns."""
    patterns = [
        r'(?:mera naam|my name is|naam hai|naa peru|naaku peru)\s+([A-Za-z\u0900-\u097F\u0C00-\u0C7F]+)',
        r'(?:मेरा नाम|नाम है)\s+([A-Za-z\u0900-\u097F\u0C00-\u0C7F]+)',
        r'(?:నా పేరు|పేరు)\s+([A-Za-z\u0C00-\u0C7F]+)',
        r'(?:i am|i\'m|main hoon|main)\s+([A-Z][a-z]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def get_bot_response(user_text):
    """Generate a response based on user input using rule-based matching."""
    text_lower = user_text.lower()

    # Try name extraction first for a personalised reply
    name = extract_name(user_text)
    if name:
        return f"Namaste {name} ji! Aapko kaise help kar sakta hoon? / {name} garu, meeru ela help cheyyali?"

    # Check each category
    for category, data in RESPONSES.items():
        for keyword in data["keywords"]:
            if keyword.lower() in text_lower or keyword in user_text:
                return data["response"]

    # Default fallback
    return "Main samajh gaya! Aap aur kuch jaanna chahte hain? Demo, pricing, ya contact info ke liye poochh sakte hain. / Demo, pricing, contact info — emaina adugandi!"


@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get bot response
    bot_response = get_bot_response(user_message)
    
    timestamp = datetime.datetime.now().isoformat()
    
    # Store in history
    conversation_history.append({
        "role": "User",
        "message": user_message,
        "timestamp": timestamp
    })
    conversation_history.append({
        "role": "Bot",
        "message": bot_response,
        "timestamp": timestamp
    })
    
    save_logs()
    
    return jsonify({
        'response': bot_response,
        'timestamp': timestamp
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(conversation_history)

@app.route('/logs/clear', methods=['POST'])
def clear_logs():
    global conversation_history
    conversation_history = []
    save_logs()
    return jsonify({'status': 'cleared'})

@app.route('/logs/download/json', methods=['GET'])
def download_json():
    return send_from_directory('../logs', 'conversation.json', as_attachment=True)

@app.route('/logs/download/txt', methods=['GET'])
def download_txt():
    return send_from_directory('../logs', 'conversation.txt', as_attachment=True)

if __name__ == '__main__':
    load_logs()
    print("🎤 VoiceBot server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
