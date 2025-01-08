from flask import Flask, render_template, request, jsonify
import base64

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process-drawing', methods = ['POST'])
def process_drawing():
    data = request.json.get("image")

    # Decode the base64 image (data:image/png:base64,...)
    header, encodeed = data.split(",", 1)
    decoded = base64.b64decode(encodeed)

    # TODO: Save the image for processing

    # TODO: Add image processing logic

    # TODO: return the result


if  __name__ == '__main__':
    app.run(debug = True)
