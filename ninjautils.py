import sqlite3

# Database file
DB_FILE = "solar_data_final.db"

# Get connection to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Get the latest data from the livedata table
def get_livedata():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livedata WHERE id = 1")
    data = cursor.fetchone()
    conn.close()
    
    if data:
        return dict(data)
    return None

# Get historical data from mqtt_log table
def get_historical_data(hours=24):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM mqtt_log 
        WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ORDER BY timestamp
    """, (hours,))
    data = cursor.fetchall()
    conn.close()
    
    if data:
        return [dict(row) for row in data]
    return []

