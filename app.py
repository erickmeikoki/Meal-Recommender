from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from google.cloud import vision, storage
import requests
import json
import logging
import sys
from flask_cors import CORS
from PIL import Image
import pillow_heif
import datetime
import io
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    stream=sys.stdout  # Ensure logs go to stdout for Google Cloud Logging
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}

# API Configuration
SPOONACULAR_BASE_URL = os.getenv('SPOONACULAR_BASE_URL', 'https://api.spoonacular.com')
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize Google Cloud clients
try:
    vision_client = vision.ImageAnnotatorClient()
    storage_client = storage.Client()
    bucket_name = "meal-recommender-uploads-kitchenapp"
    bucket = storage_client.bucket(bucket_name)
    logger.info("Successfully initialized Google Cloud clients")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud clients: {e}")
    raise

if not SPOONACULAR_API_KEY:
    logger.error("Spoonacular API key not found in environment variables")
    raise ValueError("Spoonacular API key is required")
logger.info("Successfully configured Spoonacular API")

def detect_objects(image_url):
    """Detect objects in an image using Google Cloud Vision API."""
    try:
        image = vision.Image()
        image.source.image_uri = image_url
        
        # Perform label detection
        response = vision_client.label_detection(image=image)
        labels = response.label_annotations
        
        # Filter for food-related labels
        food_items = [
            label.description for label in labels 
            if label.score >= 0.7 and any(
                food_term in label.description.lower() 
                for food_term in ['food', 'fruit', 'vegetable', 'meat', 'dish', 'ingredient']
            )
        ]
        
        return food_items
    except Exception as e:
        logger.error(f"Error in detect_objects: {e}")
        raise

def get_recipe_suggestions(ingredients):
    """Get recipe suggestions from Spoonacular API."""
    try:
        # Join ingredients with commas for the API query
        ingredients_str = ','.join(ingredients)
        
        # Check if API key is configured
        if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == "YOUR_API_KEY_HERE":
            logger.error("Spoonacular API key not properly configured")
            return []  # Return empty list instead of raising an error
            
        # Make request to Spoonacular API
        response = requests.get(
            f"{SPOONACULAR_BASE_URL}/recipes/findByIngredients",
            params={
                "ingredients": ingredients_str,
                "apiKey": SPOONACULAR_API_KEY,
                "number": 5,
                "ranking": 2,
                "ignorePantry": True
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Spoonacular API error: {response.status_code} - {response.text}")
            return []  # Return empty list on API error
            
        recipes = response.json()
        
        # Add recipe URLs to each recipe
        for recipe in recipes:
            recipe['url'] = f"https://spoonacular.com/recipes/{recipe['title'].lower().replace(' ', '-')}-{recipe['id']}"
            
        return recipes
    except Exception as e:
        logger.error(f"Error in get_recipe_suggestions: {e}")
        return []  # Return empty list on any error

@app.route('/')
def home():
    return render_template('index.html')

def upload_to_gcs(file_stream, content_type):
    """Upload a file to Google Cloud Storage."""
    try:
        # Create a unique filename using timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        blob_name = f"uploads/{timestamp}-{secure_filename(file_stream.filename)}"
        
        # Create a new blob and upload the file's content
        blob = bucket.blob(blob_name)
        blob.upload_from_file(file_stream, content_type=content_type)
        
        # Make the blob publicly readable
        blob.make_public()
        
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading to GCS: {e}")
        raise

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
            
        try:
            # Handle HEIC images
            if file.filename.lower().endswith('.heic'):
                heif_file = pillow_heif.read_heif(file)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )
                # Save as JPEG in memory
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                file = img_byte_arr
                content_type = 'image/jpeg'
            else:
                content_type = file.content_type
                
            # Upload to Google Cloud Storage
            image_url = upload_to_gcs(file, content_type)
            
            # Detect objects in the image
            try:
                food_items = detect_objects(image_url)
            except Exception as e:
                logger.error(f"Error detecting objects: {e}")
                food_items = []
            
            # Get recipe suggestions
            recipes = get_recipe_suggestions(food_items)
            
            return jsonify({
                'detected_items': food_items,
                'image_url': image_url,
                'recipes': recipes
            })
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return jsonify({
                'error': 'Error processing image',
                'detected_items': [],
                'recipes': []
            }), 500
            
    except Exception as e:
        logger.error(f"Error in analyze_image endpoint: {e}")
        return jsonify({
            'error': str(e),
            'detected_items': [],
            'recipes': []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 