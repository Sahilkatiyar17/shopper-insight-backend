
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import time
import sys
import os
import json
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Create template file
template_path = templates_dir / "index.html"
with open(template_path, "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Recommendation System Evaluator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        pre {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: 'Courier New', Courier, monospace;
        }
        .loader {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
            margin: 20px auto;
            display: none;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status {
            text-align: center;
            margin: 20px 0;
            font-weight: bold;
        }
        .customer {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }
        .recommendation {
            margin: 5px 0 5px 20px;
            padding: 5px;
            border-bottom: 1px solid #eee;
        }
        .score {
            display: inline-block;
            width: 70px;
            font-weight: bold;
            color: #333;
        }
        .excellent { color: #27ae60; }
        .good { color: #2980b9; }
        .fair { color: #f39c12; }
        .poor { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Recommendation System Evaluator</h1>
        
        <div class="card">
            <h2>Run Evaluation</h2>
            <p>Click the button below to run the recommendation system evaluation:</p>
            <button id="runButton" onclick="runEvaluation()">Run Evaluation</button>
            <div class="loader" id="loader"></div>
            <div class="status" id="status"></div>
        </div>
        
        <div class="card" id="resultsCard" style="display: none;">
            <h2>Evaluation Results</h2>
            <div id="results"></div>
        </div>
    </div>

    <script>
        function showLoader() {
            document.getElementById('loader').style.display = 'block';
            document.getElementById('status').textContent = 'Running evaluation...';
            document.getElementById('runButton').disabled = true;
            document.getElementById('resultsCard').style.display = 'none';
        }
        
        function hideLoader() {
            document.getElementById('loader').style.display = 'none';
            document.getElementById('runButton').disabled = false;
        }
        
        function formatResults(results) {
            let html = '';
            
            if (results.includes('Error')) {
                html = `<pre class="error">${results}</pre>`;
                return html;
            }
            
            // Extract different sections
            const sections = results.split('=====');
            
            for (let i = 1; i < sections.length; i++) {
                const section = sections[i].trim();
                
                if (section.includes('RECOMMENDATION SYSTEM EVALUATION')) {
                    // Format the evaluation results section
                    const lines = section.split('\n').filter(line => line.trim() !== '');
                    
                    let customerSection = false;
                    let currentCustomer = '';
                    
                    for (let j = 1; j < lines.length; j++) {
                        const line = lines[j];
                        
                        if (line.includes('(') && line.includes(')') && !line.includes('OVERALL')) {
                            // This is a customer header
                            customerSection = true;
                            currentCustomer = line;
                            html += `<div class="customer"><h3>${currentCustomer}</h3>`;
                        } else if (line.includes('OVERALL SYSTEM PERFORMANCE')) {
                            // Close any open customer section
                            if (customerSection) {
                                html += '</div>';
                                customerSection = false;
                            }
                            
                            html += `<h3>${line}</h3>`;
                        } else if (line.includes('Average relevance score')) {
                            const score = parseFloat(line.match(/[\d.]+/)[0]);
                            let scoreClass = '';
                            
                            if (score >= 80) scoreClass = 'excellent';
                            else if (score >= 60) scoreClass = 'good';
                            else if (score >= 40) scoreClass = 'fair';
                            else scoreClass = 'poor';
                            
                            html += `<p>${line.split(':')[0]}: <span class="${scoreClass}">${score.toFixed(2)}%</span></p>`;
                        } else if (line.includes('Performance rating')) {
                            const rating = line.split(':')[1].trim();
                            let ratingClass = '';
                            
                            if (rating === 'EXCELLENT') ratingClass = 'excellent';
                            else if (rating === 'GOOD') ratingClass = 'good';
                            else if (rating === 'FAIR') ratingClass = 'fair';
                            else ratingClass = 'poor';
                            
                            html += `<p>Performance rating: <span class="${ratingClass}">${rating}</span></p>`;
                        } else if (line.includes('Relevance score')) {
                            const score = parseFloat(line.match(/[\d.]+/)[0]);
                            let scoreClass = '';
                            
                            if (score >= 80) scoreClass = 'excellent';
                            else if (score >= 60) scoreClass = 'good';
                            else if (score >= 40) scoreClass = 'fair';
                            else scoreClass = 'poor';
                            
                            html += `<p>${line.split(':')[0]}: <span class="${scoreClass}">${score.toFixed(2)}%</span></p>`;
                        } else if (line.match(/^\d+\.\s/)) {
                            // This is a recommendation item
                            const parts = line.split(' - ');
                            const productInfo = parts[0];
                            const price = parts[1];
                            const score = parseFloat(parts[2].split(':')[1]);
                            
                            let scoreClass = '';
                            if (score >= 0.8) scoreClass = 'excellent';
                            else if (score >= 0.5) scoreClass = 'good';
                            else if (score >= 0.3) scoreClass = 'fair';
                            else scoreClass = 'poor';
                            
                            html += `<div class="recommendation">
                                ${productInfo} - ${price} - Score: <span class="${scoreClass}">${score.toFixed(4)}</span>
                            </div>`;
                        } else if (customerSection) {
                            html += `<p>${line}</p>`;
                        }
                    }
                    
                    // Close any open customer section
                    if (customerSection) {
                        html += '</div>';
                    }
                } else if (section.includes('GETTING RECOMMENDATIONS') || section.includes('RECOMMENDATIONS FOR')) {
                    // Format the recommendations section
                    const lines = section.split('\n').filter(line => line.trim() !== '');
                    const title = lines[0];
                    
                    if (title.includes('RECOMMENDATIONS FOR')) {
                        html += `<div class="customer"><h3>${title}</h3>`;
                        
                        for (let j = 1; j < lines.length; j++) {
                            const line = lines[j];
                            if (line.match(/^\d+\.\s/)) {
                                // This is a recommendation item
                                const parts = line.split(' - ');
                                const productInfo = parts[0];
                                const price = parts[1];
                                const score = parseFloat(parts[2].split(':')[1]);
                                
                                let scoreClass = '';
                                if (score >= 0.8) scoreClass = 'excellent';
                                else if (score >= 0.5) scoreClass = 'good';
                                else if (score >= 0.3) scoreClass = 'fair';
                                else scoreClass = 'poor';
                                
                                html += `<div class="recommendation">
                                    ${productInfo} - ${price} - Score: <span class="${scoreClass}">${score.toFixed(4)}</span>
                                </div>`;
                            }
                        }
                        
                        html += '</div>';
                    }
                }
            }
            
            return html || `<pre>${results}</pre>`;
        }
        
        function runEvaluation() {
            showLoader();
            
            fetch('/run-evaluation')
                .then(response => response.text())
                .then(data => {
                    hideLoader();
                    document.getElementById('status').textContent = 'Evaluation completed';
                    document.getElementById('resultsCard').style.display = 'block';
                    document.getElementById('results').innerHTML = formatResults(data);
                })
                .catch(error => {
                    hideLoader();
                    document.getElementById('status').textContent = 'Error running evaluation';
                    document.getElementById('resultsCard').style.display = 'block';
                    document.getElementById('results').innerHTML = `<pre class="error">Error: ${error.message}</pre>`;
                });
        }
    </script>
</body>
</html>
    """)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def run_server_subprocess():
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

@app.get("/run-evaluation")
async def run_evaluation():
    """Run the evaluation script and return the results"""
    # Check if we're in the right directory
    if not os.path.exists("src/main.py"):
        return "Error: Cannot find src/main.py. Make sure you're running this from the project root directory."
    
    # Start server
    server = run_server_subprocess()
    
    try:
        # Run evaluation
        print("\nRunning recommendation system evaluation...")
        result = subprocess.run(
            [sys.executable, "src/evaluate_recommendations.py"],
            capture_output=True,
            text=True
        )
        
        evaluation_output = result.stdout
        
        # Save results to file for easier access
        with open("recommendation_results.txt", "w") as f:
            f.write(evaluation_output)
        
        return evaluation_output
    
    finally:
        # Clean up: terminate the server
        print("\nShutting down server...")
        server.terminate()
        server.wait()
        print("Server shutdown complete.")

if __name__ == "__main__":
    print("Starting web interface for recommendation evaluation...")
    print("Open your browser and navigate to http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)
