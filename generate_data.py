import pandas as pd
import numpy as np
import random
import os

def generate_synthetic_data():
    """Generate synthetic data for garage door product recommendations"""
    
    # Set seeds for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Define product catalog
    products = {
        'garage_door_opener': {
            'name': 'Smart Garage Door Opener',
            'price': 299.99,
            'category': 'automation'
        },
        'remote_control': {
            'name': 'Universal Remote Control (2-pack)',
            'price': 49.99,
            'category': 'automation'
        },
        'safety_sensors': {
            'name': 'Photoelectric Safety Sensors',
            'price': 79.99,
            'category': 'safety'
        },
        'weather_stripping': {
            'name': 'Premium Weather Seal Kit',
            'price': 34.99,
            'category': 'weatherization'
        },
        'smart_controller': {
            'name': 'Smart Home Controller Hub',
            'price': 199.99,
            'category': 'automation'
        },
        'backup_battery': {
            'name': 'Emergency Backup Battery',
            'price': 149.99,
            'category': 'power'
        },
        'keypad_entry': {
            'name': 'Wireless Keypad Entry',
            'price': 89.99,
            'category': 'security'
        },
        'installation_kit': {
            'name': 'Professional Installation Hardware Kit',
            'price': 124.99,
            'category': 'installation'
        },
        'insulation_kit': {
            'name': 'Garage Door Insulation Kit',
            'price': 119.99,
            'category': 'weatherization'
        },
        'maintenance_kit': {
            'name': 'Annual Maintenance Kit',
            'price': 59.99,
            'category': 'maintenance'
        }
    }
    
    # Configuration options
    colors = ['grey', 'white']
    slate_widths = ['narrow', 'wide']
    window_options = [True, False]
    
    data = []
    
    # Generate 2000 samples
    for i in range(2000):
        # Random configuration
        color = random.choice(colors)
        slate_width = random.choice(slate_widths)
        windows = random.choice(window_options)
        
        # Generate customer preferences based on realistic scenarios
        customer_budget = random.choice(['low', 'medium', 'high'])
        tech_savvy = random.choice([True, False])
        security_conscious = random.choice([True, False])
        
        # Base probability for each product
        product_probabilities = {}
        
        for product_key, product_info in products.items():
            base_prob = 0.3  # Base 30% chance
            
            # Adjust based on configuration
            if color == 'white':  # White doors are premium
                base_prob += 0.1
            
            if windows:  # Windows suggest higher-end preferences
                base_prob += 0.15
                if product_info['category'] == 'automation':
                    base_prob += 0.2
                if product_info['category'] == 'security':
                    base_prob += 0.15
            
            if slate_width == 'wide':  # Wider doors need more accessories
                if product_info['category'] == 'weatherization':
                    base_prob += 0.2
                if product_info['category'] == 'installation':
                    base_prob += 0.1
            
            # Adjust based on customer profile
            if customer_budget == 'high':
                base_prob += 0.2
            elif customer_budget == 'low':
                base_prob -= 0.15
            
            if tech_savvy and product_info['category'] == 'automation':
                base_prob += 0.25
            
            if security_conscious and product_info['category'] == 'security':
                base_prob += 0.3
            
            # Product-specific adjustments
            if product_key == 'garage_door_opener':
                base_prob += 0.3  # Very popular
            elif product_key == 'remote_control':
                base_prob += 0.25  # Very common
            elif product_key == 'safety_sensors':
                base_prob += 0.2  # Safety is important
            elif product_key == 'weather_stripping':
                if slate_width == 'wide':
                    base_prob += 0.15
            elif product_key == 'smart_controller':
                if windows and tech_savvy:
                    base_prob += 0.2
            elif product_key == 'backup_battery':
                if customer_budget == 'high':
                    base_prob += 0.15
            
            # Cap probability at 0.9
            product_probabilities[product_key] = min(base_prob, 0.9)
        
        # Generate recommendations for this configuration
        for product_key, probability in product_probabilities.items():
            # Determine if this product is recommended
            is_recommended = random.random() < probability
            
            data.append({
                'color': color,
                'slate_width': slate_width,
                'windows': windows,
                'customer_budget': customer_budget,
                'tech_savvy': tech_savvy,
                'security_conscious': security_conscious,
                'product': product_key,
                'product_category': products[product_key]['category'],
                'product_price': products[product_key]['price'],
                'recommended': 1 if is_recommended else 0
            })
    
    return pd.DataFrame(data)

def save_training_data():
    """Generate and save training data"""
    print("Generating synthetic training data...")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Generate data
    df = generate_synthetic_data()
    
    # Save to CSV
    df.to_csv('data/product_recommendations.csv', index=False)
    
    print(f"Generated {len(df)} training samples")
    print(f"Configurations: {len(df[['color', 'slate_width', 'windows']].drop_duplicates())} unique")
    print(f"Products: {len(df['product'].unique())} different products")
    print("Data saved to data/product_recommendations.csv")
    
    # Display sample statistics
    print("\nRecommendation rates by product:")
    recommendation_rates = df.groupby('product')['recommended'].mean().sort_values(ascending=False)
    for product, rate in recommendation_rates.items():
        print(f"  {product}: {rate:.1%}")

if __name__ == "__main__":
    save_training_data()