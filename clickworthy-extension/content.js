console.log("ClickWorthy content script is running!");

// --- Backend API URL ---
const BACKEND_ANALYZE_API_URL = "http://localhost:8080/analyze-content";
const BACKEND_GET_SCORE_API_URL = "http://localhost:8080/get-score/"; // Will append requestId

// Map to store analysis results received from backend
const cachedScores = new Map(); // Now stores {titleScore: number, imageScore: number}

// --- Advanced CSS with Animations and Themes ---
const advancedStyle = document.createElement('style');
advancedStyle.textContent = `
  /* ClickWorthy Advanced UI Styles */
  .clickworthy-badge {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }
  
  /* Animated Borders */
  .clickworthy-border {
    transition: all 0.3s ease-in-out;
    position: relative;
  }
  
  .clickworthy-border.trustworthy {
    border: 3px solid #4CAF50 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(76, 175, 80, 0.3) !important;
  }
  
  .clickworthy-border.suspicious {
    border: 3px solid #FF9800 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(255, 152, 0, 0.3) !important;
  }
  
  .clickworthy-border.clickbait {
    border: 3px solid #F44336 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(244, 67, 54, 0.3) !important;
  }
  
  /* Gradient Borders */
  .clickworthy-border.gradient-trustworthy {
    border: 3px solid transparent !important;
    background: linear-gradient(45deg, #4CAF50, #45a049) !important;
    background-clip: padding-box !important;
    border-radius: 8px !important;
  }
  
  .clickworthy-border.gradient-suspicious {
    border: 3px solid transparent !important;
    background: linear-gradient(45deg, #FF9800, #FF5722) !important;
    background-clip: padding-box !important;
    border-radius: 8px !important;
  }
  
  .clickworthy-border.gradient-clickbait {
    border: 3px solid transparent !important;
    background: linear-gradient(45deg, #F44336, #D32F2F) !important;
    background-clip: padding-box !important;
    border-radius: 8px !important;
  }
  
  /* Glow Effects */
  .clickworthy-border.glow-trustworthy {
    border: 3px solid #4CAF50 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 20px rgba(76, 175, 80, 0.6) !important;
    animation: glow-green 2s ease-in-out infinite alternate !important;
  }
  
  .clickworthy-border.glow-suspicious {
    border: 3px solid #FF9800 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 20px rgba(255, 152, 0, 0.6) !important;
    animation: glow-orange 2s ease-in-out infinite alternate !important;
  }
  
  .clickworthy-border.glow-clickbait {
    border: 3px solid #F44336 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 20px rgba(244, 67, 54, 0.6) !important;
    animation: glow-red 2s ease-in-out infinite alternate !important;
  }
  
  /* Glow Animations */
  @keyframes glow-green {
    from { box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
    to { box-shadow: 0 0 30px rgba(76, 175, 80, 0.8); }
  }
  
  @keyframes glow-orange {
    from { box-shadow: 0 0 20px rgba(255, 152, 0, 0.6); }
    to { box-shadow: 0 0 30px rgba(255, 152, 0, 0.8); }
  }
  
  @keyframes glow-red {
    from { box-shadow: 0 0 20px rgba(244, 67, 54, 0.6); }
    to { box-shadow: 0 0 30px rgba(244, 67, 54, 0.8); }
  }
  
  /* Settings Panel */
  .clickworthy-settings {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 20px;
    border-radius: 10px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 14px;
    min-width: 250px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    display: none;
  }
  
  .clickworthy-settings h3 {
    margin: 0 0 15px 0;
    color: #4CAF50;
  }
  
  .clickworthy-settings label {
    display: block;
    margin: 10px 0 5px 0;
    font-weight: bold;
  }
  
  .clickworthy-settings select,
  .clickworthy-settings input {
    width: 100%;
    padding: 5px;
    margin-bottom: 10px;
    border: none;
    border-radius: 4px;
    background: #333;
    color: white;
  }
  
  .clickworthy-settings button {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-right: 10px;
  }
  
  .clickworthy-settings button:hover {
    background: #45a049;
  }
  
  /* Settings Toggle Button */
  .clickworthy-settings-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 50%;
    cursor: pointer;
    z-index: 10001;
    font-size: 16px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
  }
  
  .clickworthy-settings-toggle:hover {
    background: #45a049;
    transform: scale(1.1);
  }
  
  /* Dark Theme */
  .clickworthy-dark .clickworthy-settings {
    background: rgba(255, 255, 255, 0.95);
    color: #333;
  }
  
  .clickworthy-dark .clickworthy-settings select,
  .clickworthy-dark .clickworthy-settings input {
    background: #f5f5f5;
    color: #333;
  }
`;
document.head.appendChild(advancedStyle);

