import mysql.connector
import paho.mqtt.client as mqtt
import pygame
import signal
import sys
import os  # Import the os module
import numpy as np
import pyaudio

import sys

sys.stderr = open(os.devnull, 'w')


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

# PyAudio settings
sample_rate = 44100  # Sample rate in Hz
duration = 1.0       # Duration of each note in seconds

# Define frequencies for notes (e.g., A4, B4, C5, etc.)
note_frequencies = {
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'E5': 659.25,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00,
}

# Dictionary to store the last triggered note frequency for each sensor
last_triggered_frequency = {topic: None for topic in MQTT_TOPICS}

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

            # Map the distance to a frequency range
            frequency = map_distance_to_frequency(distance)

            # Check if the sensor has already triggered a note
            if frequency != last_triggered_frequency[topic]:
                # Generate a sine wave for the frequency
                wave = generate_sine_wave(frequency, duration, sample_rate)

                # Play the wave
                play_wave(wave, sample_rate)

                # Update the last triggered frequency
                last_triggered_frequency[topic] = frequency

        # Close the connection
        conn.close()

    except mysql.connector.Error as err:
        print("Error:", err)

# Function to generate a sine wave for a given frequency and duration
def generate_sine_wave(frequency, duration, sample_rate):
    """Generate a sine wave for a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

# Function to play a wave using PyAudio
def play_wave(wave, sample_rate):
    """Play a wave using PyAudio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    stream.write(wave.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to map distance to frequency
def map_distance_to_frequency(distance):
    # Define the frequency range
    min_frequency = 220  # Minimum frequency
    max_frequency = 880  # Maximum frequency

    # Map distance to frequency range
    frequency = min_frequency + (max_frequency - min_frequency) * (distance / 20.0)

    return frequency

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
