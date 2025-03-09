from flask import Flask, jsonify
from flask_cors import CORS
from openai import OpenAI
import uuid
import time
import os
import random
from html2image import Html2Image
import json
from faker import Faker 
from PIL import Image
from submit_form import submit_multi_step_zoho_form
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
SCREENSHOT_DIR = os.path.join(os.getcwd(), 'screenshots')
SCREENSHOT_CONFIG = {
    'size': (380, 780),
    'quality': 80
}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZOHO_FORM_URL = os.getenv("ZOHO_FORM_URL")

# Initialize clients
fake = Faker()
client = OpenAI(api_key=OPENAI_API_KEY)
# hti = Html2Image(
#     browser_executable='chromium',
#     custom_flags=['--headless=new'],
#     output_path=SCREENSHOT_DIR,
#     ) 
hti = Html2Image(
    browser_executable='/usr/bin/google-chrome', 
    custom_flags=[
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--remote-debugging-port=9222',
        '--force-device-scale-factor=1'
    ],
    output_path=SCREENSHOT_DIR,
)

# WhatsApp-style HTML template
WHATSAPP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>{css}</style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-content">
            <div class="back-button">‹</div>
            <img src="https://picsum.photos/seed/uniqueSeed{uniqueSeedValue}/300/200" class="profile-pic">
            <div class="contact-info">
                <div class="contact-name">{name}</div>
                <div class="online-status">online</div>
            </div>
            <div class="call-icons">
                <span style="margin-right:15px">📷</span>
                <span>📞</span>
            </div>
        </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-container">
        {messages}
    </div>

    <!-- Input Bar -->
    <div class="input-bar">
        <div class="emoji-button">😊</div>
        <input type="text" class="input-field" placeholder="Type a message">
        <div class="send-button"></div>
    </div>
</body>
</html>
"""

WHATSAPP_CSS = """

