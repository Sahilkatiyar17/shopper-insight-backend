
import requests
import json
from datetime import datetime
import random
import time

# Base URL for API
BASE_URL = "http://127.0.0.1:8000"

def create_test_customers():
    """Create multiple test customers with different profiles"""
    customers = []
    
    # Customer 1: Tech enthusiast
    tech_customer = {
        "customer_id": "tech001",
        "full_name": "Alex Tech",
        "email": "alex@example.com",
        "username": "alextech",
        "phone_number": "1234567890",
        "age": 28,
        "gender": "Male",
        "location": "California"
    }
    
    # Customer 2: Fitness enthusiast
    fitness_customer = {
        "customer_id": "fitness001",
        "full_name": "Fiona Fit",
        "email": "fiona@example.com",
        "username": "fionafit",
        "phone_number": "2345678901",
        "age": 32,
        "gender": "Female",
        "location": "Colorado"
    }
    
    # Customer 3: Fashion enthusiast
    fashion_customer = {
        "customer_id": "fashion001",
        "full_name": "Maya Style",
        "email": "maya@example.com",
        "username": "mayastyle",
        "phone_number": "3456789012",
        "age": 24,
        "gender": "Female",
        "location": "New York"
    }
    
    customers = [tech_customer, fitness_customer, fashion_customer]
    
    for customer in customers:
        response = requests.post(f"{BASE_URL}/customer/create", json=customer)
        print(f"Created customer {customer['full_name']}: {response.status_code}")
    
    return customers

def add_browsing_history(customers):
    """Add targeted browsing history for each customer type"""
    browsing_patterns = {
        "tech001": ["SmartPhone", "Laptop", "Laptop", "SmartPhone", "Laptop"],
        "fitness001": ["Yoga Mat", "fitness", "Yoga", "fitness", "Yoga Mat"],
        "fashion001": ["fashion", "fashion", "shoes", "fashion", "watch"]
    }
    
    for customer_id, patterns in browsing_patterns.items():
        for category in patterns:
            behavior_data = {
                "customer_id": customer_id,
                "browsing_category": category
            }
            response = requests.post(f"{BASE_URL}/customer/update-behavior", json=behavior_data)
            print(f"Added browsing {category} for {customer_id}: {response.status_code}")
            time.sleep(0.2)  # Small delay to avoid overwhelming the server

def add_purchase_history(customers):
    """Add targeted purchase history for each customer type"""
    # Define purchases for each customer type
    tech_purchases = [
        {"product_name": "MacBook Pro", "product_category": "Laptop", "price": 1299.99},
        {"product_name": "iPhone 13", "product_category": "SmartPhone", "price": 899.99}
    ]
    
    fitness_purchases = [
        {"product_name": "Premium Yoga Mat", "product_category": "Yoga Mat", "price": 45.99},
        {"product_name": "Resistance Bands", "product_category": "fitness", "price": 29.99}
    ]
    
    fashion_purchases = [
        {"product_name": "Designer Jeans", "product_category": "fashion", "price": 79.99},
        {"product_name": "Casual Sneakers", "product_category": "fashion", "price": 59.99}
    ]
    
    purchase_patterns = {
        "tech001": tech_purchases,
        "fitness001": fitness_purchases,
        "fashion001": fashion_purchases
    }
    
    for customer_id, purchases in purchase_patterns.items():
        for purchase in purchases:
            # Add current date/time for the purchase
            purchase["order_date"] = datetime.now().isoformat()
            
            behavior_data = {
                "customer_id": customer_id,
                "purchases": [purchase]
            }
            response = requests.post(f"{BASE_URL}/customer/update-behavior", json=behavior_data)
            print(f"Added purchase {purchase['product_name']} for {customer_id}: {response.status_code}")
            time.sleep(0.2)  # Small delay to avoid overwhelming the server

