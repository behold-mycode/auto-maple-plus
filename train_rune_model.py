#!/usr/bin/env python3
"""
Rune Model Training Script
This script helps users train their own TensorFlow model for rune solving.
"""

import os
import sys
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import json

def create_model():
    """Create a CNN model for arrow direction classification."""
    model = keras.Sequential([
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Flatten and dense layers
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(4, activation='softmax')  # 4 classes: up, down, left, right
    ])
    
    return model

def load_training_data(data_dir):
    """Load training data from directory structure."""
    print(f"Loading training data from {data_dir}")
    
    images = []
    labels = []
    class_names = ['up', 'down', 'left', 'right']
    
    for class_idx, class_name in enumerate(class_names):
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"Warning: {class_dir} does not exist")
            continue
            
        print(f"Loading {class_name} images...")
        for filename in os.listdir(class_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(class_dir, filename)
                try:
                    # Load and preprocess image
                    img = cv2.imread(filepath)
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, (64, 64))
                        img = img.astype(np.float32) / 255.0
                        
                        images.append(img)
                        labels.append(class_idx)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
    
    if not images:
        print("No training data found!")
        return None, None, None
    
    X = np.array(images)
    y = np.array(labels)
    
    print(f"Loaded {len(X)} images with {len(np.unique(y))} classes")
    print(f"Class distribution: {np.bincount(y)}")
    
    return X, y, class_names

def create_synthetic_data():
    """Create synthetic training data for demonstration."""
    print("Creating synthetic training data...")
    
    num_samples_per_class = 100
    images = []
    labels = []
    
    # Create synthetic arrow images
    for class_idx in range(4):
        for _ in range(num_samples_per_class):
            # Create a 64x64 image
            img = np.zeros((64, 64, 3), dtype=np.float32)
            
            # Add some random background
            img += np.random.normal(0, 0.1, img.shape)
            
            # Create arrow pattern based on class
            if class_idx == 0:  # up
                # Vertical arrow pointing up
                img[20:40, 30:34] = [1, 0, 0]  # Red arrow
                img[15:20, 32:32] = [1, 0, 0]
            elif class_idx == 1:  # down
                # Vertical arrow pointing down
                img[24:44, 30:34] = [0, 1, 0]  # Green arrow
                img[44:49, 32:32] = [0, 1, 0]
            elif class_idx == 2:  # left
                # Horizontal arrow pointing left
                img[30:34, 20:40] = [0, 0, 1]  # Blue arrow
                img[32:32, 15:20] = [0, 0, 1]
            else:  # right
                # Horizontal arrow pointing right
                img[30:34, 24:44] = [1, 1, 0]  # Yellow arrow
                img[32:32, 44:49] = [1, 1, 0]
            
            # Add some noise
            img += np.random.normal(0, 0.05, img.shape)
            img = np.clip(img, 0, 1)
            
            images.append(img)
            labels.append(class_idx)
    
    X = np.array(images)
    y = np.array(labels)
    class_names = ['up', 'down', 'left', 'right']
    
    print(f"Created {len(X)} synthetic images")
    return X, y, class_names

def train_model(X, y, class_names, epochs=50, batch_size=32):
    """Train the model."""
    print("Training model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create model
    model = create_model()
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Print model summary
    model.summary()
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
        keras.callbacks.ModelCheckpoint(
            'best_rune_model.h5',
            save_best_only=True,
            monitor='val_accuracy'
        )
    ]
    
    # Train model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest accuracy: {test_accuracy:.4f}")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_classes, target_names=class_names))
    
    return model, history, (X_test, y_test, y_pred_classes)

def plot_training_history(history):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot accuracy
    ax1.plot(history.history['accuracy'], label='Training Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Plot loss
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
    plt.show()

def save_model_and_metadata(model, class_names, test_results):
    """Save the trained model and metadata."""
    # Create models directory
    models_dir = os.path.join('assets', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(models_dir, 'rune_solver_model.h5')
    model.save(model_path)
    print(f"Model saved to: {model_path}")
    
    # Save metadata
    metadata = {
        'class_names': class_names,
        'input_shape': [64, 64, 3],
        'num_classes': len(class_names),
        'model_type': 'CNN',
        'description': 'Rune solver model for arrow direction classification'
    }
    
    metadata_path = os.path.join(models_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {metadata_path}")
    
    # Save test results
    X_test, y_test, y_pred_classes = test_results
    test_results_data = {
        'test_accuracy': float(model.evaluate(X_test, y_test, verbose=0)[1]),
        'predictions': y_pred_classes.tolist(),
        'true_labels': y_test.tolist()
    }
    
    results_path = os.path.join(models_dir, 'test_results.json')
    with open(results_path, 'w') as f:
        json.dump(test_results_data, f, indent=2)
    print(f"Test results saved to: {results_path}")

def main():
    """Main training function."""
    print("🎯 Rune Model Training Script")
    print("=" * 50)
    
    # Check if training data exists
    data_dir = "training_data"
    if os.path.exists(data_dir):
        print(f"Found training data directory: {data_dir}")
        X, y, class_names = load_training_data(data_dir)
        if X is None:
            print("Failed to load training data, using synthetic data")
            X, y, class_names = create_synthetic_data()
    else:
        print("No training data found, creating synthetic data")
        X, y, class_names = create_synthetic_data()
    
    # Train model
    model, history, test_results = train_model(X, y, class_names)
    
    # Plot training history
    try:
        plot_training_history(history)
    except Exception as e:
        print(f"Could not plot training history: {e}")
    
    # Save model and metadata
    save_model_and_metadata(model, class_names, test_results)
    
    print("\n🎉 Training completed!")
    print("\n📝 Next steps:")
    print("1. The model has been saved to assets/models/")
    print("2. Run test_ml_rune_solver.py to verify the model works")
    print("3. The rune solver will automatically use this model")
    print("\n💡 To improve the model:")
    print("- Collect real rune images and organize them in training_data/")
    print("- Create subdirectories: up/, down/, left/, right/")
    print("- Place arrow images in the appropriate directories")
    print("- Run this script again to train on real data")

if __name__ == "__main__":
    main() 