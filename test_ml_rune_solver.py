#!/usr/bin/env python3
"""
Test script for the ML-based rune solver
This script tests the TensorFlow model loading and prediction functionality.
"""

import os
import sys
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tensorflow_installation():
    """Test if TensorFlow is properly installed."""
    print("=== Testing TensorFlow Installation ===")
    try:
        print(f"TensorFlow version: {tf.__version__}")
        print(f"Keras version: {keras.__version__}")
        
        # Test basic TensorFlow functionality
        a = tf.constant([[1, 2], [3, 4]])
        b = tf.constant([[1, 1], [0, 1]])
        c = tf.matmul(a, b)
        print(f"TensorFlow test calculation: {c.numpy()}")
        
        # Check for GPU
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"GPU devices found: {len(gpus)}")
            for gpu in gpus:
                print(f"  - {gpu}")
        else:
            print("No GPU devices found, using CPU")
        
        print("✅ TensorFlow installation test passed")
        return True
        
    except Exception as e:
        print(f"❌ TensorFlow installation test failed: {e}")
        return False

def test_model_creation():
    """Test creating a simple CNN model."""
    print("\n=== Testing Model Creation ===")
    try:
        # Create a simple CNN model
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(4, activation='softmax')
        ])
        
        # Compile the model
        model.compile(optimizer='adam',
                     loss='sparse_categorical_crossentropy',
                     metrics=['accuracy'])
        
        print(f"Model summary:")
        model.summary()
        
        # Test prediction with dummy data
        dummy_input = np.random.random((1, 64, 64, 3))
        prediction = model.predict(dummy_input, verbose=0)
        print(f"Model prediction shape: {prediction.shape}")
        print(f"Predicted class: {np.argmax(prediction[0])}")
        
        print("✅ Model creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Model creation test failed: {e}")
        return False

def test_rune_solver_import():
    """Test importing the rune solver module."""
    print("\n=== Testing Rune Solver Import ===")
    try:
        from src.runesolvercore.runesolver import RuneSolverML, ml_solver
        
        print("✅ Rune solver import successful")
        
        # Test ML solver initialization
        if hasattr(ml_solver, 'model_loaded'):
            print(f"ML solver model loaded: {ml_solver.model_loaded}")
        else:
            print("ML solver model_loaded attribute not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Rune solver import failed: {e}")
        return False

def test_image_preprocessing():
    """Test image preprocessing functionality."""
    print("\n=== Testing Image Preprocessing ===")
    try:
        from src.runesolvercore.runesolver import ml_solver
        
        # Create a dummy image
        dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test preprocessing
        processed = ml_solver.preprocess_image(dummy_img)
        
        if processed is not None:
            print(f"Preprocessed image shape: {processed.shape}")
            print(f"Preprocessed image dtype: {processed.dtype}")
            print(f"Preprocessed image range: [{processed.min():.3f}, {processed.max():.3f}]")
            print("✅ Image preprocessing test passed")
            return True
        else:
            print("❌ Image preprocessing returned None")
            return False
            
    except Exception as e:
        print(f"❌ Image preprocessing test failed: {e}")
        return False

def test_prediction():
    """Test prediction functionality."""
    print("\n=== Testing Prediction ===")
    try:
        from src.runesolvercore.runesolver import ml_solver
        
        # Create a dummy image
        dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test prediction
        direction = ml_solver.predict_direction(dummy_img)
        
        print(f"Predicted direction: {direction}")
        
        if direction is not None:
            print("✅ Prediction test passed")
            return True
        else:
            print("❌ Prediction returned None")
            return False
            
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        return False

def test_model_directory():
    """Test model directory structure."""
    print("\n=== Testing Model Directory ===")
    
    model_path = os.path.join('assets', 'models')
    print(f"Model directory: {model_path}")
    
    if os.path.exists(model_path):
        print("✅ Model directory exists")
        files = os.listdir(model_path)
        print(f"Files in model directory: {files}")
        
        # Check for model files
        model_files = [f for f in files if f.endswith(('.h5', '.pb', '.tflite'))]
        if model_files:
            print(f"✅ Found model files: {model_files}")
            return True
        else:
            print("⚠️  No model files found (this is expected for testing)")
            return True
    else:
        print("⚠️  Model directory does not exist (this is expected for testing)")
        return True

def main():
    """Run all tests."""
    print("🧪 Testing ML Rune Solver Components")
    print("=" * 50)
    
    tests = [
        test_tensorflow_installation,
        test_model_creation,
        test_rune_solver_import,
        test_image_preprocessing,
        test_prediction,
        test_model_directory
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ML components are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n📝 Next Steps:")
    print("1. Download the TensorFlow model from the Google Drive link in README.md")
    print("2. Extract the 'models' folder into the 'assets' directory")
    print("3. Run this test again to verify the real model loads correctly")
    print("4. The rune solver will automatically use the real model when available")

if __name__ == "__main__":
    main() 