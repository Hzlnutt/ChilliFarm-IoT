// IoT Dashboard JavaScript

// API Endpoints
const API_BASE = '/api';
const SENSOR_STATUS_ENDPOINT = `${API_BASE}/status`;
const CONTROL_ENDPOINT = `${API_BASE}/control`;

// Sensor update interval (5 seconds)
const SENSOR_UPDATE_INTERVAL = 5000;

let autoRefresh = true;
let pumpStatus = 'off';
let servoAngle = 90;
let autoMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  console.log('Dashboard loaded');
  loadSensorData();
  setInterval(loadSensorData, SENSOR_UPDATE_INTERVAL);
});

// Load and display sensor data
async function loadSensorData() {
  try {
    const response = await fetch(SENSOR_STATUS_ENDPOINT);
    if (!response.ok) throw new Error('Failed to fetch sensor data');
    
    const data = await response.json();
    displaySensorData(data);
  } catch (error) {
    console.error('Error loading sensor data:', error);
    addLog('❌ Error loading sensor data: ' + error.message, 'error');
  }
}

// Display sensor data in grid
function displaySensorData(data) {
  const container = document.getElementById('sensor-container');
  
  if (Object.keys(data).length === 0) {
    container.innerHTML = '<p class="loading">No sensor data available yet</p>';
    return;
  }

  let html = '';
  for (const [sensorName, sensorData] of Object.entries(data)) {
    html += `
      <div class="sensor-card">
        <div class="sensor-name">${sensorName}</div>
        <div class="sensor-location">📍 ${sensorData.location}</div>
        <div class="sensor-value">${sensorData.value}</div>
        <div class="sensor-unit">${sensorData.unit}</div>
        <div class="sensor-timestamp">
          ${new Date(sensorData.timestamp).toLocaleString('id-ID')}
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
}

// Control Pump
async function controlPump(command) {
  try {
    const response = await fetch(CONTROL_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pump: command })
    });

    if (!response.ok) throw new Error('Failed to send pump command');

    const result = await response.json();
    pumpStatus = command;
    document.getElementById('pump-status').textContent = `Status: Pompa ${command.toUpperCase()}`;
    addLog(`✅ Pompa dikirim: ${command.toUpperCase()}`, 'success');
    console.log('Pump command sent:', result);
  } catch (error) {
    console.error('Error controlling pump:', error);
    document.getElementById('pump-status').textContent = `Status: Error - ${error.message}`;
    addLog(`❌ Error kontrol pompa: ${error.message}`, 'error');
  }
}

// Update servo display
function updateServoDisplay(value) {
  document.getElementById('servo-display').textContent = value + '°';
  servoAngle = parseInt(value);
}

// Control Servo
async function controlServo() {
  try {
    const response = await fetch(CONTROL_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ servo: servoAngle })
    });

    if (!response.ok) throw new Error('Failed to send servo command');

    const result = await response.json();
    document.getElementById('servo-status').textContent = `Status: Servo set to ${servoAngle}°`;
    addLog(`✅ Servo diatur ke ${servoAngle}°`, 'success');
    console.log('Servo command sent:', result);
  } catch (error) {
    console.error('Error controlling servo:', error);
    document.getElementById('servo-status').textContent = `Status: Error - ${error.message}`;
    addLog(`❌ Error kontrol servo: ${error.message}`, 'error');
  }
}

// Toggle Auto Mode
async function toggleAutoMode() {
  const isChecked = document.getElementById('auto-mode-toggle').checked;
  autoMode = isChecked;

  try {
    const response = await fetch(CONTROL_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auto: isChecked })
    });

    if (!response.ok) throw new Error('Failed to toggle auto mode');

    const result = await response.json();
    const status = isChecked ? 'ON' : 'OFF';
    document.getElementById('auto-status').textContent = `Auto Mode: ${status}`;
    addLog(`✅ Mode otomatis: ${status}`, 'success');
    console.log('Auto mode toggled:', result);
  } catch (error) {
    console.error('Error toggling auto mode:', error);
    document.getElementById('auto-status').textContent = `Status: Error - ${error.message}`;
    addLog(`❌ Error toggle auto mode: ${error.message}`, 'error');
    document.getElementById('auto-mode-toggle').checked = !isChecked;
  }
}

// Add log entry
function addLog(message, type = 'info') {
  const logContainer = document.getElementById('log-container');
  const timestamp = new Date().toLocaleTimeString('id-ID');
  const logEntry = document.createElement('p');
  logEntry.className = `log-entry ${type}`;
  logEntry.textContent = `[${timestamp}] ${message}`;
  logContainer.insertBefore(logEntry, logContainer.firstChild);

  // Keep only last 50 entries
  while (logContainer.children.length > 50) {
    logContainer.removeChild(logContainer.lastChild);
  }
}

// Clear log
document.addEventListener('DOMContentLoaded', function() {
  const clearLogBtn = document.getElementById('clear-log-btn');
  if (clearLogBtn) {
    clearLogBtn.addEventListener('click', function() {
      const logContainer = document.getElementById('log-container');
      logContainer.innerHTML = '<p class="log-entry">[Log cleared]</p>';
    });
  }

  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', loadSensorData);
  }
});
