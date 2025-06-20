# Smart Light Sunrise Simulator

A simple Flask application that provides an API endpoint to simulate a 30-minute sunrise on a Meross smart light bulb.

## Features

-   **API Controlled:** Trigger the sunrise effect with a simple, secure API call.
-   **Gradual Transition:** Smoothly increases brightness and transitions color from a deep orange to a warm candlelight over 30 minutes.
-   **Background Process:** The simulation runs in a background thread, so the API call returns instantly.
-   **Secure:** The API endpoint is protected by a bearer token.

## Setup and Deployment (for a Linux VM)

These instructions assume you are deploying to a Debian-based Linux server (like Ubuntu on Oracle Cloud).

### 1. Prerequisites

-   A Linux server with Python 3 and Git installed.
-   Your Meross smart light already set up in the Meross app.

### 2. Clone the Repository

Log into your server via SSH and clone this repository:

```bash
git clone <your-git-repo-url>
cd <your-repo-name>
```

### 3. Install Dependencies

It is highly recommended to use a Python virtual environment.

```bash
# Install the virtual environment package if you don't have it
sudo apt install python3-venv -y

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 4. Set Environment Variables

You must set your credentials as environment variables. The server will read these to run the application.

```bash
export MEROSS_EMAIL="your_meross_email@example.com"
export MEROSS_PASSWORD="your_meross_password"
export API_AUTH_TOKEN="your_super_secret_api_token"
export LIGHT_NAME="My Smart Light"
```
**Note:** These variables only last for your current session. For a permanent solution, add these `export` lines to your `~/.bashrc` or `~/.profile` file.

### 5. Run the Application with Gunicorn

Gunicorn is a robust production server for Python web applications.

```bash
# Make sure you are in the project directory with your virtual environment active
gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 4 --timeout 120 app:app
```
-   `--bind 0.0.0.0:8080`: Listen on port 8080 from any IP address.
-   `--workers 1`: Use a single process.
-   `--threads 4`: Allow the worker to handle multiple requests/tasks concurrently.
-   `--timeout 120`: Increase the worker timeout.

Your application is now running! Remember to open port 8080 in your cloud provider's firewall settings.

## API Usage

To trigger the sunrise simulation, make a `POST` request to the `/api/sunrise` endpoint with your authentication token.

-   **Method:** `POST`
-   **URL:** `http://<your_server_ip>:8080/api/sunrise`
-   **Headers:**
    -   `Authorization: Bearer <your_api_token>`

### Example `curl` Command

```bash
curl -X POST \
  -H "Authorization: Bearer your_super_secret_api_token" \
  http://your_server_ip:8080/api/sunrise
```

You should receive an immediate success response, and the simulation will begin on your light. Check the server logs to see the progress.