// --- Enhanced Hover Effect with Advanced UI ---
function applyHoverEffect(container, scores) {
  // Calculate overall score (average of title and image scores)
  const overallScore = (scores.titleScore + scores.imageScore) / 2;
  
  let borderClass = '';
  let borderColor = '';
  
  if (overallScore === 0) {
    borderClass = 'trustworthy';
    borderColor = '#4CAF50';
  } else if (overallScore > 0 && overallScore <= 0.2) {
    borderClass = 'trustworthy';
    borderColor = '#4CAF50';
  } else if (overallScore > 0.2 && overallScore <= 0.4) {
    borderClass = 'suspicious';
    borderColor = '#FF9800';
  } else if (overallScore > 0.4 && overallScore <= 0.6) {
    borderClass = 'suspicious';
    borderColor = '#FF9800';
  } else if (overallScore > 0.6) {
    borderClass = 'clickbait';
    borderColor = '#F44336';
  }

  // Remove any existing score badges
  const existingBadges = container.querySelectorAll('.clickworthy-badge');
  existingBadges.forEach(badge => badge.remove());

  // Ensure unique handlers are applied to prevent multiple calls
  container.removeEventListener('mouseover', container.__mouseoverHandler__);
  container.removeEventListener('mouseout', container.__mouseoutHandler__);
  container.removeEventListener('mousemove', container.__mousemoveHandler__);

  container.__mouseoverHandler__ = function(e) {
    this.style.border = `3px solid ${borderColor}`;
    this.style.borderRadius = '8px';
    this.classList.add('clickworthy-border', borderClass);
  };
  
  container.__mouseoutHandler__ = function() {
    this.style.border = '';
    this.style.borderRadius = '';
    this.classList.remove('clickworthy-border', 'trustworthy', 'suspicious', 'clickbait');
    
    // Remove tooltip if it exists
    const tooltip = document.getElementById('clickworthy-tooltip');
    if (tooltip) {
      tooltip.remove();
    }
  };
  
  container.__mousemoveHandler__ = function(e) {
    // TOOLTIP DISABLED - No tooltip movement
  };

  container.addEventListener('mouseover', container.__mouseoverHandler__);
  container.addEventListener('mouseout', container.__mouseoutHandler__);
  container.addEventListener('mousemove', container.__mousemoveHandler__);

  // Apply initial border briefly if score is already cached on page load
  const requestId = container.dataset.requestId;
  if (requestId && cachedScores.has(requestId) && cachedScores.get(requestId) !== null) {
      const cachedScoresData = cachedScores.get(requestId);
      const initialOverallScore = (cachedScoresData.titleScore + cachedScoresData.imageScore) / 2;
      let initialBorderColor = '';
      if (initialOverallScore === 0) { initialBorderColor = '#4CAF50'; }
      else if (initialOverallScore > 0 && initialOverallScore <= 0.2) { initialBorderColor = '#4CAF50'; }
      else if (initialOverallScore > 0.2 && initialOverallScore <= 0.4) { initialBorderColor = '#FF9800'; }
      else if (initialOverallScore > 0.4 && initialOverallScore <= 0.6) { initialBorderColor = '#FF9800'; }
      else if (initialOverallScore > 0.6) { initialBorderColor = '#F44336'; }
      
      container.style.border = `3px solid ${initialBorderColor}`;
      container.style.borderRadius = '8px';
      setTimeout(() => {
           container.style.border = '';
           container.style.borderRadius = '';
       }, 2000); // Remove after a short delay
   }
}

