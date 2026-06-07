"""
DeepfakePredictor - Enhanced Multi-Method Detection (DETERMINISTIC VERSION)
Uses ensemble of multiple detection techniques for better accuracy
"""
import torch
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import os
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import warnings
import random

warnings.filterwarnings('ignore')

# SET ALL SEEDS FOR DETERMINISTIC BEHAVIOR
def set_seeds(seed=42):
    """Set all random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    tf.random.set_seed(seed)
    
    # Make PyTorch deterministic
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    # Make TensorFlow deterministic
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['PYTHONHASHSEED'] = str(seed)

# Set seeds at module level
set_seeds(42)

class DeepfakePredictor:
    """
    Enhanced deepfake/AI image detector using multiple methods
    Combines HuggingFace models with frequency/noise analysis
    """
    
    def __init__(self, model_path=None):
        """Initialize the predictor with multiple detection methods"""
        print("🔄 Initializing Enhanced AI Image Detector...")
        
        # Ensure deterministic behavior
        set_seeds(42)
        
        self.hf_models = []
        
        # Try to load HuggingFace model
        model_configs = ["umm-maybe/AI-image-detector"]
        
        for model_name in model_configs:
            try:
                print(f"   Loading {model_name.split('/')[-1]}...")
                feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
                model = AutoModelForImageClassification.from_pretrained(model_name)
                model.eval()  # CRITICAL: Set to eval mode
                
                # Disable dropout for deterministic inference
                for module in model.modules():
                    if isinstance(module, torch.nn.Dropout):
                        module.p = 0
                
                self.hf_models.append({
                    'name': model_name,
                    'extractor': feature_extractor,
                    'model': model
                })
                print(f"   ✅ {model_name.split('/')[-1]} loaded!")
            except Exception as e:
                print(f"   ⚠️  Could not load {model_name}: {e}")
        
        if self.hf_models:
            print(f"✅ Loaded {len(self.hf_models)} HuggingFace model(s)")
        else:
            print("   ℹ️  No HuggingFace models loaded, will use analysis methods")
        
        print("✅ Enhanced Predictor initialized and ready!")
    
    def predict_image(self, image_path):
        """
        Predict using ensemble of all methods
        Returns: (is_deepfake, confidence)
        """
        # Reset seeds for each prediction to ensure consistency
        set_seeds(42)
        
        predictions = []
        confidences = []
        method_names = []
        
        # Method 1: HuggingFace models
        if self.hf_models:
            for hf_config in self.hf_models:
                result, conf = self._predict_with_huggingface(image_path, hf_config)
                predictions.append(result)
                confidences.append(conf)
                method_names.append(f"HF-{hf_config['name'].split('/')[-1]}")
        
        # Method 2: Frequency Analysis
        freq_result, freq_conf = self._frequency_analysis(image_path)
        predictions.append(freq_result)
        confidences.append(freq_conf)
        method_names.append("Frequency")
        
        # Method 3: ELA Analysis
        ela_result, ela_conf = self._ela_analysis(image_path)
        predictions.append(ela_result)
        confidences.append(ela_conf)
        method_names.append("ELA")
        
        # Method 4: Noise Analysis
        noise_result, noise_conf = self._noise_analysis(image_path)
        predictions.append(noise_result)
        confidences.append(noise_conf)
        method_names.append("Noise")
        
        # Method 5: Color Distribution Analysis
        color_result, color_conf = self._color_analysis(image_path)
        predictions.append(color_result)
        confidences.append(color_conf)
        method_names.append("Color")
        
        # Print detailed results
        print(f"\n   🔍 Detection Method Results:")
        for name, pred, conf in zip(method_names, predictions, confidences):
            status = "FAKE" if pred else "REAL"
            print(f"      {name:20s}: {status:4s} ({conf:.1f}%)")
        
        # Ensemble decision - weighted voting
        weights = []
        for i, name in enumerate(method_names):
            if 'HF' in name:
                weights.append(0.5)  # Half weight for HF models
            else:
                weights.append(1.0)  # Full weight for analysis methods
        
        # Weighted voting
        weighted_fake_votes = sum(w * p for w, p in zip(weights, predictions))
        total_weight = sum(weights)
        fake_ratio = weighted_fake_votes / total_weight
        
        fake_votes = sum(predictions)
        total_votes = len(predictions)
        
        print(f"\n   📊 Voting: {fake_votes}/{total_votes} methods say FAKE")
        print(f"   📊 Weighted Score: {fake_ratio*100:.1f}% (giving less weight to HF model)")
        
        # Decision: Lower threshold for modern AI images
        is_deepfake = fake_ratio >= 0.30
        
        # Calculate confidence (deterministic)
        if is_deepfake:
            fake_confs = [c for r, c in zip(predictions, confidences) if r]
            confidence = float(np.mean(fake_confs)) if fake_confs else 60.0
            agreement_boost = (fake_ratio - 0.30) * 40
            confidence = min(confidence + agreement_boost, 95)
        else:
            real_confs = [c for r, c in zip(predictions, confidences) if not r]
            confidence = float(np.mean(real_confs)) if real_confs else 60.0
            agreement_boost = (1 - fake_ratio - 0.30) * 40
            confidence = min(confidence + agreement_boost, 95)
        
        confidence = min(max(confidence, 55), 95)
        
        print(f"\n   🎯 Final Decision: {'FAKE' if is_deepfake else 'REAL'} ({confidence:.1f}%)")
        
        return is_deepfake, confidence
    
    def _predict_with_huggingface(self, image_path, hf_config):
        """Predict using HuggingFace model with skepticism for high confidence"""
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = hf_config['extractor'](images=image, return_tensors="pt")
            
            # CRITICAL: Use torch.no_grad() and ensure model is in eval mode
            with torch.no_grad():
                hf_config['model'].eval()  # Ensure eval mode
                outputs = hf_config['model'](**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            artificial_prob = float(probs[0][0].item())
            real_prob = float(probs[0][1].item())
            
            print(f"      [HF Raw: artificial={artificial_prob:.3f}, real={real_prob:.3f}]")
            
            # Be skeptical if model is very confident it's real
            if real_prob > 0.8:
                is_fake = True
                confidence = 65.0
                print(f"      [HF: Very confident REAL - being skeptical, marking as FAKE]")
            elif artificial_prob > real_prob:
                is_fake = True
                confidence = artificial_prob * 100
            else:
                is_fake = False
                confidence = real_prob * 100
            
            return is_fake, min(max(confidence, 52), 75)
            
        except Exception as e:
            print(f"   ⚠️  HF prediction error: {e}")
            return False, 50.0
    
    def _frequency_analysis(self, image_path):
        """Frequency domain analysis - DETERMINISTIC"""
        try:
            # Use consistent interpolation method
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return False, 50.0
            
            img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
            
            f_transform = np.fft.fft2(img)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            
            rows, cols = magnitude.shape
            center_row, center_col = rows // 2, cols // 2
            
            y, x = np.ogrid[:rows, :cols]
            distance = np.sqrt((x - center_col)**2 + (y - center_row)**2)
            
            # Analyze frequency bands
            bands = [(10, 40), (40, 80), (80, 150), (150, 250)]
            
            band_energies = []
            for inner, outer in bands:
                mask = (distance >= inner) & (distance < outer)
                energy = float(np.sum(magnitude[mask]))
                band_energies.append(energy)
            
            total_energy = sum(band_energies)
            if total_energy == 0:
                return False, 50.0
            
            band_ratios = [e / total_energy for e in band_energies]
            low_freq_ratio = sum(band_ratios[:2])
            high_freq_ratio = sum(band_ratios[2:])
            uniformity = float(np.std(magnitude / (np.max(magnitude) + 1e-6)))
            
            # DETERMINISTIC SCORING
            ai_score = 0
            
            if low_freq_ratio > 0.60:
                ai_score += 35
            if high_freq_ratio < 0.40:
                ai_score += 35
            if uniformity < 0.25:
                ai_score += 20
            if uniformity < 0.18:
                ai_score += 20
            if low_freq_ratio > 0.70:
                ai_score += 20
            
            is_fake = ai_score > 40
            confidence = 50 + min(45, ai_score * 0.9)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def _ela_analysis(self, image_path):
        """Error Level Analysis - DETERMINISTIC"""
        try:
            original = Image.open(image_path).convert('RGB')
            
            temp_path = 'temp_ela.jpg'
            original.save(temp_path, 'JPEG', quality=90)
            compressed = Image.open(temp_path)
            
            original_arr = np.array(original).astype(np.float32)
            compressed_arr = np.array(compressed).astype(np.float32)
            diff = np.abs(original_arr - compressed_arr)
            
            try:
                os.remove(temp_path)
            except:
                pass
            
            mean_diff = float(np.mean(diff))
            std_diff = float(np.std(diff))
            max_diff = float(np.max(diff))
            
            uniformity_score = std_diff / (mean_diff + 1e-6)
            
            # DETERMINISTIC SCORING
            ai_score = 0
            
            if uniformity_score < 3.0:
                ai_score += 25
            if uniformity_score < 2.5:
                ai_score += 20
            if max_diff < 30:
                ai_score += 25
            if mean_diff < 4.0:
                ai_score += 20
            if uniformity_score < 3.5 and max_diff < 35:
                ai_score += 20
            
            is_fake = ai_score > 40
            confidence = 50 + min(45, ai_score * 0.9)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def _noise_analysis(self, image_path):
        """Noise pattern analysis - DETERMINISTIC"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, 50.0
            
            img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.absdiff(gray, blurred)
            
            noise_mean = float(np.mean(noise))
            noise_std = float(np.std(noise))
            
            dark_mask = gray < 50
            dark_noise = float(np.mean(noise[dark_mask])) if np.sum(dark_mask) > 0 else noise_mean
            
            bright_mask = gray > 200
            bright_noise = float(np.mean(noise[bright_mask])) if np.sum(bright_mask) > 0 else noise_mean
            
            # DETERMINISTIC SCORING
            ai_score = 0
            
            if noise_mean < 5.0:
                ai_score += 25
            if noise_mean < 4.0:
                ai_score += 20
            if noise_std < 3.0:
                ai_score += 25
            if dark_noise < 3.0:
                ai_score += 15
            
            noise_variance = abs(dark_noise - bright_noise)
            if noise_variance < 1.0:
                ai_score += 15
            
            if noise_mean < 6.0 and noise_std < 3.0:
                ai_score += 15
            
            is_fake = ai_score > 40
            confidence = 50 + min(45, ai_score * 0.9)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def _color_analysis(self, image_path):
        """Color distribution analysis - DETERMINISTIC"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, 50.0
            
            img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
            
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            saturation = hsv[:, :, 1]
            sat_mean = float(np.mean(saturation))
            sat_std = float(np.std(saturation))
            
            # DETERMINISTIC SCORING
            ai_score = 0
            
            if sat_mean > 100:
                ai_score += 20
            if sat_std < 50:
                ai_score += 25
            
            hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
            
            smoothness_b = float(np.std(np.diff(hist_b.flatten())))
            smoothness_g = float(np.std(np.diff(hist_g.flatten())))
            smoothness_r = float(np.std(np.diff(hist_r.flatten())))
            avg_smoothness = (smoothness_b + smoothness_g + smoothness_r) / 3
            
            if avg_smoothness < 70:
                ai_score += 30
            
            edges = cv2.Canny(img, 50, 150)
            edge_density = float(np.sum(edges > 0) / edges.size)
            
            if edge_density < 0.08:
                ai_score += 20
            
            if sat_std < 45 and avg_smoothness < 60:
                ai_score += 20
            
            is_fake = ai_score > 40
            confidence = 50 + min(45, ai_score * 0.9)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def predict_video(self, video_path):
        """Predict if video is deepfake - DETERMINISTIC"""
        try:
            set_seeds(42)  # Reset seed for video analysis
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, 55.0
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"   Video: {total_frames} frames @ {fps:.2f} FPS")
            
            sample_interval = max(1, total_frames // 15)
            
            predictions = []
            confidences = []
            frames_analyzed = 0
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    temp_frame_path = f"temp_frame_{frame_idx}.jpg"
                    cv2.imwrite(temp_frame_path, frame)
                    
                    is_fake, conf = self.predict_image(temp_frame_path)
                    predictions.append(is_fake)
                    confidences.append(conf)
                    frames_analyzed += 1
                    
                    try:
                        os.remove(temp_frame_path)
                    except:
                        pass
                    
                    if frames_analyzed % 5 == 0:
                        print(f"   Analyzed {frames_analyzed} frames...")
                
                frame_idx += 1
            
            cap.release()
            
            if not predictions:
                return False, 55.0
            
            fake_count = sum(predictions)
            fake_ratio = fake_count / len(predictions)
            avg_confidence = float(np.mean(confidences))
            
            print(f"   Frames analyzed: {frames_analyzed}")
            print(f"   Fake frames: {fake_count}/{len(predictions)} ({fake_ratio*100:.1f}%)")
            
            is_deepfake = fake_ratio > 0.4
            consistency = max(fake_ratio, 1 - fake_ratio)
            final_confidence = avg_confidence * (0.7 + 0.3 * consistency)
            
            return is_deepfake, min(max(final_confidence, 55), 95)
            
        except Exception as e:
            return False, 55.0