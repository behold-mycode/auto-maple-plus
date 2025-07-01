#!/usr/bin/env python3
"""
Resolution Checker for GeForce NOW
Helps determine the actual game resolution vs window size.
"""

import cv2
import numpy as np
import mss
import json
import os
from pathlib import Path

def check_window_resolution():
    """Check the current window resolution and compare with templates."""
    
    # Load window config
    try:
        with open('window_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: window_config.json not found. Run window_selector.py first.")
        return
    
    print(f"Current window: {config['width']}x{config['height']}")
    print(f"Expected: 1366x768")
    print(f"Scale: {config['width']/1366:.3f}x, {config['height']/768:.3f}y")
    print()

def capture_and_analyze():
    """Capture the window and analyze its content."""
    
    # Load window config
    try:
        with open('window_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: window_config.json not found.")
        return
    
    print("Capturing window content...")
    
    with mss.mss() as sct:
        region = {
            'left': config['left'],
            'top': config['top'],
            'width': config['width'],
            'height': config['height']
        }
        
        screenshot = sct.grab(region)
        img = np.array(screenshot)
        
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    # Save the screenshot
    cv2.imwrite('current_window.png', img)
    print(f"Saved current_window.png")
    
    # Analyze the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    print(f"\nImage analysis:")
    print(f"  Size: {img.shape[1]}x{img.shape[0]}")
    print(f"  Unique colors: {len(np.unique(gray))}")
    
    # Check for common UI elements that should be at specific positions
    # This helps determine if the game is scaled
    
    # Look for minimap in top-right area
    top_right = gray[50:150, -200:-50]  # Adjust these coordinates as needed
    print(f"  Top-right region variance: {np.var(top_right):.2f}")
    
    return img

def test_template_matching():
    """Test template matching with current window."""
    
    print("\nTesting template matching...")
    
    # Load templates
    templates = {
        'player': 'assets/player_template.png',
        'minimap_tl': 'assets/minimap_tl_template.png',
        'minimap_br': 'assets/minimap_br_template.png'
    }
    
    # Capture current window
    img = capture_and_analyze()
    if img is None:
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    for name, template_path in templates.items():
        if not os.path.exists(template_path):
            print(f"  {name}: Template not found")
            continue
            
        template = cv2.imread(template_path, 0)
        if template is None:
            print(f"  {name}: Failed to load template")
            continue
        
        print(f"  {name}: Template size {template.shape}")
        
        # Test different thresholds
        for threshold in [0.3, 0.5, 0.7, 0.8, 0.9]:
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            matches = list(zip(*locations[::-1]))
            
            if matches:
                print(f"    Threshold {threshold}: {len(matches)} matches")
                if len(matches) <= 5:  # Show first few matches
                    for i, match in enumerate(matches[:3]):
                        print(f"      Match {i+1}: {match}")
            else:
                print(f"    Threshold {threshold}: No matches")

def create_custom_templates():
    """Guide user to create custom templates for their resolution."""
    
    print("\n" + "="*50)
    print("CUSTOM TEMPLATE CREATION GUIDE")
    print("="*50)
    print()
    print("Since GeForce NOW scales the game content, you may need custom templates.")
    print()
    print("Steps to create custom templates:")
    print("1. Take a screenshot of your game window")
    print("2. Open the screenshot in an image editor")
    print("3. Crop out the following elements:")
    print("   - Player dot on minimap (small white/colored dot)")
    print("   - Top-left corner of minimap")
    print("   - Bottom-right corner of minimap")
    print("4. Save them as:")
    print("   - assets/player_template.png")
    print("   - assets/minimap_tl_template.png")
    print("   - assets/minimap_br_template.png")
    print()
    print("Template sizes should be small (10-30 pixels)")
    print("Make sure to capture the actual game elements, not window borders")
    print()
    
    response = input("Would you like to open the current screenshot for reference? (y/N): ")
    if response.lower().startswith('y'):
        # Try to open the image
        import subprocess
        import platform
        
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", "current_window.png"])
        elif platform.system() == "Windows":
            subprocess.run(["start", "current_window.png"])
        else:  # Linux
            subprocess.run(["xdg-open", "current_window.png"])
        
        print("Screenshot opened. Use it to create custom templates.")

def main():
    """Main function."""
    print("GeForce NOW Resolution Checker")
    print("="*40)
    print("This tool helps determine the actual game resolution")
    print("when using GeForce NOW streaming.")
    print()
    
    check_window_resolution()
    test_template_matching()
    create_custom_templates()
    
    print("\n" + "="*50)
    print("RECOMMENDATIONS")
    print("="*50)
    print("1. If template matching works at low thresholds (0.3-0.5):")
    print("   - Your resolution is close enough, just lower thresholds")
    print()
    print("2. If no matches found even at 0.3:")
    print("   - Create custom templates from your actual game")
    print("   - Or try the template scaling script")
    print()
    print("3. For best results:")
    print("   - Set MapleStory to 1366x768 in-game")
    print("   - Make sure GeForce NOW window is not maximized")
    print("   - Position window so it's fully visible")

if __name__ == "__main__":
    main() 