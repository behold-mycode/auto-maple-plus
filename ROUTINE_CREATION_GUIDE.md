# Routine Creation Guide

## 📋 **Overview**

Routines in Auto Maple Plus are CSV files that tell the bot where to go and what to do. The program **does NOT automatically generate routines** - you create them manually using the built-in tools.

## 🛠️ **How to Create Routines**

### **Method 1: Using the GUI (Recommended)**

1. **Load your command book** first (File → Load Command Book)
2. **Start Auto Maple** and go to the "Edit" tab
3. **Use the recording feature**:
   - Click "Record Position" to capture your current position
   - Move to different locations and record each position
   - Select recorded positions to add commands to them
4. **Add commands** to each position using the GUI
5. **Save the routine** (File → Save Routine)

### **Method 2: Manual CSV Creation**

You can create CSV files manually. Here's the format:

```csv
@, label=Start
*, x=0.500, y=0.238, frequency=1, skip=False, adjust=False
    Buff
    MainAttack, direction=left, jump=False
*, x=0.600, y=0.238, frequency=1, skip=False, adjust=False
    SecondaryAttack, direction=right
    MobilitySkill, direction=left
@, label=Loop
*, x=0.400, y=0.238, frequency=1, skip=False, adjust=False
    UltimateSkill, direction=left
    SupportSkill
>, label=Loop
```

## 📝 **CSV Format Reference**

### **Components**

| Symbol | Component | Description | Example |
|--------|-----------|-------------|---------|
| `@` | Label | Creates a reference point | `@, label=Start` |
| `*` | Point | Location with commands | `*, x=0.500, y=0.238` |
| `>` | Jump | Jump to a label | `>, label=Start` |
| `$` | Setting | Change bot settings | `$, setting=value` |

### **Point Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | float | required | X coordinate (0.0 to 1.0) |
| `y` | float | required | Y coordinate (0.0 to 1.0) |
| `frequency` | int | 1 | Execute every N iterations |
| `skip` | bool | False | Skip first execution |
| `adjust` | bool | False | Fine-tune position |

### **Command Parameters**

Commands are indented under points. Common parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `direction` | string | 'left', 'right', 'up', 'down' |
| `jump` | bool | Whether to jump before skill |
| `attacks` | int | Number of attacks |
| `repetitions` | int | Number of repetitions |

## 🎮 **Step-by-Step Routine Creation**

### **Step 1: Plan Your Route**
1. **Identify key locations** in your farming map
2. **Plan the movement path** between locations
3. **Decide what skills** to use at each location
4. **Consider efficiency** - minimize travel time

### **Step 2: Record Positions**
1. **Start Auto Maple** and go to Edit tab
2. **Position your character** at the first location
3. **Press F1** (or your record key) to record position
4. **Move to next location** and repeat
5. **Continue until** you've recorded all positions

### **Step 3: Add Commands**
1. **Select a recorded position** in the list
2. **Add movement commands** (Move, Adjust)
3. **Add skill commands** from your command book
4. **Set parameters** like direction and jump
5. **Repeat for each position**

### **Step 4: Create Loops**
1. **Add labels** at key points (e.g., start of route)
2. **Add jump commands** to create loops
3. **Test the routine** to ensure it flows correctly

### **Step 5: Optimize**
1. **Adjust timing** between commands
2. **Fine-tune positions** for better efficiency
3. **Add safety commands** (buffs, pet feeding)
4. **Test and refine** the routine

## 📁 **File Organization**

### **Routine Storage**
Routines are stored in: `resources/routines/[classname]/`

### **Naming Convention**
- Use descriptive names: `mapname_route.csv`
- Examples: `clp.csv`, `dcup2.csv`, `lh6.csv`

### **File Structure**
```
resources/routines/
├── adele/
│   ├── clp.csv
│   └── dcup2.csv
├── kanna/
│   ├── cf1.csv
│   └── lh6.csv
└── shadower/
    ├── CCMottledForest2.csv
    └── LLOutlawStreet3.csv
```

## 🔧 **Advanced Techniques**

### **Conditional Execution**
```csv
*, x=0.500, y=0.238, frequency=5, skip=False, adjust=False
    Buff
    MainAttack, direction=left
```
This point executes every 5 iterations.

### **Skip First Execution**
```csv
*, x=0.500, y=0.238, frequency=1, skip=True, adjust=False
    SecondaryAttack
```
This point skips the first time through the routine.

### **Position Adjustment**
```csv
*, x=0.500, y=0.238, frequency=1, skip=False, adjust=True
    UltimateSkill
```
This point fine-tunes position before executing commands.

### **Complex Loops**
```csv
@, label=MainLoop
*, x=0.500, y=0.238, frequency=1, skip=False, adjust=False
    MainAttack, direction=left
*, x=0.600, y=0.238, frequency=1, skip=False, adjust=False
    SecondaryAttack, direction=right
@, label=CheckBuffs
*, x=0.500, y=0.238, frequency=10, skip=False, adjust=False
    Buff
>, label=MainLoop
```

## 🎯 **Best Practices**

### **Efficiency Tips**
1. **Minimize travel distance** between points
2. **Use appropriate skill ranges** for each location
3. **Group similar activities** together
4. **Plan for different map layouts**

### **Safety Tips**
1. **Add buff commands** at regular intervals
2. **Include pet feeding** commands
3. **Add emergency stops** (cash shop entry)
4. **Test routines thoroughly** before long runs

### **Maintenance Tips**
1. **Backup your routines** regularly
2. **Document complex routines** with comments
3. **Update routines** when game changes occur
4. **Share routines** with the community

## 🚀 **Creating Dozens of Routines**

### **Template Approach**
1. **Create a base template** for your character class
2. **Copy and modify** for different maps
3. **Use consistent naming** conventions
4. **Maintain a routine library**

### **Map-Specific Optimization**
1. **Study each map's layout** carefully
2. **Identify optimal farming spots**
3. **Plan efficient movement paths**
4. **Test and refine** each routine

### **Character-Specific Considerations**
1. **Use your character's strengths** (range, mobility, etc.)
2. **Optimize skill combinations** for each map
3. **Consider cooldown management**
4. **Adapt to your character's limitations**

## 🔍 **Troubleshooting**

### **Common Issues**
1. **Character not moving**: Check coordinates and pathfinding
2. **Skills not working**: Verify keybindings in command book
3. **Routine not looping**: Check label and jump syntax
4. **Poor efficiency**: Optimize movement paths and timing

### **Debugging Tips**
1. **Use the View tab** to monitor routine execution
2. **Check console output** for error messages
3. **Test individual commands** before full routines
4. **Use the minimap** to verify positions

## 📚 **Resources**

### **Example Routines**
- Study existing routines in `resources/routines/`
- Learn from community-created routines
- Adapt successful patterns to your needs

### **Community Resources**
- Join Auto Maple Discord/forums
- Share and download routines
- Get help with complex routine creation
- Stay updated on game changes

### **Tools**
- **Minimap Debugger**: `python minimap_debugger.py`
- **Window Selector**: `python window_selector.py`
- **Position Recorder**: Built into the GUI

## 🎉 **Getting Started**

1. **Create your command book** using the template
2. **Load it in Auto Maple**
3. **Record your first positions**
4. **Add basic commands**
5. **Test and refine**
6. **Create more complex routines**

Remember: Routine creation is an iterative process. Start simple and gradually add complexity as you become more familiar with the system! 