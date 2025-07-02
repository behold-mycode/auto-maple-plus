# Astelle Setup Guide

## ⚠️ **IMPORTANT: Arduino Setup Required**

This project uses **Arduino Leonardo** for keyboard input instead of software-based methods. This ensures cross-platform compatibility and undetectable input.

### **Arduino Setup (Required First Step)**

1. **Follow the Arduino Setup Guide**: Read `ARDUINO_SETUP.md` for complete instructions
2. **Upload Arduino Sketch**: Upload `arduino_keyboard_controller.ino` to your Arduino Leonardo
3. **Configure Port**: Set your Arduino port in `src/common/settings.py`
4. **Test Connection**: Ensure Arduino is connected before starting Auto Maple

### **Why Arduino?**
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Undetectable**: Sends genuine hardware keyboard events
- **Reliable**: No dependency on OS-specific APIs
- **Secure**: Physical hardware input, not software simulation

## 🎯 **Updated Keybindings Summary**

### **Movement**
- **Jump**: `space`
- **Blink/Teleport**: `alt` (as requested)
- **Up Jump**: `ctrl`

### **Main Attack Skills**
- **Ray (Main Attack)**: `a`
- **Boom (Secondary)**: `s`
- **Pole (3rd Job)**: `d`
- **Link (4th Job)**: `g`

### **Stellar Skills (Number Keys for Easy Sequence)**
- **Antares (1st Job)**: `1`
- **Algol (2nd Job)**: `2`
- **Alchiba (3rd Job)**: `3`
- **Bellatrix (3rd Job)**: `4`
- **Fomalhaut (3rd Job)**: `5`
- **Izar (4th Job)**: `6`
- **Vega (4th Job)**: `7`
- **Sadalmelik (4th Job)**: `8`

### **5th Job Skills**
- **Shine**: `q`
- **Sirius**: `w`
- **Sadalsuud**: `e`
- **Time Binder**: `r`
- **Savior's Circle**: `t`

