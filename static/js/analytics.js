let xpLineChart, xpBarChart;
let xpDataCache = null; // Store the original data for filtering
const username = document.getElementById('analytics-container').getAttribute('data-username');

// Fetch and display server status
fetch('/api/server_status')
  .then(res => res.json())
  .then(data => {
    document.getElementById('server-status').innerHTML = `
      <ul class="list-group bg-dark rounded">
        <li class="list-group-item bg-dark text-light border-secondary">
          <strong>Status:</strong> <span class="${data.server === 'online' ? 'text-success' : 'text-danger'}">${data.server}</span>
        </li>
        <li class="list-group-item bg-dark text-light border-secondary">
          <strong>Message:</strong> ${data.message}
        </li>
        <li class="list-group-item bg-dark text-light border-secondary">
          <strong>Uptime:</strong> ${data.uptime}
        </li>
      </ul>
    `;
  });

// Fetch and display user study stats (total sessions, average XP, recent sessions)
fetch('/api/user_game_stats?username=' + encodeURIComponent(username))
  .then(res => res.json())
  .then(data => {
    // Update stats
    if (data.message) {
      document.getElementById('user-stats').innerHTML = `<span class="text-danger">${data.message}</span>`;
      document.getElementById('no-xp-data').style.display = 'block';
      return;
    }
    document.getElementById('total-sessions').textContent = data.total_sessions ?? 0;
    document.getElementById('average-xp').textContent = data.average_xp ?? 0;

    // Recent sessions
    let recentList = document.getElementById('recent-sessions');
    recentList.innerHTML = '';
    if (data.recent_sessions && data.recent_sessions.length > 0) {
      data.recent_sessions.forEach(function(session, idx) {
        let li = document.createElement('li');
        li.className = "list-group-item bg-dark text-light border-secondary";
        li.innerHTML = `Session ${idx + 1}: ${session.xp} XP | Date: ${session.date || 'N/A'}`;
        recentList.appendChild(li);
      });
    } else {
      let li = document.createElement('li');
      li.className = "list-group-item bg-dark text-light border-secondary";
      li.textContent = "No recent sessions.";
      recentList.appendChild(li);
    }

    // XP chart logic (keep your existing chart/filter code here)
    xpDataCache = data.xp_over_time;
    if (xpDataCache && xpDataCache.dates && xpDataCache.dates.length > 0) {
      renderXPLineChart(xpDataCache);
      renderXPBarChart(xpDataCache);
    } else {
      document.getElementById('no-xp-data').style.display = 'block';
    }
  });

// Fetch and display user study stats (unchanged, but store data)
fetch('/api/user_game_stats?username=' + encodeURIComponent(username))
  .then(res => res.json())
  .then(data => {
    xpDataCache = data.xp_over_time; // Store for filtering
    if (xpDataCache && xpDataCache.dates && xpDataCache.dates.length > 0) {
      renderXPLineChart(xpDataCache);
      renderXPBarChart(xpDataCache);
    } else {
      document.getElementById('no-xp-data').style.display = 'block';
    }
  });

// Filtering logic
function filterXPData(period) {
  if (!xpDataCache) return xpDataCache;
  const now = new Date();
  let filtered = {dates: [], values: []};
  xpDataCache.dates.forEach((dateStr, i) => {
    const date = new Date(dateStr);
    let include = false;
    if (period === 'day') {
      include = date.toDateString() === now.toDateString();
    } else if (period === 'week') {
      const weekAgo = new Date(now);
      weekAgo.setDate(now.getDate() - 6);
      include = date >= weekAgo && date <= now;
    } else if (period === 'month') {
      const monthAgo = new Date(now);
      monthAgo.setDate(now.getDate() - 29);
      include = date >= monthAgo && date <= now;
    }
    if (include) {
      filtered.dates.push(dateStr);
      filtered.values.push(xpDataCache.values[i]);
    }
  });
  return filtered;
}

// Chart rendering functions
function renderXPLineChart(xpData) {
  const ctx = document.getElementById('xpChart').getContext('2d');
  if (xpLineChart) xpLineChart.destroy();
  xpLineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: xpData.dates,
      datasets: [{
        label: 'XP Earned',
        data: xpData.values,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.2)',
        fill: true,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } }
    }
  });
}

function renderXPBarChart(xpData) {
  const ctx = document.getElementById('xpBarChart').getContext('2d');
  if (xpBarChart) xpBarChart.destroy();
  xpBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: xpData.dates,
      datasets: [{
        label: 'XP Earned (Bar)',
        data: xpData.values,
        backgroundColor: 'rgba(59,130,246,0.7)',
        borderColor: '#3b82f6',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } }
    }
  });
}

// Filter button event listeners
document.getElementById('filter-day').onclick = () => {
  const filtered = filterXPData('day');
  renderXPLineChart(filtered);
  renderXPBarChart(filtered);
};
document.getElementById('filter-week').onclick = () => {
  const filtered = filterXPData('week');
  renderXPLineChart(filtered);
  renderXPBarChart(filtered);
};
document.getElementById('filter-month').onclick = () => {
  const filtered = filterXPData('month');
  renderXPLineChart(filtered);
  renderXPBarChart(filtered);
};