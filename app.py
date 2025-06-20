import os
import asyncio
import threading
from functools import wraps
from flask import Flask, request, jsonify
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.credentials import MerossCloudCreds
from meross_iot.meross_factory import MerossManagerFactory
# Also make sure this one is there

# --- Configuration ---
# These are loaded from environment variables.
# On your server, you will set these before running the app.
MEROSS_EMAIL = os.environ.get("MEROSS_EMAIL")
MEROSS_PASSWORD = os.environ.get("MEROSS_PASSWORD")
API_AUTH_TOKEN = os.environ.get("API_AUTH_TOKEN")
LIGHT_NAME = os.environ.get("LIGHT_NAME", "My Smart Light")

# --- Simulation Parameters ---
SUNRISE_DURATION_MINUTES = 30
SUNRISE_START_COLOR = (255, 120, 0)  # Deeper orange for start
CANDLELIGHT_COLOR = (255, 182, 77)   # Warm candlelight for end

app = Flask(__name__)

# A simple flag to prevent multiple sunrise routines from running at once.
is_sunrise_running = False

def token_required(f):
    """Decorator function to secure an endpoint with a bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            # Expected format: "Authorization: Bearer <your-token>"
            token = request.headers["Authorization"].split(" ")[1]

        if not token or token != API_AUTH_TOKEN:
            return jsonify({"error": "Authentication Token is missing or invalid!"}), 401
        
        return f(*args, **kwargs)
    return decorated

# This is the corrected version of the function in app.py

# This is the corrected version of the function in app.py

async def sunrise_simulation_async():
    """
    The core async logic for the 30-minute sunrise simulation.
    This function contains all the Meross-specific interactions.
    """
    global is_sunrise_running
    is_sunrise_running = True
    print("Starting sunrise simulation in background thread...")

    manager = None
    try:
        #
        # --- THIS IS THE CORRECTED CODE BLOCK FOR VERSION 0.4.9.0 ---
        #
        # For this library version, we must use the MerossManagerFactory to authenticate.
        print("Authenticating with Meross cloud via factory...")
        manager = await MerossManagerFactory.async_from_credentials(
            email=MEROSS_EMAIL,
            password=MEROSS_PASSWORD
        )
        print("Authentication successful.")

        # The manager is now fully initialized. We just need to discover devices.
        print("Discovering devices...")
        await manager.async_device_discovery()
        #
        # --- END OF CORRECTION ---
        #

        device = manager.find_devices(device_name=LIGHT_NAME, online_status=True)
        if not device:
            print(f"ERROR: Could not find an online device named '{LIGHT_NAME}'. Aborting simulation.")
            return

        light = device[0]
        await light.async_turn_on()
        
        total_steps = SUNRISE_DURATION_MINUTES * 12 # One step every 5 seconds
        
        for i in range(total_steps):
            progress = i / total_steps
            current_brightness = max(1, int(100 * progress))
            
            r = int(SUNRISE_START_COLOR[0] + (CANDLELIGHT_COLOR[0] - SUNRISE_START_COLOR[0]) * progress)
            g = int(SUNRISE_START_COLOR[1] + (CANDLELIGHT_COLOR[1] - SUNRISE_START_COLOR[1]) * progress)
            b = int(SUNRISE_START_COLOR[2] + (CANDLELIGHT_COLOR[2] - SUNRISE_START_COLOR[2]) * progress)

            print(f"Progress: {progress:.1%}, Brightness: {current_brightness}%, Color: ({r},{g},{b})")
            await light.async_set_light_color(rgb=(r, g, b), luminance=current_brightness)
            await asyncio.sleep(5)

        print("Sunrise simulation complete. Setting final state.")
        await light.async_set_light_color(rgb=CANDLELIGHT_COLOR, luminance=100)

    except Exception as e:
        print(f"FATAL ERROR during sunrise simulation: {e}")
    finally:
        if manager is not None:
            # The manager handles closing the http_api_client
            manager.close()

        is_sunrise_running = False
        print("Background sunrise thread finished and cleaned up.")

def run_sunrise_in_background():
    """
    Wrapper function to run the async simulation in a way that a new
    thread can manage. It creates and manages its own asyncio event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sunrise_simulation_async())
    loop.close()

@app.route("/api/sunrise", methods=["POST"])
@token_required
def trigger_sunrise():
    """
    API endpoint to trigger the sunrise simulation. Starts the process
    in a background thread to return an immediate response.
    """
    global is_sunrise_running
    if is_sunrise_running:
        return jsonify({"error": "A sunrise simulation is already in progress."}), 409 # 409 Conflict

    # Use a thread to run the async function in the background.
    # This is crucial so the API call doesn't wait 30 minutes for a response.
    thread = threading.Thread(target=run_sunrise_in_background)
    thread.start()
    
    return jsonify({"message": "Sunrise simulation has been started successfully in the background."}), 202

@app.route("/")
def health_check():
    """
    A simple health-check endpoint. Can be used by uptime monitors.
    """
    return "Sunrise simulator is alive and running."

if __name__ == "__main__":
    # This block is for local development only.
    # In production, Gunicorn will be used to run the app.
    print("Starting Flask development server...")
    print("WARNING: This is for local testing only. Use Gunicorn in production.")
    # Port 8080 is a common choice for web apps
    app.run(host='0.0.0.0', port=8080)
