import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import random

class ProductRecommendationModel:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.products = self._get_products()
        self.model_path = 'models/recommendation_model.pkl'
        self.encoders_path = 'models/encoders.pkl'
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Load or train model
        if os.path.exists(self.model_path) and os.path.exists(self.encoders_path):
            self.load_model()
        else:
            self.train_model()
    
    def _get_products(self):
        """Define available additional products"""
        return {
            'garage_door_opener': {
                'name': 'Smart Garage Door Opener',
                'price': 299.99,
                'description': 'WiFi-enabled opener with smartphone app control'
            },
            'remote_control': {
                'name': 'Universal Remote Control (2-pack)',
                'price': 49.99,
                'description': 'Compatible remote controls with rolling code technology'
            },
            'safety_sensors': {
                'name': 'Photoelectric Safety Sensors',
                'price': 79.99,
                'description': 'Infrared safety beam sensors for enhanced protection'
            },
            'weather_stripping': {
                'name': 'Premium Weather Seal Kit',
                'price': 34.99,
                'description': 'Complete weather stripping kit for energy efficiency'
            },
            'smart_controller': {
                'name': 'Smart Home Controller Hub',
                'price': 199.99,
                'description': 'Integrate with Alexa, Google Home, and Apple HomeKit'
            },
            'backup_battery': {
                'name': 'Emergency Backup Battery',
                'price': 149.99,
                'description': 'Ensures operation during power outages'
            },
            'keypad_entry': {
                'name': 'Wireless Keypad Entry',
                'price': 89.99,
                'description': 'Convenient keyless entry system'
            },
            'installation_kit': {
                'name': 'Professional Installation Hardware Kit',
                'price': 124.99,
                'description': 'Premium mounting hardware and accessories'
            },
            'insulation_kit': {
                'name': 'Garage Door Insulation Kit',
                'price': 119.99,
                'description': 'Reflective insulation panels for temperature control'
            },
            'maintenance_kit': {
                'name': 'Annual Maintenance Kit',
                'price': 59.99,
                'description': 'Lubricants, springs, and maintenance supplies'
            }
        }
    
    def _generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic training data"""
        np.random.seed(42)
        random.seed(42)
        
        data = []
        
        for _ in range(n_samples):
            # Base configuration
            color = random.choice(['grey', 'white'])
            slate_width = random.choice(['narrow', 'wide'])
            windows = random.choice([True, False])
            
            # Generate realistic product recommendations based on configuration
            recommended_products = []
            
            # Base recommendations (high probability for everyone)
            if random.random() > 0.3:  # 70% chance
                recommended_products.append('garage_door_opener')
            if random.random() > 0.4:  # 60% chance
                recommended_products.append('remote_control')
            if random.random() > 0.5:  # 50% chance
                recommended_products.append('safety_sensors')
            
            # Configuration-specific recommendations
            if windows:
                if random.random() > 0.3:  # Windows = more likely to want smart features
                    recommended_products.append('smart_controller')
                if random.random() > 0.4:
                    recommended_products.append('keypad_entry')
            
            if slate_width == 'wide':
                if random.random() > 0.4:  # Wider doors = more likely to need insulation
                    recommended_products.append('insulation_kit')
                if random.random() > 0.5:
                    recommended_products.append('weather_stripping')
            
            if color == 'white':
                if random.random() > 0.6:  # White doors = premium choice = more accessories
                    recommended_products.append('backup_battery')
                if random.random() > 0.5:
                    recommended_products.append('installation_kit')
            
            # Always include maintenance for some variety
            if random.random() > 0.7:
                recommended_products.append('maintenance_kit')
            
            # Create individual records for each recommended product
            for product in recommended_products:
                data.append({
                    'color': color,
                    'slate_width': slate_width,
                    'windows': windows,
                    'recommended_product': product,
                    'target': 1  # This product is recommended
                })
            
            # Add some negative examples (products not recommended)
            all_products = list(self.products.keys())
            not_recommended = [p for p in all_products if p not in recommended_products]
            
            # Add a few negative examples
            for product in random.sample(not_recommended, min(2, len(not_recommended))):
                data.append({
                    'color': color,
                    'slate_width': slate_width,
                    'windows': windows,
                    'recommended_product': product,
                    'target': 0  # This product is not recommended
                })
        
        return pd.DataFrame(data)
    
    def train_model(self):
        """Train the recommendation model"""
        print("Training recommendation model...")
        
        # Generate synthetic data
        df = self._generate_synthetic_data()
        
        # Encode categorical variables
        categorical_cols = ['color', 'slate_width', 'recommended_product']
        
        for col in categorical_cols:
            self.encoders[col] = LabelEncoder()
            df[col + '_encoded'] = self.encoders[col].fit_transform(df[col])
        
        # Convert boolean to int
        df['windows_encoded'] = df['windows'].astype(int)
        
        # Prepare features and target
        feature_cols = ['color_encoded', 'slate_width_encoded', 'windows_encoded', 'recommended_product_encoded']
        X = df[feature_cols]
        y = df['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Save model and encoders
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.encoders, self.encoders_path)
        
        print(f"Model trained with accuracy: {self.model.score(X_test, y_test):.3f}")
    
    def load_model(self):
        """Load pre-trained model and encoders"""
        self.model = joblib.load(self.model_path)
        self.encoders = joblib.load(self.encoders_path)
    
    def predict(self, color, slate_width, windows):
        """Predict recommended products for given configuration"""
        try:
            recommendations = []
            
            # Get probabilities for each product
            for product_key in self.products.keys():
                # Prepare input data
                input_data = {
                    'color': color,
                    'slate_width': slate_width,
                    'windows': windows,
                    'recommended_product': product_key
                }
                
                # Encode input
                encoded_data = []
                encoded_data.append(self.encoders['color'].transform([input_data['color']])[0])
                encoded_data.append(self.encoders['slate_width'].transform([input_data['slate_width']])[0])
                encoded_data.append(int(input_data['windows']))
                encoded_data.append(self.encoders['recommended_product'].transform([input_data['recommended_product']])[0])
                
                # Predict probability
                prob = self.model.predict_proba([encoded_data])[0][1]  # Probability of recommendation
                
                if prob > 0.5:  # Threshold for recommendation
                    product_info = self.products[product_key].copy()
                    product_info['probability'] = prob
                    product_info['key'] = product_key
                    recommendations.append(product_info)
            
            # Sort by probability and return top recommendations
            recommendations.sort(key=lambda x: x['probability'], reverse=True)
            return recommendations[:4]  # Return top 4 recommendations
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            # Return default recommendations as fallback
            default_products = ['garage_door_opener', 'remote_control', 'safety_sensors', 'weather_stripping']
            return [self.products[key] for key in default_products]