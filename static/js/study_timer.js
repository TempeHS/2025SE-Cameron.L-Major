console.log("study_timer.js loaded!");

let timerInterval;
let elapsedSeconds = 0;
let running = false;
window.elapsedSeconds = elapsedSeconds; // Ensure global for progress bar

// --- CSRF TOKEN HELPER ---
function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

function sendStudyTimeToServer(seconds) {
  fetch("/log_study_time", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({ seconds: seconds }),
  })
    .then(response => response.json())
    .then(data => {
      console.log("Study time logged:", data);
      if (data.new_achievements && data.new_achievements.length > 0) {
        data.new_achievements.forEach(name => showAchievementNotification(name));
      }
    })
    .catch(error => console.error("Error:", error));
}

// Simple notification 
function showAchievementNotification(name) {
  const notif = document.createElement('div');
  notif.className = 'alert alert-success position-fixed top-0 end-0 m-4';
  notif.style.zIndex = 9999;
  notif.innerHTML = `<strong>Achievement Unlocked!</strong> ${name}`;
  document.body.appendChild(notif);
  setTimeout(() => notif.remove(), 4000);
}

function updateDisplay() {
  const hours = String(Math.floor(elapsedSeconds / 3600)).padStart(2, '0');
  const minutes = String(Math.floor((elapsedSeconds % 3600) / 60)).padStart(2, '0');
  const seconds = String(elapsedSeconds % 60).padStart(2, '0');
  const display = document.getElementById('timer-display');
  if (display) {
    display.textContent = `${hours}:${minutes}:${seconds}`;
    console.log(`Display updated: ${hours}:${minutes}:${seconds}`);
  } else {
    console.error("Timer display element not found!");
  }
  // Sync global for progress bar
  window.elapsedSeconds = elapsedSeconds;
  // Update the progress bar every time the display updates
  if (typeof window.updateProgressBar === "function") {
    window.updateProgressBar();
  }
}

function logStudyTimerEvent(event) {
  console.log("Logging event to backend:", event);
  fetch('/log_study_timer_event', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({event: event})
  })
  .then(res => res.json())
  .then(data => console.log("Backend log response:", data))
  .catch(err => console.error("Failed to log event:", err));
}

// Save state to localStorage
function saveState() {
  localStorage.setItem('studyTimerElapsed', elapsedSeconds);
  localStorage.setItem('studyTimerRunning', running ? '1' : '0');
}

// Load state from localStorage
function loadState() {
  const savedElapsed = localStorage.getItem('studyTimerElapsed');
  const savedRunning = localStorage.getItem('studyTimerRunning');

  if (savedElapsed !== null) {
    elapsedSeconds = parseInt(savedElapsed, 10) || 0;
    window.elapsedSeconds = elapsedSeconds;
  }

  running = savedRunning === '1';
}

// --- Emoji Progress Bar and Motivational Quote Logic ---
window.updateProgressBar = function() {
  const emojiBarElem = document.getElementById('emoji-progress-bar');
  const emojiPercentElem = document.getElementById('emoji-progress-percent');
  const sessionGoalSelect = document.getElementById('session-goal');
  let sessionGoal = parseInt(sessionGoalSelect ? sessionGoalSelect.value : 30, 10);

  const totalBlocks = 10;
  let percent = 0;
  if (window.elapsedSeconds !== undefined && sessionGoal > 0) {
    percent = Math.min(100, (window.elapsedSeconds / (sessionGoal * 60)) * 100);
  }
  const filledBlocks = Math.round((percent / 100) * totalBlocks);
  const emptyBlocks = totalBlocks - filledBlocks;
  const emojiBar = "🟩".repeat(filledBlocks) + "⬜".repeat(emptyBlocks);

  if (emojiBarElem) emojiBarElem.textContent = emojiBar;
  if (emojiPercentElem) emojiPercentElem.textContent = Math.floor(percent) + "%";
};

