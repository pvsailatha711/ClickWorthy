from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import json
import os
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import re
import requests # NEW: Import the requests library
from PIL import Image # For image processing
from io import BytesIO # To handle image bytes in memory

# Download VADER lexicon (should already be done)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')
try:
    nltk.data.find('tokenizers/punkt.zip')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# --- Backend API URL to send results to ---
# Reads from environment variable for Docker, defaults to localhost
BACKEND_RESULT_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8080/analysis-result')


# --- NLP Title Analysis Function (improved) ---
def analyze_title_nlp(title):
    nlp_score = 0.0
    
    # VADER sentiment analysis - Increased sensitivity
    vs = analyzer.polarity_scores(title)
    if abs(vs['compound']) > 0.5:
        nlp_score += abs(vs['compound']) * 0.25  # Increased for stronger detection
    
    # Question marks analysis - More aggressive
    question_mark_count = title.count('?')
    if question_mark_count >= 2: 
        nlp_score += 0.25  # Increased
    elif question_mark_count == 1 and (vs['neg'] > 0.3 or vs['compound'] < -0.3): 
        nlp_score += 0.15  # Increased
    
    # Question words analysis - More aggressive
    sentences = sent_tokenize(title)
    if len(sentences) == 1 and title.strip().endswith('?'):
        if "what" in title.lower() or "how" in title.lower() or "why" in title.lower() or "who" in title.lower():
            nlp_score += 0.15  # Increased
    
    # Enhanced clickbait patterns
    title_upper = title.upper()
    title_lower = title.lower()
    
    # Emotional and hyperbolic words - INCREASED penalties
    emotional_hyperbolic_words = ["SHOCKING", "AMAZING", "UNBELIEVABLE", "MUST SEE", "CRAZY", "HEARTBREAKING", 
                                 "ANGRY", "SAD", "HAPPY", "WOW", "INSANE", "EPIC", "MIND-BLOWING", "EXPLODES", 
                                 "DANGER", "WARNING", "IMPOSSIBLE", "NEVER", "ALWAYS", "INSTANT", "BREAKING",
                                 "TERRIFYING", "HORRIFYING", "STUNNING", "INCREDIBLE", "OUTRAGEOUS"]
    for word in emotional_hyperbolic_words:
        if word in title_upper: 
            nlp_score += 0.20  # Significantly increased
    
    # Superlatives - INCREASED penalties
    superlatives = ["BEST", "ULTIMATE", "FASTEST", "TOP", "GREATEST", "ONLY", "SECRET", "WORST", 
                   "CHEAPEST", "HIGHEST", "MOST", "LEAST", "FIRST", "LAST", "BIGGEST", "SMALLEST"]
    for word in superlatives:
        if word in title_upper: 
            nlp_score += 0.15  # Increased
    
    # Vague phrases - INCREASED penalties
    vague_phrases = ["YOU WON'T BELIEVE", "WHAT HAPPENED NEXT", "I TRIED SOMETHING", "THE SHOCKING TRUTH", 
                    "THIS ONE TRICK", "THEY DON'T WANT YOU TO KNOW", "THIS WILL CHANGE YOUR LIFE", 
                    "THE TRUTH REVEALED", "SOMETHING BIG IS HAPPENING", "WHAT IF", "YOU WONT GUESS", 
                    "THE REAL REASON", "THIS IS WHY", "THE SECRET", "HIDDEN TRUTH", "GONE WRONG",
                    "YOU NEED TO SEE", "WAIT FOR IT", "WATCH TILL THE END", "MUST WATCH"]
    for phrase in vague_phrases:
        if phrase in title_upper: 
            nlp_score += 0.30  # Significantly increased
    
    # Command words - More aggressive
    command_words = ["WATCH", "SEE", "CLICK", "DO THIS", "DON'T MISS", "GET THIS", "FIND OUT", "LEARN", "CHECK OUT"]
    for word in command_words:
        if word in title_upper and '!' in title: 
            nlp_score += 0.18  # Increased
    
    # Personal pronouns and engagement - More aggressive
    if "YOU" in title_upper and '?' in title: 
        nlp_score += 0.18  # Increased
    
    # Hashtags and viral indicators - VERY high penalty
    hashtag_count = title.count('#')
    if hashtag_count >= 3:
        nlp_score += 0.40  # High penalty for excessive hashtags
    elif hashtag_count >= 1:
        nlp_score += 0.15 * hashtag_count
    
    if "#viralvideo" in title_lower or "#youtubeshorts" in title_lower or "#trending" in title_lower: 
        nlp_score += 0.35  # Increased
    
    # Uncertainty patterns - More aggressive
    if re.search(r"(is this real\??)|(you sure\??)|(can you believe\??)", title, re.IGNORECASE): 
        nlp_score += 0.25  # Increased
    
    # Exclamation marks - INCREASED penalties
    exclamation_count = title.count('!')
    if exclamation_count >= 2: 
        nlp_score += min(0.20 * exclamation_count, 0.50)  # Significantly increased
    elif exclamation_count == 1: 
        nlp_score += 0.08  # Increased
    
    # Emojis - INCREASED penalties
    emoji_regex_pattern = r'(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])'
    emoji_count = len(re.findall(emoji_regex_pattern, title))
    if emoji_count >= 3: 
        nlp_score += 0.35  # High penalty for excessive emojis
    elif emoji_count >= 2: 
        nlp_score += min(0.15 * emoji_count, 0.30)  # Increased
    elif emoji_count == 1: 
        nlp_score += 0.08  # Increased
    
    # ALL CAPS analysis - INCREASED penalties
    upper_case_count = sum(1 for c in title if c.isupper())
    upper_case_percentage = upper_case_count / len(title) if len(title) > 0 else 0
    if upper_case_percentage > 0.4 and len(title) > 10: 
        nlp_score += 0.25  # Increased
    if title == title.upper() and len(title) > 5: 
        nlp_score += 0.35  # Significantly increased
    
    # Numbers in title (often clickbait)
    if re.search(r'\d+', title):
        # Check for patterns like "10 things", "5 reasons", etc.
        if re.search(r'\d+\s+(things|ways|reasons|secrets|tricks|hacks|tips)', title, re.IGNORECASE):
            nlp_score += 0.20
    
    # Positive indicators for legitimate content - STRONGER reduction
    legitimate_indicators = ["TUTORIAL", "HOW TO", "GUIDE", "REVIEW", "ANALYSIS", "EXPLAINED", 
                           "DISCUSSION", "TALK", "CONVERSATION", "INTERVIEW", "DEMO", "DEMONSTRATION",
                           "DOCUMENTARY", "LECTURE", "COURSE", "LESSON"]
    for indicator in legitimate_indicators:
        if indicator in title_upper:
            nlp_score -= 0.15  # Stronger reduction for legitimate content
    
    # Cap the score at 1.0 and ensure it doesn't go below 0
    return max(0.0, min(nlp_score, 1.0))