// Function to remove any floating score elements
function removeFloatingScores() {
  // Remove any element with the specific tooltip ID
  const tooltip = document.getElementById('clickworthy-tooltip');
  if (tooltip) {
    tooltip.remove();
    console.log('ClickWorthy: Removed clickworthy-tooltip element');
  }
  
  // Remove any div with "ClickWorthy Analysis" text
  const allDivs = document.querySelectorAll('div');
  allDivs.forEach(div => {
    if (div.textContent && div.textContent.includes('ClickWorthy Analysis')) {
      div.remove();
      console.log('ClickWorthy: Removed ClickWorthy Analysis tooltip');
    }
  });
  
  // Remove any element with tooltip-like styling that contains ClickWorthy text
  const tooltipElements = document.querySelectorAll('div[style*="position: absolute"], div[style*="position: fixed"]');
  tooltipElements.forEach(element => {
    if (element.textContent && element.textContent.includes('ClickWorthy')) {
      element.remove();
      console.log('ClickWorthy: Removed positioned ClickWorthy element');
    }
  });
  
  // Remove any element with high z-index that contains ClickWorthy text
  const allElements = document.querySelectorAll('*');
  allElements.forEach(element => {
    const style = window.getComputedStyle(element);
    const zIndex = parseInt(style.zIndex);
    if (zIndex > 1000 && element.textContent && element.textContent.includes('ClickWorthy')) {
      element.remove();
      console.log('ClickWorthy: Removed high z-index ClickWorthy element');
    }
  });
}

// Function to clean up any existing score badges and score-related elements
function cleanupExistingBadges() {
  // Remove badges from all video containers
  const videoContainers = document.querySelectorAll('ytd-rich-item-renderer, ytm-shorts-lockup-view-model-v2');
  videoContainers.forEach(container => {
    const badges = container.querySelectorAll('.clickworthy-badge');
    badges.forEach(badge => badge.remove());
  });
  
  // Remove any badges that might be floating in the body
  const bodyBadges = document.querySelectorAll('.clickworthy-badge');
  bodyBadges.forEach(badge => badge.remove());
  
  // Remove any tooltips that might be stuck
  const tooltips = document.querySelectorAll('#clickworthy-tooltip');
  tooltips.forEach(tooltip => tooltip.remove());
  
  // Remove any elements with specific score-related classes or IDs
  const scoreElements = document.querySelectorAll('[class*="score"], [id*="score"], [class*="clickworthy"], [id*="clickworthy"]');
  scoreElements.forEach(element => {
    if (element.classList.contains('clickworthy-badge') || element.id === 'clickworthy-tooltip') {
      element.remove();
    }
  });
  
  // Call floating scores cleanup
  removeFloatingScores();
  
  console.log(`ClickWorthy: Cleaned up existing elements`);
}

// Immediate cleanup function for stuck tooltips
function removeStuckTooltips() {
  // Remove any div with absolute positioning and ClickWorthy content
  const allDivs = document.querySelectorAll('div');
  allDivs.forEach(div => {
    const style = window.getComputedStyle(div);
    const isPositioned = style.position === 'absolute' || style.position === 'fixed';
    const hasClickworthyContent = div.textContent && div.textContent.includes('ClickWorthy');
    
    if (isPositioned && hasClickworthyContent) {
      div.remove();
      console.log('ClickWorthy: Removed stuck tooltip div');
    }
  });
  
  // Specifically target the "ClickWorthy Analysis" tooltip
  const analysisTooltips = document.querySelectorAll('div');
  analysisTooltips.forEach(div => {
    if (div.textContent && div.textContent.includes('ClickWorthy Analysis')) {
      div.remove();
      console.log('ClickWorthy: Removed ClickWorthy Analysis tooltip');
    }
  });
  
  // Remove any element with the exact tooltip styling
  const tooltipElements = document.querySelectorAll('div[style*="position: absolute"][style*="background: rgba(0, 0, 0, 0.9)"][style*="z-index: 10000"]');
  tooltipElements.forEach(element => {
    element.remove();
    console.log('ClickWorthy: Removed tooltip with specific styling');
  });
}

