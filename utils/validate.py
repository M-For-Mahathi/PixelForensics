"""
Validation Script - Test predictor accuracy on labeled dataset
Measures: Accuracy, Precision, Recall, F1 Score
"""
import os
import json
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.predictor import DeepfakePredictor

def validate_predictor(real_images_dir, fake_images_dir, output_file='validation_report.json'):
    """
    Validate predictor on labeled test set
    
    Args:
        real_images_dir: Directory with real images
        fake_images_dir: Directory with fake/AI images
        output_file: Where to save validation report
    """
    print("\n" + "="*70)
    print("🧪 VALIDATION SCRIPT - Testing Predictor Accuracy")
    print("="*70)
    
    # Initialize predictor with PROPER threshold (0.50 = balanced)
    predictor = DeepfakePredictor({'ensemble_threshold': 0.50})
    
    # Collect test images
    print(f"\n📁 Loading test images...")
    real_images = []
    fake_images = []
    
    # Get real images
    if os.path.exists(real_images_dir):
        for file in os.listdir(real_images_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                real_images.append(os.path.join(real_images_dir, file))
        print(f"   ✅ Found {len(real_images)} REAL images")
    else:
        print(f"   ⚠️  Directory not found: {real_images_dir}")
    
    # Get fake images
    if os.path.exists(fake_images_dir):
        for file in os.listdir(fake_images_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                fake_images.append(os.path.join(fake_images_dir, file))
        print(f"   ✅ Found {len(fake_images)} FAKE images")
    else:
        print(f"   ⚠️  Directory not found: {fake_images_dir}")
    
    total_images = len(real_images) + len(fake_images)
    
    if total_images == 0:
        print("\n❌ No test images found! Please add images to test directories.")
        print(f"   Real images: {real_images_dir}")
        print(f"   Fake images: {fake_images_dir}")
        return
    
    print(f"\n📊 Total test images: {total_images}")
    print(f"   Real: {len(real_images)} | Fake: {len(fake_images)}")
    
    # Initialize counters
    true_positives = 0   # Correctly identified as fake
    true_negatives = 0   # Correctly identified as real
    false_positives = 0  # Real image marked as fake
    false_negatives = 0  # Fake image marked as real
    
    method_stats = {}
    all_confidences = []
    detailed_results = []
    
    print(f"\n🔬 Running validation...")
    print("-" * 70)
    
    # Test on REAL images (should be marked as NOT fake)
    print(f"\n📷 Testing on REAL images...")
    for idx, img_path in enumerate(real_images, 1):
        try:
            result = predictor.predict_image(img_path)
            
            if result.is_fake:
                false_positives += 1  # ERROR: Real marked as fake
                outcome = "❌ FALSE POSITIVE"
            else:
                true_negatives += 1   # CORRECT: Real marked as real
                outcome = "✅ TRUE NEGATIVE"
            
            all_confidences.append(result.confidence)
            
            # Track per-method results
            for method, details in result.method_results.items():
                if method not in method_stats:
                    method_stats[method] = {'correct': 0, 'total': 0}
                method_stats[method]['total'] += 1
                if not details['is_fake']:  # Should say REAL
                    method_stats[method]['correct'] += 1
            
            detailed_results.append({
                'image': os.path.basename(img_path),
                'true_label': 'real',
                'predicted': 'fake' if result.is_fake else 'real',
                'confidence': result.confidence,
                'correct': not result.is_fake
            })
            
            if idx % 10 == 0:
                print(f"   Progress: {idx}/{len(real_images)} - {outcome}")
        
        except Exception as e:
            print(f"   ⚠️  Error on {os.path.basename(img_path)}: {e}")
    
    # Test on FAKE images (should be marked as fake)
    print(f"\n🤖 Testing on FAKE/AI images...")
    for idx, img_path in enumerate(fake_images, 1):
        try:
            result = predictor.predict_image(img_path)
            
            if result.is_fake:
                true_positives += 1   # CORRECT: Fake marked as fake
                outcome = "✅ TRUE POSITIVE"
            else:
                false_negatives += 1  # ERROR: Fake marked as real
                outcome = "❌ FALSE NEGATIVE"
            
            all_confidences.append(result.confidence)
            
            # Track per-method results
            for method, details in result.method_results.items():
                if method not in method_stats:
                    method_stats[method] = {'correct': 0, 'total': 0}
                method_stats[method]['total'] += 1
                if details['is_fake']:  # Should say FAKE
                    method_stats[method]['correct'] += 1
            
            detailed_results.append({
                'image': os.path.basename(img_path),
                'true_label': 'fake',
                'predicted': 'fake' if result.is_fake else 'real',
                'confidence': result.confidence,
                'correct': result.is_fake
            })
            
            if idx % 10 == 0:
                print(f"   Progress: {idx}/{len(fake_images)} - {outcome}")
        
        except Exception as e:
            print(f"   ⚠️  Error on {os.path.basename(img_path)}: {e}")
    
    # Calculate metrics
    print("\n" + "="*70)
    print("📊 VALIDATION RESULTS")
    print("="*70)
    
    print(f"\n📈 Confusion Matrix:")
    print(f"   True Positives (TP):  {true_positives:3d}  (Fake correctly detected)")
    print(f"   True Negatives (TN):  {true_negatives:3d}  (Real correctly detected)")
    print(f"   False Positives (FP): {false_positives:3d}  (Real wrongly flagged as fake)")
    print(f"   False Negatives (FN): {false_negatives:3d}  (Fake wrongly marked as real)")
    
    # Calculate key metrics
    accuracy = (true_positives + true_negatives) / total_images if total_images > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    
    print(f"\n🎯 Overall Metrics:")
    print(f"   Accuracy:  {accuracy*100:5.1f}%  (Overall correctness)")
    print(f"   Precision: {precision*100:5.1f}%  (Of flagged images, how many were actually fake)")
    print(f"   Recall:    {recall*100:5.1f}%  (Of all fakes, how many did we catch)")
    print(f"   F1 Score:  {f1_score*100:5.1f}%  (Harmonic mean of precision & recall)")
    print(f"   Avg Confidence: {avg_confidence:.1f}%")
    
    # Per-method accuracy
    print(f"\n🔍 Per-Method Accuracy:")
    for method, stats in sorted(method_stats.items()):
        method_acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"   {method:30s}: {method_acc:5.1f}% ({stats['correct']}/{stats['total']})")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_set': {
            'real_images': len(real_images),
            'fake_images': len(fake_images),
            'total_images': total_images
        },
        'confusion_matrix': {
            'true_positives': true_positives,
            'true_negatives': true_negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        },
        'metrics': {
            'accuracy': round(accuracy * 100, 2),
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1_score * 100, 2),
            'avg_confidence': round(avg_confidence, 2)
        },
        'per_method_accuracy': {
            method: round(stats['correct'] / stats['total'] * 100, 2)
            for method, stats in method_stats.items()
            if stats['total'] > 0
        },
        'detailed_results': detailed_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Validation report saved to: {output_file}")
    
    # Assessment
    print("\n" + "="*70)
    print("🎓 ASSESSMENT")
    print("="*70)
    
    if accuracy >= 0.85:
        print("✅ EXCELLENT: Your predictor is production-ready!")
    elif accuracy >= 0.75:
        print("⚠️  GOOD: Decent accuracy, but could be improved")
    elif accuracy >= 0.60:
        print("⚠️  FAIR: Works but needs significant improvement")
    else:
        print("❌ POOR: Major issues - needs debugging")
    
    if false_positives > total_images * 0.15:
        print("⚠️  HIGH FALSE POSITIVE RATE: Consider raising ensemble threshold")
    
    if false_negatives > total_images * 0.20:
        print("⚠️  HIGH FALSE NEGATIVE RATE: Consider lowering ensemble threshold")
    
    print("="*70 + "\n")
    
    return report


