from flask import Flask, render_template, request, jsonify
import os
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random
from openai import OpenAI
from models.recommendation_model import ProductRecommendationModel
import threading
import time

# Load environment variables from .env file if it exists
def load_env_file():
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value

load_env_file()

app = Flask(__name__)

# Initialize OpenAI client
openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    print("Warning: OPENAI_API_KEY not found. Weather recommendations will not work.")
    client = None
else:
    client = OpenAI(api_key=openai_key)

# Initialize ML model with error handling
try:
    recommendation_model = ProductRecommendationModel()
    print("✓ ML model loaded successfully")
except Exception as e:
    print(f"⚠️ ML model failed to load: {e}")
    print("⚠️ Using fallback recommendations")
    recommendation_model = None

# Independence, Ohio coordinates
INDEPENDENCE_LAT = 41.382
INDEPENDENCE_LON = -81.641

def get_fallback_recommendations(color, slate_width, windows):
    """Fallback recommendations when ML model fails"""
    products = {
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
        }
    }
    
    # Basic rule-based recommendations
    recommendations = []
    
    # Always recommend these basics
    recommendations.append(products['garage_door_opener'])
    recommendations.append(products['remote_control'])
    recommendations.append(products['safety_sensors'])
    
    # Add weather stripping for wide doors or white doors (premium choice)
    if slate_width == 'wide' or color == 'white':
        recommendations.append(products['weather_stripping'])
    
    return recommendations

def get_weather_grid_info():
    """Get the grid information for Independence, Ohio from NWS"""
    try:
        import requests
        url = f"https://api.weather.gov/points/{INDEPENDENCE_LAT},{INDEPENDENCE_LON}"
        response = requests.get(url, headers={'User-Agent': 'GarageDoorApp/1.0'})
        if response.status_code == 200:
            data = response.json()
            return {
                'gridId': data['properties']['gridId'],
                'gridX': data['properties']['gridX'],
                'gridY': data['properties']['gridY']
            }
    except Exception as e:
        print(f"Error getting grid info: {e}")
    return None

