
import subprocess
import time
import sys
import os

def run_server():
    """Start the FastAPI server as a subprocess"""
    print("Starting the recommendation server...")
    server_process = subprocess.Popen(
        [sys.executable, "src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server a moment to start
    time.sleep(2)
    return server_process

def run_evaluation():
    """Run the evaluation script and capture output"""
    print("\nRunning recommendation system evaluation...")
    result = subprocess.run(
        [sys.executable, "src/evaluate_recommendations.py"],
        capture_output=True,
        text=True
    )
    
    return result.stdout

def main():
    """Main function to run the server and evaluation"""
    # Check if we're in the right directory
    if not os.path.exists("src/main.py"):
        print("Error: Cannot find src/main.py. Make sure you're running this from the project root directory.")
        return
    
    # Start server
    server = run_server()
    
    try:
        # Run evaluation
        evaluation_output = run_evaluation()
        
        # Print results
        print("\n" + "="*80)
        print("RECOMMENDATION SYSTEM EVALUATION RESULTS")
        print("="*80 + "\n")
        print(evaluation_output)
        
    finally:
        # Clean up: terminate the server
        print("\nShutting down server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
