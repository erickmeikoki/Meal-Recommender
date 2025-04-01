# Food Image Analyzer

A web application that analyzes food images using Google Cloud Vision API and suggests recipes using the Spoonacular API.

## Live Demo

Visit the application at: [https://kitchenapp-455317.uc.r.appspot.com](https://kitchenapp-455317.uc.r.appspot.com)

## Features

- Upload food images (supports JPG, PNG, HEIC formats)
- Detect food items in images using Google Cloud Vision API
- Get recipe suggestions based on detected ingredients
- Modern, responsive UI with drag-and-drop upload
- HEIC image format support for iOS users

## Technologies Used

- Backend:
  - Python 3.9
  - Flask
  - Google Cloud Vision API
  - Google Cloud Storage
  - Spoonacular API
- Frontend:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

## Setup

1. Clone the repository:

   ```bash
   git clone [repository-url]
   cd food-image-analyzer
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   Create a `.env` file with:

   ```
   SPOONACULAR_API_KEY=your_api_key_here
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
   ```

4. Run the application:

   ```bash
   python app.py
   ```

## Deployment

The application is deployed on Google App Engine:

1. Update `env_variables.yaml` with your API keys
2. Deploy using:

   ```bash
   gcloud app deploy app.yaml
   ```

## Usage

1. Click the upload button or drag and drop an image of your ingredients
2. Wait for the image processing and ingredient detection
3. Review the detected ingredients
4. Browse through suggested recipes
5. Click on any recipe to view detailed information and cooking instructions

## API Requirements

- **Google Cloud Vision API**: Required for ingredient detection from images
- **Spoonacular API**: Required for recipe suggestions and details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
