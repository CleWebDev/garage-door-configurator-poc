import os
import subprocess
import sys

def setup_application():
    """Setup the garage door configurator application"""
    
    print("Setting up Garage Door Configurator...")
    
    # Create directory structure
    directories = [
        'static/images',
        'static/css',
        'static/js',
        'templates',
        'models',
        'data'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Generate training data
    print("\nGenerating synthetic training data...")
    try:
        from generate_data import save_training_data
        save_training_data()
        print("✓ Training data generated successfully")
    except Exception as e:
        print(f"✗ Error generating training data: {e}")
        return False
    
    # Train the ML model
    print("\nTraining machine learning model...")
    try:
        from models.recommendation_model import ProductRecommendationModel
        model = ProductRecommendationModel()
        print("✓ ML model trained successfully")
    except Exception as e:
        print(f"✗ Error training ML model: {e}")
        return False
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Add your garage door images to static/images/")
    print("   Required files:")
    print("   - grey-narrow.webp")
    print("   - grey-narrow-windows.webp") 
    print("   - grey-wide.webp")
    print("   - grey-wide-windows.webp")
    print("   - white-narrow.webp")
    print("   - white-narrow-windows.webp")
    print("   - white-wide.webp")
    print("   - white-wide-windows.webp")
    print("\n2. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print("\n3. Run the application:")
    print("   python app.py")
    
    return True

if __name__ == "__main__":
    setup_application()