// Add CSS to hide any badges and score-related elements that might appear
const style = document.createElement('style');
style.textContent = `
  .clickworthy-badge {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }
`;
document.head.appendChild(style);

// Function to specifically remove the ClickWorthy Analysis tooltip
function removeClickworthyTooltip() {
  // Remove by ID
  const tooltipById = document.getElementById('clickworthy-tooltip');
  if (tooltipById) {
    tooltipById.remove();
  }
  
  // Remove by text content
  const allDivs = document.querySelectorAll('div');
  allDivs.forEach(div => {
    if (div.textContent && div.textContent.includes('ClickWorthy Analysis')) {
      div.remove();
    }
  });
  
  // Remove by styling (black background, high z-index)
  const tooltipElements = document.querySelectorAll('div');
  tooltipElements.forEach(div => {
    const style = window.getComputedStyle(div);
    if (style.backgroundColor.includes('rgba(0, 0, 0, 0.9)') && 
        parseInt(style.zIndex) > 1000 && 
        div.textContent && div.textContent.includes('ClickWorthy')) {
      div.remove();
    }
  });
}

// Clean up badges on script start
cleanupExistingBadges();
removeClickworthyTooltip();

// Clean up again after a short delay to catch any that were added during page load
setTimeout(() => {
  cleanupExistingBadges();
  removeClickworthyTooltip();
}, 1000);

setTimeout(() => {
  cleanupExistingBadges();
  removeClickworthyTooltip();
}, 2000);

// Periodically clean up any stray badges (every 2 seconds)
setInterval(() => {
  cleanupExistingBadges();
  removeClickworthyTooltip();
}, 2000);

function sendAnalysisRequest(videoData, containerElement) {
  const requestId = generateUniqueId(); // Generate a unique ID for this request
  videoData.requestId = requestId; // Attach requestId to the data

  // Store a placeholder or pending state for this requestId
  cachedScores.set(requestId, null); // null indicates analysis is pending
  containerElement.dataset.requestId = requestId; // Store requestId on the DOM element

  fetch(BACKEND_ANALYZE_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Origin': 'chrome-extension://fbdemagnbjffdanpndebkpojkmllolho' // IMPORTANT: Your Extension ID
    },
    body: JSON.stringify(videoData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === "received") {
      console.log(`ClickWorthy: Request ${data.requestId} sent to backend. Polling for score...`);
      // Start polling for the score
      pollForScore(data.requestId, containerElement);
    } else {
      console.error(`ClickWorthy: Error sending request to backend for ${videoData.title}:`, data.message);
    }
  })
  .catch(error => console.error(`ClickWorthy: Network error sending request for ${videoData.title}:`, error));
}


function pollForScore(requestId, containerElement) {
  const pollInterval = setInterval(() => {
    fetch(BACKEND_GET_SCORE_API_URL + requestId, {
      method: 'GET',
      headers: {
        'Origin': 'chrome-extension://fbdemagnbjffdanpndebkpojkmllolho' // IMPORTANT: Your Extension ID
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "completed") {
        clearInterval(pollInterval); // Stop polling
        const scores = {
          titleScore: data.titleScore,
          imageScore: data.imageScore
        };
        cachedScores.set(requestId, scores); // Cache the received scores
        console.log(`ClickWorthy: Scores received for Request ID ${requestId}: Title=${data.titleScore}, Image=${data.imageScore}`);
        applyHoverEffect(containerElement, scores); // Apply final color with both scores
      } else if (data.status === "pending") {
        // Keep polling
      } else {
        clearInterval(pollInterval); // Stop polling on error
        console.error(`ClickWorthy: Error polling for score for Request ID ${requestId}:`, data.message);
      }
    })
    .catch(error => {
      clearInterval(pollInterval); // Stop polling on network error
      console.error(`ClickWorthy: Network error polling for score for Request ID ${requestId}:`, error);
    });
  }, 1000); // Poll every 1 second
}