# --- Advanced Image Analysis Function ---
def analyze_thumbnail_image(thumbnail_url):
    image_score = 0.0
    if not thumbnail_url:
        return image_score

    # URL-based analysis
    lower_url = thumbnail_url.lower()
    if "shocking" in lower_url or "secret" in lower_url or "unbelievable" in lower_url:
        image_score += 0.1
    
    # Low quality thumbnail indicators
    if "/default.jpg" in lower_url or "/mqdefault.jpg" in lower_url:
        image_score += 0.08

    # Base score for having a visual thumbnail (reduced)
    base_visual_score = 0.02
    image_score += base_visual_score

    # --- Enhanced Image Content Analysis ---
    try:
        # Download the image
        response = requests.get(thumbnail_url, stream=True, timeout=5)
        response.raise_for_status()

        # Open the image using Pillow
        img = Image.open(BytesIO(response.content))

        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # --- Advanced Color Psychology Analysis ---
        image_score += analyze_color_psychology(img)
        
        # --- Text Overlay Detection ---
        image_score += detect_text_overlays(img)
        
        # --- Facial Expression Analysis ---
        image_score += analyze_facial_expressions(img)
        
        # --- Composition Analysis ---
        image_score += analyze_composition(img)
        
        # --- Brightness and Contrast Analysis ---
        image_score += analyze_brightness_contrast(img)

    except requests.exceptions.RequestException as e:
    except Image.UnidentifiedImageError:
    except Exception as e:

    # Cap the score at 1.0
    return min(image_score, 1.0)

