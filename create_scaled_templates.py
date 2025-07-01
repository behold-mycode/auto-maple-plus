#!/usr/bin/env python3
"""
Template Scaling Script
Automatically scales template images to match your actual window resolution.
"""

import cv2
import numpy as np
import json
import os
import shutil
from pathlib import Path

def scale_templates():
    """Scale all templates to match the user's window resolution."""
    
    # Load window config
    try:
        with open('window_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: window_config.json not found. Run window_selector.py first.")
        return False
    
    # Calculate scaling factors
    expected_width = 1366
    expected_height = 768
    actual_width = config['width']
    actual_height = config['height']
    
    scale_x = actual_width / expected_width
    scale_y = actual_height / expected_height
    
    print(f"Window resolution: {actual_width}x{actual_height}")
    print(f"Expected resolution: {expected_width}x{expected_height}")
    print(f"Scale factors: x={scale_x:.3f}, y={scale_y:.3f}")
    
    if abs(scale_x - 1.0) < 0.05 and abs(scale_y - 1.0) < 0.05:
        print("Resolution is close enough to expected, no scaling needed.")
        return True
    
    # Create backup directory
    backup_dir = Path("assets/templates_backup")
    backup_dir.mkdir(exist_ok=True)
    
    # Templates to scale
    templates = [
        'player_template.png',
        'other_template.png',
        'minimap_tl_template.png',
        'minimap_br_template.png',
        'rune_template.png'
    ]
    
    print(f"\nScaling templates...")
    
    for template_name in templates:
        template_path = Path('assets') / template_name
        
        if not template_path.exists():
            print(f"  Skipping {template_name} (not found)")
            continue
            
        # Backup original
        backup_path = backup_dir / template_name
        if not backup_path.exists():
            shutil.copy2(template_path, backup_path)
            print(f"  Backed up {template_name}")
        
        # Load template
        template = cv2.imread(str(template_path), cv2.IMREAD_UNCHANGED)
        if template is None:
            print(f"  Error loading {template_name}")
            continue
        
        # Calculate new size
        orig_h, orig_w = template.shape[:2]
        new_w = max(1, int(orig_w * scale_x))
        new_h = max(1, int(orig_h * scale_y))
        
        # Scale template
        if len(template.shape) == 3:
            scaled = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            scaled = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Save scaled template
        cv2.imwrite(str(template_path), scaled)
        print(f"  Scaled {template_name}: {orig_w}x{orig_h} -> {new_w}x{new_h}")
    
    print(f"\n✅ Template scaling complete!")
    print(f"Original templates backed up to: {backup_dir}")
    return True

def restore_original_templates():
    """Restore original templates from backup."""
    backup_dir = Path("assets/templates_backup")
    
    if not backup_dir.exists():
        print("No backup found.")
        return False
    
    templates = list(backup_dir.glob('*.png'))
    if not templates:
        print("No template backups found.")
        return False
    
    print("Restoring original templates...")
    for backup_path in templates:
        original_path = Path('assets') / backup_path.name
        shutil.copy2(backup_path, original_path)
        print(f"  Restored {backup_path.name}")
    
    print("✅ Original templates restored!")
    return True

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        restore_original_templates()
    else:
        print("Template Scaling for Auto Maple Plus")
        print("=" * 40)
        print("This will scale templates to match your window resolution.")
        print("Run with --restore to restore original templates.")
        print()
        
        response = input("Continue with scaling? (y/N): ")
        if response.lower().startswith('y'):
            scale_templates()
        else:
            print("Cancelled.")

if __name__ == "__main__":
    main() 