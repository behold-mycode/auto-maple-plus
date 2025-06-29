# Changelog

## [2.1.0] - 2024-01-XX - Machine Learning Enhancement

### 🚀 Major Features
- **Enhanced Machine Learning Rune Solver**: Completely rewrote the rune-solving system to use TensorFlow for more accurate arrow detection
- **Automatic Model Management**: System automatically loads pre-trained models or creates placeholder models for testing
- **Fallback Mechanisms**: Seamless fallback to computer vision methods when ML models are unavailable
- **Cross-Platform ML Support**: Optimized TensorFlow installation for macOS (Metal), Windows (CUDA), and Linux

### 🛠️ New Tools
- **`test_ml_rune_solver.py`**: Comprehensive testing script for ML components
- **`train_rune_model.py`**: Model training script with synthetic data generation and real data support
- **Model Training Pipeline**: Complete workflow for creating custom rune-solving models

### 📦 Dependencies
- Added TensorFlow 2.13+ with platform-specific optimizations
- Added scikit-learn for model training and evaluation
- Added matplotlib for training visualization
- Added tensorflow-macos and tensorflow-metal for Apple Silicon support

### 🔧 Technical Improvements
- **RuneSolverML Class**: New ML-based rune solver with automatic model loading
- **Image Preprocessing**: Optimized image processing pipeline for ML inference
- **Label Map Parsing**: Automatic parsing of TensorFlow label maps
- **Model Metadata**: Comprehensive model metadata and test results storage

### 🎯 ML Features
- **Synthetic Data Generation**: Create training data automatically for testing
- **Real Data Training**: Support for training on actual rune images
- **Model Evaluation**: Comprehensive model performance metrics
- **Training Visualization**: Plot training history and model performance

### 🔄 Backward Compatibility
- Maintains full compatibility with existing computer vision methods
- Automatic fallback ensures system works even without ML models
- No breaking changes to existing functionality

## [2.0.0] - 2024-01-XX - Cross-Platform Arduino Edition

### 🚀 Major Features
- **Cross-Platform Support**: Now works on Windows, macOS, and Linux
- **Arduino Leonardo Integration**: Replaced Windows-only interception with Arduino-based USB HID keyboard
- **Hardware-Level Input**: Genuine keyboard events indistinguishable from real input

### 🔧 Technical Changes
- **Removed Windows Dependencies**: Eliminated interception_python and pywin32
- **Added Arduino Support**: New arduino_input.py module for cross-platform keyboard input
- **Updated Capture System**: Enhanced screen capture for cross-platform compatibility
- **Improved Window Detection**: Template-based and manual window detection methods

### 📦 Dependencies
- Removed: interception_python, pywin32
- Added: pyserial, pynput (macOS), keyboard (Windows/Linux)
- Updated: All existing dependencies to latest compatible versions

### 🛠️ New Tools
- **`arduino_keyboard_controller.ino`**: Arduino sketch for USB HID keyboard emulation
- **`test_arduino.py`**: Arduino connection and key input testing
- **`window_selector.py`**: Interactive window selection tool
- **`minimap_debugger.py`**: Minimap detection debugging tool
- **`fix_minimap.py`**: Manual minimap configuration tool

### 📚 Documentation
- **`ARDUINO_SETUP.md`**: Comprehensive Arduino setup guide
- **Updated README.md**: Cross-platform setup instructions
- **Platform-specific notes**: Detailed setup for each operating system

### 🔄 Compatibility
- **Windows**: Full compatibility with Arduino Leonardo
- **macOS**: Full compatibility with screen recording permissions
- **Linux**: Full compatibility with dialout group permissions

### 🎯 Features
- **Undetectable Input**: Hardware-level keyboard events
- **No OS Dependencies**: Works on any platform with Arduino support
- **Improved Reliability**: More stable than software-based input methods
- **Future-Proof**: Hardware solution that won't be affected by OS updates

## [1.0.0] - Original Release

### 🚀 Initial Features
- **Computer Vision**: OpenCV-based minimap parsing and object detection
- **Pathfinding**: A* algorithm for efficient navigation
- **Routine System**: CSV-based routine execution
- **Command Books**: Modular character-specific action definitions
- **Rune Solving**: Computer vision-based arrow detection
- **Discord Integration**: Status updates and remote control
- **GUI Interface**: Comprehensive user interface for bot control

### 🔧 Technical Foundation
- **Template Matching**: OpenCV-based image recognition
- **Screen Capture**: MSS-based screen capture system
- **Input Simulation**: Windows interception for keyboard input
- **Modular Architecture**: Extensible component-based design 