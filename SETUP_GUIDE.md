# Auto Maple Plus - macOS Setup & Usage Guide

## 🎯 Quick Start Guide

### 1. **Hardware Setup**
- **Arduino Leonardo**: Connect via USB to your Mac
- **Upload Sketch**: Open `arduino_keyboard_controller.ino` in Arduino IDE and upload to your Leonardo
- **Note Port**: The port will be something like `/dev/cu.usbmodemHIDPC1` on macOS

### 2. **Software Setup**
- **Virtual Environment**: Already set up ✅
- **Dependencies**: Already installed ✅
- **Cross-Platform**: Already configured ✅

### 3. **Configuration**
1. **Set Arduino Port**: Edit `src/common/settings.py`
   ```python
   ARDUINO_PORT = "/dev/cu.usbmodemHIDPC1"  # Your actual port
   ARDUINO_BAUD_RATE = 115200
   ```

2. **Test Arduino**: Run `python test_arduino.py` to verify connection

### 4. **Launch Program**
```bash
python main.py
```

---

## 🖥️ GUI Interface Guide

The program opens with a **tabbed interface** containing 6 main sections:

### **Tab 1: View** - Monitor Your Character
- **Minimap Display**: Shows your character position and game state
- **Status Panel**: Displays current routine and bot status
- **Details Panel**: Shows detailed information about current actions

### **Tab 2: Edit** - Create/Modify Routines
- **Minimap Editor**: Click on minimap to create movement paths
- **Routine Commands**: Add/edit commands for your character
- **Command List**: View and modify the sequence of actions

### **Tab 3: Settings** - Configure Your Setup
- **Key Bindings**: Set up your MapleStory key bindings
- **Character Settings**: Configure character-specific options
- **General Settings**: Adjust program behavior

### **Tab 4: Notifier Settings** - Discord/Alert Setup
- **Discord Webhook**: Set up Discord notifications
- **Alert Settings**: Configure what events trigger alerts

### **Tab 5: Runtime Console** - Monitor Program
- **Status Messages**: Real-time program status
- **Error Logs**: View any issues or warnings

### **Tab 6: Automation Settings** - Advanced Features
- **Auto Login**: Configure automatic login
- **2FA Settings**: Set up two-factor authentication
- **World Selection**: Choose your MapleStory world

---

## 🎮 How to Use with MapleStory

### **Step 1: Load a Command Book**
1. Go to **Settings** tab
2. Click **"Load Command Book"** in the menu
3. Select a command book from `resources/command_books/`
4. This defines what keys your character can use

### **Step 2: Create a Routine**
1. Go to **Edit** tab
2. **Minimap Editor**: Click on the minimap to create a path
3. **Add Commands**: Use the command panel to add actions
4. **Save Routine**: Save your routine for later use

### **Step 3: Start Automation**
1. **Load Routine**: Load your saved routine
2. **Start Bot**: Use the start/stop key (default: F1)
3. **Monitor**: Watch the View tab to see what's happening

---

## 🔧 Common Issues & Solutions

### **Empty GUI Boxes**
- **Cause**: No command book loaded
- **Solution**: Load a command book from Settings → Load Command Book

### **Arduino Not Working**
- **Test**: Run `python test_arduino.py`
- **Check**: Verify port in `src/common/settings.py`
- **Verify**: Arduino sketch is uploaded correctly

### **Screen Capture Issues**
- **macOS**: Grant screen recording permissions
- **Full Screen**: Program uses full screen capture on macOS

### **Key Bindings Not Working**
- **Check**: Settings tab → Key Bindings
- **Verify**: Keys match your MapleStory settings
- **Test**: Use the key binding test feature

---

## 🎯 Basic Routine Example

### **Simple Farming Routine**
1. **Load Command Book**: Choose a class (e.g., `kanna`)
2. **Create Path**: Click minimap to create a simple rectangle
3. **Add Commands**:
   - `MOVE` - Move to next point
   - `ATTACK` - Attack monsters
   - `JUMP` - Jump to avoid obstacles
   - `BUFF` - Use buffs
4. **Save & Run**: Save routine and start bot

---

## 🔑 Important Keys

- **F1**: Start/Stop bot
- **F2**: Emergency stop
- **F3**: Toggle GUI visibility
- **F4**: Reload routine

---

## 📁 File Structure

```
auto-maple-plus/
├── src/common/settings.py     # Arduino port & main settings
├── resources/command_books/   # Character command definitions
├── resources/routines/        # Saved routines
├── assets/                   # Game images for detection
└── arduino_keyboard_controller.ino  # Arduino sketch
```

---

## 🆘 Getting Help

1. **Check Console**: Look at Runtime Console tab for errors
2. **Test Arduino**: Run `python test_arduino.py`
3. **Verify Settings**: Check all settings in Settings tab
4. **Load Command Book**: Make sure you have a command book loaded

---

## 🎮 Ready to Start!

1. **Configure Arduino port** in settings
2. **Load a command book** for your character class
3. **Create a simple routine** or load an existing one
4. **Start MapleStory** and position your character
5. **Press F1** to start the bot

The program will now automate your MapleStory character using genuine hardware keyboard inputs via Arduino! 🚀 