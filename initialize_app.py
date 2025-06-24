#!/usr/bin/env python3
"""
Initialize the garage door configurator application
This script sets up all required components before running the main app
"""

import os
import sys

def check_and_create_directories():
    """Ensure all required directories exist"""
    directories = ['models', 'data', 'static/images', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory: {directory}")

def create_init_file():
    """Create __init__.py in models directory"""
    init_file = 'models/__init__.py'
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Models package\n')
        print("✓ Created models/__init__.py")

def generate_training_data():
    """Generate synthetic training data"""
    try:
        from generate_data import save_training_data
        if not os.path.exists('data/product_recommendations.csv'):
            print("Generating training data...")
            save_training_data()
            print("✓ Training data generated")
        else:
            print("✓ Training data already exists")
    except Exception as e:
        print(f"✗ Error generating training data: {e}")
        return False
    return True

def train_model():
    """Train the ML model"""
    try:
        # Check if model files exist
        if os.path.exists('models/recommendation_model.pkl') and os.path.exists('models/encoders.pkl'):
            print("✓ ML model already trained")
            return True
            
        print("Training ML model...")
        from models.recommendation_model import ProductRecommendationModel
        model = ProductRecommendationModel()
        print("✓ ML model trained successfully")
        return True
    except Exception as e:
        print(f"✗ Error training model: {e}")
        return False

def check_images():
    """Check if required images exist"""
    required_images = [
        'grey-narrow.webp',
        'grey-narrow-windows.webp', 
        'grey-wide.webp',
        'grey-wide-windows.webp',
        'white-narrow.webp',
        'white-narrow-windows.webp',
        'white-wide.webp',
        'white-wide-windows.webp'
    ]
    
    missing_images = []
    for image in required_images:
        if not os.path.exists(f'static/images/{image}'):
            missing_images.append(image)
    
    if missing_images:
        print("⚠️  Missing garage door images:")
        for image in missing_images:
            print(f"   - static/images/{image}")
        print("\nAdd these images to static/images/ directory")
        return False
    else:
        print("✓ All garage door images found")
        return True

def check_environment():
    """Check environment variables"""
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("   Weather recommendations will not work without it")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    else:
        print("✓ OPENAI_API_KEY is set")
        return True

def main():
    """Main initialization function"""
    print("Initializing Garage Door Configurator...")
    print("=" * 50)
    
    # Step 1: Create directories
    check_and_create_directories()
    
    # Step 2: Create __init__.py
    create_init_file()
    
    # Step 3: Generate training data
    if not generate_training_data():
        print("Failed to generate training data. Exiting.")
        sys.exit(1)
    
    # Step 4: Train model
    if not train_model():
        print("Failed to train model. Exiting.")
        sys.exit(1)
    
    # Step 5: Check images
    images_ok = check_images()
    
    # Step 6: Check environment
    env_ok = check_environment()
    
    print("\n" + "=" * 50)
    if images_ok and env_ok:
        print("✅ Application ready!")
        print("Run: python app.py")
    else:
        print("⚠️  Application partially ready")
        if not images_ok:
            print("   - Add missing images to continue")
        if not env_ok:
            print("   - Set OPENAI_API_KEY for full functionality")
        print("   - You can still run: python app.py")

if __name__ == "__main__":
    main()