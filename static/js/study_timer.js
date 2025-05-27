let timerInterval;
let elapsedSeconds = 0;
let running = false;

function updateDisplay() {
  const hours = String(Math.floor(elapsedSeconds / 3600)).padStart(2, '0');
  const minutes = String(Math.floor((elapsedSeconds % 3600) / 60)).padStart(2, '0');
  const seconds = String(elapsedSeconds % 60).padStart(2, '0');
  document.getElementById('timer-display').textContent = `${hours}:${minutes}:${seconds}`;
}

document.addEventListener('DOMContentLoaded', function() {
  if (
    document.getElementById('start-btn') &&
    document.getElementById('pause-btn') &&
    document.getElementById('reset-btn')
  ) {
    document.getElementById('start-btn').onclick = function() {
      if (!running) {
        running = true;
        timerInterval = setInterval(() => {
          elapsedSeconds++;
          updateDisplay();
        }, 1000);
        document.getElementById('pause-btn').disabled = false;
        document.getElementById('reset-btn').disabled = false;
        this.disabled = true;
      }
    };

    document.getElementById('pause-btn').onclick = function() {
      if (running) {
        running = false;
        clearInterval(timerInterval);
        document.getElementById('start-btn').disabled = false;
        this.disabled = true;
      }
    };

    document.getElementById('reset-btn').onclick = function() {
      running = false;
      clearInterval(timerInterval);
      elapsedSeconds = 0;
      updateDisplay();
      document.getElementById('start-btn').disabled = false;
      document.getElementById('pause-btn').disabled = true;
      this.disabled = true;
    };

    updateDisplay();
  }
});