def fetch_weather_forecast_sync():
    """Fetch weather forecast from National Weather Service (synchronous)"""
    try:
        import requests
        
        grid_info = get_weather_grid_info()
        if not grid_info:
            print("Failed to get grid info for Independence, Ohio")
            return None
            
        url = f"https://api.weather.gov/gridpoints/{grid_info['gridId']}/{grid_info['gridX']},{grid_info['gridY']}/forecast"
        print(f"Fetching weather from: {url}")
        
        headers = {'User-Agent': 'GarageDoorApp/1.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            periods = data['properties']['periods'][:6]  # Get next 6 periods
            print(f"Successfully fetched {len(periods)} weather periods")
            return periods
        else:
            print(f"Weather API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching weather: {e}")
    return None

async def fetch_weather_forecast():
    """Fetch weather forecast from National Weather Service"""
    try:
        grid_info = get_weather_grid_info()
        if not grid_info:
            return None
            
        url = f"https://api.weather.gov/gridpoints/{grid_info['gridId']}/{grid_info['gridX']},{grid_info['gridY']}/forecast"
        
        async with aiohttp.ClientSession() as session:
            headers = {'User-Agent': 'GarageDoorApp/1.0'}
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['properties']['periods'][:6]  # Get next 6 periods
    except Exception as e:
        print(f"Error fetching weather: {e}")
    return None

def generate_weather_recommendation(weather_data, delivery_date, delivery_plus_1, delivery_plus_2):
    """Use OpenAI to generate weather description and installation recommendation"""
    try:
        if not client:
            return {
                'description': "Weather information is currently unavailable (OpenAI API key not configured).",
                'recommendation': "We recommend scheduling installation on a clear day when possible."
            }
            
        if not weather_data:
            print("No weather data available from National Weather Service")
            return {
                'description': "Weather information is currently unavailable for Independence, Ohio.",
                'recommendation': "We recommend scheduling installation on a clear day when possible."
            }
        
        print(f"Processing weather data with OpenAI for {len(weather_data)} periods")
        
        # Format weather data for OpenAI
        weather_text = ""
        for period in weather_data:
            weather_text += f"{period['name']}: {period['detailedForecast']}\n"
        
        print("Weather data for OpenAI:")
        print(weather_text)
        
        prompt = f"""Based on the following weather forecast for Independence, Ohio, write a single paragraph recommending the best day for garage door installation.

The garage door will be DELIVERED on {delivery_date.strftime('%A, %B %d')}. Installation can only happen on or after the delivery date.

Installation options (choose the best one):
- {delivery_date.strftime('%A, %B %d')} (delivery day - installation possible)
- {delivery_plus_1.strftime('%A, %B %d')} (day after delivery)
- {delivery_plus_2.strftime('%A, %B %d')} (two days after delivery)

Weather forecast:
{weather_text}

Write one paragraph starting with "For your garage door installation..." that explains which specific day from the THREE OPTIONS ABOVE is best and why. Only recommend dates on or after {delivery_date.strftime('%A, %B %d')} since that's when the door arrives. Focus on which of these three specific dates has the best weather conditions for outdoor installation work."""
        
        print("Sending request to OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print(f"OpenAI response: {content}")
        
        # Clean up the response - remove any numbering or formatting
        content = content.replace('1.', '').replace('2.', '')
        content = content.replace('**', '')  # Remove markdown bold
        content = content.strip()
        
        # Since we're only asking for one paragraph, use the entire response
        recommendation = content
        
        # Ensure proper formatting
        if not recommendation.lower().startswith('for your garage door'):
            if 'recommend' in recommendation.lower() or 'best' in recommendation.lower():
                recommendation = f"For your garage door installation, {recommendation.lower()}"
        
        return {
            'description': '',  # No weather description, only recommendation
            'recommendation': recommendation.strip()
        }
            
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return {
            'description': f"Error processing weather information for Independence, Ohio: {str(e)}",
            'recommendation': "We recommend scheduling installation on a clear day when possible."
        }

@app.route('/')
def index():
    """Render the main configurator page"""
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def configure():
    """Handle configuration request with concurrent processing"""
    try:
        data = request.json
        color = data.get('color')
        slate_width = data.get('slate_width') 
        windows = data.get('windows')
        
        # Generate delivery timeline (1-6 days)
        delivery_days = random.randint(1, 6)
        today = datetime.now()
        delivery_date = today + timedelta(days=delivery_days)
        delivery_plus_1 = delivery_date + timedelta(days=1)
        delivery_plus_2 = delivery_date + timedelta(days=2)
        
        print(f"Today: {today.strftime('%A, %B %d')}")
        print(f"Delivery in {delivery_days} days: {delivery_date.strftime('%A, %B %d')}")
        print(f"Option 2: {delivery_plus_1.strftime('%A, %B %d')}")
        print(f"Option 3: {delivery_plus_2.strftime('%A, %B %d')}")
        
        # Get ML recommendations (synchronous)
        if recommendation_model:
            try:
                recommendations = recommendation_model.predict(color, slate_width, windows == 'yes')
            except Exception as e:
                print(f"ML model error: {e}, using fallback")
                recommendations = get_fallback_recommendations(color, slate_width, windows == 'yes')
        else:
            recommendations = get_fallback_recommendations(color, slate_width, windows == 'yes')
        
        # Fetch weather data (synchronous)
        try:
            weather_data = fetch_weather_forecast_sync()
        except Exception as e:
            print(f"Weather fetch error: {e}")
            weather_data = None
        
        # Generate weather recommendation using OpenAI
        weather_info = generate_weather_recommendation(
            weather_data, delivery_date, delivery_plus_1, delivery_plus_2
        )
        
        result = {
            'recommendations': recommendations,
            'delivery_date': delivery_date.strftime('%B %d'),
            'delivery_days': delivery_days,
            'weather_description': weather_info['description'],
            'weather_recommendation': weather_info['recommendation'],
            'delivery_options': {
                'option1': delivery_date.strftime('%A, %B %d'),
                'option2': delivery_plus_1.strftime('%A, %B %d'),
                'option3': delivery_plus_2.strftime('%A, %B %d')
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in configure: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/order', methods=['POST'])
def place_order():
    """Handle order placement"""
    try:
        data = request.json
        order_id = f"GD{random.randint(10000, 99999)}"
        
        return jsonify({
            'order_id': order_id,
            'message': f'Your garage door order #{order_id} has been placed successfully!',
            'status': 'confirmed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)