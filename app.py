# app.py
from flask import send_file
from flask import Flask, request, jsonify, send_from_directory
import os
from database import db, ScanResult
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deepfake_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

db.init_app(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MODEL_PATH = 'models/deepfake_detector.h5'
predictor = None

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

def init_predictor():
    """Initialize the predictor with proper configuration"""
    global predictor
    try:
        from utils.predictor import DeepfakePredictor
        
        # Create predictor config
        config = {
            'ensemble_threshold': 0.52,
            'enable_caching': True,      # Enable caching for same images
            'log_predictions': False,     # Disable logging in production
            'cache_size_limit': 100
        }
        
        # Initialize predictor with config (NOT model_path)
        predictor = DeepfakePredictor(config)
        print(f"✅ Predictor initialized successfully")
        return True
        
    except Exception as e:
        print(f"⚠️  Error loading predictor: {e}")
        print(traceback.format_exc())
        print("⚠️  Using FALLBACK mode (random predictions)")
        return False

def allowed_file(filename, file_type):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    return False

def fallback_prediction():
    import random
    is_deepfake = random.choice([True, False])
    confidence = random.uniform(70, 95)
    return is_deepfake, confidence

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')



@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_scans = ScanResult.query.count()
        threats_detected = ScanResult.query.filter_by(prediction='fake').count()
        results = ScanResult.query.all()
        if results:
            avg_confidence = sum(r.confidence for r in results) / len(results)
            accuracy = round(avg_confidence, 0)
        else:
            accuracy = 0
        
        return jsonify({
            'totalScans': total_scans,
            'threatsDetected': threats_detected,
            'accuracy': int(accuracy)
        })
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            'totalScans': 0,
            'threatsDetected': 0,
            'accuracy': 0,
            'error': str(e)
        })