def get_recommendations_for_all(customers):
    """Get recommendations for all test customers"""
    results = {}
    
    for customer in customers:
        customer_id = customer["customer_id"]
        response = requests.get(f"{BASE_URL}/recommendations/{customer_id}")
        
        if response.status_code == 200:
            recommendations = response.json()
            results[customer_id] = recommendations
            
            print(f"\nRECOMMENDATIONS FOR {customer['full_name']} ({customer_id}):")
            for i, rec in enumerate(recommendations.get("recommendations", []), 1):
                print(f"{i}. {rec['product_name']} ({rec['category']}) - ${rec['price']} - Score: {rec['score']:.4f}")
        else:
            print(f"Error getting recommendations for {customer_id}: {response.status_code}")
            results[customer_id] = {"error": response.status_code}
    
    return results

def evaluate_recommendation_quality(customers, recommendations):
    """Evaluate how well the recommendations match customer profiles"""
    # Expected categories for each customer type
    expected_categories = {
        "tech001": ["SmartPhone", "Laptop", "Electronics"],
        "fitness001": ["Yoga", "Yoga Mat", "fitness"],
        "fashion001": ["fashion", "shoes", "watch"]
    }
    
    results = {}
    
    for customer_id, expected in expected_categories.items():
        if customer_id not in recommendations:
            results[customer_id] = {"error": "No recommendations found"}
            continue
            
        recs = recommendations[customer_id].get("recommendations", [])
        if not recs:
            results[customer_id] = {"error": "Empty recommendations"}
            continue
            
        # Count how many recommendations match expected categories
        matches = 0
        for rec in recs:
            category = rec["category"].lower()
            for exp_cat in expected:
                if exp_cat.lower() in category or category in exp_cat.lower():
                    matches += 1
                    break
                    
        # Calculate percentage of relevant recommendations
        relevance = (matches / len(recs)) * 100
        
        results[customer_id] = {
            "total_recommendations": len(recs),
            "relevant_recommendations": matches,
            "relevance_score": relevance
        }
        
    return results

def print_evaluation_results(customers, eval_results):
    """Print the evaluation results in a formatted way"""
    print("\n===== RECOMMENDATION SYSTEM EVALUATION =====")
    
    total_relevance = 0
    count = 0
    
    for customer in customers:
        customer_id = customer["customer_id"]
        if customer_id in eval_results:
            result = eval_results[customer_id]
            
            if "error" in result:
                print(f"\n{customer['full_name']} ({customer_id}): Error - {result['error']}")
                continue
                
            print(f"\n{customer['full_name']} ({customer_id}):")
            print(f"  Total recommendations: {result['total_recommendations']}")
            print(f"  Relevant recommendations: {result['relevant_recommendations']}")
            print(f"  Relevance score: {result['relevance_score']:.2f}%")
            
            total_relevance += result['relevance_score']
            count += 1
    
    if count > 0:
        avg_relevance = total_relevance / count
        print(f"\nOVERALL SYSTEM PERFORMANCE:")
        print(f"  Average relevance score: {avg_relevance:.2f}%")
        
        if avg_relevance >= 80:
            performance = "EXCELLENT"
        elif avg_relevance >= 60:
            performance = "GOOD"
        elif avg_relevance >= 40:
            performance = "FAIR"
        else:
            performance = "POOR"
            
        print(f"  Performance rating: {performance}")
    else:
        print("\nNot enough data to evaluate system performance")

def main():
    """Run the evaluation process"""
    print("===== CREATING TEST CUSTOMERS =====")
    customers = create_test_customers()
    
    print("\n===== ADDING BROWSING HISTORY =====")
    add_browsing_history(customers)
    
    print("\n===== ADDING PURCHASE HISTORY =====")
    add_purchase_history(customers)
    
    print("\n===== WAITING FOR SYSTEM TO PROCESS DATA =====")
    time.sleep(2)  # Give the system time to process the data
    
    print("\n===== GETTING RECOMMENDATIONS =====")
    recommendations = get_recommendations_for_all(customers)
    
    print("\n===== EVALUATING RECOMMENDATION QUALITY =====")
    evaluation = evaluate_recommendation_quality(customers, recommendations)
    
    print_evaluation_results(customers, evaluation)
    
    print("\n===== EVALUATION COMPLETE =====")

if __name__ == "__main__":
    main()
