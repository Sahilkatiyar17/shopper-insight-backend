
import requests
import json
from datetime import datetime, timedelta
import random

# Base URL for API
BASE_URL = "http://127.0.0.1:8000"

# Sample customer data
customer_data = {
    "customer_id": "eh0svcmt",
    "full_name": "Dhruv",
    "email": "dhruv@gmail.com",
    "username": "Dhruv_1234",
    "phone_number": "9653259612",
    "age": 20,
    "gender": "Male",
    "location": "Karnataka"
}

# Sample address
address_data = {
    "customer_id": "eh0svcmt",
    "address_type": "billing",
    "address": "901/A Manraj heights, Match Factory Lane, Opp Omkar Meridia, Krishna Chowk, Kurla(w), Mumbai, 400070, India"
}

# Sample browsing history
browsing_data = [
    {"category": "SmartPhone", "timestamp": "2025-04-04 12:01:05"},
    {"category": "Laptop", "timestamp": "2025-04-04 12:00:53"},
    {"category": "Laptop", "timestamp": "2025-04-04 12:00:43"},
    {"category": "Yoga Mat", "timestamp": "2025-04-04 12:00:35"},
    {"category": "Yoga mat", "timestamp": "2025-04-04 12:00:29"}
]

# Sample purchase history
purchase_data = [
    {"product_name": "Shoes", "product_category": "fashion", "price": 4724.0, "order_date": "2025-04-04 12:01:34.035000+00:00"},
    {"product_name": "Resistance Bands", "product_category": "fitness", "price": 2861.0, "order_date": "2025-04-04 12:01:34.035000+00:00"},
    {"product_name": "Treadmill", "product_category": "fitness", "price": 2136.0, "order_date": "2025-04-04 12:01:34.035000+00:00"}
]

def create_customer():
    """Create a test customer"""
    response = requests.post(f"{BASE_URL}/customer/create", json=customer_data)
    print("Create Customer Response:", response.status_code)
    print(response.json())
    return response.json()

def add_address():
    """Add a test address"""
    response = requests.post(f"{BASE_URL}/customer/add-address", json=[address_data])
    print("Add Address Response:", response.status_code)
    print(response.json())
    return response.json()

def add_browsing_history():
    """Add browsing history for the customer"""
    for browsing in browsing_data:
        behavior_data = {
            "customer_id": customer_data["customer_id"],
            "browsing_category": browsing["category"]
        }
        response = requests.post(f"{BASE_URL}/customer/update-behavior", json=behavior_data)
        print(f"Add Browsing Response for {browsing['category']}:", response.status_code)
    
    return "Browsing history added"

def add_purchase_history():
    """Add purchase history for the customer"""
    for purchase in purchase_data:
        behavior_data = {
            "customer_id": customer_data["customer_id"],
            "purchases": [purchase]
        }
        response = requests.post(f"{BASE_URL}/customer/update-behavior", json=behavior_data)
        print(f"Add Purchase Response for {purchase['product_name']}:", response.status_code)
    
    return "Purchase history added"

def get_recommendations():
    """Get recommendations for the customer"""
    response = requests.get(f"{BASE_URL}/recommendations/{customer_data['customer_id']}")
    print("Get Recommendations Response:", response.status_code)
    recommendations = response.json()
    print("\nTOP RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations.get("recommendations", []), 1):
        print(f"{i}. {rec['product_name']} ({rec['category']}) - ${rec['price']} - Score: {rec['score']:.4f}")
    
    return recommendations

def process_new_browsing_interaction():
    """Process a new browsing interaction"""
    categories = ["SmartPhone", "Laptop", "Yoga Mat", "Fitness", "Fashion"]
    category = random.choice(categories)
    
    interaction = {
        "customer_id": customer_data["customer_id"],
        "category": category
    }
    
    response = requests.post(f"{BASE_URL}/recommendations/process-browsing", json=interaction)
    print(f"Process Browsing Response for {category}:", response.status_code)
    print(response.json())
    
    # Also update in the main system
    behavior_data = {
        "customer_id": customer_data["customer_id"],
        "browsing_category": category
    }
    requests.post(f"{BASE_URL}/customer/update-behavior", json=behavior_data)
    
    return response.json()

def main():
    """Run the test script"""
    print("===== SETTING UP TEST DATA =====")
    create_customer()
    add_address()
    add_browsing_history()
    add_purchase_history()
    
    print("\n===== TESTING RECOMMENDATIONS =====")
    recommendations_before = get_recommendations()
    
    print("\n===== PROCESSING NEW INTERACTION =====")
    process_new_browsing_interaction()
    
    print("\n===== UPDATED RECOMMENDATIONS =====")
    recommendations_after = get_recommendations()
    
    print("\n===== TEST COMPLETE =====")

if __name__ == "__main__":
    main()
