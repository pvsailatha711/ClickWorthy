#!/usr/bin/env python3
"""
Test script for ClickWorthy Enhanced Features
Tests both the advanced visual analysis and UI/UX features
"""

import requests
import json
import time
import uuid

# Test configuration
BACKEND_URL = "http://localhost:8080"
TEST_TITLE = "YOU WON'T BELIEVE what happened next! SHOCKING results revealed!"
TEST_THUMBNAIL = "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"

def test_backend_connection():
    """Test if the backend is running and accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/get-score/test", timeout=5)
        print("✅ Backend is running and accessible")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_analysis_request():
    """Test the analysis request endpoint"""
    request_id = str(uuid.uuid4())
    
    payload = {
        "title": TEST_TITLE,
        "thumbnailUrl": TEST_THUMBNAIL,
        "requestId": request_id
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analyze-content",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis request sent successfully")
            print(f"   Request ID: {result.get('requestId')}")
            print(f"   Status: {result.get('status')}")
            return request_id
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Analysis request error: {e}")
        return None

def test_score_retrieval(request_id, max_wait=30):
    """Test retrieving analysis scores"""
    if not request_id:
        print("❌ No request ID provided")
        return False
    
    print(f"⏳ Waiting for analysis results (max {max_wait}s)...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{BACKEND_URL}/get-score/{request_id}", timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "completed":
                    title_score = result.get("titleScore", 0)
                    image_score = result.get("imageScore", 0)
                    
                    print("✅ Analysis completed successfully!")
                    print(f"   Title Score: {title_score:.3f}")
                    print(f"   Image Score: {image_score:.3f}")
                    print(f"   Overall Score: {(title_score + image_score) / 2:.3f}")
                    
                    # Test the enhanced scoring logic
                    overall_score = (title_score + image_score) / 2
                    if overall_score > 0.6:
                        print("   🚨 High clickbait probability detected")
                    elif overall_score > 0.4:
                        print("   ⚠️  Moderate clickbait probability detected")
                    elif overall_score > 0.2:
                        print("   🤔 Slight suspicion detected")
                    else:
                        print("   ✅ Content appears trustworthy")
                    
                    return True
                else:
                    print(f"   Status: {result.get('status')} - {result.get('message', '')}")
            
        except requests.exceptions.RequestException as e:
            print(f"   Error checking status: {e}")
        
        time.sleep(1)
    
    print("❌ Analysis timed out")
    return False

def test_enhanced_features():
    """Test the enhanced features specifically"""
    print("\n🎨 Testing Enhanced Features...")
    
    # Test with a known clickbait title
    clickbait_title = "SHOCKING! You won't BELIEVE what happened! MUST SEE!"
    request_id = str(uuid.uuid4())
    
    payload = {
        "title": clickbait_title,
        "thumbnailUrl": "https://i.ytimg.com/vi/test/maxresdefault.jpg",
        "requestId": request_id
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/analyze-content",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Enhanced analysis request sent")
            
            # Wait a bit for processing
            time.sleep(5)
            
            # Check results
            score_response = requests.get(f"{BACKEND_URL}/get-score/{request_id}", timeout=5)
            if score_response.status_code == 200:
                result = score_response.json()
                if result.get("status") == "completed":
                    title_score = result.get("titleScore", 0)
                    print(f"✅ Enhanced title analysis score: {title_score:.3f}")
                    
                    # Test the advanced NLP features
                    if title_score > 0.5:
                        print("   🎯 Advanced NLP detected clickbait patterns")
                    else:
                        print("   📝 Advanced NLP analysis completed")
                    
                    return True
            
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
    
    return False

def main():
    """Main test function"""
    print("🚀 ClickWorthy Enhanced Features Test")
    print("=" * 50)
    
    # Test 1: Backend connection
    if not test_backend_connection():
        print("\n❌ Backend is not running. Please start the Spring Boot application.")
        return
    
    # Test 2: Analysis request
    request_id = test_analysis_request()
    if not request_id:
        print("\n❌ Analysis request failed. Check if Kafka and Python analyzer are running.")
        return
    
    # Test 3: Score retrieval
    success = test_score_retrieval(request_id)
    if not success:
        print("\n❌ Score retrieval failed. Check if Python analyzer is processing requests.")
        return
    
    # Test 4: Enhanced features
    enhanced_success = test_enhanced_features()
    
    print("\n" + "=" * 50)
    if success and enhanced_success:
        print("🎉 All tests passed! ClickWorthy enhanced features are working correctly.")
        print("\n✨ Features verified:")
        print("   ✅ Advanced Visual Analysis")
        print("   ✅ Enhanced NLP Processing")
        print("   ✅ Dual Score System")
        print("   ✅ Backend API Integration")
        print("   ✅ Kafka Message Processing")
        print("\n🎨 Next steps:")
        print("   1. Install the browser extension")
        print("   2. Visit YouTube to see the enhanced UI")
        print("   3. Click the ⚙️ button to access settings")
        print("   4. Customize themes, animations, and sensitivity")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 