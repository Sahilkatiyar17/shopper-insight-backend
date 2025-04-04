
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from datetime import datetime, timedelta
import json
import random
from typing import List, Dict, Any

class RecommendationSystem:
    def __init__(self, db_path="customers.db"):
        self.db_path = db_path
        self.init_db()
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize the recommendation tables in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Product Catalog Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_catalog (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                product_category TEXT,
                price FLOAT,
                description TEXT,
                tags TEXT
            )
        ''')
        
        # Customer Recommendations Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                recommendations TEXT,  # JSON string containing recommended product IDs and scores
                recommendation_type TEXT,  # e.g., 'browsing_based', 'purchase_based', 'hybrid'
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Generate sample product catalog if empty
        self._ensure_product_catalog()
    
    def _ensure_product_catalog(self):
        """Make sure we have a product catalog with sample data for recommendations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if product catalog is empty
        cursor.execute("SELECT COUNT(*) FROM product_catalog")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Define sample products across different categories
            sample_products = [
                # Electronics - Smartphones
                {"name": "Galaxy S22", "category": "SmartPhone", "price": 799.99, 
                 "description": "Latest Samsung smartphone with advanced camera", 
                 "tags": "samsung phone android camera"},
                {"name": "iPhone 13", "category": "SmartPhone", "price": 899.99, 
                 "description": "Apple's flagship smartphone with A15 Bionic chip", 
                 "tags": "apple phone ios camera"},
                {"name": "Google Pixel 6", "category": "SmartPhone", "price": 699.99, 
                 "description": "Google smartphone with best-in-class photography", 
                 "tags": "google phone android camera photography"},
                
                # Electronics - Laptops
                {"name": "MacBook Pro", "category": "Laptop", "price": 1299.99, 
                 "description": "Powerful Apple laptop for professionals", 
                 "tags": "apple laptop macOS productivity"},
                {"name": "Dell XPS 13", "category": "Laptop", "price": 999.99, 
                 "description": "Compact Windows laptop with InfinityEdge display", 
                 "tags": "dell laptop windows productivity"},
                {"name": "Lenovo ThinkPad", "category": "Laptop", "price": 1099.99, 
                 "description": "Business laptop known for reliability", 
                 "tags": "lenovo laptop windows business"},
                
                # Fitness
                {"name": "Premium Yoga Mat", "category": "Yoga Mat", "price": 45.99, 
                 "description": "Extra thick yoga mat for comfort", 
                 "tags": "yoga fitness exercise mat"},
                {"name": "Yoga Block Set", "category": "Yoga", "price": 19.99, 
                 "description": "Set of 2 yoga blocks for proper alignment", 
                 "tags": "yoga fitness exercise props"},
                {"name": "Premium Resistance Bands", "category": "fitness", "price": 29.99, 
                 "description": "Set of resistance bands for strength training", 
                 "tags": "fitness strength training bands home workout"},
                {"name": "Smart Treadmill", "category": "fitness", "price": 1499.99, 
                 "description": "Treadmill with smart features and programs", 
                 "tags": "fitness cardio treadmill running machine"},
                {"name": "Adjustable Dumbbells", "category": "fitness", "price": 299.99, 
                 "description": "Space-saving adjustable weight dumbbells", 
                 "tags": "fitness strength weights dumbbells"},
                
                # Fashion
                {"name": "Running Shoes", "category": "fashion", "price": 89.99, 
                 "description": "Lightweight running shoes with cushioning", 
                 "tags": "shoes running fitness footwear"},
                {"name": "Casual Sneakers", "category": "fashion", "price": 59.99, 
                 "description": "Comfortable everyday sneakers", 
                 "tags": "shoes casual fashion footwear"},
                {"name": "Formal Shoes", "category": "fashion", "price": 129.99, 
                 "description": "Elegant formal shoes for special occasions", 
                 "tags": "shoes formal dress footwear"},
                {"name": "Fitness Tracker Watch", "category": "fashion", "price": 149.99, 
                 "description": "Smart watch with fitness tracking features", 
                 "tags": "watch smartwatch fitness tracker"},
                {"name": "Designer Jeans", "category": "fashion", "price": 79.99, 
                 "description": "Premium denim jeans with perfect fit", 
                 "tags": "jeans pants denim fashion"},
            ]
            
            # Insert sample products
            for product in sample_products:
                cursor.execute('''
                    INSERT INTO product_catalog (product_name, product_category, price, description, tags)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product["name"], product["category"], product["price"], 
                      product["description"], product["tags"]))
            
            conn.commit()
        
        conn.close()
    
    def _get_customer_data(self, customer_id):
        """Get all relevant customer data needed for recommendations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get customer profile
        cursor.execute("SELECT * FROM customer_profiles WHERE customer_id = ?", (customer_id,))
        profile = cursor.fetchone()
        
        if not profile:
            conn.close()
            return None
        
        # Get customer segment
        cursor.execute("""
            SELECT customer_segment, avg_order_value FROM customer_segments 
            WHERE customer_id = ?
        """, (customer_id,))
        segment = cursor.fetchone() or ("Standard", 0)
        
        # Get browsing history (last 30 days)
        cursor.execute("""
            SELECT category FROM browsing_history 
            WHERE customer_id = ? 
            AND timestamp >= datetime('now', '-30 days')
            ORDER BY timestamp DESC
        """, (customer_id,))
        browsing_history = cursor.fetchall()
        
        # Get purchase history (last 180 days)
        cursor.execute("""
            SELECT product_name, product_category, price 
            FROM purchase_history 
            WHERE customer_id = ?
            AND order_date >= datetime('now', '-180 days')
            ORDER BY order_date DESC
        """, (customer_id,))
        purchase_history = cursor.fetchall()
        
        conn.close()
        
        return {
            "profile": {
                "customer_id": profile[0],
                "full_name": profile[1],
                "gender": profile[6],
                "age": profile[5],
                "location": profile[7]
            },
            "segment": {
                "type": segment[0],
                "avg_order_value": segment[1]
            },
            "browsing_history": [category[0] for category in browsing_history],
            "purchase_history": [
                {"product_name": p[0], "category": p[1], "price": p[2]} 
                for p in purchase_history
            ]
        }
    
    def _get_all_products(self):
        """Get all products from the catalog"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM product_catalog")
        products = cursor.fetchall()
        
        conn.close()
        
        return [{
            "product_id": p[0],
            "product_name": p[1],
            "category": p[2],
            "price": p[3],
            "description": p[4],
            "tags": p[5]
        } for p in products]
    
    def _calculate_category_weights(self, customer_data):
        """Calculate weights for each product category based on user behavior"""
        categories = {}
        
        # Weight from browsing history (more recent = higher weight)
        browse_weight_factor = 0.7
        for i, category in enumerate(customer_data["browsing_history"]):
            # Normalize the category name to handle case differences
            category_lower = category.lower()
            weight = browse_weight_factor * (1.0 / (i + 1))  # Higher weight for more recent
            if category_lower in categories:
                categories[category_lower] += weight
            else:
                categories[category_lower] = weight
        
        # Weight from purchase history (higher price = higher weight)
        purchase_weight_factor = 1.0
        for purchase in customer_data["purchase_history"]:
            category_lower = purchase["category"].lower()
            # Weight based on price relative to user's average order value
            segment_avg = max(customer_data["segment"]["avg_order_value"], 1)
            price_weight = purchase["price"] / segment_avg
            
            weight = purchase_weight_factor * price_weight
            if category_lower in categories:
                categories[category_lower] += weight
            else:
                categories[category_lower] = weight
        
        # Normalize weights
        if categories:
            total = sum(categories.values())
            categories = {k: v/total for k, v in categories.items()}
        
        return categories
    
    def _content_based_filtering(self, customer_id, category_weights, top_n=10):
        """Generate recommendations based on product content and user preferences"""
        products = self._get_all_products()
        
        if not products or not category_weights:
            return []
        
        # Score products based on category weights
        scored_products = []
        for product in products:
            score = 0
            product_category = product["category"].lower()
            
            # Direct category match
            if product_category in category_weights:
                score += category_weights[product_category] * 2
            
            # Check for partial matches in category name
            for category, weight in category_weights.items():
                if category in product_category or product_category in category:
                    score += weight * 0.5
            
            # Check if any category keyword is in product tags
            for category, weight in category_weights.items():
                if category in product["tags"].lower():
                    score += weight * 0.3
            
            # Adjust score based on customer segment and product price
            customer_data = self._get_customer_data(customer_id)
            if customer_data:
                segment_type = customer_data["segment"]["type"].lower()
                if segment_type == "premium" and product["price"] > 100:
                    score *= 1.2
                elif segment_type == "budget" and product["price"] < 50:
                    score *= 1.2
            
            if score > 0:
                scored_products.append({
                    "product_id": product["product_id"],
                    "score": score,
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "price": product["price"]
                })
        
        # Sort by score and get top N
        scored_products.sort(key=lambda x: x["score"], reverse=True)
        return scored_products[:top_n]
    
    def _collaborative_based_suggestions(self, customer_id, top_n=5):
        """Simple collaborative-like suggestions based on user segment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user segment
        cursor.execute("""
            SELECT customer_segment FROM customer_segments 
            WHERE customer_id = ?
        """, (customer_id,))
        segment_result = cursor.fetchone()
        
        if not segment_result:
            conn.close()
            return []
        
        segment = segment_result[0]
        
        # Find similar users in the same segment
        cursor.execute("""
            SELECT DISTINCT ph.product_category 
            FROM purchase_history ph
            JOIN customer_segments cs ON ph.customer_id = cs.customer_id
            WHERE cs.customer_segment = ? AND ph.customer_id != ?
            GROUP BY ph.product_category
            ORDER BY COUNT(*) DESC
            LIMIT ?
        """, (segment, customer_id, top_n))
        
        popular_categories = cursor.fetchall()
        conn.close()
        
        if not popular_categories:
            return []
        
        # Get products from these categories
        popular_categories = [cat[0] for cat in popular_categories]
        products = self._get_all_products()
        
        collaborative_suggestions = []
        for category in popular_categories:
            category_products = [p for p in products if p["category"].lower() == category.lower()]
            if category_products:
                # Pick a random product from this category to add diversity
                product = random.choice(category_products)
                collaborative_suggestions.append({
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "price": product["price"],
                    "score": 0.5  # Default score for collaborative suggestions
                })
        
        return collaborative_suggestions
    
    def generate_recommendations(self, customer_id, limit=10):
        """Generate personalized product recommendations for a customer"""
        customer_data = self._get_customer_data(customer_id)
        
        if not customer_data:
            return {"error": "Customer not found"}
        
        # Calculate category weights based on browsing and purchase history
        category_weights = self._calculate_category_weights(customer_data)
        
        # Generate content-based recommendations
        content_recommendations = self._content_based_filtering(
            customer_id, category_weights, top_n=int(limit * 0.7)
        )
        
        # Get collaborative-based suggestions to add diversity
        collaborative_recommendations = self._collaborative_based_suggestions(
            customer_id, top_n=int(limit * 0.3)
        )
        
        # Combine recommendations, ensuring no duplicates
        all_recommendations = content_recommendations.copy()
        existing_ids = {rec["product_id"] for rec in all_recommendations}
        
        for rec in collaborative_recommendations:
            if rec["product_id"] not in existing_ids and len(all_recommendations) < limit:
                all_recommendations.append(rec)
                existing_ids.add(rec["product_id"])
        
        # Sort final recommendations by score
        all_recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # Store recommendations in the database
        self._store_recommendations(customer_id, all_recommendations)
        
        return {
            "customer_id": customer_id,
            "recommendations": all_recommendations[:limit]
        }
    
    def _store_recommendations(self, customer_id, recommendations):
        """Store generated recommendations in the database"""
        if not recommendations:
            return
        
        # Format recommendations as JSON string
        rec_json = json.dumps([{
            "product_id": rec["product_id"],
            "score": rec["score"],
            "timestamp": datetime.now().isoformat()
        } for rec in recommendations])
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Store new recommendations
        cursor.execute("""
            INSERT INTO customer_recommendations 
            (customer_id, recommendations, recommendation_type, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (customer_id, rec_json, "hybrid"))
        
        # Keep only the most recent 5 recommendation sets per customer
        cursor.execute("""
            DELETE FROM customer_recommendations
            WHERE recommendation_id NOT IN (
                SELECT recommendation_id
                FROM customer_recommendations
                WHERE customer_id = ?
                ORDER BY created_at DESC
                LIMIT 5
            )
            AND customer_id = ?
        """, (customer_id, customer_id))
        
        conn.commit()
        conn.close()
    
    def get_stored_recommendations(self, customer_id):
        """Retrieve the most recent stored recommendations for a customer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT recommendations, created_at 
            FROM customer_recommendations
            WHERE customer_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (customer_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        rec_json, timestamp = result
        rec_data = json.loads(rec_json)
        
        # Check if recommendations are recent (within last 24 hours)
        rec_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        is_recent = (datetime.now() - rec_time) < timedelta(hours=24)
        
        if not is_recent:
            # If recommendations are old, generate new ones
            return None
        
        # Get product details for the recommended products
        products = self._get_all_products()
        product_map = {p["product_id"]: p for p in products}
        
        recommendations = []
        for rec in rec_data:
            product_id = rec["product_id"]
            if product_id in product_map:
                product = product_map[product_id]
                recommendations.append({
                    "product_id": product_id,
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "price": product["price"],
                    "score": rec["score"]
                })
        
        return {
            "customer_id": customer_id,
            "recommendations": recommendations,
            "timestamp": timestamp
        }
    
    def process_new_interaction(self, customer_id, interaction_type, data):
        """Process a new user interaction to update recommendations"""
        # For now, just invalidate old recommendations so new ones will be generated
        # In a more sophisticated system, you'd update existing recommendations incrementally
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Mark existing recommendations as outdated by setting a flag or deleting them
        # Here we'll use a simple approach of just deleting them
        cursor.execute("""
            DELETE FROM customer_recommendations
            WHERE customer_id = ?
        """, (customer_id,))
        
        conn.commit()
        conn.close()
        
        # Return success
        return {
            "status": "success",
            "message": f"Processed new {interaction_type} interaction for customer {customer_id}"
        }
