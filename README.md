
# Recommendation System Evaluator

This project contains a recommendation system built with FastAPI and a frontend interface to test and visualize the recommendations.

## Setup Instructions

1. Install the required packages:
   ```
   pip install -r src/requirements.txt
   ```

2. Start the backend server:
   ```
   python src/main.py
   ```
   This will start the FastAPI server on http://127.0.0.1:8000

3. In a separate terminal, you can run the frontend:
   ```
   npm install
   npm run dev
   ```
   This will start the React frontend on http://localhost:3000 or another available port.

## Evaluating the Recommendation System

### Option 1: Using the Frontend

1. Start the backend server as described above
2. Open the frontend in your browser
3. Use the interface to:
   - Create test customers
   - View recommendations for each customer
   - Add browsing history to see how recommendations change

### Option 2: Run the Evaluation Script

Run the evaluation script to get a detailed report of the recommendation system's performance:

```
python src/run_evaluation.py
```

This script will:
1. Start the server automatically
2. Run the evaluation tests
3. Display the results including accuracy metrics
4. Stop the server when done

### Option 3: Manual Evaluation

You can also run the evaluation steps manually:

1. Start the server: `python src/main.py`
2. In a separate terminal, run: `python src/evaluate_recommendations.py`

## Interpreting Results

The evaluation results include:
- Relevance scores for each customer profile (tech enthusiast, fitness enthusiast, fashion enthusiast)
- Overall system performance rating
- Recommendations for each customer with confidence scores

A relevance score above 80% is considered EXCELLENT, 60-80% is GOOD, 40-60% is FAIR, and below 40% is POOR.