def analyze_color_psychology(img):
    """Analyze colors for emotional manipulation patterns"""
    score = 0.0
    
    # Sample pixels for color analysis
    red_count = 0
    yellow_count = 0
    orange_count = 0
    bright_count = 0
    saturated_count = 0
    high_contrast_count = 0
    total_pixels = 0
    
    for x in range(0, img.width, max(1, img.width // 50)):
        for y in range(0, img.height, max(1, img.height // 50)):
            r, g, b = img.getpixel((x, y))
            total_pixels += 1
            
            # Red (urgency, danger, excitement) - MORE AGGRESSIVE
            if r > (g + b) * 1.2:  # Lowered from 1.3
                red_count += 1
            
            # Yellow (attention, warning, energy) - MORE AGGRESSIVE
            if r > 180 and g > 180 and b < 150:  # Lowered from 200
                yellow_count += 1
            
            # Orange (energy, enthusiasm, urgency) - MORE AGGRESSIVE
            if r > 180 and g > 80 and g < 200 and b < 100:  # Lowered from 200
                orange_count += 1
            
            # Bright colors (attention-grabbing) - MORE AGGRESSIVE
            if (r + g + b) / 3 > 180:  # Lowered from 200
                bright_count += 1
            
            # Saturated colors (clickbait indicator)
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            if max_val > 100 and (max_val - min_val) > 100:
                saturated_count += 1
            
            # High contrast (attention-grabbing)
            if max_val > 200 and min_val < 50:
                high_contrast_count += 1
    
    if total_pixels > 0:
        red_ratio = red_count / total_pixels
        yellow_ratio = yellow_count / total_pixels
        orange_ratio = orange_count / total_pixels
        bright_ratio = bright_count / total_pixels
        saturated_ratio = saturated_count / total_pixels
        contrast_ratio = high_contrast_count / total_pixels
        
        # High red content (urgency indicators) - MORE AGGRESSIVE
        if red_ratio > 0.10:  # Lowered from 0.15
            score += 0.15  # Increased from 0.12
")
        
        # High yellow content (attention-grabbing) - MORE AGGRESSIVE
        if yellow_ratio > 0.15:  # Lowered from 0.2
            score += 0.12  # Increased from 0.08
")
        
        # High orange content (energy/urgency) - MORE AGGRESSIVE
        if orange_ratio > 0.10:  # Lowered from 0.15
            score += 0.10  # Increased from 0.06
")
        
        # Very bright overall (attention-grabbing) - MORE AGGRESSIVE
        if bright_ratio > 0.30:  # Lowered from 0.4
            score += 0.08  # Increased from 0.05
")
        
        # High saturation (clickbait indicator) - NEW
        if saturated_ratio > 0.25:
            score += 0.12
")
        
        # High contrast (attention-grabbing) - NEW
        if contrast_ratio > 0.20:
            score += 0.10
")
    
    return score

def detect_text_overlays(img):
    """Detect potential text overlays on thumbnails"""
    score = 0.0
    
    # Analyze edges and contrast for potential text areas
    edge_pixels = 0
    high_contrast_pixels = 0
    total_pixels = 0
    
    for x in range(0, img.width, max(1, img.width // 100)):
        for y in range(0, img.height, max(1, img.height // 100)):
            r, g, b = img.getpixel((x, y))
            total_pixels += 1
            
            # Check for high contrast areas (potential text)
            brightness = (r + g + b) / 3
            if brightness < 50 or brightness > 200:
                high_contrast_pixels += 1
            
            # Check for sharp edges (text boundaries)
            if x > 0 and y > 0:
                prev_r, prev_g, prev_b = img.getpixel((x-1, y-1))
                edge_diff = abs(r - prev_r) + abs(g - prev_g) + abs(b - prev_b)
                if edge_diff > 100:
                    edge_pixels += 1
    
    if total_pixels > 0:
        contrast_ratio = high_contrast_pixels / total_pixels
        edge_ratio = edge_pixels / total_pixels
        
        # High contrast areas (potential text overlays)
        if contrast_ratio > 0.3:
            score += 0.1
")
        
        # Sharp edges (text boundaries)
        if edge_ratio > 0.2:
            score += 0.08
")
    
    return score

def analyze_facial_expressions(img):
    """Analyze facial expressions for exaggerated emotions"""
    score = 0.0
    
    # Simple skin tone detection (basic face detection)
    skin_pixels = 0
    total_pixels = 0
    
    for x in range(0, img.width, max(1, img.width // 100)):
        for y in range(0, img.height, max(1, img.height // 100)):
            r, g, b = img.getpixel((x, y))
            total_pixels += 1
            
            # Basic skin tone detection
            if r > 95 and g > 40 and b > 20 and r > g and r > b:
                if abs(r - g) > 15 and abs(r - b) > 15:
                    skin_pixels += 1
    
    if total_pixels > 0:
        skin_ratio = skin_pixels / total_pixels
        
        # High skin tone content (potential faces)
        if skin_ratio > 0.2:
            score += 0.05
")
            
            # Check for exaggerated expressions (bright eyes, open mouth areas)
            # This is a simplified version - real implementation would use ML
            bright_eye_pixels = 0
            for x in range(0, img.width, max(1, img.width // 200)):
                for y in range(0, img.height, max(1, img.height // 200)):
                    r, g, b = img.getpixel((x, y))
                    if (r + g + b) / 3 > 180:  # Very bright pixels (potential eyes)
                        bright_eye_pixels += 1
            
            bright_eye_ratio = bright_eye_pixels / total_pixels
            if bright_eye_ratio > 0.05:
                score += 0.03
")
    
    return score

def analyze_composition(img):
    """Analyze image composition for clickbait patterns"""
    score = 0.0
    
    # Check for centered, prominent subjects
    center_x, center_y = img.width // 2, img.height // 2
    center_region_brightness = 0
    edge_region_brightness = 0
    center_pixels = 0
    edge_pixels = 0
    
    for x in range(0, img.width, max(1, img.width // 100)):
        for y in range(0, img.height, max(1, img.height // 100)):
            r, g, b = img.getpixel((x, y))
            brightness = (r + g + b) / 3
            
            # Check if pixel is in center region
            center_distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            max_distance = (center_x ** 2 + center_y ** 2) ** 0.5
            
            if center_distance < max_distance * 0.3:  # Center 30% of image
                center_region_brightness += brightness
                center_pixels += 1
            else:
                edge_region_brightness += brightness
                edge_pixels += 1
    
    if center_pixels > 0 and edge_pixels > 0:
        avg_center_brightness = center_region_brightness / center_pixels
        avg_edge_brightness = edge_region_brightness / edge_pixels
        
        # Center is much brighter than edges (spotlight effect)
        if avg_center_brightness > avg_edge_brightness * 1.5:
            score += 0.06
    
    return score

def analyze_brightness_contrast(img):
    """Analyze brightness and contrast patterns"""
    score = 0.0
    
    # Calculate average brightness
    pixels = list(img.getdata())
    avg_brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3)
    
    # Extreme brightness (common in clickbait thumbnails)
    if avg_brightness > 220 or avg_brightness < 30:
        score += 0.08
")
    
    # Check for high contrast (common in clickbait)
    contrast_score = 0
    for x in range(0, img.width, max(1, img.width // 50)):
        for y in range(0, img.height, max(1, img.height // 50)):
            r, g, b = img.getpixel((x, y))
            brightness = (r + g + b) / 3
            if brightness < 30 or brightness > 220:
                contrast_score += 1
    
    contrast_percentage = contrast_score / (img.width * img.height // 2500)
    if contrast_percentage > 0.4:
        score += 0.08
")
    
    return score

# --- Function to send results back to Spring Boot (updated) ---
def send_score_to_backend(request_id, title_score, image_score):
    payload = {
        "requestId": request_id,
        "titleScore": title_score,
        "imageScore": image_score
    }
    try:
        # Send POST request to Spring Boot backend
        response = requests.post(BACKEND_RESULT_API_URL, json=payload)
        response.raise_for_status()
}")
    except requests.exceptions.RequestException as e:


# --- Main Kafka Consumer Logic ---
conf = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'group.id': 'clickbait_analysis_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
topic = 'analysis-requests'

try:
    consumer.subscribe([topic])
    print(f"Python Kafka Consumer subscribed to topic: {topic}")
    print("Waiting for messages... (Press Ctrl+C to stop)")

    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                 (msg.topic(), msg.partition(), msg.offset()))
            else:
                sys.stderr.write('%% Error: %s: %s\n' % (msg.error().code(), msg.error().str()))
        else:
            try:
                message_value = json.loads(msg.value().decode('utf-8'))
                title = message_value.get('title', '')
                thumbnail_url = message_value.get('thumbnailUrl', None)
                request_id = message_value.get('requestId', 'N/A')

                print(f"\nProcessing Request ID: {request_id}")

                # --- Separate Title and Image Analysis ---
                title_score = analyze_title_nlp(title)
                image_score = analyze_thumbnail_image(thumbnail_url)

                # Send both scores back to Spring Boot
                send_score_to_backend(request_id, title_score, image_score)

            except json.JSONDecodeError:
}")
            except UnicodeDecodeError:
}")
            except Exception as e:

except KeyboardInterrupt:
    sys.stderr.write('%% Aborted by user\n')
finally:
    consumer.close()