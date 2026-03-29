import streamlit as st
try:
    import speech_recognition as sr
except ImportError:
    sr = None
from gtts import gTTS
import os
import tempfile
import base64
from datetime import datetime
import json
import requests
from googletrans import Translator
import html
import re

# Page configuration
st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        padding: 2rem 0;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header Styling */
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        color: rgba(255,255,255,0.95);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] h1 {
        color: #ffffff;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e1;
    }
    
    /* Text Input Styling */
    .stTextInput > div > div > input {
        border-radius: 16px;
        border: 2px solid rgba(255,255,255,0.3);
        padding: 16px 20px;
        font-size: 15px;
        background: rgba(255,255,255,0.98) !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #1e293b !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
        opacity: 0.7;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 8px 16px rgba(102,126,234,0.3);
        background: #ffffff !important;
        color: #1e293b !important;
        outline: none;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.5rem 1.75rem;
        border-radius: 20px;
        margin-bottom: 1.25rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        animation: slideIn 0.3s ease-out;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 15%;
        margin-right: 5%;
        border: none;
        box-shadow: 0 8px 24px rgba(102,126,234,0.4);
    }
    
    .assistant-message {
        background: rgba(255,255,255,0.98);
        border: 1px solid rgba(255,255,255,0.5);
        margin-right: 15%;
        margin-left: 5%;
        color: #1e293b;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .chat-message strong {
        font-weight: 600;
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .chat-message div {
        line-height: 1.7;
        font-size: 15px;
    }
    
    /* Urgent Badge */
    .urgent-badge {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
        font-size: 0.85rem;
        box-shadow: 0 4px 12px rgba(239,68,68,0.4);
        animation: pulse 2s infinite;
        letter-spacing: 0.5px;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 14px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3);
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Voice Input Button */
    button[kind="secondary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(245,87,108,0.4) !important;
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 0.75rem;
        opacity: 0.65;
        margin-top: 8px;
        font-weight: 400;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.1);
        color: #ffffff;
        padding: 10px 15px;
        font-weight: 500;
    }
    
    /* Toggle Styling */
    .stToggle label {
        color: #e2e8f0;
        font-weight: 500;
    }
    
    /* Slider Styling */
    .stSlider {
        color: #667eea;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* Container Styling */
    .stContainer {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Footer */
    footer {
        visibility: hidden;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Info/Success/Error Messages */
    .stInfo, .stSuccess, .stError, .stWarning {
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea;
    }
    
    /* Markdown in sidebar */
    [data-testid="stSidebar"] .stMarkdown code {
        background: rgba(102,126,234,0.2);
        color: #a5b4fc;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
    }
    
    /* Chat Container */
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    # Initial welcome message - clean plain text only
    welcome_text = 'السلام علیکم! میں آپ کی مدد کے لیے حاضر ہوں۔\n\nAssalam o Alaikum! Main aap ki madad ke liye hazir hoon.\n\nHello! I am here to help you. How are you feeling today?'
    st.session_state.messages = [
        {
            'type': 'assistant',
            'text': welcome_text,
            'timestamp': datetime.now().strftime('%I:%M %p'),
            'urgency': 'NORMAL',
            'language': 'english'  # Default language for initial message
        }
    ]
    
if 'detected_language' not in st.session_state:
    st.session_state.detected_language = 'english'

if 'audio_enabled' not in st.session_state:
    st.session_state.audio_enabled = True

if 'translator' not in st.session_state:
    st.session_state.translator = Translator()

if 'last_processed_input' not in st.session_state:
    st.session_state.last_processed_input = None

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Backend triage session state (flowchart progress)
if 'backend_session_state' not in st.session_state:
    st.session_state.backend_session_state = None

# Backend API URL - use env var or default for local/HF Spaces
BACKEND_URL = os.environ.get("TRIAGE_BACKEND_URL", "http://localhost:8000")
VOICE_INPUT_ENABLED = os.environ.get("ENABLE_VOICE_INPUT", "false").lower() == "true"

# Language configurations
LANGUAGE_CONFIG = {
    'english': {
        'name': 'English',
        'code': 'en',
        'tts_code': 'en',
        'speech_code': 'en-US',
        'display': 'English'
    },
    'urdu': {
        'name': 'Urdu (Roman)',
        'code': 'ur',
        'tts_code': 'ur',
        'speech_code': 'ur-PK',
        'display': 'اردو (Urdu)'
    },
    'punjabi': {
        'name': 'Punjabi (Roman)',
        'code': 'pa',
        'tts_code': 'pa',
        'speech_code': 'pa-IN',
        'display': 'ਪੰਜਾਬੀ (Punjabi)'
    }
}

# Transliteration function for Roman Urdu/Punjabi
def transliterate_to_roman(text, target_lang='ur'):
    """
    Transliterate Urdu/Punjabi text to Roman script
    """
    # Common Urdu to Roman transliteration mappings
    urdu_to_roman = {
        'مجھے': 'mujhe',
        'آپ': 'aap',
        'ہے': 'hai',
        'میں': 'mein',
        'کو': 'ko',
        'بخار': 'bukhar',
        'درد': 'dard',
        'سر': 'sar',
        'پیٹ': 'pet',
        'تھکاوٹ': 'thakawat',
        'پیاس': 'pyas',
        'سینے': 'seene',
        'کیا': 'kya',
        'کب': 'kab',
        'کتنا': 'kitna',
        'دن': 'din',
        'ہفتہ': 'hafta',
        'مہینہ': 'mahina',
    }
    
    # Try to transliterate if it's Urdu script
    for urdu, roman in urdu_to_roman.items():
        text = text.replace(urdu, roman)
    
    return text

def auto_detect_language(text):
    """
    Automatically detect the language of the input text (Roman Urdu, Roman Punjabi, or English)
    Returns: 'english', 'urdu', or 'punjabi'
    """
    try:
        text_lower = text.lower().strip()
        
        # Check for Urdu script (Arabic/Persian characters)
        if any('\u0600' <= c <= '\u06FF' for c in text):
            return 'urdu'
        
        # Check for Punjabi script (Gurmukhi)
        if any('\u0A00' <= c <= '\u0A7F' for c in text):
            return 'punjabi'
        
        # Expanded Roman Urdu keywords (more comprehensive)
        urdu_roman_keywords = [
            'mujhe', 'aap', 'hai', 'mein', 'ko', 'bukhar', 'dard', 'sir', 'pet', 'thakawat', 
            'shukriya', 'kya', 'kab', 'kitna', 'se', 'ke', 'liye', 'hazir', 'hoon', 'hain',
            'aur', 'ya', 'bhi', 'nahi', 'nahin', 'kyun', 'kaise', 'kahan', 'kab', 'kabse',
            'sir', 'sar', 'dard', 'pet', 'seene', 'chest', 'thand', 'pyas', 'khansi',
            'matli', 'ulti', 'balgham', 'thakawat', 'thakan', 'thak', 'gaya', 'gayi',
            'lagti', 'lagta', 'lag raha', 'lag rahi', 'ho raha', 'ho rahi', 'aa raha', 'aa rahi'
        ]
        urdu_count = sum(1 for keyword in urdu_roman_keywords if keyword in text_lower)
        
        # Expanded Roman Punjabi keywords
        punjabi_roman_keywords = [
            'mainu', 'tuhanu', 'hai', 'ton', 'bukhar', 'dard', 'sir', 'dhanvaad', 'ki', 
            'kinne', 'nu', 'da', 'di', 'de', 'te', 'naal', 'vich', 'kol', 'nal',
            'ho', 'gaya', 'gayi', 'lagda', 'lagdi', 'aa', 'ja', 'karo', 'kari'
        ]
        punjabi_count = sum(1 for keyword in punjabi_roman_keywords if keyword in text_lower)
        
        # Check for specific Urdu patterns
        urdu_patterns = ['mujhe', 'aap ko', 'aapka', 'aapki', 'mein', 'se', 'ke liye', 'ho raha', 'lag raha']
        urdu_pattern_count = sum(1 for pattern in urdu_patterns if pattern in text_lower)
        
        # Check for specific Punjabi patterns
        punjabi_patterns = ['mainu', 'tuhanu', 'tuhada', 'tuhadi', 'vich', 'ton', 'naal']
        punjabi_pattern_count = sum(1 for pattern in punjabi_patterns if pattern in text_lower)
        
        # Weighted scoring
        urdu_score = urdu_count + (urdu_pattern_count * 2)
        punjabi_score = punjabi_count + (punjabi_pattern_count * 2)
        
        # If Urdu score is higher, likely Roman Urdu
        if urdu_score > punjabi_score and urdu_score > 0:
            return 'urdu'
        # If Punjabi score is higher, likely Roman Punjabi
        elif punjabi_score > urdu_score and punjabi_score > 0:
            return 'punjabi'
        # Default to English
        else:
            return 'english'
    except Exception as e:
        # Default to English on error
        return 'english'

def detect_and_translate_input(text, target_language='ur'):
    """
    Detect language and translate/transliterate input text
    """
    try:
        # Detect if text is in Urdu/Punjabi script
        if any('\u0600' <= c <= '\u06FF' for c in text):
            # If it's Urdu script, transliterate to Roman
            roman_text = transliterate_to_roman(text, target_language)
            return roman_text
        else:
            # Already in Roman or English, return as is
            return text
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

def translate_response(text, target_language='ur'):
    """
    Translate response to target language and provide Roman version
    """
    try:
        if target_language == 'en':
            return text
        
        # Translate to target language
        translator = st.session_state.translator
        translated = translator.translate(text, dest=LANGUAGE_CONFIG[target_language]['code'])
        
        # Get both script and roman versions
        native_script = translated.text
        roman_version = transliterate_to_roman(native_script, target_language)
        
        # Return formatted response with both versions
        return f"{native_script}\n\n{roman_version}\n\n{text}"
    
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

# Function to record audio
def record_audio(language='en-US', duration=5):
    """
    Record audio from microphone and convert to text
    """
    if sr is None:
        st.error("Voice input is not available in this deployment.")
        return None

    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            st.info(f"🎤 **Listening...** Please speak clearly. Recording for {duration} seconds.")
            
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Record audio
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            st.success("✅ **Recording complete!** Processing your speech...")
            
            # Convert speech to text
            try:
                text = recognizer.recognize_google(audio, language=language)
                return text
            except sr.UnknownValueError:
                st.error("❌ **Could not understand audio.** Please speak more clearly and try again.")
                return None
            except sr.RequestError as e:
                st.error(f"❌ **Speech recognition error:** {e}")
                return None
                
    except Exception as e:
        st.error(f"❌ **Microphone error:** {e}. Please check your microphone connection.")
        return None

# Function to play audio
def text_to_speech(text, language='en', play_audio=True):
    """
    Convert text to speech and return audio file
    """
    try:
        # Clean text (remove Roman and extra formatting for better TTS)
        clean_text = text.split('\n')[0] if '\n' in text else text
        clean_text = clean_text.strip()
        
        # Handle Punjabi - gTTS doesn't support Punjabi ('pa') well, use Hindi as fallback
        if language == 'punjabi':
            # For Roman Punjabi, use Hindi TTS (phonetically similar and works better)
            # gTTS 'pa' code often fails or doesn't work properly
            try:
                tts = gTTS(text=clean_text, lang='hi', slow=False)
            except Exception as e:
                # If Hindi also fails, try English as last resort
                st.warning(f"Punjabi TTS issue, using English: {e}")
                tts = gTTS(text=clean_text, lang='en', slow=False)
        else:
            # Generate speech for other languages (English, Urdu)
            tts_lang = LANGUAGE_CONFIG[language]['tts_code']
            tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            
            if play_audio:
                # Read audio file and encode to base64
                with open(fp.name, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode()
                    
                # Auto-play audio using HTML
                audio_html = f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            
            return fp.name
            
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

# Function to get demo response - responds in same language only (Roman Urdu, Roman Punjabi, or English)
def get_demo_response(user_input, language='english'):
    """
    Generate demo response based on user input - returns response in the same language only
    """
    user_lower = user_input.lower().strip()
    urgency = 'NORMAL'
    
    # Clean dummy responses - respond in the same language only (Roman Urdu, Roman Punjabi, or English)
    if any(word in user_lower for word in ['bukhar', 'fever', 'head', 'hurting', 'headache', 'sir dard', 'sir mein dard']):
        if language == 'urdu':
            response = "Shukriya. Aapko bukhar kitne din se hai? Kya aapko thand bhi lagti hai?"
        elif language == 'punjabi':
            response = "Dhanvaad. Tuhanu bukhar kinne dinan ton hai? Kya aapko thand bhi lag rahi hai?"
        else:
            response = "Thank you for sharing. How many days have you had fever? Do you also have chills or body aches?"
    
    elif any(word in user_lower for word in ['chest pain', 'seene mein dard', 'seene dard', 'chest']):
        urgency = 'URGENT'
        if language == 'urdu':
            response = "Yeh sanjeeda ho sakta hai! Kya dard bayen bazu mein bhi hai? Foran 1122 call karein!"
        elif language == 'punjabi':
            response = "Eh sanjeeda ho sakda hai! Kya dard bayen bazu vich hai? Turant 1122 call karo!"
        else:
            response = "This could be serious! Does the pain radiate to your left arm? Please call emergency services (1122) immediately!"
    
    elif any(word in user_lower for word in ['thakawat', 'tired', 'thakan', 'fatigue', 'thak gaya']):
        if language == 'urdu':
            response = "Samajh gaya. Aapko thakawat kab se hai? Kya aapko bohot zyada pyas lagti hai?"
        elif language == 'punjabi':
            response = "Samajh gaya. Aapko thakawat kinne dinan ton hai? Kya aapko bahut pyas lag rahi hai?"
        else:
            response = "I understand. How long have you been feeling tired? Are you very thirsty? Have you experienced any weight loss recently?"
    
    elif any(word in user_lower for word in ['stomach', 'pet', 'abdomen', 'pain', 'pet mein dard']):
        if language == 'urdu':
            response = "Aapko pet mein dard kab se hai? Kya aapko matli ya ulti bhi ho rahi hai?"
        elif language == 'punjabi':
            response = "Aapko pet vich dard kinne dinan ton hai? Kya aapko ulti ho rahi hai?"
        else:
            response = "How long have you had stomach pain? Are you also experiencing nausea or vomiting? What did you eat recently?"
    
    elif any(word in user_lower for word in ['cough', 'khansi', 'coughing']):
        if language == 'urdu':
            response = "Khansi kab se hai? Kya aapko balgham bhi aa raha hai? Kya yeh dry cough hai ya phlegm ke saath?"
        elif language == 'punjabi':
            response = "Khansi kinne dinan ton hai? Kya aapko balgham aa raha hai?"
        else:
            response = "How long have you had the cough? Are you also producing phlegm? Is it a dry cough or with phlegm?"
    
    else:
        if language == 'urdu':
            response = "Shukriya. Kya aap mujhe apni alamat ke bare mein mazeed bata sakte hain? Kab se yeh masla shuru hua?"
        elif language == 'punjabi':
            response = "Dhanvaad. Ki tusi mainu apne lakshanan bare hor dass sakde ho? Kinne dinan ton eh shuru hoya?"
        else:
            response = "Thank you for sharing. Can you tell me more about your symptoms? When did they start? Are there any other symptoms you're experiencing?"
    
    # Ensure response is clean text only - remove any potential HTML
    response = re.sub(r'<[^>]+>', '', response)  # Remove all HTML tags
    response = html.unescape(response)  # Decode HTML entities like &lt; &gt; etc
    response = response.strip()
    
    # Final safety check - ensure no HTML remnants
    if '<' in response or '>' in response:
        response = re.sub(r'<[^>]+>', '', response)
    
    return response, urgency

# Function to send to backend (real triage API with demo fallback)
def send_to_backend(patient_input, language, conversation_history, backend_session_state=None):
    """
    Send patient input to triage backend API.
    Falls back to demo response if API is unavailable.
    Returns: dict with response_text, urgency_level, triage_result?, session_state?
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/diagnose",
            json={
                "patient_input": patient_input,
                "language": language,
                "conversation_history": conversation_history,
                "session_state": backend_session_state,
            },
            timeout=60,
        )
        if response.status_code == 200:
            data = response.json()
            result = {
                "response_text": data.get("response_text", ""),
                "urgency_level": data.get("urgency_level", "NORMAL"),
                "reasoning": data.get("reasoning"),
                "triage_result": data.get("triage_result"),
            }
            if "session_state" in data and data["session_state"]:
                result["session_state"] = data["session_state"]
            return result
        else:
            st.warning(f"Backend returned {response.status_code}. Using demo mode.")
    except requests.exceptions.ConnectionError:
        st.warning("Could not connect to triage backend. Using demo mode. Start the backend with: `uvicorn backend.api:app --reload`")
    except Exception as e:
        st.warning(f"Backend error: {e}. Using demo mode.")

    # DEMO FALLBACK - pattern matching when API unavailable
    response_text, urgency = get_demo_response(patient_input, language)
    response_text = str(response_text).strip()
    response_text = re.sub(r"<[^>]+>", "", response_text)
    if "السلام علیکم" in response_text and len(response_text) < 200:
        if language == "urdu":
            response_text = "Shukriya. Main aap ki madad karne ke liye tayar hoon. Baraye karam apni alamat ke bare mein mazeed bataein."
        elif language == "punjabi":
            response_text = "Dhanvaad. Main tuhadi madad karan lai tiyar haan. Kirpa karke apne lakshanan bare hor daso."
        else:
            response_text = "Thank you. I'm here to help. Please tell me more about your symptoms. What are you experiencing?"

    return {
        "response_text": response_text,
        "urgency_level": urgency,
        "reasoning": "Demo mode: Pattern matching",
    }

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;'>
        <h1 style='font-size: 2rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>⚙️ Settings</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Language display (auto-detected)
    st.markdown("### 🌐 Language Detection")
    if 'detected_language' in st.session_state:
        detected = st.session_state.detected_language
        st.info(f"**Detected:** {LANGUAGE_CONFIG[detected]['display']}")
    else:
        st.info("**Auto-detection enabled** - Language will be detected from your input")
    
    # Keep language selector hidden but available for fallback
    selected_language = st.session_state.get('detected_language', 'english')
    
    st.divider()
    
    # Audio settings
    st.markdown("### 🔊 Audio Settings")
    audio_enabled = st.toggle("Enable Audio Responses", value=True, key='audio_toggle')
    st.session_state.audio_enabled = audio_enabled
    
    st.divider()
    
    # Recording duration
    st.markdown("### 🎤 Voice Input")
    if VOICE_INPUT_ENABLED:
        recording_duration = st.slider("Recording Duration (seconds)", 3, 10, 5, help="Adjust how long you want to record your voice input")
    else:
        recording_duration = 5
        st.info("Voice input is available in local desktop runs only.")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.backend_session_state = None
        st.rerun()
    
    st.divider()
    
    # Instructions
    st.markdown("""
    <div style='background: rgba(102,126,234,0.1); padding: 1.25rem; border-radius: 12px; border-left: 4px solid #667eea;'>
        <h4 style='color: #e2e8f0; margin-top: 0; margin-bottom: 0.75rem;'>📖 How to Use</h4>
        <ol style='color: #cbd5e1; padding-left: 1.25rem; line-height: 1.8; font-size: 0.9rem;'>
            <li><strong>Type</strong> your symptoms in Roman Urdu/Punjabi/English</li>
            <li><strong>Or click</strong> 🎤 Voice Input to speak (local runs)</li>
            <li>AI will respond in your selected language</li>
            <li>Toggle audio to hear responses</li>
        </ol>
        
        <h4 style='color: #e2e8f0; margin-top: 1rem; margin-bottom: 0.75rem;'>💡 Example Inputs</h4>
        <ul style='color: #cbd5e1; padding-left: 1.25rem; line-height: 1.8; font-size: 0.9rem;'>
            <li><strong>Urdu:</strong> "Mujhe bukhar hai"</li>
            <li><strong>Punjabi:</strong> "Mainu sir dard hai"</li>
            <li><strong>English:</strong> "I have chest pain"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Main chat interface
st.markdown("""
<div style='text-align: center; padding: 2rem 0 1.5rem 0; margin-bottom: 2rem;'>
    <h1 style='font-size: 3rem; margin: 0; background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>
        🏥 AI Health Assistant
    </h1>
    <p style='font-size: 1.1rem; color: rgba(255,255,255,0.95); margin-top: 0.5rem; font-weight: 500; letter-spacing: 0.5px;'>
        صحت کا ساتھی • ਸਿਹਤ ਸਾਥੀ • Health Companion
    </p>
    <div style='width: 100px; height: 4px; background: linear-gradient(90deg, #667eea 0%, #f093fb 100%); margin: 1rem auto; border-radius: 2px;'></div>
</div>
""", unsafe_allow_html=True)

# Display chat messages
chat_container = st.container()
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
        # Get clean message text - ensure no HTML is in the text itself
        message_text = str(message.get('text', '')).strip()
        # Remove any HTML that might have accidentally gotten into the message
        message_text = re.sub(r'<[^>]+>', '', message_text)
        message_text = html.unescape(message_text)
        
        if message['type'] == 'user':
            # Escape HTML in message text to prevent XSS and display issues
            escaped_text = html.escape(message_text)
            # Replace newlines with <br> for proper line breaks
            formatted_text = escaped_text.replace('\n', '<br>')
            
            # Build HTML string properly
            html_content = (
                '<div class="chat-message user-message" style="animation-delay: ' + str(idx * 0.1) + 's;">'
                '<div><strong>👤 You</strong></div>'
                '<div style="margin-top: 0.5rem; font-size: 15px; line-height: 1.7;">' + formatted_text + '</div>'
                '<div class="timestamp">🕐 ' + html.escape(str(message.get('timestamp', ''))) + '</div>'
                '</div>'
            )
            st.markdown(html_content, unsafe_allow_html=True)
        else:
            urgency_badge = ""
            if message.get('urgency') == 'URGENT':
                urgency_badge = '<div class="urgent-badge">⚠️ URGENT - Immediate Attention Needed</div>'
            
            triage_card = ""
            triage_result = message.get('triage_result')
            if triage_result:
                triage_level = triage_result.get('triage', 'STANDARD')
                action = triage_result.get('action', '')
                score = triage_result.get('score', 0)
                triage_colors = {'IMMEDIATE': '#ef4444', 'VERY_URGENT': '#f97316', 'URGENT': '#eab308', 'STANDARD': '#22c55e'}
                color = triage_colors.get(triage_level, '#64748b')
                triage_card = (f'<div style="background: {color}22; border-left: 4px solid {color}; padding: 1rem; margin: 0.75rem 0; border-radius: 8px;">'
                    f'<div style="font-size: 0.9rem; font-weight: 600;">Triage: {html.escape(triage_level)} (Score: {score})</div>'
                    f'<div style="font-size: 0.85rem; margin-top: 0.25rem;">Action: {html.escape(action)}</div></div>')
            
            # Escape HTML in message text to prevent XSS and display issues
            escaped_text = html.escape(message_text)
            # Replace newlines with <br> for proper line breaks
            formatted_text = escaped_text.replace('\n', '<br>')
            
            # Get language for this message (stored when message was created)
            msg_language = message.get('language', st.session_state.get('detected_language', 'english'))
            
            # Create unique key for speak button
            speak_button_key = f'speak_{idx}_{hash(message_text)}'
            
            # Create columns for message and speak button
            col1, col2 = st.columns([11, 1])
            
            with col1:
                # Build HTML string properly
                html_content = (
                    '<div class="chat-message assistant-message" style="animation-delay: ' + str(idx * 0.1) + 's;">'
                    + urgency_badge + triage_card +
                    '<div><strong>🤖 AI Assistant</strong></div>'
                    '<div style="white-space: pre-wrap; margin-top: 0.5rem; font-size: 15px; line-height: 1.7;">' + formatted_text + '</div>'
                    '<div class="timestamp">🕐 ' + html.escape(str(message.get('timestamp', ''))) + '</div>'
                    '</div>'
                )
                st.markdown(html_content, unsafe_allow_html=True)
            
            with col2:
                # Speak button - compact and styled
                if st.button("🔊", key=speak_button_key, help="Click to hear this message", use_container_width=True):
                    # Generate and play audio
                    with st.spinner("🔊 Playing..."):
                        text_to_speech(message_text, msg_language, play_audio=True)

# Input area
st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)

# Use a form to handle input submission properly and prevent infinite loops
with st.form(key='chat_form', clear_on_submit=True):
    col1, col2 = st.columns([5, 1.2], gap="medium")
    
    with col1:
        # Check if we have pending voice input
        if 'pending_voice_input' in st.session_state and st.session_state.pending_voice_input:
            voice_text = st.session_state.pending_voice_input
            del st.session_state.pending_voice_input
            user_input = st.text_input(
                "Type your message here / اپنا پیغام یہاں لکھیں",
                value=voice_text,
                placeholder="💬 e.g., Mujhe bukhar aur sar dard hai...",
                key=f'user_input_{st.session_state.input_key}',
                label_visibility='collapsed'
            )
        else:
            user_input = st.text_input(
                "Type your message here / اپنا پیغام یہاں لکھیں",
                placeholder="💬 e.g., Mujhe bukhar aur sar dard hai...",
                key=f'user_input_{st.session_state.input_key}',
                label_visibility='collapsed'
            )
    
    with col2:
        submit_button = st.form_submit_button("📤 Send", use_container_width=True)

# Voice button outside form
col1, col2, col3 = st.columns([4, 1.2, 4.8], gap="medium")
with col2:
    voice_button = st.button(
        "🎤 Voice",
        use_container_width=True,
        type="secondary",
        disabled=not VOICE_INPUT_ENABLED,
        help=None if VOICE_INPUT_ENABLED else "Voice input is disabled for cloud deployment."
    )

# Handle voice input - automatically send after transcription
if voice_button:
    # Use detected language or default to english
    current_lang = st.session_state.get('detected_language', 'english')
    with st.spinner("🎤 Listening... Please speak clearly"):
        speech_code = LANGUAGE_CONFIG[current_lang]['speech_code']
        transcribed_text = record_audio(language=speech_code, duration=recording_duration)
        
        if transcribed_text and transcribed_text.strip():
            # Automatically process and send the voice input
            processed_text = transcribed_text.strip()
            
            # Check if we haven't already processed this
            if processed_text != st.session_state.last_processed_input:
                st.session_state.last_processed_input = processed_text
                st.session_state.input_key += 1
                
                # Auto-detect language from user input
                detected_lang = auto_detect_language(processed_text)
                st.session_state.detected_language = detected_lang
                
                # Add user message
                st.session_state.messages.append({
                    'type': 'user',
                    'text': processed_text,
                    'timestamp': datetime.now().strftime('%I:%M %p'),
                    'language': detected_lang
                })
                
                # Process input and get response
                with st.spinner("🤔 Analyzing your symptoms and preparing response..."):
                    # Detect and translate input if needed
                    processed_input = detect_and_translate_input(processed_text, detected_lang)
                    
                    # Send to backend with detected language
                    backend_response = send_to_backend(
                        processed_input,
                        detected_lang,
                        st.session_state.messages,
                        st.session_state.backend_session_state,
                    )
                    
                    if backend_response:
                        if "session_state" in backend_response:
                            st.session_state.backend_session_state = backend_response["session_state"]
                        # Add assistant response - ensure text is clean and doesn't contain HTML
                        response_text = str(backend_response['response_text']).strip()
                        # Aggressively remove ALL HTML tags and entities
                        response_text = re.sub(r'<[^>]+>', '', response_text)  # Remove all HTML tags
                        response_text = html.unescape(response_text)  # Decode HTML entities
                        response_text = response_text.strip()
                        
                        # Make absolutely sure it's not the initial welcome message
                        initial_message_keywords = ['السلام علیکم', 'Assalam o Alaikum', 'Hello! I am here to help']
                        if any(keyword in response_text for keyword in initial_message_keywords) and len(response_text) < 250:
                            # Generate a fresh generic response instead
                            if selected_language == 'urdu':
                                response_text = "شکریہ۔ میں آپ کی مدد کرنے کے لیے تیار ہوں۔ براہ کرم اپنی علامات کے بارے میں مزید بتائیں۔\n\nShukriya. Main aap ki madad karne ke liye tayar hoon. Baraye karam apni alamat ke bare mein mazeed bataein.\n\nThank you. I'm here to help. Please tell me more about your symptoms."
                            elif selected_language == 'punjabi':
                                response_text = "ਧੰਨਵਾਦ। ਮੈਂ ਤੁਹਾਡੀ ਮਦਦ ਕਰਨ ਲਈ ਤਿਆਰ ਹਾਂ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਲੱਛਣਾਂ ਬਾਰੇ ਹੋਰ ਦੱਸੋ।\n\nDhanvaad. Main tuhadi madad karan lai tiyar haan. Kirpa karke apne lakshanan bare hor daso.\n\nThank you. I'm here to help. Please tell me more about your symptoms."
                            else:
                                response_text = "Thank you. I'm here to help. Please tell me more about your symptoms. What are you experiencing?"
                        
                        msg = {
                            'type': 'assistant',
                            'text': response_text,
                            'timestamp': datetime.now().strftime('%I:%M %p'),
                            'urgency': backend_response.get('urgency_level', 'NORMAL'),
                            'language': detected_lang,
                        }
                        if backend_response.get('triage_result'):
                            msg['triage_result'] = backend_response['triage_result']
                        st.session_state.messages.append(msg)
                        
                        # Play audio if enabled
                        if st.session_state.audio_enabled:
                            with st.spinner("🔊 Generating audio response..."):
                                text_to_speech(
                                    response_text,
                                    detected_lang,
                                    play_audio=True
                                )
                
                st.success(f"✅ **Voice message sent!**")
                st.rerun()
            else:
                st.info("Message already processed.")
                st.rerun()

# Handle text input - prevent infinite loop by checking if we've already processed this input
if submit_button and user_input and user_input.strip() and user_input != st.session_state.last_processed_input:
    # Store the input we're about to process
    st.session_state.last_processed_input = user_input.strip()
    st.session_state.input_key += 1  # Increment to clear input on next render
    
    # Auto-detect language from user input
    detected_lang = auto_detect_language(user_input.strip())
    st.session_state.detected_language = detected_lang
    
    # Add user message
    st.session_state.messages.append({
        'type': 'user',
        'text': user_input.strip(),
        'timestamp': datetime.now().strftime('%I:%M %p'),
        'language': detected_lang
    })
    
    # Process input and get response
    with st.spinner("🤔 Analyzing your symptoms and preparing response..."):
        # Detect and translate input if needed
        processed_input = detect_and_translate_input(user_input.strip(), detected_lang)
        
        # Send to backend with detected language
        backend_response = send_to_backend(
            processed_input,
            detected_lang,
            st.session_state.messages,
            st.session_state.backend_session_state,
        )
        
        if backend_response:
            if "session_state" in backend_response:
                st.session_state.backend_session_state = backend_response["session_state"]
            # Add assistant response - ensure text is clean and doesn't contain HTML
            response_text = str(backend_response['response_text']).strip()
            # Aggressively remove ALL HTML tags and entities
            response_text = re.sub(r'<[^>]+>', '', response_text)  # Remove all HTML tags
            response_text = html.unescape(response_text)  # Decode HTML entities
            response_text = response_text.strip()
            
            # Make absolutely sure it's not the initial welcome message
            initial_message_keywords = ['السلام علیکم', 'Assalam o Alaikum', 'Hello! I am here to help']
            if any(keyword in response_text for keyword in initial_message_keywords) and len(response_text) < 250:
                # Generate a fresh generic response instead
                if selected_language == 'urdu':
                    response_text = "شکریہ۔ میں آپ کی مدد کرنے کے لیے تیار ہوں۔ براہ کرم اپنی علامات کے بارے میں مزید بتائیں۔\n\nShukriya. Main aap ki madad karne ke liye tayar hoon. Baraye karam apni alamat ke bare mein mazeed bataein.\n\nThank you. I'm here to help. Please tell me more about your symptoms."
                elif selected_language == 'punjabi':
                    response_text = "ਧੰਨਵਾਦ। ਮੈਂ ਤੁਹਾਡੀ ਮਦਦ ਕਰਨ ਲਈ ਤਿਆਰ ਹਾਂ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਲੱਛਣਾਂ ਬਾਰੇ ਹੋਰ ਦੱਸੋ।\n\nDhanvaad. Main tuhadi madad karan lai tiyar haan. Kirpa karke apne lakshanan bare hor daso.\n\nThank you. I'm here to help. Please tell me more about your symptoms."
                else:
                    response_text = "Thank you. I'm here to help. Please tell me more about your symptoms. What are you experiencing?"
            
            msg = {
                'type': 'assistant',
                'text': response_text,
                'timestamp': datetime.now().strftime('%I:%M %p'),
                'urgency': backend_response.get('urgency_level', 'NORMAL'),
                'language': detected_lang,
            }
            if backend_response.get('triage_result'):
                msg['triage_result'] = backend_response['triage_result']
            st.session_state.messages.append(msg)
            
            # Play audio if enabled
            if st.session_state.audio_enabled:
                with st.spinner("🔊 Generating audio response..."):
                    text_to_speech(
                        response_text,
                        detected_lang,
                        play_audio=True
                    )
    
    # Rerun to show the new messages (form will clear input automatically)
    st.rerun()

# Footer
st.markdown("<div style='margin: 3rem 0 1rem 0;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); margin-top: 2rem;'>
    <p style='color: rgba(255,255,255,0.9); font-size: 0.95rem; font-weight: 500; margin: 0.5rem 0;'>
        🏥 AI Health Assistant - Agentic Healthcare Challenge 2026
    </p>
    <p style='color: rgba(255,255,255,0.7); font-size: 0.85rem; margin: 0.5rem 0 0 0; line-height: 1.6;'>
        ⚠️ This system is for triage support only. Always consult with healthcare professionals for medical advice.
    </p>
</div>
""", unsafe_allow_html=True)
