# Auto Maple Plus - Cross-Platform Edition

Auto Maple Plus is an intelligent Python bot that plays MapleStory, a 2D side-scrolling MMORPG, using **Arduino-based hardware keyboard input**, **TensorFlow machine learning**, OpenCV template matching, and other computer vision techniques. This fork has been modified to work on **Windows, macOS, and Linux** using an Arduino Leonardo as a USB HID keyboard.

Community-created resources, such as **command books** for each class and **routines** for each map, can be found in the **[resources repository](https://github.com/tanjeffreyz/auto-maple-resources)**.

## 🆕 Cross-Platform Compatibility

This version replaces the Windows-specific interception library with an **Arduino Leonardo** that acts as a USB HID keyboard. This enables:

- ✅ **Windows** - Full compatibility
- ✅ **macOS** - Full compatibility  
- ✅ **Linux** - Full compatibility
- ✅ **Undetectable input** - Genuine hardware keyboard events
- ✅ **No OS dependencies** - Works on any platform

See **[ARDUINO_SETUP.md](ARDUINO_SETUP.md)** for detailed setup instructions.

## 🤖 Enhanced Machine Learning

The rune-solving system now features:

- **TensorFlow-based arrow detection** - More accurate than traditional CV methods
- **Automatic model loading** - Works with or without pre-trained models
- **Fallback to computer vision** - Ensures reliability even without ML models
- **Model training tools** - Create your own models with `train_rune_model.py`
- **Cross-platform ML support** - Optimized for macOS (Metal), Windows (CUDA), and Linux

<br>

<h2 align="center">
  Minimap
</h2>

<table align="center" border="0">
  <tr>
    <td>
      <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="100%"/>
    </td>
  </tr>
</table>

<table align="center" border="0">
  <tr>
    <td width="100%">
Auto Maple uses computer vision to track the player's position on the minimap. It then uses the <b>A* pathfinding algorithm</b> to find the shortest path to the next location in the routine. The bot will automatically walk to the next location while avoiding obstacles and other players.
    </td>
  </tr>
</table>

<br>

<h2 align="center">
  Routines
</h2>

<table align="center" border="0">
  <tr>
    <td>
      <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="100%"/>
    </td>
  </tr>
</table>

<table align="center" border="0">
  <tr>
    <td width="100%">
Routines are CSV files that contain a sequence of locations and commands. The bot will execute these commands in order, moving from one location to the next. Each location can have multiple commands associated with it, such as attacking monsters, using skills, or collecting items.
    </td>
  </tr>
</table>

<br>

<h2 align="center">
  Runes
</h2>

<table align="center" border="0">
  <tr>
    <td>
      <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="100%"/>
    </td>
  </tr>
</table>

<table align="center" border="0">
  <tr>
    <td width="100%">
Auto Maple has the ability to automatically solve "runes", or in-game arrow key puzzles. It first uses OpenCV's color filtration and <b>Canny edge detection</b> algorithms to isolate the arrow keys and reduce as much background noise as possible. Then, it runs multiple inferences on the preprocessed frames using a custom-trained <b>TensorFlow</b> model until two inferences agree. Because of this preprocessing, Auto Maple is extremely accurate at solving runes in all kinds of (often colorful and chaotic) environments.

**NEW**: The ML system now includes automatic model creation, training tools, and fallback mechanisms for maximum reliability.
    </td>
  </tr>
</table>

<br>

<h2 align="center">
  Video Demonstration
</h2>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg"><b>Click below to watch the full video</b></a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg">
    <img src="https://user-images.githubusercontent.com/69165598/123308656-c5b61100-d4d8-11eb-99ac-c465665474b5.gif" width="600px"/>
  </a>
</p>

<br>

<h2 align="center">
  Setup
</h2>

## Hardware Requirements

- **Arduino Leonardo** (or any Arduino with ATmega32u4 that supports USB HID)
- USB cable to connect Arduino to your computer
- Computer running Windows, macOS, or Linux

## Quick Setup

1. **Download and install [Python 3](https://www.python.org/downloads/)**
2. **Download and install [Git](https://git-scm.com/downloads)**
3. **Clone this repository:**
   ```bash
   git clone https://github.com/your-username/auto-maple-plus.git
   cd auto-maple-plus
   ```
4. **Set up Arduino Leonardo:**
   - Connect Arduino Leonardo to your computer
   - Upload `arduino_keyboard_controller.ino` to your Arduino
   - Find your Arduino port (see [ARDUINO_SETUP.md](ARDUINO_SETUP.md))
5. **Configure Arduino settings:**
   - Edit `src/common/settings.py`
   - Set `arduino_port` to your Arduino's port
   - Example: `arduino_port = "/dev/tty.usbmodem14101"` (macOS/Linux) or `arduino_port = "COM3"` (Windows)
6. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
7. **Set up Machine Learning (Optional but Recommended):**
   ```bash
   # Test ML components
   python test_ml_rune_solver.py
   
   # Train your own model (if you don't have the original)
   python train_rune_model.py
   ```
8. **Download the [TensorFlow model](https://drive.google.com/drive/folders/1SPdTNF4KZczoWyWTgfyTBRvLvy7WSGpu?usp=sharing)** and extract the "models" folder into the "assets" directory (optional - the system will work without it)
9. **Run Auto Maple:**
   ```bash
   python main.py
   ```

## Machine Learning Setup

### Option 1: Use Pre-trained Model
1. Download the TensorFlow model from the Google Drive link above
2. Extract the "models" folder into the "assets" directory
3. Run `python test_ml_rune_solver.py` to verify it works

### Option 2: Train Your Own Model
1. Run `python train_rune_model.py` to create a synthetic model for testing
2. For better accuracy, collect real rune images:
   - Create `training_data/` directory
   - Add subdirectories: `up/`, `down/`, `left/`, `right/`
   - Place arrow images in appropriate directories
   - Run the training script again

### Option 3: Use Computer Vision Only
The system will automatically fall back to traditional computer vision methods if no ML model is available.

## Detailed Setup

For detailed Arduino setup instructions, troubleshooting, and advanced configuration, see **[ARDUINO_SETUP.md](ARDUINO_SETUP.md)**.

## Platform-Specific Notes

### macOS
- May require screen recording permissions in System Preferences > Security & Privacy > Privacy > Screen Recording
- Arduino ports typically appear as `/dev/tty.usbmodem*` or `/dev/cu.usbmodem*`
- TensorFlow will use Metal acceleration on Apple Silicon (M1/M2)

### Linux
- May need to add user to dialout group: `sudo usermod -a -G dialout $USER`
- Arduino ports typically appear as `/dev/ttyACM*`
- TensorFlow will use CPU or CUDA if available

### Windows
- Arduino ports appear as `COM#` in Device Manager
- No additional permissions required
- TensorFlow will use CPU or CUDA if available

## Why Arduino?

The original Auto Maple used Windows-specific interception libraries that don't work on macOS or Linux. By using an Arduino Leonardo as a USB HID keyboard, we can send genuine hardware keystrokes that are indistinguishable from real keyboard input, making the bot work on any platform while being more reliable and undetectable.

## Testing

Run these scripts to verify everything is working:

```bash
# Test Arduino connection
python test_arduino.py

# Test ML components
python test_ml_rune_solver.py

# Test window detection
python window_selector.py

# Test minimap detection
python minimap_debugger.py
```
