import cv2
import numpy as np
from mtcnn import MTCNN
from PIL import Image

class FaceExtractor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.detector = MTCNN()
        print("✓ Face detector initialized")
    
    def extract_face(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"✗ Could not read image: {image_path}")
                return None
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            faces = self.detector.detect_faces(img_rgb)
            
            if len(faces) == 0:
                print(f"✗ No face detected in: {image_path}")
                return None
            
            largest_face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
            x, y, w, h = largest_face['box']
            
            padding = int(0.1 * max(w, h))
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = w + 2 * padding
            h = h + 2 * padding
            
            face_img = img_rgb[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, self.target_size)
            face_img = face_img.astype('float32') / 255.0
            
            return face_img
            
        except Exception as e:
            print(f"✗ Error processing {image_path}: {str(e)}")
            return None
    
    def preprocess_image_simple(self, image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize(self.target_size)
            img_array = np.array(img).astype('float32') / 255.0
            return img_array
        except Exception as e:
            print(f"✗ Error in simple preprocessing: {str(e)}")
            return None