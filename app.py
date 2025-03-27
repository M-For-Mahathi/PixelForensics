from flask import Flask, request, jsonify, send_from_directory
import os
from database import db, ScanResult
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deepfake_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create Uploads Folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store Deepfake Scan Results
@app.route('/store_result', methods=['POST'])
def store_result():
    data = request.json
    filename = data.get('filename')
    prediction = data.get('prediction')
    confidence = data.get('confidence')

    if not filename or not prediction or confidence is None:
        return jsonify({"error": "Missing data"}), 400

    new_result = ScanResult(filename=filename, prediction=prediction, confidence=confidence)
    db.session.add(new_result)
    db.session.commit()

    return jsonify({"message": "Result stored successfully!"}), 201

# Image Upload Route
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    return jsonify({"message": "Upload successful", "image_url": f"/images/{image.filename}"}), 201

# Serve Uploaded Images
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Video Upload Route
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(video_path)

    return jsonify({"message": "Upload successful", "video_url": f"/videos/{video.filename}"}), 201

# Serve Uploaded Videos
@app.route('/videos/<filename>')
def get_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API Status Check
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "API is running!"})

@app.route('/detect-deepfake', methods=['POST'])
def detect_deepfake():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the video
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(video_path)

    # Dummy AI Model (Replace this with actual deepfake detection logic)
    import random
    is_deepfake = random.choice([True, False])  # Simulating detection
    confidence = random.randint(70, 99)  # Simulating confidence percentage

    # Dummy reasons for deepfake detection
    facial_artifacts = "Unnatural blurring and inconsistencies detected." if is_deepfake else "No facial anomalies found."
    lighting_issues = "Shadows and reflections do not match real-world physics." if is_deepfake else "Lighting appears natural."
    pixel_anomalies = "Irregular pixel distribution suggests AI-generated content." if is_deepfake else "No pixel anomalies detected."

    # API Response
    return jsonify({
        "is_deepfake": is_deepfake,
        "confidence": confidence,
        "facial_artifacts": facial_artifacts,
        "lighting_issues": lighting_issues,
        "pixel_anomalies": pixel_anomalies
    })

# Run Flask App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
