import PIL.Image
import threading
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import os
import base64
from io import BytesIO

# Config the Google AI API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API key not add to env variable")
genai.configure(api_key = API_KEY)

app = Flask(__name__)

# Uploads directory exists
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

# Timer and tracking for the last saved image
timer = None
extracted_text = ""


def text_extraction(image_path):
    global extracted_text

    image_path = image_path.strip()

    try:
        sample_file = PIL.Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        return

    # Choose a Gemini Model
    model = genai.GenerativeModel(model_name = 'gemini-1.5-flash')

    #  Prompt
    prompt = "Extract text for the handwriting (only provide text of the image in the response nothing else"

    # Get the text
    try:
        response = model.generate_content([prompt, sample_file])

        # Prepare the output data
        new_entry = {
            "ID": f"Image_ID_{image_path}",
            "Text": response.text
        }

        # output dir exist
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok = True)

        # Save the respone in  JSON format
        output_file_path = os.path.join(output_dir, "output_file.json")

        # Load existing data if the file exists
        if os.path.exists(output_file_path):
            try:
                with open(output_file_path, 'r') as json_file:
                    existing_data = json.load(json_file)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except json.JSONDecodeError:
                print("Error reading existing JSON file. Creating a new one")
                existing_data  =[]

        else:
            existing_data = []

        # Append the new entry
        existing_data.append(new_entry)

        # Save and Update the JSON file
        with open(output_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent = 4)

        text = response.text

        if text:
            extracted_text = text
        else:
            extracted_text = "No text detected."

        # Display the text
        print(text)

        return jsonify({"message": "Image saved successfully with white background!", "extracted_text": extracted_text}), 200

    except Exception as e:
        print(f"Error is extracting text: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process-drawing', methods = ['POST'])
def process_drawing():
    global timer

    try:
        data = request.json.get("image")
        if not data:
            return jsonify({"error": "No image data provided"}), 400

        # Decode the base64 image (data:image/png:base64,...)
        header, encoded = data.split(",", 1)
        decoded = base64.b64decode(encoded)

        # Open the image with Pillow
        image = PIL.Image.open(BytesIO(decoded))

        # Create a new image with a white background
        width, height = image.size
        white_background = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 255))  # White background
        white_background.paste(image, (0, 0), image.convert("RGBA").split()[3])  # Paste image with transparency mask

        # Save the image with the white background
        image_path = os.path.join(UPLOAD_FOLDER, 'drawing_with_white_background.png')
        white_background.save(image_path)

        # Function to handle text extraction
        def extract():
            #nonlocal extracted_text
            with app.app_context():  # Ensure Flask app context for the thread
                text_extraction(image_path)

        # Reset the timer
        if timer:
            timer.cancel()

        # Start a new timer
        timer = threading.Timer(10.0, extract)
        timer.start()

        # Wait for the thread to complete
        timer.join()

        # Return the extracted text after the thread finishes
        return jsonify({
            "message": "Image saved successfully with white background!",
            "extracted_text": extracted_text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if  __name__ == '__main__':
    app.run(debug = True)
