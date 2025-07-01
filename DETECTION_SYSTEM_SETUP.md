# Detection System Setup Guide

This guide helps you set up the improved cross-platform detection system in Auto Maple Plus.

## Overview

The new detection system provides:
- **Cross-platform window detection** (macOS Quartz + Windows Win32)
- **Window caching** to avoid repeated expensive searches
- **Improved template matching** with normalized thresholds
- **Manual override options** for both window and minimap detection

## Quick Start

### 1. Window Setup (Required)

Run the window selector to capture your MapleStory window:

```bash
python simple_window_selector.py
```

**Instructions:**
1. Make sure MapleStory is open and visible
2. Click "Start Selection" 
3. Click the **top-left corner** of your MapleStory window
4. Click the **bottom-right corner** of your MapleStory window
5. The tool saves your window coordinates to `window_config.json`

### 2. Minimap Setup (Optional but Recommended)

If automatic minimap detection fails, use the minimap fixer:

```bash
python fix_minimap.py
```

**Instructions:**
1. Takes a screenshot of your configured window
2. Draw a rectangle around your minimap
3. Saves coordinates to `minimap_config.json`

### 3. Test Your Setup

Validate everything is working:

```bash
python test_detection_system.py
```

This will test:
- Window detection and caching
- Minimap calibration
- Template matching accuracy

## How It Works

### Window Detection Priority

The system tries these methods in order:

1. **Cached Rectangle** - Previously found window (fastest)
2. **window_config.json** - From window selector tool
3. **Manual Settings** - If enabled in settings
4. **OS Native Detection**:
   - macOS: Quartz window services
   - Windows: Win32 FindWindow API
5. **Template Fallback** - Image-based detection (TODO)
6. **Default Fallback** - (0, 0, 1366, 768)

### Minimap Detection Priority

1. **minimap_config.json** - From manual selection
2. **Template Matching** - Automatic corner detection
3. **Failure** - Retry on next frame

### Template Matching Improvements

- Uses normalized correlation (`TM_CCOEFF_NORMED`)
- Scores are always between -1 and 1
- Configurable thresholds (default 0.8)
- Better false positive rejection

## Configuration Files

### window_config.json
```json
{
  "left": 100,
  "top": 50, 
  "width": 1366,
  "height": 768
}
```

### minimap_config.json
```json
{
  "mm_left": 1200,
  "mm_top": 100,
  "mm_right": 1350,
  "mm_bottom": 250
}
```

## Troubleshooting

### Window Detection Issues

**Problem**: "Using default window coordinates"
- **Solution**: Run `simple_window_selector.py` to set up window detection

**Problem**: Window detection fails on macOS
- **Solution**: Install Quartz dependencies:
  ```bash
  pip install pyobjc-core pyobjc-framework-Quartz
  ```

### Minimap Detection Issues

**Problem**: "Could not find minimap corners"
- **Solution**: Run `fix_minimap.py` to manually configure
- **Alternative**: Lower threshold in `capture.py` (try 0.6 instead of 0.8)

**Problem**: Minimap ratio seems wrong
- **Solution**: Delete `minimap_config.json` and reconfigure

### Template Matching Issues

**Problem**: Too many false positives
- **Solution**: Increase threshold in detection functions
- **Check**: Window is properly locked to game area

**Problem**: No matches found
- **Solution**: Decrease threshold or check if templates match your resolution

## Advanced Configuration

### Manual Window Position

In `settings.py`, enable manual override:

```python
use_manual_window_position = True
maple_window_left = 100
maple_window_top = 50  
maple_window_width = 1366
maple_window_height = 768
```

### Adjusting Template Thresholds

Edit thresholds in `src/modules/capture.py`:

```python
# More strict (fewer false positives)
utils.single_match(frame, template, threshold=0.9)

# More lenient (more matches)
utils.single_match(frame, template, threshold=0.6)
```

## Dependencies

### Required
- opencv-python>=4.8.0
- mss>=9.0.1
- numpy>=1.25.2

### macOS Only
- pyobjc-core>=10.2
- pyobjc-framework-Quartz>=10.2

## Files Overview

- **simple_window_selector.py** - GUI tool for window setup
- **fix_minimap.py** - GUI tool for minimap setup  
- **test_detection_system.py** - Validation script
- **src/modules/capture.py** - Main detection logic
- **src/common/utils.py** - Template matching functions

## Expected Resolution

This system is optimized for **1366x768** resolution. For best results:

1. Set your MapleStory window to exactly 1366x768
2. Use windowed mode (not fullscreen)
3. Position window where it won't be covered by other apps

## Migration from Old System

If you're upgrading from a previous version:

1. **Backup**: Your old templates and settings are preserved
2. **Clean Start**: Delete any existing `*_config.json` files and reconfigure
3. **Test**: Run the validation script to ensure everything works

The new system maintains compatibility with existing templates while providing much more reliable detection. 