def quick_test():
    """Quick test with existing uploads folder"""
    print("\n🚀 QUICK TEST MODE - Using uploads folder")
    print("   This will test on whatever images you've already uploaded")
    
    uploads_dir = "uploads"
    
    if not os.path.exists(uploads_dir):
        print(f"\n❌ No uploads folder found at: {uploads_dir}")
        return
    
    # Get all images from uploads
    test_images = []
    for file in os.listdir(uploads_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            test_images.append(os.path.join(uploads_dir, file))
    
    if len(test_images) == 0:
        print(f"\n❌ No images found in uploads folder")
        return
    
    print(f"\n✅ Found {len(test_images)} images in uploads")
    
    # Test each image
    predictor = DeepfakePredictor({'ensemble_threshold': 0.35})
    
    print(f"\n🔬 Testing images...")
    print("-" * 60)
    
    for img_path in test_images:
        try:
            result = predictor.predict_image(img_path)
            verdict = "🔴 FAKE" if result.is_fake else "🟢 REAL"
            print(f"\n{os.path.basename(img_path)}")
            print(f"   Verdict: {verdict} (Confidence: {result.confidence:.1f}%)")
        except Exception as e:
            print(f"\n⚠️  Error on {os.path.basename(img_path)}: {e}")
    
    print("\n" + "-" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # Quick test mode
        quick_test()
    else:
        # Full validation mode
        real_dir = "data/test/real"
        fake_dir = "data/test/fake"
        
        # Check if directories exist
        if not os.path.exists(real_dir) or not os.path.exists(fake_dir):
            print("\n⚠️  Test directories not found!")
            print(f"\nPlease create these directories and add test images:")
            print(f"   {real_dir}  - Add real photos here")
            print(f"   {fake_dir}  - Add AI-generated images here")
            print(f"\nOr run in quick mode: python validate.py quick")
            sys.exit(1)
        
        # Run full validation
        validate_predictor(real_dir, fake_dir)