function generateUniqueId() {
  return 'req-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

// This function is now only on the backend (in kafka_consumer.py)
function getClickbaitScore() {
    return 0; // Dummy value, calculation is backend
}


function getVideoTitlesAndAnalyze() {
  // Select both types of video item containers
  const videoItems = document.querySelectorAll('ytd-rich-item-renderer, ytm-shorts-lockup-view-model-v2');

  videoItems.forEach(item => {
    let titleElement;
    let thumbnailUrl = null;
    let containerElement = item; // The element we will apply border to

    // Determine title and thumbnail element based on container type
    if (item.tagName === 'YTD-RICH-ITEM-RENDERER') {
      titleElement = item.querySelector('#video-title');
      // Corrected selector for regular video thumbnails based on your provided HTML
      const imgElement = item.querySelector('a#thumbnail yt-image img.yt-core-image');
      thumbnailUrl = imgElement ? imgElement.src : null;
    } else if (item.tagName === 'YTM-SHORTS-LOCKUP-VIEW-MODEL-V2') {
      titleElement = item.querySelector('h3.shortsLockupViewModelHostMetadataTitle a span[role="text"]');
      // Selector for Shorts thumbnail based on your provided HTML
      const imgElement = item.querySelector('img.shortsLockupViewModelHostThumbnail.yt-core-image');
      thumbnailUrl = imgElement ? imgElement.src : null;
    }

    if (titleElement && titleElement.textContent.trim()) {
      const title = titleElement.textContent.trim();
      const videoId = title; // Simplified video ID for caching; for production use actual YouTube video ID

      // Only process if this video hasn't been processed or is not pending
      if (!cachedScores.has(videoId) || cachedScores.get(videoId) === null) {
        const videoData = { title: title, thumbnailUrl: thumbnailUrl, videoId: videoId }; // Include videoId for caching
        cachedScores.set(videoId, null); // Mark as pending
        sendAnalysisRequest(videoData, containerElement);
      } else if (cachedScores.get(videoId) !== null) {
          // If already analyzed and cached, apply effect directly
          applyHoverEffect(containerElement, cachedScores.get(videoId));
      }
    }
  });
}


function observeDOM() {
  const targetNode = document.querySelector('ytd-app'); // Observe the entire app container
  const config = { childList: true, subtree: true };

  const observer = new MutationObserver(function(mutationsList, observer) {
    let shouldAnalyze = false;
    for (let mutation of mutationsList) {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        const addedVideoContainers = Array.from(mutation.addedNodes).some(node =>
          node.tagName === 'YTD-RICH-ITEM-RENDERER' ||
          node.tagName === 'YTD-RICH-SHELF-RENDERER' || // Still including for completeness if it appears
          node.tagName === 'YTD-GRID-VIDEO-RENDERER' || // Still including for completeness
          node.tagName === 'YTD-SHORT-FORM-VIDEO-RENDERER' || // For dedicated Shorts page (if different from YTM)
          node.tagName === 'YTM-SHORTS-LOCKUP-VIEW-MODEL-V2'
        );
        if (addedVideoContainers) {
          shouldAnalyze = true;
          break;
        }
      }
    }
    if (shouldAnalyze) {
      setTimeout(getVideoTitlesAndAnalyze, 500); // Debounce and re-analyze
    }
  });

  if (targetNode) {
    observer.observe(targetNode, config);
    setTimeout(getVideoTitlesAndAnalyze, 1000); // Initial call after a delay
  }
}

// Start observing the DOM when the script runs
observeDOM();