import machine
import utime
from umqtt.simple import MQTTClient
from machine import Pin
import network

# WiFi credentials
wifi_ssid = "BTWholeHome-SK2"
wifi_password = "Neq4NJHG43HW"

# MQTT broker configuration
mqtt_server = "192.168.0.37"
mqtt_port = 1883
mqtt_username = "abc"
mqtt_password = "1234"

# LED pin
LED_PIN = 15

# Initialize LED pin
led = Pin(LED_PIN, Pin.OUT)

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            pass
    print("Connected to WiFi:", wlan.ifconfig())
    return wlan

# Function to turn on LED
def turn_on_led():
    led.value(1)  # Turn on LED

# Function to turn off LED
def turn_off_led():
    led.value(0)  # Turn off LED

# Function to control LED based on message received
def sub_cb(topic, msg):
    print("Received message on topic:", topic)
    print("Message:", msg)
    turn_on_led()
    global last_msg_time
    last_msg_time = utime.ticks_ms()  # Update last message time

# Connect to WiFi
wlan = connect_wifi()

# Initialize MQTT client
try:
    client = MQTTClient("pico", mqtt_server, port=mqtt_port, user=mqtt_username, password=mqtt_password)
    client.connect()
except Exception as e:
    print("Error connecting to MQTT broker:", e)
    machine.reset()

# Subscribe to all topics
try:
    client.set_callback(sub_cb)
    client.subscribe(b"#")  # Subscribe to all topics
except Exception as e:
    print("Error subscribing to MQTT topics:", e)
    machine.reset()

# Initialize last message time
last_msg_time = utime.ticks_ms()

# Main loop
while True:
    try:
        client.wait_msg()

        # Check if no message received for 2 seconds
        if utime.ticks_diff(utime.ticks_ms(), last_msg_time) > 2000:
            turn_off_led()
            last_msg_time = utime.ticks_ms()  # Update last message time when turning off LED
    except Exception as e:
        print("Error in main loop:", e)
        machine.reset()

