from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import json
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
# Make sure this matches your Spring Boot application's address and port
BACKEND_RESULT_API_URL = "http://localhost:8080/analysis-result"


# --- NLP Title Analysis Function (improved) ---
def analyze_title_nlp(title):
    nlp_score = 0.0
    
    # VADER sentiment analysis
    vs = analyzer.polarity_scores(title)
    if abs(vs['compound']) > 0.5:
        nlp_score += abs(vs['compound']) * 0.15  # Reduced from 0.2
    
    # Question marks analysis
    question_mark_count = title.count('?')
    if question_mark_count >= 2: 
        nlp_score += 0.15
    elif question_mark_count == 1 and (vs['neg'] > 0.3 or vs['compound'] < -0.3): 
        nlp_score += 0.1
    
    # Question words analysis
    sentences = sent_tokenize(title)
    if len(sentences) == 1 and title.strip().endswith('?'):
        if "what" in title.lower() or "how" in title.lower() or "why" in title.lower() or "who" in title.lower():
            nlp_score += 0.1
    
    # Enhanced clickbait patterns
    title_upper = title.upper()
    
    # Emotional and hyperbolic words (reduced penalties)
    emotional_hyperbolic_words = ["SHOCKING", "AMAZING", "UNBELIEVABLE", "MUST SEE", "CRAZY", "HEARTBREAKING", 
                                 "ANGRY", "SAD", "HAPPY", "WOW", "INSANE", "EPIC", "MIND-BLOWING", "EXPLODES", 
                                 "DANGER", "WARNING", "IMPOSSIBLE", "NEVER", "ALWAYS", "INSTANT", "BREAKING"]
    for word in emotional_hyperbolic_words:
        if word in title_upper: 
            nlp_score += 0.12  # Reduced from 0.15
    
    # Superlatives (reduced penalties)
    superlatives = ["BEST", "ULTIMATE", "FASTEST", "TOP", "GREATEST", "ONLY", "SECRET", "WORST", 
                   "CHEAPEST", "HIGHEST", "MOST", "LEAST", "FIRST", "LAST"]
    for word in superlatives:
        if word in title_upper: 
            nlp_score += 0.08  # Reduced from 0.1
    
    # Vague phrases (reduced penalties)
    vague_phrases = ["YOU WON'T BELIEVE", "WHAT HAPPENED NEXT", "I TRIED SOMETHING", "THE SHOCKING TRUTH", 
                    "THIS ONE TRICK", "THEY DON'T WANT YOU TO KNOW", "THIS WILL CHANGE YOUR LIFE", 
                    "THE TRUTH REVEALED", "SOMETHING BIG IS HAPPENING", "WHAT IF", "YOU WONT GUESS", 
                    "THE REAL REASON", "THIS IS WHY", "THE SECRET", "HIDDEN TRUTH"]
    for phrase in vague_phrases:
        if phrase in title_upper: 
            nlp_score += 0.18  # Reduced from 0.2
    
    # Command words
    command_words = ["WATCH", "SEE", "CLICK", "DO THIS", "DON'T MISS", "GET THIS", "FIND OUT", "LEARN"]
    for word in command_words:
        if word in title_upper and '!' in title: 
            nlp_score += 0.12  # Reduced from 0.15
    
    # Personal pronouns and engagement
    if "YOU" in title_upper and '?' in title: 
        nlp_score += 0.12  # Reduced from 0.15
    
    # Hashtags and viral indicators (reduced penalty)
    if "#viralvideo" in title.lower() or "#youtubeshorts" in title.lower() or "#trending" in title.lower(): 
        nlp_score += 0.4  # Reduced from 0.6
    
    # Uncertainty patterns
    if re.search(r"(is this real\??)|(you sure\??)|(can you believe\??)", title, re.IGNORECASE): 
        nlp_score += 0.15  # Reduced from 0.2
    
    # Exclamation marks (reduced penalties)
    exclamation_count = title.count('!')
    if exclamation_count >= 2: 
        nlp_score += min(0.12 * exclamation_count, 0.3)  # Reduced from 0.15
    elif exclamation_count == 1: 
        nlp_score += 0.03  # Reduced from 0.05
    
    # Emojis (reduced penalties)
    emoji_regex_pattern = r'(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])'
    emoji_count = len(re.findall(emoji_regex_pattern, title))
    if emoji_count >= 2: 
        nlp_score += min(0.08 * emoji_count, 0.2)  # Reduced from 0.1
    elif emoji_count == 1: 
        nlp_score += 0.03  # Reduced from 0.05
    
    # ALL CAPS analysis (reduced penalties)
    upper_case_count = sum(1 for c in title if c.isupper())
    upper_case_percentage = upper_case_count / len(title) if len(title) > 0 else 0
    if upper_case_percentage > 0.4 and len(title) > 10: 
        nlp_score += 0.15  # Reduced from 0.2
    if title == title.upper() and len(title) > 5: 
        nlp_score += 0.2  # Reduced from 0.3
    
    # Positive indicators for legitimate content
    legitimate_indicators = ["TUTORIAL", "HOW TO", "GUIDE", "REVIEW", "ANALYSIS", "EXPLAINED", 
                           "DISCUSSION", "TALK", "CONVERSATION", "INTERVIEW", "DEMO", "DEMONSTRATION"]
    for indicator in legitimate_indicators:
        if indicator in title_upper:
            nlp_score -= 0.05  # Reduce score for legitimate content
    
    # Cap the score at 1.0 and ensure it doesn't go below 0
    return max(0.0, min(nlp_score, 1.0))

