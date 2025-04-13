from flask import Flask, render_template_string, jsonify
import time
from ninjautils import get_livedata

app = Flask(__name__)

# HTML template with embedded JavaScript for auto-refresh
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PV Ninja - Live Solar Data</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .dashboard {
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-top: 20px;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .data-label {
            font-weight: bold;
            color: #7f8c8d;
        }
        .data-value {
            font-weight: bold;
            color: #2c3e50;
        }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }
        .unit {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .refresh-indicator {
            position: fixed;
            top: 10px;
            right: 10px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #2ecc71;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }
        .warning {
            display: inline-block;
            background-color: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: 10px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="refresh-indicator" id="refresh-indicator"></div>
    <h1>PV Ninja Live Data</h1>
    
    <div class="dashboard" id="dashboard">
        <div class="data-row">
            <span class="data-label">Inverter Mode:</span>
            <span class="data-value" id="inverter_mode">Loading...</span>
        </div>
        <div class="data-row">
            <span class="data-label">Battery SoC:</span>
            <span class="data-value" id="battery_soc">Loading...</span>
            <span class="unit">%</span>
        </div>
        <div class="data-row">
            <span class="data-label">Solar Production:</span>
            <span class="data-value" id="solar_production">Loading...</span>
            <span class="unit">W</span>
        </div>
        <div class="data-row">
            <span class="data-label">Potential Production:</span>
            <span class="data-value" id="potential_production">Loading...</span>
            <span class="unit">W</span>
        </div>
        <div class="data-row">
            <span class="data-label">Load Power:</span>
            <span class="data-value" id="load_power">Loading...</span>
            <span class="unit">W</span>
        </div>
        <div class="data-row">
            <span class="data-label">Battery Power:</span>
            <span class="data-value" id="battery_power">Loading...</span>
            <span class="unit">W</span>
        </div>
        <div class="data-row">
            <span class="data-label">Grid Power:</span>
            <span class="data-value" id="grid_power">Loading...</span>
            <span class="unit">W</span>
        </div>
        <div class="data-row">
            <span class="data-label">Export Limit:</span>
            <span class="data-value" id="export_limit">Loading...</span>
            <span class="unit">%</span>
        </div>
        <div class="data-row">
            <span class="data-label">Solar Surplus:</span>
            <span class="data-value" id="solar_surplus">Loading...</span>
            <span class="unit">W</span>
        </div>
        <div class="data-row">
            <span class="data-label">Recommended Export Limit:</span>
            <span class="data-value" id="recommended_export_limit">Loading...</span>
            <span class="unit">%</span>
        </div>
    </div>
    
    <div class="timestamp" id="timestamp">Last updated: Loading...</div>

    <script>
        function formatNumber(value) {
            if (value === null) return "N/A";
            return parseFloat(value).toFixed(1);
        }
        
        function updateData() {
            fetch('/api/livedata')
                .then(response => response.json())
                .then(data => {
                    if (data) {
                        document.getElementById('inverter_mode').textContent = data.inverter_mode || 'N/A';
                        document.getElementById('battery_soc').textContent = formatNumber(data.battery_soc);
                        document.getElementById('solar_production').textContent = formatNumber(data.solar_production);
                        document.getElementById('potential_production').textContent = formatNumber(data.potential_production);
                        document.getElementById('load_power').textContent = formatNumber(data.load_power);
                        document.getElementById('battery_power').textContent = formatNumber(data.battery_power);
                        document.getElementById('grid_power').textContent = formatNumber(data.grid_power);
                        document.getElementById('export_limit').textContent = formatNumber(data.export_limit);
                        document.getElementById('solar_surplus').textContent = formatNumber(data.solar_surplus);
                        document.getElementById('recommended_export_limit').textContent = formatNumber(data.recommended_export_limit);
                        
                        const interfaceTime = new Date().toLocaleTimeString();
                        const interfaceDate = new Date();
                        let dataTime = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'Unknown';
                        let dataDate = data.timestamp ? new Date(data.timestamp) : null;
                        
                        // Some SQLite timestamps might need formatting
                        if (data.timestamp && typeof data.timestamp === 'string' && data.timestamp.includes('T')) {
                            dataTime = data.timestamp.split('T')[1].split('.')[0];
                            dataDate = new Date(data.timestamp);
                        }
                        
                        let timestampHTML = `Interface: ${interfaceTime} | Data: ${dataTime}`;
                        
                        // Check if timestamps are more than 3 minutes apart
                        if (dataDate && interfaceDate) {
                            const timeDifference = Math.abs(interfaceDate - dataDate) / 60000; // difference in minutes
                            if (timeDifference > 3) {
                                timestampHTML += `<span class="warning">Old Data - Something might be wrong</span>`;
                            }
                        }
                        
                        document.getElementById('timestamp').innerHTML = timestampHTML;
                        
                        // Blink the refresh indicator
                        const indicator = document.getElementById('refresh-indicator');
                        indicator.style.backgroundColor = '#2ecc71';
                        setTimeout(() => {
                            indicator.style.backgroundColor = 'transparent';
                        }, 500);
                    }
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
        
        // Update data immediately on load
        updateData();
        
        // Then update every 3 seconds
        setInterval(updateData, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/livedata')
def api_livedata():
    data = get_livedata()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

