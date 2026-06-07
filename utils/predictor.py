"""
DeepfakePredictor v2.0 - Production-Ready Multi-Model Ensemble
Final version with metadata analysis and proper threshold
"""
import torch
import numpy as np
from PIL import Image
import cv2
import os
from transformers import AutoFeatureExtractor, AutoModelForImageClassification, AutoImageProcessor
import warnings
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Import metadata analyzer
try:
    from utils.metadata_analyzer import MetadataAnalyzer
    METADATA_AVAILABLE = True
except ImportError:
    try:
        from metadata_analyzer import MetadataAnalyzer
        METADATA_AVAILABLE = True
    except ImportError:
        METADATA_AVAILABLE = False
        print("⚠️ MetadataAnalyzer not found - metadata analysis will be skipped")

warnings.filterwarnings('ignore')

@dataclass
class PredictionResult:
    """Structured prediction result"""
    is_fake: bool
    confidence: float
    method_results: Dict[str, dict]
    ensemble_score: float
    metadata_info: Dict[str, any] = None

class DeepfakePredictor:
    """
    Production-ready deepfake/AI image detector
    Uses ensemble of HF models + 5 analysis methods + metadata
    """
    
    def __init__(self, config=None):
        """Initialize predictor with configuration"""
        print("\n🔄 Initializing DeepfakePredictor v2.0...")
        print("="*60)
        
        self.config = config or {}
        # CRITICAL: Default threshold is 0.50 (can be overridden by config)
        self.ensemble_threshold = self.config.get('ensemble_threshold', 0.52)
        self.hf_models = []
        self.stats = {
            'total_predictions': 0,
            'fake_detected': 0,
            'real_detected': 0
        }
        
        # Initialize metadata analyzer if available
        self.metadata_analyzer = MetadataAnalyzer() if METADATA_AVAILABLE else None
        if self.metadata_analyzer:
            print("✅ Metadata Analyzer initialized")
        
        # Load state-of-the-art HuggingFace models
        model_configs = [
            {
                'name': 'Ateeqq/ai-vs-human-image-detector',
                'weight': 1.0,
                'description': 'Primary detector (99.2% acc)'
            },
            {
                'name': 'dima806/ai_vs_real_image_detection',
                'weight': 0.9,
                'description': 'Secondary detector (98.2% acc)'
            }
        ]
        
        for config in model_configs:
            try:
                print(f"\n📦 Loading {config['description']}...")
                print(f"   Model: {config['name']}")
                
                try:
                    processor = AutoImageProcessor.from_pretrained(config['name'])
                except:
                    processor = AutoFeatureExtractor.from_pretrained(config['name'])
                
                model = AutoModelForImageClassification.from_pretrained(config['name'])
                model.eval()
                
                # Disable dropout for deterministic inference
                for module in model.modules():
                    if isinstance(module, torch.nn.Dropout):
                        module.p = 0
                
                # Check label mapping
                id2label = model.config.id2label
                print(f"   ✓ Label mapping: {id2label}")
                
                self.hf_models.append({
                    'name': config['name'],
                    'processor': processor,
                    'model': model,
                    'weight': config['weight'],
                    'id2label': id2label,
                    'description': config['description']
                })
                
                print(f"   ✅ Loaded successfully! (weight: {config['weight']})")
                
            except Exception as e:
                print(f"   ⚠️  Could not load {config['name']}: {e}")
                print(f"   Skipping this model...")
        
        if not self.hf_models:
            print("\n⚠️  WARNING: No HuggingFace models loaded!")
            print("   Will rely only on analysis methods (not recommended)")
        else:
            print(f"\n✅ Loaded {len(self.hf_models)} HuggingFace model(s)")
        
        print("\n" + "="*60)
        print("✅ DeepfakePredictor v2.0 initialized and ready!")
        print(f"   Ensemble threshold: {self.ensemble_threshold}")
        print("="*60 + "\n")
    
    def predict_image(self, image_path: str) -> PredictionResult:
        """
        Predict using ensemble of all methods
        Returns: PredictionResult object
        """
        print(f"\n🔍 Analyzing: {os.path.basename(image_path)}")
        print("-" * 60)
        
        method_results = {}
        all_predictions = []
        all_confidences = []
        all_weights = []
        
        # HuggingFace models
        if self.hf_models:
            for hf_config in self.hf_models:
                is_fake, confidence, raw_probs = self._predict_with_huggingface(image_path, hf_config)
                
                method_name = hf_config['description']
                method_results[method_name] = {
                    'is_fake': is_fake,
                    'confidence': confidence,
                    'raw_output': raw_probs
                }
                
                all_predictions.append(is_fake)
                all_confidences.append(confidence)
                all_weights.append(hf_config['weight'])
                
                status = "🔴 FAKE" if is_fake else "🟢 REAL"
                print(f"   {method_name:30s}: {status} ({confidence:.1f}%)")
        
        # Frequency Analysis
        is_fake, confidence = self._frequency_analysis(image_path)
        method_results['Frequency Analysis'] = {
            'is_fake': is_fake,
            'confidence': confidence
        }
        all_predictions.append(is_fake)
        all_confidences.append(confidence)
        all_weights.append(0.6)
        
        status = "🔴 FAKE" if is_fake else "🟢 REAL"
        print(f"   {'Frequency Analysis':30s}: {status} ({confidence:.1f}%)")
        
        # ELA Analysis
        is_fake, confidence = self._ela_analysis(image_path)
        method_results['ELA Analysis'] = {
            'is_fake': is_fake,
            'confidence': confidence
        }
        all_predictions.append(is_fake)
        all_confidences.append(confidence)
        all_weights.append(0.6)
        
        status = "🔴 FAKE" if is_fake else "🟢 REAL"
        print(f"   {'ELA Analysis':30s}: {status} ({confidence:.1f}%)")
        
        # Noise Analysis
        is_fake, confidence = self._noise_analysis(image_path)
        method_results['Noise Analysis'] = {
            'is_fake': is_fake,
            'confidence': confidence
        }
        all_predictions.append(is_fake)
        all_confidences.append(confidence)
        all_weights.append(0.6)
        
        status = "🔴 FAKE" if is_fake else "🟢 REAL"
        print(f"   {'Noise Analysis':30s}: {status} ({confidence:.1f}%)")
        
        # Color Analysis
        is_fake, confidence = self._color_analysis(image_path)
        method_results['Color Analysis'] = {
            'is_fake': is_fake,
            'confidence': confidence
        }
        all_predictions.append(is_fake)
        all_confidences.append(confidence)
        all_weights.append(0.5)
        
        status = "🔴 FAKE" if is_fake else "🟢 REAL"
        print(f"   {'Color Analysis':30s}: {status} ({confidence:.1f}%)")
        
        # Metadata Analysis
        metadata_info = {}
        if self.metadata_analyzer:
            is_fake, confidence, metadata_info = self.metadata_analyzer.analyze(image_path)
            method_results['Metadata Analysis'] = {
                'is_fake': is_fake,
                'confidence': confidence,
                'details': metadata_info
            }
            all_predictions.append(is_fake)
            all_confidences.append(confidence)
            if not metadata_info.get('has_exif'):
                all_weights.append(1.2)  # Extra high weight when EXIF is missing
            else:
                all_weights.append(0.8)  # Normal high weight when EXIF exists
            
            status = "🔴 FAKE" if is_fake else "🟢 REAL"
            print(f"   {'Metadata Analysis':30s}: {status} ({confidence:.1f}%)")
            
            if metadata_info.get('has_exif'):
                summary = self.metadata_analyzer.get_summary(metadata_info)
                print(f"      📋 {summary}")
            else:
                print(f"      ⚠️  No EXIF metadata (typical of AI images)")
        
        # Weighted ensemble voting
        weighted_fake_votes = sum(w * p for w, p in zip(all_weights, all_predictions))
        total_weight = sum(all_weights)
        ensemble_score = weighted_fake_votes / total_weight
        
        fake_count = sum(all_predictions)
        total_methods = len(all_predictions)
        
        print(f"\n📊 Ensemble Voting:")
        print(f"   Methods voting FAKE: {fake_count}/{total_methods}")
        print(f"   Weighted Score: {ensemble_score*100:.1f}%")
        print(f"   Threshold: {self.ensemble_threshold*100:.0f}%")
        
        # Final decision
        is_deepfake = ensemble_score >= self.ensemble_threshold
        
        # Calculate final confidence
        if is_deepfake:
            fake_confs = [c for p, c in zip(all_predictions, all_confidences) if p]
            base_confidence = np.mean(fake_confs) if fake_confs else 60.0
            agreement_boost = (ensemble_score - self.ensemble_threshold) * 50
            final_confidence = min(base_confidence + agreement_boost, 95.0)
        else:
            real_confs = [c for p, c in zip(all_predictions, all_confidences) if not p]
            base_confidence = np.mean(real_confs) if real_confs else 60.0
            agreement_boost = (1 - ensemble_score - self.ensemble_threshold) * 50
            final_confidence = min(base_confidence + agreement_boost, 95.0)
        
        final_confidence = float(np.clip(final_confidence, 55.0, 95.0))
        
        # Update stats
        self.stats['total_predictions'] += 1
        if is_deepfake:
            self.stats['fake_detected'] += 1
        else:
            self.stats['real_detected'] += 1
        
        verdict = "🔴 AI-GENERATED/FAKE" if is_deepfake else "🟢 REAL"
        print(f"\n🎯 FINAL VERDICT: {verdict}")
        print(f"   Confidence: {final_confidence:.1f}%")
        print("-" * 60)
        
        return PredictionResult(
            is_fake=is_deepfake,
            confidence=final_confidence,
            method_results=method_results,
            ensemble_score=ensemble_score,
            metadata_info=metadata_info
        )
    
    def _predict_with_huggingface(self, image_path: str, hf_config: dict) -> Tuple[bool, float, dict]:
        """Predict using HuggingFace model with proper label mapping"""
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = hf_config['processor'](images=image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = hf_config['model'](**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            id2label = hf_config['id2label']
            
            fake_idx = None
            real_idx = None
            
            for idx, label in id2label.items():
                label_lower = label.lower()
                if any(keyword in label_lower for keyword in ['artificial', 'fake', 'ai', 'generated']):
                    fake_idx = idx
                elif any(keyword in label_lower for keyword in ['real', 'human', 'authentic']):
                    real_idx = idx
            
            if fake_idx is None or real_idx is None:
                fake_idx = 0
                real_idx = 1
            
            fake_prob = float(probs[0][fake_idx].item())
            real_prob = float(probs[0][real_idx].item())
            
            is_fake = fake_prob > real_prob
            confidence = (fake_prob if is_fake else real_prob) * 100
            confidence = float(np.clip(confidence, 55.0, 95.0))
            
            return is_fake, confidence, {
                'fake_prob': fake_prob,
                'real_prob': real_prob,
                'fake_idx': fake_idx,
                'real_idx': real_idx
            }
            
        except Exception as e:
            print(f"      [⚠️  HF prediction error: {e}]")
            return False, 50.0, {}
    
    def _frequency_analysis(self, image_path: str) -> Tuple[bool, float]:
        """Frequency domain analysis"""
        try:
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
            
            ai_score = 0
            if low_freq_ratio > 0.65:
                ai_score += 30
            if high_freq_ratio < 0.35:
                ai_score += 30
            if uniformity < 0.22:
                ai_score += 25
            if low_freq_ratio > 0.75:
                ai_score += 15
            
            is_fake = ai_score > 50
            confidence = 50 + min(45, ai_score * 0.8)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def _ela_analysis(self, image_path: str) -> Tuple[bool, float]:
        """Error Level Analysis"""
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
            
            ai_score = 0
            if uniformity_score < 2.8:
                ai_score += 30
            if max_diff < 25:
                ai_score += 30
            if mean_diff < 3.5:
                ai_score += 25
            if uniformity_score < 3.2 and max_diff < 30:
                ai_score += 15
            
            is_fake = ai_score > 50
            confidence = 50 + min(45, ai_score * 0.8)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def _noise_analysis(self, image_path: str) -> Tuple[bool, float]:
        """Noise pattern analysis"""
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
            
            ai_score = 0
            if noise_mean < 4.5:
                ai_score += 30
            if noise_std < 2.5:
                ai_score += 30
            if dark_noise < 2.5:
                ai_score += 20
            
            noise_variance = abs(dark_noise - bright_noise)
            if noise_variance < 0.8:
                ai_score += 20
            
            is_fake = ai_score > 50
            confidence = 50 + min(45, ai_score * 0.8)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def _color_analysis(self, image_path: str) -> Tuple[bool, float]:
        """Color distribution analysis"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, 50.0
            
            img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            saturation = hsv[:, :, 1]
            sat_mean = float(np.mean(saturation))
            sat_std = float(np.std(saturation))
            
            ai_score = 0
            if sat_mean > 110:
                ai_score += 25
            if sat_std < 45:
                ai_score += 30
            
            hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
            
            smoothness_b = float(np.std(np.diff(hist_b.flatten())))
            smoothness_g = float(np.std(np.diff(hist_g.flatten())))
            smoothness_r = float(np.std(np.diff(hist_r.flatten())))
            avg_smoothness = (smoothness_b + smoothness_g + smoothness_r) / 3
            
            if avg_smoothness < 65:
                ai_score += 25
            
            edges = cv2.Canny(img, 50, 150)
            edge_density = float(np.sum(edges > 0) / edges.size)
            
            if edge_density < 0.07:
                ai_score += 20
            
            is_fake = ai_score > 50
            confidence = 50 + min(45, ai_score * 0.8)
            
            return is_fake, float(confidence)
            
        except Exception as e:
            return False, 50.0
    
    def get_stats(self) -> dict:
        """Return predictor statistics"""
        return self.stats.copy()