# --- Advanced Image Analysis Function ---
def analyze_thumbnail_image(thumbnail_url):
    image_score = 0.0
    if not thumbnail_url:
        print("  Image Debug: No thumbnail_url provided.")
        return image_score

    print(f"  Image Debug: Analyzing thumbnail URL: {thumbnail_url}")

    # URL-based analysis
    lower_url = thumbnail_url.lower()
    if "shocking" in lower_url or "secret" in lower_url or "unbelievable" in lower_url:
        image_score += 0.1
        print(f"  Image Debug: Added 0.1 for URL keyword match. Current score: {image_score:.2f}")
    
    # Low quality thumbnail indicators
    if "/default.jpg" in lower_url or "/mqdefault.jpg" in lower_url:
        image_score += 0.08
        print(f"  Image Debug: Added 0.08 for low quality default URL. Current score: {image_score:.2f}")

    # Base score for having a visual thumbnail (reduced)
    base_visual_score = 0.02
    image_score += base_visual_score
    print(f"  Image Debug: Added {base_visual_score} for thumbnail presence. Current score: {image_score:.2f}")

    # --- Enhanced Image Content Analysis ---
    try:
        # Download the image
        print("  Image Debug: Attempting to download image...")
        response = requests.get(thumbnail_url, stream=True, timeout=5)
        response.raise_for_status()
        print("  Image Debug: Image downloaded successfully.")

        # Open the image using Pillow
        img = Image.open(BytesIO(response.content))
        print(f"  Image Debug: Image opened with Pillow. Mode: {img.mode}, Size: {img.size}")

        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print("  Image Debug: Converted image to RGB.")

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
        print(f"  Image Debug: Error downloading thumbnail {thumbnail_url}: {e}")
    except Image.UnidentifiedImageError:
        print(f"  Image Debug: Could not identify image from URL {thumbnail_url}")
    except Exception as e:
        print(f"  Image Debug: An unexpected error occurred during image processing for {thumbnail_url}: {e}")

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
    total_pixels = 0
    
    for x in range(0, img.width, max(1, img.width // 50)):
        for y in range(0, img.height, max(1, img.height // 50)):
            r, g, b = img.getpixel((x, y))
            total_pixels += 1
            
            # Red (urgency, danger, excitement)
            if r > (g + b) * 1.3:
                red_count += 1
            
            # Yellow (attention, warning, energy)
            if r > 200 and g > 200 and b < 150:
                yellow_count += 1
            
            # Orange (energy, enthusiasm, urgency)
            if r > 200 and g > 100 and g < 200 and b < 100:
                orange_count += 1
            
            # Bright colors (attention-grabbing)
            if (r + g + b) / 3 > 200:
                bright_count += 1
    
    if total_pixels > 0:
        red_ratio = red_count / total_pixels
        yellow_ratio = yellow_count / total_pixels
        orange_ratio = orange_count / total_pixels
        bright_ratio = bright_count / total_pixels
        
        # High red content (urgency indicators)
        if red_ratio > 0.15:
            score += 0.12
            print(f"  Color Analysis: Added 0.12 for high red content ({red_ratio:.2f})")
        
        # High yellow content (attention-grabbing)
        if yellow_ratio > 0.2:
            score += 0.08
            print(f"  Color Analysis: Added 0.08 for high yellow content ({yellow_ratio:.2f})")
        
        # High orange content (energy/urgency)
        if orange_ratio > 0.15:
            score += 0.06
            print(f"  Color Analysis: Added 0.06 for high orange content ({orange_ratio:.2f})")
        
        # Very bright overall (attention-grabbing)
        if bright_ratio > 0.4:
            score += 0.05
            print(f"  Color Analysis: Added 0.05 for very bright image ({bright_ratio:.2f})")
    
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
            print(f"  Text Detection: Added 0.1 for high contrast areas ({contrast_ratio:.2f})")
        
        # Sharp edges (text boundaries)
        if edge_ratio > 0.2:
            score += 0.08
            print(f"  Text Detection: Added 0.08 for sharp edges ({edge_ratio:.2f})")
    
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
            print(f"  Face Detection: Added 0.05 for potential faces ({skin_ratio:.2f})")
            
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
                print(f"  Face Detection: Added 0.03 for bright eye areas ({bright_eye_ratio:.2f})")
    
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
            print(f"  Composition: Added 0.06 for spotlight effect")
    
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
        print(f"  Brightness: Added 0.08 for extreme brightness ({avg_brightness:.2f})")
    
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
        print(f"  Contrast: Added 0.08 for high contrast ({contrast_percentage:.2f})")
    
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
        print(f"  Successfully sent scores for Request ID {request_id} to backend. Title: {title_score:.2f}, Image: {image_score:.2f}")
        print(f"  Backend response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"  Error sending scores for Request ID {request_id} to backend: {e}")


# --- Main Kafka Consumer Logic ---
conf = {
    'bootstrap.servers': 'localhost:9092',
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
                print(f"  Title: \"{title}\"")
                print(f"  Thumbnail URL: {thumbnail_url}")

                # --- Separate Title and Image Analysis ---
                title_score = analyze_title_nlp(title)
                image_score = analyze_thumbnail_image(thumbnail_url)

                print(f"  Title Analysis Score: {title_score:.2f}")
                print(f"  Image Analysis Score: {image_score:.2f}")

                # Send both scores back to Spring Boot
                send_score_to_backend(request_id, title_score, image_score)

            except json.JSONDecodeError:
                print(f"  Could not decode JSON from message value: {msg.value()}")
            except UnicodeDecodeError:
                print(f"  Could not decode message value as UTF-8: {msg.value()}")
            except Exception as e:
                print(f"  An error occurred during processing: {e}")

except KeyboardInterrupt:
    sys.stderr.write('%% Aborted by user\n')
finally:
    consumer.close()