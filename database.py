from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ScanResult(db.Model):
    __tablename__ = 'scan_result'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    prediction = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ScanResult {self.filename} - {self.prediction} ({self.confidence}%)>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'prediction': self.prediction,
            'confidence': round(self.confidence, 2),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

if __name__ == "__main__":
    from flask import Flask
    import os
    
    app = Flask(__name__)
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'deepfake_results.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("="*60)
        print("✅ DATABASE CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"Database file: {os.path.join(BASE_DIR, 'deepfake_results.db')}")
        print(f"Table created: scan_result")
        print("="*60)