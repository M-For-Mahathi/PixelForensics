import cv2
import numpy as np
import os
from preprocessing.face_extractor import FaceExtractor

class VideoProcessor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.face_extractor = FaceExtractor(target_size)
        print("✓ Video processor initialized")
    
    def extract_frames(self, video_path, num_frames=10):
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"✗ Could not open video: {video_path}")
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"📹 Video: {total_frames} frames, {fps:.2f} FPS")
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            extracted_faces = []
            temp_dir = "temp_frames"
            os.makedirs(temp_dir, exist_ok=True)
            
            for idx, frame_num in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                temp_path = os.path.join(temp_dir, f"frame_{idx}.jpg")
                cv2.imwrite(temp_path, frame)
                face = self.face_extractor.extract_face(temp_path)
                
                if face is not None:
                    extracted_faces.append(face)
                
                os.remove(temp_path)
            
            cap.release()
            os.rmdir(temp_dir)
            
            print(f"✓ Extracted {len(extracted_faces)} faces from {num_frames} frames")
            return extracted_faces
            
        except Exception as e:
            print(f"✗ Error processing video: {str(e)}")
            return []
    
    def process_video_for_prediction(self, video_path, num_frames=15):
        faces = self.extract_frames(video_path, num_frames)
        
        if len(faces) == 0:
            return None

        faces_batch = np.array(faces)
        return faces_batch