document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded");
  const startBtn = document.getElementById('start-btn');
  const pauseBtn = document.getElementById('pause-btn');
  const resetBtn = document.getElementById('reset-btn');
  const saveBtn = document.getElementById('save-btn');
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  const timerDiv = document.getElementById('study-timer');
  const bgSelect = document.getElementById('bg-select');

  console.log("Timer elements:", {startBtn, pauseBtn, resetBtn, saveBtn, fullscreenBtn, timerDiv, bgSelect});

  // --- Timer Logic ---
  if (startBtn && pauseBtn && resetBtn && saveBtn) {
    // Load previous state
    loadState();
    updateDisplay();

    // Enable/disable buttons based on state
    function updateButtons() {
      startBtn.disabled = running;
      pauseBtn.disabled = !running;
      resetBtn.disabled = elapsedSeconds === 0;
      saveBtn.disabled = elapsedSeconds === 0;
    }

    if (running) {
      timerInterval = setInterval(() => {
        elapsedSeconds++;
        window.elapsedSeconds = elapsedSeconds;
        updateDisplay();
        saveState();
        updateButtons();
      }, 1000);
    } else {
      updateButtons();
    }

    startBtn.onclick = function() {
      if (!running) {
        running = true;
        timerInterval = setInterval(() => {
          elapsedSeconds++;
          window.elapsedSeconds = elapsedSeconds;
          updateDisplay();
          saveState();
          updateButtons();
        }, 1000);
        updateButtons();
        saveState();
        logStudyTimerEvent('start');
      }
    };

    pauseBtn.onclick = function() {
      if (running) {
        running = false;
        clearInterval(timerInterval);
        updateButtons();
        saveState();
        logStudyTimerEvent('pause');
      }
    };

    resetBtn.onclick = function() {
      running = false;
      clearInterval(timerInterval);
      elapsedSeconds = 0;
      window.elapsedSeconds = elapsedSeconds;
      updateDisplay();
      updateButtons();
      saveState();
      logStudyTimerEvent('reset');
    };

    saveBtn.onclick = function() {
      if (elapsedSeconds > 0) {
        sendStudyTimeToServer(elapsedSeconds);
        running = false;
        clearInterval(timerInterval);
        elapsedSeconds = 0;
        window.elapsedSeconds = elapsedSeconds;
        updateDisplay();
        updateButtons();
        saveState();
        logStudyTimerEvent('save');
      }
    };

  } else {
    console.error("One or more timer buttons not found in DOM.");
  }

  // --- Fullscreen and Background Logic ---
  function setFullscreenBg() {
    if (document.fullscreenElement === timerDiv) {
      timerDiv.style.backgroundImage = `url('/static/images/${bgSelect.value}')`;
      timerDiv.style.backgroundSize = 'cover';
      timerDiv.style.backgroundPosition = 'center';
    }
  }
  function clearFullscreenBg() {
    timerDiv.style.backgroundImage = '';
  }

  if (fullscreenBtn && timerDiv) {
    fullscreenBtn.onclick = function() {
      if (!document.fullscreenElement) {
        timerDiv.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    };

    document.addEventListener('fullscreenchange', function() {
      if (document.fullscreenElement === timerDiv) {
        fullscreenBtn.textContent = "Exit Fullscreen";
        setFullscreenBg();
      } else {
        fullscreenBtn.textContent = "Fullscreen";
        clearFullscreenBg();
      }
    });
  }

  if (bgSelect && timerDiv) {
    bgSelect.addEventListener('change', function() {
      setFullscreenBg();
    });
  }

  // --- Motivational Quotes ---
  const quotes = [
    "Stay focused and never give up!",
    "Small steps every day lead to big results.",
    "You’re closer than you think!",
    "Consistency is the key to success.",
    "Believe in yourself and all that you are."
  ];
  let quoteIdx = 0;
  const quoteElem = document.getElementById('motivational-quote');
  if (quoteElem) {
    setInterval(() => {
      quoteIdx = (quoteIdx + 1) % quotes.length;
      quoteElem.textContent = quotes[quoteIdx];
    }, 30000);
  }

  // Always show the emoji progress bar, even at 0%
  window.updateProgressBar();

  // Update progress bar when session goal changes
  const sessionGoalSelect = document.getElementById('session-goal');
  if (sessionGoalSelect) {
    sessionGoalSelect.addEventListener('change', function() {
      if (typeof window.updateProgressBar === "function") {
        window.updateProgressBar();
      }
    });
  }
});