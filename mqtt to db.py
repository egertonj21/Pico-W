import mysql.connector
import paho.mqtt.client as mqtt

# MQTT Broker Settings
MQTT_BROKER_HOST = "broker.example.com"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "your/mqtt/topic"

# MariaDB Settings
DB_HOST = "localhost"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "your_database"
TABLE_NAME = "users"

# Callback function to handle MQTT messages
def on_message(client, userdata, message):
    payload = message.payload.decode()
    # Process the message and extract relevant data
    # Insert the data into the MariaDB table
    insert_data(payload)

# Function to insert data into the MariaDB table
def insert_data(data):
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    sql = "INSERT INTO {} (data_column) VALUES (%s)".format(TABLE_NAME)
    cursor.execute(sql, (data,))
    conn.commit()
    conn.close()

# Set up the MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
client.subscribe(MQTT_TOPIC)
client.loop_forever()
