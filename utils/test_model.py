"""
Test script for production deepfake detector
Tests consistency, analyzes method performance, and validates configuration
"""
from utils.predictor_old import DeepfakePredictor
import sys
import os
import json
from datetime import datetime

def test_consistency(image_path, num_runs=5):
    """Test if model gives consistent results across multiple runs"""
    print("="*70)
    print("🧪 TESTING PRODUCTION MODEL")
    print("="*70)
    print(f"Image: {image_path}")
    print(f"Test runs: {num_runs}")
    print("="*70)
    
    # Initialize predictor with default config
    config = {
        'ensemble_threshold': 0.35,
        'enable_caching': False,  # Disable caching for consistency test
        'log_predictions': False   # Disable logging for test
    }
    
    print("\n🔄 Initializing predictor...")
    predictor = DeepfakePredictor(config)
    
    results = []
    
    # Run prediction multiple times
    for i in range(num_runs):
        print(f"\n{'='*70}")
        print(f"RUN {i+1}/{num_runs}")
        print(f"{'='*70}")
        
        result = predictor.predict_image(image_path)
        
        results.append({
            'run': i+1,
            'is_fake': result.is_fake,
            'confidence': result.confidence,
            'weighted_score': result.ensemble_details['weighted_score'],
            'agreement': result.ensemble_details['agreement'],
            'method_scores': result.method_scores
        })
        
        print(f"\n✅ Run {i+1} Complete:")
        print(f"   Result: {'FAKE/AI' if result.is_fake else 'REAL'}")
        print(f"   Confidence: {result.confidence:.2f}%")
    
    # Analyze consistency
    print(f"\n{'='*70}")
    print("📊 CONSISTENCY ANALYSIS")
    print(f"{'='*70}")
    
    all_predictions = [r['is_fake'] for r in results]
    all_confidences = [r['confidence'] for r in results]
    all_scores = [r['weighted_score'] for r in results]
    
    # Check consistency
    predictions_consistent = len(set(all_predictions)) == 1
    
    # Allow small variance in confidence (±1%)
    conf_variance = max(all_confidences) - min(all_confidences)
    confidences_stable = conf_variance < 1.0
    
    print(f"\nResults across {num_runs} runs:")
    print(f"{'Run':<6} {'Prediction':<12} {'Confidence':<12} {'Weighted Score':<15} {'Agreement':<10}")
    print("-" * 70)
    for r in results:
        pred = "FAKE/AI" if r['is_fake'] else "REAL"
        print(f"{r['run']:<6} {pred:<12} {r['confidence']:<12.2f} {r['weighted_score']*100:<15.2f} {r['agreement']*100:<10.1f}%")
    
    print(f"\n{'='*70}")
    print("🎯 CONSISTENCY VERDICT")
    print(f"{'='*70}")
    
    if predictions_consistent:
        print(f"✅ Predictions: CONSISTENT")
        print(f"   All runs predicted: {'FAKE/AI' if all_predictions[0] else 'REAL'}")
    else:
        print(f"⚠️  Predictions: INCONSISTENT")
        fake_count = sum(all_predictions)
        print(f"   {fake_count}/{num_runs} runs said FAKE")
        print(f"   🔍 This suggests the image is borderline - check method breakdown")
    
    if confidences_stable:
        print(f"✅ Confidence: STABLE (variance: {conf_variance:.2f}%)")
        print(f"   Range: {min(all_confidences):.2f}% - {max(all_confidences):.2f}%")
    else:
        print(f"⚠️  Confidence: VARIABLE (variance: {conf_variance:.2f}%)")
        print(f"   Range: {min(all_confidences):.2f}% - {max(all_confidences):.2f}%")
    
    # Method breakdown (from last run)
    print(f"\n{'='*70}")
    print("🔬 METHOD BREAKDOWN (Last Run)")
    print(f"{'='*70}")
    
    last_methods = results[-1]['method_scores']
    for method_name, scores in last_methods.items():
        status = "FAKE" if scores['is_fake'] else "REAL"
        print(f"{method_name:12s}: {status:4s} | Confidence: {scores['confidence']:5.1f}% | Weight: {scores['weight']}")
    
    print(f"\n{'='*70}")
    
    # Overall assessment
    if predictions_consistent and confidences_stable:
        print("✅ EXCELLENT: Model is stable and consistent")
        return True
    elif predictions_consistent:
        print("✅ GOOD: Predictions consistent, slight confidence variance (acceptable)")
        return True
    else:
        print("⚠️  ATTENTION NEEDED: Inconsistent predictions detected")
        print("   💡 Recommendation: This image may be borderline. Try adjusting ensemble_threshold")
        return False

