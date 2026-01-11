# ClickWorthy

A real-time clickbait detection system for YouTube that combines Natural Language Processing and Computer Vision to help users identify potentially misleading content.

## Overview

ClickWorthy analyzes YouTube video titles and thumbnails to provide an objective assessment of content quality. The system uses a dual-score approach, examining both textual and visual elements to detect common clickbait patterns.

## Features

- **Dual Analysis System**: Combines NLP for title analysis and computer vision for thumbnail evaluation
- **Real-Time Detection**: Provides instant visual feedback through color-coded borders when hovering over videos
- **Comprehensive Analysis**: Evaluates sentiment, emotional triggers, color psychology, saturation, contrast, and visual composition
- **Non-Intrusive Interface**: Subtle border indicators that don't interfere with the YouTube experience
- **Microservices Architecture**: Scalable design with asynchronous processing using Apache Kafka

## Color Indicators

- Green: Trustworthy content with minimal clickbait characteristics
- Orange: Potentially misleading content with moderate clickbait indicators
- Red: High probability of clickbait based on multiple detection criteria

## Technology Stack

### Frontend
- Chrome Extension (Vanilla JavaScript)
- Real-time DOM observation and mutation handling

### Backend
- Spring Boot (Java 17+)
- RESTful API for content analysis requests
- Apache Kafka for message queuing

### AI/ML Components
- Python 3.8+
- NLTK for natural language processing
- VADER sentiment analysis
- Pillow for image processing

## Architecture

The system follows a microservices architecture:

1. Browser extension captures video metadata (title, thumbnail URL)
2. Spring Boot backend receives requests and publishes to Kafka
3. Python analyzer consumes Kafka messages and performs NLP + CV analysis
4. Results are sent back to the backend via REST API
5. Extension polls for results and applies visual indicators

## Installation

### Prerequisites
- Docker and Docker Compose
- Java 17 or higher
- Python 3.8 or higher
- Chrome/Chromium browser

### Windows Users (Recommended)

1. Run the startup script:
   - **Option 1**: Right-click `start.ps1` and select "Run with PowerShell"
   - **Option 2**: Open PowerShell and run:
   ```powershell
   .\start.ps1
   ```

This script automatically:
- Checks for required prerequisites (Docker, Python, Java)
- Creates Python virtual environment (first time only)
- Starts Kafka and Zookeeper in Docker
- Starts the Python NLP analyzer
- Starts the Spring Boot backend

Three terminal windows will open showing each service running.

2. Install the browser extension:
   - Navigate to chrome://extensions/
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `clickworthy-extension` folder

3. Visit YouTube and hover over video thumbnails to see clickbait indicators

To stop all services, run:
```powershell
.\stop.ps1
```

### macOS/Linux Users

1. Start Kafka:
```bash
cd clickWorthy-kafkaSetup
docker-compose up -d
```

2. Set up Python environment (first time only):
```bash
cd clickworthy-nlp-analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Start Python analyzer:
```bash
cd clickworthy-nlp-analyzer
source venv/bin/activate
python kafka_consumer.py
```

4. Start Spring Boot backend:
```bash
cd clickworthy-backend
./mvnw spring-boot:run
```

5. Install browser extension as described above

## Analysis Methodology

### Title Analysis
- Sentiment analysis using VADER
- Detection of emotional and hyperbolic language
- Identification of clickbait patterns (questions, commands, superlatives)
- Emoji and hashtag density measurement
- ALL CAPS and excessive punctuation detection

### Thumbnail Analysis
- Color psychology (red, yellow, orange detection for urgency indicators)
- Saturation and contrast measurement
- Brightness analysis
- Text overlay detection
- Facial expression analysis
- Composition complexity evaluation

## Configuration

### Backend (application.properties)
- Kafka bootstrap servers
- CORS configuration for YouTube domains
- Producer and consumer settings

### Python Analyzer (kafka_consumer.py)
- Kafka consumer group configuration
- Analysis threshold tuning
- Backend API endpoint

## Scoring System

Scores range from 0.0 to 1.0:
- 0.0 - 0.15: Low clickbait probability (Green)
- 0.15 - 0.35: Moderate clickbait probability (Orange)
- 0.35 - 1.0: High clickbait probability (Red)

The final score is calculated as the average of title and thumbnail scores, weighted equally.

## Development

### Project Structure
```
ClickWorthy/
├── clickworthy-extension/     # Chrome extension
├── clickworthy-backend/        # Spring Boot API
├── clickworthy-nlp-analyzer/   # Python ML service
├── clickWorthy-kafkaSetup/     # Kafka configuration
├── start.ps1                   # Windows startup script
├── stop.ps1                    # Windows shutdown script
└── docker-compose.yml          # Docker orchestration
```

### Testing

The system can be tested by:
1. Visiting YouTube and observing border colors on various video types
2. Checking browser console for analysis logs (development mode)
3. Monitoring Kafka messages and Python analyzer output

## Limitations

- Requires active internet connection for thumbnail analysis
- Analysis accuracy depends on training data and threshold tuning
- Currently supports Chrome/Chromium browsers only
- Image analysis is basic computer vision without deep learning models

## Future Enhancements

- Enhanced thumbnail analysis with deep learning models for better visual pattern recognition
- Machine learning model training on labeled clickbait datasets
- Support for Firefox and Edge browsers
- User feedback system for continuous improvement
- Performance metrics and accuracy tracking
- Caching layer for frequently analyzed content
- Advanced text detection in thumbnails using OCR
- Facial expression analysis using computer vision models

## Contributing

Contributions are welcome. Please ensure code follows existing patterns and includes appropriate documentation.

## Acknowledgments

Built using open-source technologies including Spring Boot, Apache Kafka, NLTK, and Pillow.