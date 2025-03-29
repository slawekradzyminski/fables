#!/usr/bin/env python3
import sys
import time
import requests
import subprocess
import signal
import os
from pathlib import Path

def kill_existing_process(port: int = 8000) -> None:
    """Kill any process using the specified port."""
    try:
        # Using lsof to find process using the port
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            pid = int(result.stdout.strip())
            print(f"Killing existing process on port {port} (PID: {pid})")
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)  # Give it time to shut down
    except (subprocess.SubprocessError, ValueError, ProcessLookupError) as e:
        print(f"No process found using port {port}")

def check_health(base_url: str, max_retries: int = 30, delay: float = 1.0) -> bool:
    """
    Check if the application is healthy by calling the health endpoint.
    
    Args:
        base_url: Base URL of the application
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        bool: True if healthy, False otherwise
    """
    health_url = f"{base_url}/health"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(health_url)
            if response.status_code == 200:
                data = response.json()
                if not data["openai_key_configured"]:
                    print("WARNING: OpenAI API key is not configured!")
                    return False
                print(f"Health check passed on attempt {attempt + 1}")
                return True
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Health check failed after {max_retries} attempts")
                return False
    return False

def check_swagger_ui(base_url: str) -> bool:
    """
    Check if Swagger UI is accessible.
    
    Args:
        base_url: Base URL of the application
        
    Returns:
        bool: True if Swagger UI is accessible, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("Swagger UI is accessible")
            return True
        else:
            print(f"Swagger UI check failed with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Swagger UI check failed with error: {e}")
        return False

def start_application() -> subprocess.Popen:
    """Start the FastAPI application using uvicorn in detached mode."""
    # Get the project root directory (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    
    # Create log directory if it doesn't exist
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Open log files
    out_log = open(log_dir / "uvicorn.out", "a")
    err_log = open(log_dir / "uvicorn.err", "a")
    
    # Start uvicorn with logs redirected to files
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=project_root,
        stdout=out_log,
        stderr=err_log,
        start_new_session=True  # This is sufficient for detaching on macOS
    )
    return process

def main():
    base_url = "http://127.0.0.1:8000"
    
    # Kill any existing process on port 8000
    kill_existing_process(8000)
    
    # Start the application
    print("Starting the application...")
    app_process = start_application()
    
    try:
        # Check if the application is healthy
        if not check_health(base_url):
            print("Application failed to start properly")
            if app_process:
                os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
            sys.exit(1)
        
        print("Application is healthy!")
        
        # Check if Swagger UI is accessible
        if not check_swagger_ui(base_url):
            print("Swagger UI is not accessible")
            if app_process:
                os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
            sys.exit(1)
        
        print("All checks passed! The application is running correctly.")
        print(f"Swagger UI available at: {base_url}/docs")
        print("Application is running in detached mode. Use 'lsof -i :8000' to find and kill it later.")
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        if app_process:
            os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
        sys.exit(0)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        if app_process:
            os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
        sys.exit(1)

if __name__ == "__main__":
    main() 