def test_single_image(image_path):
    """Test single image with detailed output"""
    print("="*70)
    print("🔍 SINGLE IMAGE ANALYSIS")
    print("="*70)
    print(f"Image: {image_path}")
    print("="*70)
    
    # Initialize with production config
    config = {
        'ensemble_threshold': 0.35,
        'enable_caching': True,
        'log_predictions': True
    }
    
    predictor = DeepfakePredictor(config)
    result = predictor.predict_image(image_path)
    
    # Display detailed results
    print(f"\n{'='*70}")
    print("📊 DETAILED RESULTS")
    print(f"{'='*70}")
    print(f"\n🎯 Final Verdict: {'FAKE/AI-GENERATED' if result.is_fake else 'REAL'}")
    print(f"🎯 Confidence: {result.confidence:.2f}%")
    print(f"\n📈 Ensemble Details:")
    print(f"   Weighted Score: {result.ensemble_details['weighted_score']*100:.1f}%")
    print(f"   Threshold Used: {result.ensemble_details['threshold_used']*100:.1f}%")
    print(f"   Agreement: {result.ensemble_details['agreement']*100:.1f}%")
    
    print(f"\n🔬 Method Breakdown:")
    for method, scores in result.method_scores.items():
        status = "FAKE" if scores['is_fake'] else "REAL"
        print(f"   {method:12s}: {status:4s} ({scores['confidence']:5.1f}%) [weight: {scores['weight']}]")
    
    print(f"\n📝 Metadata:")
    print(f"   Timestamp: {result.timestamp}")
    print(f"   Image Hash: {result.image_hash[:16]}...")
    
    # Save detailed results
    output_file = f"result_{os.path.basename(image_path)}.json"
    with open(output_file, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"{'='*70}\n")
    
    return result

def test_multiple_images(image_paths):
    """Test multiple images and generate comparison report"""
    print("="*70)
    print("📊 BATCH IMAGE ANALYSIS")
    print("="*70)
    print(f"Testing {len(image_paths)} images")
    print("="*70)
    
    config = {
        'ensemble_threshold': 0.35,
        'enable_caching': True,
        'log_predictions': True
    }
    
    predictor = DeepfakePredictor(config)
    
    results = []
    for i, path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] Processing: {os.path.basename(path)}")
        
        if not os.path.exists(path):
            print(f"   ❌ File not found, skipping...")
            continue
        
        try:
            result = predictor.predict_image(path)
            results.append({
                'file': os.path.basename(path),
                'is_fake': result.is_fake,
                'confidence': result.confidence,
                'weighted_score': result.ensemble_details['weighted_score']
            })
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary report
    print(f"\n{'='*70}")
    print("📊 BATCH SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n{'File':<30} {'Prediction':<12} {'Confidence':<12} {'Score':<10}")
    print("-" * 70)
    for r in results:
        pred = "FAKE/AI" if r['is_fake'] else "REAL"
        print(f"{r['file'][:28]:<30} {pred:<12} {r['confidence']:<12.1f} {r['weighted_score']*100:<10.1f}%")
    
    # Statistics
    fake_count = sum(1 for r in results if r['is_fake'])
    real_count = len(results) - fake_count
    
    print(f"\n{'='*70}")
    print(f"Total Images: {len(results)}")
    print(f"   FAKE/AI: {fake_count}")
    print(f"   REAL: {real_count}")
    print(f"{'='*70}\n")
    
    # Get stats
    stats = predictor.get_stats()
    print(f"📈 Predictor Stats:")
    print(f"   Total predictions: {stats['total_predictions']}")
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Model loaded: {stats['model_loaded']}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: No image path provided!")
        print("\nUsage:")
        print("  Test single image:")
        print("    python test_model.py <image_path>")
        print("\n  Test consistency:")
        print("    python test_model.py <image_path> --consistency")
        print("\n  Test multiple images:")
        print("    python test_model.py <image1> <image2> <image3> ...")
        print("\nExamples:")
        print("  python test_model.py test_image.jpg")
        print("  python test_model.py test_image.jpg --consistency")
        print("  python test_model.py img1.jpg img2.jpg img3.jpg")
        sys.exit(1)
    
    # Parse arguments
    if '--consistency' in sys.argv:
        image_path = sys.argv[1]
        if not os.path.exists(image_path):
            print(f"❌ Error: File not found: {image_path}")
            sys.exit(1)
        
        is_consistent = test_consistency(image_path, num_runs=5)
        
        if is_consistent:
            print("\n🎉 Your model is working correctly!")
        else:
            print("\n💡 Consider adjusting the ensemble_threshold in predictor config")
    
    elif len(sys.argv) > 2:
        # Multiple images
        image_paths = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
        test_multiple_images(image_paths)
    
    else:
        # Single image
        image_path = sys.argv[1]
        if not os.path.exists(image_path):
            print(f"❌ Error: File not found: {image_path}")
            sys.exit(1)
        
        test_single_image(image_path)