### **Utility**
- **Pulse**: `y`
- **NPC/Gather**: `f` (as requested)
- **Pet Feed**: `9`
- **Cash Shop**: `` ` ``

## 🚀 **Step-by-Step Setup**

### **Step 0: Arduino Setup (REQUIRED)**
1. **Read Arduino Guide**: `ARDUINO_SETUP.md`
2. **Upload Sketch**: Upload `arduino_keyboard_controller.ino` to Arduino Leonardo
3. **Configure Port**: Edit `src/common/settings.py` and set `arduino_port`
4. **Test Connection**: Ensure Arduino is connected and recognized

### **Step 1: Load Your Command Book**

1. **Start Auto Maple Plus**
2. **Go to File → Load Command Book**
3. **Select**: `resources/command_books/astelle.py`
4. **Verify** the command book loads successfully

### **Step 2: Test Your Keybindings**

1. **Go to Settings tab**
2. **Check "Astelle Keybindings" section**
3. **Verify all keys match your actual keybindings**
4. **If any keys are wrong, modify the command book file**

### **Step 3: Load Your Routine**

1. **Go to File → Load Routine**
2. **Select**: `resources/routines/astelle/generic_flat_map.csv`
3. **Verify** the routine loads in the View tab

### **Step 4: Test the Routine**

1. **Go to a flat map** (like a training map)
2. **Position your character** at the starting point
3. **Enable Auto Maple** (F12 or your enable key)
4. **Watch** the routine execute
5. **Adjust** positions if needed

## 🗺️ **Generic Flat Map Routine Explanation**

### **Routine Structure**
```
Start → Position 1 → Position 2 → Position 3 → Position 4 → Buff Check → Loop
```

### **Position Details**

**Position 1 (x=0.300, y=0.238)**
- Applies buffs
- Uses Ray (left direction, 2 attacks)
- Uses Boom (left direction, 1 attack)

**Position 2 (x=0.500, y=0.238)**
- Uses Ray (right direction, 2 attacks)
- Uses Pole (right direction)

**Position 3 (x=0.700, y=0.238)**
- Uses Ray (left direction, 2 attacks)
- Uses Link (left direction)

**Position 4 (x=0.500, y=0.238)**
- Uses Ray (right direction, 2 attacks)
- Uses Boom (right direction, 1 attack)

**Buff Check (x=0.400, y=0.238)**
- Runs every 10 iterations
- Applies buffs
- Feeds pet

**Stellar Skills (x=0.600, y=0.238)**
- Uses Ray + Antares + Algol
- Uses Ray + Fomalhaut + Izar

## 🛠️ **Customization Guide**

### **Modifying Keybindings**

If you need to change any keybindings:

1. **Edit** `resources/command_books/astelle.py`
2. **Find the Key class** (around line 10)
3. **Change the key values** to match your setup
4. **Save the file**
5. **Reload the command book** in Auto Maple

**Note**: The command book uses Arduino input methods (`from src.common.arduino_input import press, key_down, key_up`). This ensures cross-platform compatibility and undetectable input.

### **Adding New Skills**

To add a new skill:

1. **Add the key** to the Key class
2. **Create a new command class** following the pattern
3. **Add it to your routine** in the CSV file

### **Modifying the Routine**

To change the routine:

1. **Use the Edit tab** to modify positions
2. **Add/remove commands** at each position
3. **Adjust timing** with frequency parameters
4. **Save** the routine

## 🎮 **Manual Play Integration**

### **Stellar Skill Sequence**
For manual play, you can easily use the Stellar skills in order:
```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
```

This creates a natural flow from 1st job to 4th job skills.

### **Burst Rotation**
For bossing, you can create a burst sequence:
```
q (Shine) → w (Sirius) → e (Sadalsuud) → r (Time Binder) → t (Savior's Circle)
```

## 🔧 **Troubleshooting**

### **Arduino Issues (Most Common)**

1. **Arduino not detected**
   - Check USB cable connection
   - Verify Arduino IDE shows correct board
   - Check port name in `src/common/settings.py`
   - Try different USB ports

2. **Serial connection failed**
   - Ensure Arduino is connected before starting bot
   - Check that no other program is using the serial port
   - Verify baud rate (default: 115200)
   - Check permissions (Linux/macOS)

3. **Keys not working**
   - Ensure MapleStory window is focused
   - Check that Arduino sketch uploaded successfully
   - Test with Serial Monitor to see if commands are received
   - Verify key mappings in Arduino code

### **Common Issues**

1. **Character not moving**
   - Check if blink key is correct (`alt`)
   - Verify movement function in command book

2. **Skills not working**
   - Verify keybindings in Settings tab
   - Check if skills are available for your level

3. **Routine not looping**
   - Check label and jump syntax in CSV
   - Verify routine file format

4. **Poor efficiency**
   - Adjust position coordinates
   - Modify skill timing and frequency

### **Testing Individual Skills**

1. **Go to Edit tab**
2. **Select a position**
3. **Add individual skills**
4. **Test each skill** to ensure it works

## 📈 **Optimization Tips**

### **For Different Maps**

1. **Study the map layout**
2. **Identify optimal farming spots**
3. **Adjust position coordinates**
4. **Modify skill combinations**

### **For Different Levels**

1. **Remove unavailable skills** from routine
2. **Add new skills** as you level up
3. **Adjust buff combinations**
4. **Optimize for your current damage output**

### **For Bossing**

1. **Create separate boss routine**
2. **Focus on burst skills**
3. **Add safety skills** (Sadalmelik for I-frame)
4. **Use Time Binder** for binding

## 🎉 **Next Steps**

1. **Test the basic routine** on a simple map
2. **Adjust positions** to match your map
3. **Modify skill combinations** based on your level
4. **Create additional routines** for different maps
5. **Optimize for efficiency** and damage output

## 📚 **Resources**

- **Command Book**: `resources/command_books/astelle.py`
- **Routine**: `resources/routines/astelle/generic_flat_map.csv`
- **Setup Guide**: `ASTELLE_SETUP_GUIDE.md`
- **Arduino Setup**: `ARDUINO_SETUP.md`
- **Arduino Sketch**: `arduino_keyboard_controller.ino`
- **Routine Creation Guide**: `ROUTINE_CREATION_GUIDE.md`

Remember: Start simple and gradually add complexity as you become familiar with the system! 