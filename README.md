# 🎯 ClickWorthy - Advanced Clickbait Detection

**ClickWorthy** is a sophisticated browser extension that detects clickbait on YouTube videos using advanced NLP and computer vision techniques. The system analyzes both video titles and thumbnails to provide comprehensive clickbait detection with beautiful, customizable UI.

## ✨ **New Advanced Features**

### 🎨 **Advanced Visual Analysis**
- **Color Psychology Analysis**: Detects emotional manipulation through colors (red for urgency, yellow for attention, orange for energy)
- **Text Overlay Detection**: Identifies potential text overlays on thumbnails using edge detection
- **Facial Expression Analysis**: Basic detection of exaggerated facial expressions
- **Composition Analysis**: Analyzes image composition for spotlight effects and clickbait patterns
- **Brightness & Contrast Analysis**: Detects extreme brightness and high contrast patterns

### 🎭 **Advanced UI/UX**
- **Animated Borders**: Smooth transitions with multiple border styles (solid, dashed, gradient, glow)
- **Responsive Design**: Beautiful hover effects and smooth animations
- **Accessibility**: High contrast modes and customizable sensitivity levels

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   Spring Boot   │    │   Python NLP    │
│   Extension     │───▶│   Backend       │───▶│   Analyzer      │
│                 │    │   (Java)        │    │   (Kafka)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         └──────────────│   Kafka         │    │   Image         │
                        │   Message       │    │   Processing    │
                        │   Queue         │    │   (PIL/NLTK)    │
                        └─────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Java 17 or higher
- Python 3.8 or higher
- Docker and Docker Compose
- Chrome/Chromium browser

### **1. Start Kafka Infrastructure**
```bash
cd clickWorthy-kafkaSetup
docker-compose up -d
```

### **2. Set Up Python Environment**
```bash
cd clickworthy-nlp-analyzer
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### **3. Start Python Analyzer**
```bash
# In the activated virtual environment
python kafka_consumer.py
```

### **4. Start Spring Boot Backend**
```bash
cd clickworthy-backend
./mvnw spring-boot:run
```

### **5. Install Browser Extension**
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `clickworthy-extension` folder
5. The extension will appear in your browser toolbar

## 🎯 **How It Works**

### **1. Content Analysis Pipeline**
1. **Extension Detection**: Monitors YouTube pages for video thumbnails
2. **Data Extraction**: Captures video titles and thumbnail URLs
3. **Backend Processing**: Sends data to Spring Boot backend via REST API
4. **Kafka Messaging**: Backend publishes analysis requests to Kafka
5. **NLP Analysis**: Python consumer processes requests with advanced algorithms
6. **Visual Analysis**: Analyzes thumbnail images using computer vision techniques
7. **Result Delivery**: Scores are sent back to backend and cached
8. **UI Display**: Extension retrieves scores and displays colored borders

### **2. Advanced Visual Analysis**
- **Color Psychology**: Analyzes red, yellow, orange, and bright color ratios
- **Text Detection**: Identifies high-contrast areas and sharp edges
- **Face Analysis**: Basic skin tone detection and expression analysis
- **Composition**: Detects spotlight effects and centered subjects
- **Brightness**: Analyzes extreme brightness and contrast patterns

### **3. Enhanced UI Features**
- **Smart Borders**: Color-coded borders based on clickbait scores
- **Animation Control**: Customizable animation speeds and styles

## 🎨 **UI Customization**

### **Accessing Settings**
- Click the ⚙️ button in the top-right corner of any YouTube page
- Customize theme, animation speed, border style, and sensitivity
- Settings are automatically saved to localStorage

### **Border Styles**
- **Solid**: Clean, simple borders
- **Dashed**: Dashed line borders
- **Gradient**: Beautiful gradient borders
- **Glow**: Animated glow effects

### **Sensitivity Levels**
- **Low**: Less sensitive detection (fewer false positives)
- **Normal**: Balanced detection
- **High**: More sensitive detection (catches more potential clickbait)

## 🔧 **Configuration**

### **Backend Configuration**
Edit `clickworthy-backend/src/main/resources/application.properties`:
```properties
# Kafka Configuration
spring.kafka.bootstrap-servers=localhost:9092
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.apache.kafka.common.serialization.StringSerializer

# Server Configuration
server.port=8080
```

### **Python Analyzer Configuration**
Edit `clickworthy-nlp-analyzer/kafka_consumer.py`:
```python
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
ANALYSIS_REQUEST_TOPIC = 'clickbait-analysis-requests'
ANALYSIS_RESULT_TOPIC = 'clickbait-analysis-results'

# Backend API Configuration
BACKEND_API_URL = 'http://localhost:8080/analysis-result'
```

## 📊 **Score Interpretation**

### **Title Score (0.0 - 1.0)**
- **0.0 - 0.2**: Trustworthy titles
- **0.2 - 0.4**: Slightly suspicious
- **0.4 - 0.6**: Moderately suspicious
- **0.6+**: High clickbait probability

### **Image Score (0.0 - 1.0)**
- **0.0 - 0.2**: Trustworthy thumbnails
- **0.2 - 0.4**: Slightly attention-grabbing
- **0.4 - 0.6**: Moderately manipulative
- **0.6+**: Highly manipulative visuals

### **Overall Score**
- **Green Border**: Trustworthy content
- **Orange Border**: Suspicious content
- **Red Border**: High clickbait probability

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Extension not working**
   - Check if backend is running on port 8080
   - Verify Kafka is running with `docker-compose ps`
   - Check browser console for errors

2. **No analysis results**
   - Ensure Python analyzer is running
   - Check Kafka topics are created
   - Verify network connectivity

3. **Performance issues**
   - Reduce image analysis sampling in Python code
   - Adjust sensitivity settings in extension
   - Check system resources

### **Debug Mode**
Enable debug logging in Python analyzer:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 **Future Enhancements**

- **Machine Learning Integration**: Train models on user feedback
- **Social Features**: Share analysis results with community
- **Advanced Image Recognition**: Use deep learning for better visual analysis
- **Real-time Learning**: Adapt to new clickbait patterns
- **Mobile Support**: iOS and Android extensions

## 📝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ for a better internet experience** 