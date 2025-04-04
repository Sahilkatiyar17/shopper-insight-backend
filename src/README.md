
# E-Commerce Recommendation System

This backend system provides personalized product recommendations for e-commerce users based on their browsing history, purchase history, and customer segment.

## Features

- Content-based filtering using browsing and purchase history
- Collaborative filtering based on user segments
- Product category weighting based on user interests
- Recommendation storage in SQLite database
- Integration with FastAPI application

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the FastAPI application:

```bash
python main.py
```

## API Endpoints

### Customer Endpoints

- `POST /customer/create` - Create a new customer
- `POST /customer/add-address` - Add address(es) to a customer
- `GET /customer/get-profile/{customer_id}` - Get customer profile
- `POST /customer/update-behavior` - Update customer browsing or purchase behavior

### Recommendation Endpoints

- `GET /recommendations/{customer_id}` - Get personalized recommendations for a customer
- `POST /recommendations/process-browsing` - Process a new browsing interaction
- `POST /recommendations/process-purchase` - Process a new purchase interaction

## Testing

Run the test script to create a sample customer and generate recommendations:

```bash
python test_recommendations.py
```

## How It Works

1. Customer data is stored in the SQLite database
2. When a customer logs in or views their profile, recommendations are generated based on:
   - Their browsing history
   - Their purchase history
   - Their customer segment (Premium, Regular, Budget)
   - Similar customers' behaviors
3. Recommendations are stored in the database with a timestamp
4. Recent recommendations are reused to improve performance
5. New interactions trigger recalculation of recommendations

## Database Schema

The system uses several tables:
- `customer_profiles` - Basic customer information
- `customer_addresses` - Customer shipping and billing addresses
- `browsing_history` - Customer browsing activities
- `purchase_history` - Customer purchase records
- `customer_segments` - Customer segmentation data
- `product_catalog` - Product information
- `customer_recommendations` - Stored recommendations for customers
