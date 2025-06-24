# Garage Door Configurator

A complete garage door configuration application with machine learning-powered product recommendations, weather integration, and real-time delivery estimates.

## Features

- Interactive garage door configurator with live preview
- Machine learning product recommendations based on configuration
- Weather-based delivery recommendations using OpenAI and National Weather Service
- Smooth typing animations for AI responses
- Responsive design matching the provided template

## Local Windows Setup (Virtual Environment)

### Prerequisites
- Python 3.8 or higher
- Git (optional)

### Step 1: Create Project Directory
```cmd
mkdir garage-door-app
cd garage-door-app
```

### Step 2: Create Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### Step 4: Copy Application Files
Create the following directory structure and copy the provided files:

```
garage-door-app/
├── app.py
├── generate_data.py
├── setup.py
├── requirements.txt
├── models/
│   └── recommendation_model.py
├── templates/
│   └── index.html
└── static/
    └── images/
        ├── grey-narrow.webp
        ├── grey-narrow-windows.webp
        ├── grey-wide.webp
        ├── grey-wide-windows.webp
        ├── white-narrow.webp
        ├── white-narrow-windows.webp
        ├── white-wide.webp
        └── white-wide-windows.webp
```

### Step 5: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 6: Add Garage Door Images
Copy your 8 garage door images to the `static/images/` directory with the exact filenames listed above.

### Step 7: Set OpenAI API Key
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

### Step 8: Run Setup Script
```cmd
python setup.py
```

### Step 9: Start the Application
```cmd
python app.py
```

The application will be available at `http://localhost:5000`

## Digital Ocean App Platform Deployment

### Step 1: Prepare for Deployment

Create an `app.yaml` file in your project root:

```yaml
name: garage-door-configurator
services:
- name: web
  source_dir: /
  github:
    repo: your-username/garage-door-app
    branch: main
  run_command: gunicorn app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    scope: RUN_TIME
    type: SECRET
```

### Step 2: Push to GitHub
```cmd
git init
git add .
git commit -m "Initial commit - Garage Door Configurator"
git branch -M main
git remote add origin https://github.com/your-username/garage-door-app.git
git push -u origin main
```

### Step 3: Deploy to Digital Ocean

1. **Create App on Digital Ocean:**
   - Go to Digital Ocean App Platform
   - Click "Create App"
   - Choose "GitHub" as source
   - Select your repository
   - Choose the main branch

2. **Configure Build Settings:**
   - Build Command: `python setup.py`
   - Run Command: `gunicorn app:app`
   - HTTP Port: 5000

3. **Set Environment Variables:**
   - Go to your app's Settings tab
   - Click on "Environment Variables"
   - Add the following variables:
     - Key: `OPENAI_API_KEY`
     - Value: `your-openai-api-key-here`
     - Scope: `All components`
     - Type: `Secret`

4. **Deploy:**
   - Click "Create Resources"
   - Wait for deployment to complete

### Step 4: Add OpenAI API Key in Digital Ocean

1. Navigate to your app in the Digital Ocean dashboard
2. Click on the "Settings" tab
3. Scroll down to "App-Level Environment Variables"
4. Click "Edit"
5. Add environment variable:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key
   - **Scope:** All components
   - **Type:** Secret
6. Click "Save"
7. Your app will automatically redeploy with the new environment variable

## File Structure

```
garage-door-app/
├── app.py                          # Main Flask application
├── generate_data.py                # Synthetic data generation
├── setup.py                        # Setup script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── app.yaml                        # Digital Ocean deployment config
├── models/
│   ├── __init__.py                 # Empty file to make it a package
│   ├── recommendation_model.py     # ML model for recommendations
│   ├── recommendation_model.pkl    # Trained model (generated)
│   └── encoders.pkl               # Label encoders (generated)
├── data/
│   └── product_recommendations.csv # Training data (generated)
├── templates/
│   └── index.html                 # Main HTML template
└── static/
    ├── css/                       # Additional CSS (if needed)
    ├── js/                        # Additional JS (if needed)
    └── images/                    # Garage door images
        ├── grey-narrow.webp
        ├── grey-narrow-windows.webp
        ├── grey-wide.webp
        ├── grey-wide-windows.webp
        ├── white-narrow.webp
        ├── white-narrow-windows.webp
        ├── white-wide.webp
        └── white-wide-windows.webp
```

## API Endpoints

- `GET /` - Main configurator page
- `POST /configure` - Process configuration and return recommendations
- `POST /order` - Place order

## Technology Stack

- **Backend:** Flask (Python)
- **Machine Learning:** scikit-learn with RandomForest
- **APIs:** OpenAI GPT-3.5, National Weather Service
- **Frontend:** Vanilla JavaScript with typing animations
- **Deployment:** Digital Ocean App Platform with Gunicorn

## Features in Detail

### Machine Learning Model
- Uses RandomForest classifier trained on synthetic data
- Considers configuration options, customer preferences, and product categories
- Provides personalized product recommendations based on door configuration

### Weather Integration
- Fetches real-time weather data from National Weather Service API
- Uses OpenAI to generate natural language weather descriptions
- Provides installation day recommendations based on weather conditions
- Specifically uses Independence, Ohio coordinates (41°22′55″N 81°38′27″W)

### Async Processing
- Concurrent API calls to weather service and ML model
- Improves response time by running tasks in parallel
- Smooth user experience with loading indicators

### Typing Animation
- ChatGPT-style typing effect for weather recommendations
- Enhances user engagement and perceived intelligence
- Configurable typing speed

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError for models package:**
   ```cmd
   # Create empty __init__.py file in models directory
   echo. > models\__init__.py
   ```

2. **OpenAI API Key not working:**
   - Verify the key is correct
   - Check that environment variable is set properly
   - Ensure you have credits in your OpenAI account

3. **Weather API not responding:**
   - Check internet connection
   - Verify National Weather Service API is accessible
   - The app will gracefully handle weather API failures

4. **Images not loading:**
   - Ensure all 8 image files are in static/images/
   - Check file names match exactly (case sensitive)
   - Verify file format is .webp

### Local Development Tips

- Use `python app.py` for development with debug mode
- Check console logs for detailed error messages
- Test each component separately if issues arise

### Digital Ocean Deployment Issues

- Check build logs in the Digital Ocean dashboard
- Verify all environment variables are set correctly
- Ensure requirements.txt includes all dependencies
- Monitor application logs for runtime errors

## Support

For issues with this application, check:
1. Console logs in browser developer tools
2. Server logs (locally or in Digital Ocean dashboard)
3. Verify all API keys and dependencies are correctly configured