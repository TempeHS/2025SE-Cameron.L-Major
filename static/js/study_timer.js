console.log("study_timer.js loaded!");

let timerInterval;
let elapsedSeconds = 0;
let running = false;

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

document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded");
  const startBtn = document.getElementById('start-btn');
  const pauseBtn = document.getElementById('pause-btn');
  const resetBtn = document.getElementById('reset-btn');
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  const timerDiv = document.getElementById('study-timer');

  console.log("Timer elements:", {startBtn, pauseBtn, resetBtn, fullscreenBtn, timerDiv});

  if (startBtn && pauseBtn && resetBtn) {
    startBtn.onclick = function() {
      console.log("Start button clicked!");
      if (!running) {
        running = true;
        timerInterval = setInterval(() => {
          elapsedSeconds++;
          console.log("Timer tick:", elapsedSeconds);
          updateDisplay();
        }, 1000);
        pauseBtn.disabled = false;
        resetBtn.disabled = false;
        this.disabled = true;
        logStudyTimerEvent('start');
      }
    };

    pauseBtn.onclick = function() {
      console.log("Pause button clicked!");
      if (running) {
        running = false;
        clearInterval(timerInterval);
        startBtn.disabled = false;
        this.disabled = true;
        logStudyTimerEvent('pause');
      }
    };

    resetBtn.onclick = function() {
      console.log("Reset button clicked!");
      running = false;
      clearInterval(timerInterval);
      elapsedSeconds = 0;
      updateDisplay();
      startBtn.disabled = false;
      pauseBtn.disabled = true;
      this.disabled = true;
      logStudyTimerEvent('reset');
    };

    updateDisplay();
  } else {
    console.error("One or more timer buttons not found in DOM.");
  }

  // Fullscreen logic
  if (fullscreenBtn && timerDiv) {
    fullscreenBtn.onclick = function() {
      console.log("Fullscreen button clicked!");
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
        console.log("Entered fullscreen mode.");
      } else {
        fullscreenBtn.textContent = "Fullscreen";
        console.log("Exited fullscreen mode.");
      }
    });
  } else {
    console.warn("Fullscreen button or timerDiv not found.");
  }
});