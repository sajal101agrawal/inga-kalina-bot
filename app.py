from flask import Flask, jsonify
from flask_cors import CORS
from openai import OpenAI
import uuid
import time
import os
from html2image import Html2Image
import json
from faker import Faker 
from PIL import Image
from submit_form import submit_multi_step_zoho_form

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
OPENAI_API_KEY = "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" 
SCREENSHOT_DIR = os.path.join(os.getcwd(), 'screenshots')
SCREENSHOT_CONFIG = {
    'size': (380, 780),
    'quality': 80
}
ZOHO_FORM_URL = "https://forms.ingakalnina.com/ingakalnina/form/MissorMatch/formperma/NFBNE2POeln5oK56kHhxJTigSShna5y4T52M8tI0iW0"

# Initialize clients
fake = Faker()
client = OpenAI(api_key=OPENAI_API_KEY)
hti = Html2Image(
    browser_executable='chromium',
    custom_flags=['--headless=new'],
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
            <div class="profile-pic"></div>
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
    height: 550px;  /* 680 - 60 (header) - 60 (input) */
    overflow-y: auto;
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
    margin: 10px 0;
    max-width: 80%;
    clear: both;
}

.sent { 
    background: #dcf8c6; 
    float: right;
    border-radius: 7.5px 0 7.5px 7.5px;
    padding: 6px 12px;
}

.received { 
    background: white; 
    float: left;
    border-radius: 0 7.5px 7.5px 7.5px;
    padding: 6px 12px;
}

.time {
    font-size: 0.75em;
    color: #667781;
    margin-top: 3px;
    text-align: right;
}
"""

# --------------------------------------------------------------

def generate_conversation():
    """Generate realistic WhatsApp-style conversation with 3 logical breaks making sure that each part has equal number and length of messages"""
    prompt = """
    Generate a realistic WhatsApp conversation between two people discussing relationship issues.
    Follow these rules:
    1. Create 25-30 messages total
    2. Include natural breaks where screen transitions would occur
    3. Return ONLY RAW JSON (no markdown formatting) with structure:
       { "messages": [{"sender": "PersonA/PersonB", "text": "...", "time": "HH:MM"}] }
    4. Include realistic timing between messages
    5. Use casual language with emojis and typos
    """
    
    try:
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
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}\nRaw Response: {raw_json}")
        return {"error": "Failed to parse conversation"}
    except Exception as e:
        print(f"API Error: {str(e)}")
        return {"error": "Conversation generation failed"}
     
def split_conversation(conversation):
    """Split conversation into 3 logical parts for screenshots"""
    total = len(conversation['messages'])
    return [
        conversation['messages'][:total//3],
        conversation['messages'][total//3:2*total//3],
        conversation['messages'][2*total//3:]
    ]
    
# In create_whatsapp_html function:
def create_whatsapp_html(conversation_part, first_name):
    """Generate WhatsApp-like HTML with full UI"""
    messages_html = []
    for msg in conversation_part:
        cls = "sent" if msg['sender'] == "PersonA" else "received"
        messages_html.append(f"""
            <div class="message {cls}">
                <div class="text">{msg['text']}</div>
                <div class="time">{msg['time']}</div>
            </div>
        """)
    
    return WHATSAPP_TEMPLATE.format(
        css=WHATSAPP_CSS,
        name=first_name,
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
    try:
        # 1. Generate conversation
        conversation = generate_conversation()
        if 'error' in conversation:
            return jsonify({"error": "Conversation generation failed"}), 500
        
        # 2. Split conversation into 3 parts
        parts = split_conversation(conversation)
        
        # 3. Generate and submit screenshots
        screenshot_paths = []
        html_paths = []
        
        for i, part in enumerate(parts):
            # Generate HTML
            html_content = create_whatsapp_html(part, first_name)
            
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
        for path in html_content:
             os.remove(path)
            
        return jsonify({"status": "success", "screenshots": len(screenshot_paths)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# --------------------------------------------------------------

@app.route("/run", methods=["POST"])
def run():
    try:
        run_automation()
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"status": "fail", "error": e})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)