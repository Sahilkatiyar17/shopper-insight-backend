
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime

# Import the recommendation router
from recommendation_api import recommendation_router, initialize_recommendation_database

app = FastAPI()

class CustomerAgent:
    def __init__(self, db_path="customers.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Customer Profiles Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_profiles (
                customer_id TEXT PRIMARY KEY,
                full_name TEXT,
                email TEXT UNIQUE,
                username TEXT UNIQUE,
                phone_number TEXT,
                age INTEGER,
                gender TEXT,
                location TEXT
            )
        ''')
        
        # Addresses Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_addresses (
                address_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                address_type TEXT CHECK(address_type IN ('shipping', 'billing')),
                address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id) ON DELETE CASCADE
            )
        ''')
        
        # Customer Security Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_security (
                customer_id TEXT PRIMARY KEY,
                password_hash TEXT,
                FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id) ON DELETE CASCADE
            )
        ''')
        
        # Browsing History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browsing_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                category TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id) ON DELETE CASCADE
            )
        ''')
        
        # Purchase History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_history (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                product_name TEXT,
                product_category TEXT,
                price FLOAT,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id) ON DELETE CASCADE
            )
        ''')
        
        # Customer Segments Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_segments (
                customer_id TEXT PRIMARY KEY,
                customer_segment TEXT,
                avg_order_value FLOAT,
                last_active_season TEXT,
                FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

# Initialize CustomerAgent
customer_agent = CustomerAgent()

# Pydantic models for request validation
class Customer(BaseModel):
    customer_id: str
    full_name: str
    email: str
    username: str
    phone_number: str
    age: int
    gender: str
    location: str

class Address(BaseModel):
    customer_id: str
    address_type: str
    address: str

class Security(BaseModel):
    customer_id: str
    password_hash: str

class Purchase(BaseModel):
    product_name: str
    product_category: str
    price: float
    order_date: datetime

class BehaviorUpdate(BaseModel):
    customer_id: str
    browsing_category: Optional[str] = None
    purchases: Optional[List[Purchase]] = []
# API Endpoints

@app.post("/customer/create")
async def create_customer(customer: Customer):
    conn = customer_agent.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO customer_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer.customer_id, customer.full_name, customer.email, customer.username,
            customer.phone_number, customer.age, customer.gender, customer.location
        ))
        conn.commit()
        return {"message": "Customer created successfully", "customer_id": customer.customer_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.post("/customer/add-address")
async def add_address(addresses:List[Address]):
    conn = customer_agent.get_connection()
    cursor = conn.cursor()
    try:
       for address in addresses:
            cursor.execute('''
                INSERT INTO customer_addresses (customer_id, address_type, address) 
                VALUES (?, ?, ?)
            ''', (address.customer_id, address.address_type, address.address))
       conn.commit()
       return {"message": f"{len(addresses)} address(es) added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.get("/customer/get-profile/{customer_id}")
async def get_customer_profile(customer_id: str):
    conn = customer_agent.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get customer profile
        cursor.execute('''
            SELECT * FROM customer_profiles 
            WHERE customer_id = ?
        ''', (customer_id,))
        profile = cursor.fetchone()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get addresses
        cursor.execute('''
            SELECT address_id, address_type, address FROM customer_addresses 
            WHERE customer_id = ?
        ''', (customer_id,))
        addresses = cursor.fetchall()
        
        # Get browsing history
        cursor.execute('''
            SELECT category, timestamp FROM browsing_history 
            WHERE customer_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (customer_id,))
        browsing_history = cursor.fetchall()
        
        # Get purchase history
        cursor.execute('''
            SELECT product_name, product_category, price, order_date 
            FROM purchase_history 
            WHERE customer_id = ?
            ORDER BY order_date DESC
            LIMIT 10
        ''', (customer_id,))
        purchase_history = cursor.fetchall()

        # Get detailed customer segment information
        cursor.execute('''
            SELECT 
                customer_segment,
                avg_order_value,
                last_active_season,
                (SELECT COUNT(*) FROM purchase_history WHERE customer_id = ?) as total_orders,
                (SELECT SUM(price) FROM purchase_history WHERE customer_id = ?) as total_spent,
                (SELECT MAX(order_date) FROM purchase_history WHERE customer_id = ?) as last_purchase_date
            FROM customer_segments 
            WHERE customer_id = ?
        ''', (customer_id, customer_id, customer_id, customer_id))
        
        segment = cursor.fetchone()

        # Format segment data
        segment_data = {
            "segment": segment[0] if segment else "Standard",
            "avg_order_value": float(segment[1]) if segment else 0.0,
            "last_active_season": segment[2] if segment else "Unknown",
            "total_orders": segment[3] if segment else 0,
            "total_spent": float(segment[4]) if segment else 0.0,
            "last_purchase_date": segment[5] if segment else None
        } if segment else None

        return {
            "profile": {
                "customer_id": profile[0],
                "full_name": profile[1],
                "email": profile[2],
                "username": profile[3],
                "phone_number": profile[4],
                "age": profile[5],
                "gender": profile[6],
                "location": profile[7]
            },
            "segment": segment_data,
            "addresses": [
                {
                    "address_id": addr[0],
                    "address_type": addr[1],
                    "address": addr[2]
                } for addr in addresses
            ],
            "browsing_history": [
                {
                    "category": history[0],
                    "timestamp": history[1]
                } for history in browsing_history
            ],
            "purchase_history": [
                {
                    "product_name": purchase[0],
                    "product_category": purchase[1],
                    "price": float(purchase[2]),
                    "order_date": purchase[3]
                } for purchase in purchase_history
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        conn.close()

@app.post("/customer/update-behavior")
async def update_behavior(behavior: BehaviorUpdate):
    print("Received Request:", behavior.dict())  # ✅ Log incoming request
    conn = customer_agent.get_connection()
    cursor = conn.cursor()
    
    try:
        # Validate customer exists
        cursor.execute("SELECT COUNT(*) FROM customer_profiles WHERE customer_id = ?", (behavior.customer_id,))
        if cursor.fetchone()[0] == 0:
            print("Customer not found:", behavior.customer_id)  # ✅ Log missing customer
            raise HTTPException(status_code=404, detail="Customer not found")

        # Store browsing history
        if behavior.browsing_category:
            cursor.execute('''
                INSERT INTO browsing_history (customer_id, category, timestamp) 
                VALUES (?, ?, datetime('now'))
            ''', (behavior.customer_id, behavior.browsing_category))
            conn.commit()
            print(f"Browsing data inserted: {behavior.customer_id} - {behavior.browsing_category}")  # ✅ Log success
            
            # Update recommendations based on new browsing data
            from recommendation_api import process_browsing
            await process_browsing({
                "customer_id": behavior.customer_id,
                "category": behavior.browsing_category
            })

            return {"message": "Browsing history updated successfully"}
    
        # Store purchase history
        if behavior.purchases:
            for purchase in behavior.purchases:
                print("Inserting purchase:", purchase.dict())  # ✅ Log each purchase
                cursor.execute('''
                    INSERT INTO purchase_history (customer_id, product_name, product_category, price, order_date) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (behavior.customer_id, purchase.product_name, purchase.product_category, purchase.price, purchase.order_date))
            conn.commit() # ✅ Commit after inserting purchases
            print(f"Purchase history updated for {behavior.customer_id}")

        # Update customer segments based on purchase history
        cursor.execute('''
            REPLACE INTO customer_segments (customer_id, avg_order_value, last_active_season, customer_segment)
            SELECT 
                ph.customer_id,
                COALESCE(AVG(ph.price), 0),
                CASE
                    WHEN MAX(ph.order_date) >= DATE('now', '-3 months') THEN 'Recent'
                    WHEN MAX(ph.order_date) >= DATE('now', '-6 months') THEN 'Semi-Recent'
                    ELSE 'Inactive'
                END,
                CASE
                    WHEN AVG(ph.price) > 100 THEN 'Premium'
                    WHEN AVG(ph.price) BETWEEN 50 AND 100 THEN 'Regular'
                    ELSE 'Budget'
                END
            FROM purchase_history ph
            WHERE ph.customer_id = ?
            GROUP BY ph.customer_id
        ''', (behavior.customer_id,))

        conn.commit()
        print(f"Customer segment updated for {behavior.customer_id}")

        return {"message": "Behavior updated successfully"}
    
    except Exception as e:
        print(f"Error updating behavior: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        conn.close()

# Add the recommendation router to the app
app.include_router(recommendation_router)

# Initialize databases
@app.on_event("startup")
async def startup_event():
    # Initialize recommendation database
    initialize_recommendation_database()

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
