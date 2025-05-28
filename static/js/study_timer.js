console.log("study_timer.js loaded!");

let timerInterval;
let elapsedSeconds = 0;
let running = false;

function sendStudyTimeToServer(seconds) {
  fetch("/log_study_time", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ seconds: seconds }),
  })
    .then(response => response.json())
    .then(data => console.log("Study time logged:", data))
    .catch(error => console.error("Error:", error));
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
}

function logStudyTimerEvent(event) {
  console.log("Logging event to backend:", event);
  fetch('/log_study_timer_event', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
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
  }

  running = savedRunning === '1';
}

document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded");
  const startBtn = document.getElementById('start-btn');
  const pauseBtn = document.getElementById('pause-btn');
  const resetBtn = document.getElementById('reset-btn');
  const saveBtn = document.getElementById('save-btn');  // new save button
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  const timerDiv = document.getElementById('study-timer');

  console.log("Timer elements:", {startBtn, pauseBtn, resetBtn, saveBtn, fullscreenBtn, timerDiv});

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
      updateDisplay();
      updateButtons();
      saveState();
      logStudyTimerEvent('reset');
    };

    saveBtn.onclick = function() {
      if (elapsedSeconds > 0) {
        sendStudyTimeToServer(elapsedSeconds);
        // Optionally reset timer after save
        running = false;
        clearInterval(timerInterval);
        elapsedSeconds = 0;
        updateDisplay();
        updateButtons();
        saveState();
        logStudyTimerEvent('save');
      }
    };

  } else {
    console.error("One or more timer buttons not found in DOM.");
  }

  // Fullscreen logic unchanged...
  if (fullscreenBtn && timerDiv) {
    fullscreenBtn.onclick = function() {
      if (!document.fullscreenElement) {
        timerDiv.requestFullscreen();
        logStudyTimerEvent('fullscreen_enter');
      } else {
        document.exitFullscreen();
        logStudyTimerEvent('fullscreen_exit');
      }
    };

    document.addEventListener('fullscreenchange', function() {
      if (document.fullscreenElement) {
        fullscreenBtn.textContent = "Exit Fullscreen";
      } else {
        fullscreenBtn.textContent = "Fullscreen";
      }
    });
  } else {
    console.warn("Fullscreen button or timerDiv not found.");
  }
});
