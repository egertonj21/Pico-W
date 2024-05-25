import mysql.connector
import paho.mqtt.client as mqtt
import pygame
import signal
import sys

# MQTT Settings
MQTT_BROKER = "192.168.0.87"
MQTT_PORT = 1883
MQTT_TOPICS = ["ultrasonic/distance_sensor1", "ultrasonic/distance_sensor2", "ultrasonic/distance_sensor3"]

# MariaDB Settings
DB_HOST = "localhost"
DB_USER = "new_user"
DB_PASSWORD = "user_password"
DB_NAME = "mydatabase"
TABLE_NAME = "distance_log"

# Initialize pygame mixer for playing sound
pygame.mixer.init()

# Load the sound files for each sensor
sound_files = {
    'low': {
        'distance_sensor1': "pianoA.wav",
        'distance_sensor2': "pianoD.wav",
        'distance_sensor3': "pianoG.wav"
    },
    'medium': {
        'distance_sensor1': "pianoB.wav",
        'distance_sensor2': "pianoE.wav",
        'distance_sensor3': "pianoA.wav"
    },
    'high': {
        'distance_sensor1': "pianoC.wav",
        'distance_sensor2': "pianoF.wav",
        'distance_sensor3': "pianoB.wav"
    }
}

# Callback function to handle MQTT messages
def on_message(client, userdata, message):
    # Get the topic and convert the received message payload (distance) to float
    topic = message.topic
    distance = float(message.payload.decode())

    try:
        # Connect to the MariaDB database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Check if the connection was successful
        if conn.is_connected():
            print("Connected to MariaDB")

            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()

            # Extract sensor ID from topic
            sensor_id = topic.split("/")[-1]

            # Insert the received distance and sensor ID into the table
            sql = f"INSERT INTO {TABLE_NAME} (sensor_id, distance) VALUES (%s, %s)"
            cursor.execute(sql, (sensor_id, distance))

            # Commit the transaction
            conn.commit()

            print(f"Distance logged successfully for sensor {sensor_id}: {distance}")

            # Play the appropriate sound based on the distance and sensor
            sound_file = sound_files['low'][sensor_id] if distance < 10 \
                else sound_files['medium'][sensor_id] if 10 <= distance < 20 \
                else sound_files['high'][sensor_id]

            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()

        # Close the connection
        conn.close()

    except mysql.connector.Error as err:
        print("Error:", err)

# Create MQTT client instance
client = mqtt.Client()
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT)

# Subscribe to all MQTT topics
for topic in MQTT_TOPICS:
    client.subscribe(topic)

# Function to handle graceful shutdown
def signal_handler(sig, frame):
    print("Exiting gracefully...")
    client.disconnect()
    pygame.quit()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Start the MQTT loop to handle incoming messages
client.loop_forever()