body { 
    margin: 0;
    font-family: -apple-system, sans-serif; 
    background: #ece5dd;
    height: 680px;
    width: 380px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

/* Header Section */
.header {
    background: #075e54;
    padding: 10px 15px;
    color: white;
    display: flex;
    align-items: center;
    width: 380px;
    z-index: 100;
}

/* Message spacing adjustments */
.message {
    margin: 5px 0;  /* Reduced from 10px */
    max-width: 80%;
    clear: both;
}

.sent { 
    background: #dcf8c6; 
    float: right;
    border-radius: 7.5px 0 7.5px 7.5px;
    padding: 6px 12px 4px 12px;  /* Reduced bottom padding */
    position: relative;
}

/* Blue tick styling */
.sent .status {
    font-size: 0.75em;
    color: #34B7F1;
    margin-left: 5px;
    display: inline-block;
    vertical-align: middle;
}

.time {
    font-size: 0.75em;
    color: #667781;
    margin-top: 2px;  /* Reduced from 3px */
    text-align: right;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

.header-content {
    display: flex;
    align-items: center;
    width: 100%;
}

.back-button {
    font-size: 24px;
    margin-right: 15px;
}

.profile-pic {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
    background: #ddd
}

.contact-info {
    flex-grow: 1;
}

.contact-name {
    font-weight: 500;
}

.online-status {
    font-size: 0.8em;
    opacity: 0.8;
}

/* Chat Container */
.chat-container { 
    padding: 5px;
    padding-top: 0px;
    height: 560px;  /* 680 - 60 (header) - 60 (input) */
    overflow-y: hidden;
}

/* Input Bar */
.input-bar {
    width: 380px;
    background: white;
    padding: 10px;
    display: flex;
    align-items: center;
    border-top: 1px solid #ddd;
    z-index: 200;
}

.input-field {
    flex-grow: 1;
    background: #f5f5f5;
    border-radius: 20px;
    padding: 10px 15px;
    margin: 0 10px;
    border: none;
}

/* Message Bubbles */
.message {
    margin: 3px 0;
    max-width: 80%;
    clear: both;
}

.received { 
    background: white; 
    float: left;
    border-radius: 0 7.5px 7.5px 7.5px;
    padding: 6px 12px;
}
"""

DOUBLE_BLUE_TICK = """<svg viewBox="0 0 16 11" height="11" width="16" preserveAspectRatio="xMidYMid meet" class="" fill="none"><title>msg-dblcheck</title><path d="M11.0714 0.652832C10.991 0.585124 10.8894 0.55127 10.7667 0.55127C10.6186 0.55127 10.4916 0.610514 10.3858 0.729004L4.19688 8.36523L1.79112 6.09277C1.7488 6.04622 1.69802 6.01025 1.63877 5.98486C1.57953 5.95947 1.51817 5.94678 1.45469 5.94678C1.32351 5.94678 1.20925 5.99544 1.11192 6.09277L0.800883 6.40381C0.707784 6.49268 0.661235 6.60482 0.661235 6.74023C0.661235 6.87565 0.707784 6.98991 0.800883 7.08301L3.79698 10.0791C3.94509 10.2145 4.11224 10.2822 4.29844 10.2822C4.40424 10.2822 4.5058 10.259 4.60313 10.2124C4.70046 10.1659 4.78086 10.1003 4.84434 10.0156L11.4903 1.59863C11.5623 1.5013 11.5982 1.40186 11.5982 1.30029C11.5982 1.14372 11.5348 1.01888 11.4078 0.925781L11.0714 0.652832ZM8.6212 8.32715C8.43077 8.20866 8.2488 8.09017 8.0753 7.97168C7.99489 7.89128 7.8891 7.85107 7.75791 7.85107C7.6098 7.85107 7.4892 7.90397 7.3961 8.00977L7.10411 8.33984C7.01947 8.43717 6.97715 8.54508 6.97715 8.66357C6.97715 8.79476 7.0237 8.90902 7.1168 9.00635L8.1959 10.0791C8.33132 10.2145 8.49636 10.2822 8.69102 10.2822C8.79681 10.2822 8.89838 10.259 8.99571 10.2124C9.09304 10.1659 9.17556 10.1003 9.24327 10.0156L15.8639 1.62402C15.9358 1.53939 15.9718 1.43994 15.9718 1.32568C15.9718 1.1818 15.9125 1.05697 15.794 0.951172L15.4386 0.678223C15.3582 0.610514 15.2587 0.57666 15.1402 0.57666C14.9964 0.57666 14.8715 0.635905 14.7657 0.754395L8.6212 8.32715Z" fill="currentColor"></path></svg>"""

# --------------------------------------------------------------

def generate_conversation():
    """Generate realistic WhatsApp-style conversation with 3 logical breaks making sure that each part has equal number and length of messages"""
    prompt = """
    Generate a realistic WhatsApp conversation between two people discussing relationship issues.
    Follow these rules:
    1. IMPORTANT: Create 30 messages total having similar length.
    2. Include natural breaks where screen transitions would occur
    3. Return ONLY RAW JSON (no markdown formatting) with structure:
       { "messages": [{"sender": "PersonA/PersonB", "text": "...", "time": "HH:MM"}] }
    4. Include realistic timing between messages
    5. Use casual language with emojis and typos
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    # Clean response: remove markdown backticks and whitespace
    raw_json = response.choices[0].message.content
    clean_json = raw_json.replace('```json', '').replace('```', '').strip()
    
    return json.loads(clean_json)
     
def split_conversation(conversation):
    """Split conversation into 3 logical parts for screenshots"""
    total = len(conversation['messages'])
    return [
        conversation['messages'][:total//3],
        conversation['messages'][total//3:2*total//3],
        conversation['messages'][2*total//3:]
    ]
    
# Create_whatsapp_html function:
def create_whatsapp_html(conversation_part, first_name, uniqueSeedValue):
    """Generate WhatsApp-like HTML with full UI and ticks"""
    messages_html = []
    for msg in conversation_part:
        cls = "sent" if msg['sender'] == "PersonA" else "received"
        tick = f'<div class="status">{DOUBLE_BLUE_TICK}</div>' if cls == "sent" else ''
        messages_html.append(f"""
            <div class="message {cls}">
                <div class="text">{msg['text']}</div>
                <div class="time">
                    {msg['time']}
                    {tick}
                </div>
            </div>
        """)
    
    return WHATSAPP_TEMPLATE.format(
        css=WHATSAPP_CSS,
        name=first_name,
        uniqueSeedValue = uniqueSeedValue,
        messages="\n".join(messages_html)
    )

def submit_to_zoho(screenshot_paths, first_name):
    
    submit_multi_step_zoho_form(
        url=ZOHO_FORM_URL,
        file_paths=screenshot_paths,
        first_name=first_name,
        last_name=fake.last_name(),
        email=fake.email(),
        phone_number=fake.phone_number(),
    )
    
def run_automation():
    first_name = fake.first_name()

    # 1. Generate conversation
    conversation = generate_conversation()
    if 'error' in conversation:
        return jsonify({"error": "Conversation generation failed"}), 500
    
    # 2. Split conversation into 3 parts
    parts = split_conversation(conversation)
    
    # 3. Generate and submit screenshots
    screenshot_paths = []
    html_paths = []
    
    # Generate random seed value
    uniqueSeedValue = random.randint(1, 999)
    
    for i, part in enumerate(parts):
        
        # Generate HTML
        html_content = create_whatsapp_html(part, first_name, uniqueSeedValue)
        
        # Generate a unique filename
        unique_id = str(uuid.uuid4())
        screenshot_filename = f"screenshot_{unique_id}.png"
        screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
        
        # Create temporary HTML file (needed for some versions of html2image)
        temp_html_path = os.path.join(SCREENSHOT_DIR, f"temp_{unique_id}.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        html_paths.append(temp_html_path)
            
        # Create screenshot from HTML string 
        hti.screenshot(
            html_str=html_content,
            save_as=screenshot_filename,
            size=SCREENSHOT_CONFIG['size']
        )
        time.sleep(0.5)
        # Crop the bottom 100px
        img = Image.open(screenshot_path)
        width, height = img.size
        img.crop((0, 0, width, height - 200)).save(screenshot_path)

        time.sleep(0.5)
        screenshot_paths.append(screenshot_path)
        
    # 4. Submit screenshots to Zoho Form
    submit_to_zoho(screenshot_paths, first_name)
    
    # 5 Cleanup temporary files
    # for path in screenshot_paths:
    #     os.remove(path)
    
    # 6 Cleanup temporary HTML files
    for path in html_paths:
            os.remove(path)
        
    return jsonify({"status": "success", "screenshots": len(screenshot_paths)})

# --------------------------------------------------------------

@app.route("/run", methods=["GET"])
def run():
    try:
        run_automation()
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)