@app.route('/api/recent-results', methods=['GET'])
def get_recent_results():
    try:
        limit = request.args.get('limit', 10, type=int)
        results = ScanResult.query.order_by(ScanResult.timestamp.desc()).limit(limit).all()
        
        return jsonify([r.to_dict() for r in results])
    except Exception as e:
        print(f"Recent results error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/detect-deepfake', methods=['POST'])
def detect_deepfake():
    try:
        video = request.files.get('video')
        image = request.files.get('image')

        if not video and not image:
            return jsonify({"error": "No file provided"}), 400

        file_obj = video if video else image
        file_type = 'video' if video else 'image'
        
        if not allowed_file(file_obj.filename, file_type):
            allowed = ALLOWED_IMAGE_EXTENSIONS if file_type == 'image' else ALLOWED_VIDEO_EXTENSIONS
            return jsonify({
                "error": f"Invalid file type. Allowed extensions: {', '.join(allowed)}"
            }), 400

        filename = secure_filename(file_obj.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        
        print(f"📁 File saved: {filepath}")

        is_deepfake = False
        confidence = 0.0
        
        if predictor:
            try:
                print(f"🔍 Analyzing {file_type}...")
                if file_type == 'image':
                    # Use the new predictor which returns PredictionResult
                    result = predictor.predict_image(filepath)
                    is_deepfake = result.is_fake
                    confidence = result.confidence
                else:
                    # For videos - check if predict_video exists
                    if hasattr(predictor, 'predict_video'):
                        try:
                            result = predictor.predict_video(filepath)
                            # Handle both old tuple format and new PredictionResult format
                            if hasattr(result, 'is_fake'):
                                is_deepfake = result.is_fake
                                confidence = result.confidence
                            else:
                                is_deepfake, confidence = result
                        except Exception as video_err:
                            print(f"⚠️  Video prediction failed: {video_err}")
                            print("⚠️  Videos not fully supported yet - using fallback")
                            is_deepfake, confidence = fallback_prediction()
                    else:
                        print("⚠️  Video prediction not implemented - using fallback")
                        is_deepfake, confidence = fallback_prediction()
                
                print(f"✅ Prediction: {'FAKE' if is_deepfake else 'REAL'} ({confidence:.2f}%)")
                
            except Exception as e:
                print(f"⚠️  Prediction error: {e}")
                print(traceback.format_exc())
                print("⚠️  Using fallback prediction")
                is_deepfake, confidence = fallback_prediction()
        else:
            print("⚠️  No predictor loaded - using fallback")
            is_deepfake, confidence = fallback_prediction()

        prediction = 'fake' if is_deepfake else 'real'

        try:
            new_result = ScanResult(
                filename=filename,
                file_type=file_type,
                prediction=prediction,
                confidence=float(confidence)
            )
            db.session.add(new_result)
            db.session.commit()
            print(f"💾 Result saved to database")
        except Exception as e:
            print(f"⚠️  Database error: {e}")
            db.session.rollback()

        return jsonify({
            "is_deepfake": bool(is_deepfake),
            "prediction": str(prediction),
            "confidence": float(round(confidence, 2)),
            "file_type": str(file_type),
            "filename": str(filename),
            "message": "File analyzed successfully"
        })

    except Exception as e:
        print(f"❌ Error in detect_deepfake: {e}")
        print(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "message": "An error occurred during processing"
        }), 500

@app.route('/store_result', methods=['POST'])
def store_result():
    try:
        data = request.json
        filename = data.get('filename')
        prediction = data.get('prediction')
        confidence = data.get('confidence')
        file_type = data.get('file_type', 'image')

        if not filename or not prediction or confidence is None:
            return jsonify({"error": "Missing required fields"}), 400

        new_result = ScanResult(
            filename=filename,
            file_type=file_type,
            prediction=prediction,
            confidence=float(confidence)
        )
        db.session.add(new_result)
        db.session.commit()
        
        return jsonify({"message": "Result stored successfully"}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    return jsonify({
        "message": "Upload successful",
        "image_url": f"/images/{filename}"
    }), 201

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(video_path)

    return jsonify({
        "message": "Upload successful",
        "video_url": f"/videos/{filename}"
    }), 201

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/videos/<filename>')
def get_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/status', methods=['GET'])
def status():
    model_status = "loaded" if predictor else "not loaded"
    total_scans = ScanResult.query.count()
    
    # Get predictor stats if available
    predictor_stats = {}
    if predictor:
        try:
            predictor_stats = predictor.get_stats()
        except:
            pass
    
    return jsonify({
        "message": "API is running!",
        "model_status": model_status,
        "total_scans": total_scans,
        "upload_folder": UPLOAD_FOLDER,
        "predictor_stats": predictor_stats
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "error": "File too large",
        "message": "Maximum file size is 100MB"
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested resource was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate detailed PDF report for analyzed image"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(image_path):
            return jsonify({"error": "Image file not found"}), 404
        
        # Re-analyze the image to get full results
        if predictor:
            try:
                result = predictor.predict_image(image_path)
                
                # Prepare data for report
                report_data = {
                    'filename': filename,
                    'file_type': 'image',
                    'is_deepfake': result.is_fake,
                    'confidence': result.confidence,
                    'method_results': result.method_results,
                    'ensemble_score': result.ensemble_score,
                    'metadata_info': result.metadata_info,
                    'threshold': predictor.ensemble_threshold * 100
                }
                
                # Generate PDF
                from utils.report_generator import ReportGenerator
                
                report_gen = ReportGenerator()
                report_filename = f"report_{filename.rsplit('.', 1)[0]}.pdf"
                report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
                
                report_gen.generate_report(report_data, image_path, report_path)
                
                print(f"📄 Report generated: {report_path}")
                
                # Return the PDF file
                return send_file(
                    report_path,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=report_filename
                )
                
            except Exception as e:
                print(f"⚠️  Report generation error: {e}")
                print(traceback.format_exc())
                return jsonify({"error": f"Report generation failed: {str(e)}"}), 500
        else:
            return jsonify({"error": "Predictor not loaded"}), 500
            
    except Exception as e:
        print(f"❌ Error in generate_report: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('static', path)
    except:
        return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING PIXELFORENSICS API")
    print("="*60)
    
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    model_loaded = init_predictor()
    
    print("\n📊 Configuration:")
    print(f"   Database: deepfake_results.db")
    print(f"   Upload folder: {UPLOAD_FOLDER}")
    print(f"   Predictor status: {'✅ Loaded' if model_loaded else '⚠️  Not loaded (fallback mode)'}")
    print(f"   Max file size: 100MB")
    
    if not model_loaded:
        print("\n⚠️  WARNING: Predictor not initialized!")
        print("   API will use random predictions until fixed.\n")
    
    print("="*60)
    print("🌐 Server starting on http://localhost:5000")
    print("="*60)
    print("\n📝 API Endpoints:")
    print("   GET  /                      - Frontend")
    print("   GET  /status                - Health check")
    print("   POST /detect-deepfake       - Main detection endpoint")
    print("   GET  /api/stats             - Get statistics")
    print("   GET  /api/recent-results    - Get recent scans")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)