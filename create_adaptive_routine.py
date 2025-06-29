#!/usr/bin/env python3
"""
Adaptive Routine Generator for Astelle
This script creates map-adaptive routines that patrol the ground level of any map.
"""

import os
import sys
import json
from datetime import datetime

def create_adaptive_routine(map_name, map_width_ratio=1.0, ground_level=0.238, num_positions=6):
    """
    Creates an adaptive routine for any map.
    
    Args:
        map_name: Name of the map
        map_width_ratio: How much of the map width to use (0.1 to 1.0)
        ground_level: Y coordinate for ground level (usually 0.238)
        num_positions: Number of patrol positions
    """
    
    # Calculate patrol positions
    start_x = 0.1 + (0.8 * (1.0 - map_width_ratio)) / 2  # Start from left side
    end_x = 0.9 - (0.8 * (1.0 - map_width_ratio)) / 2    # End at right side
    
    positions = []
    for i in range(num_positions):
        x = start_x + (end_x - start_x) * (i / (num_positions - 1))
        positions.append(round(x, 3))
    
    # Create the routine content
    routine_lines = [
        f"@, label=Start",
        f"*, x={positions[0]}, y={ground_level}, frequency=1, skip=False, adjust=False",
        f"    Buff",
        f"    Ray, direction=left, jump=False, attacks=2",
        f"    Boom, direction=left, jump=False, attacks=1",
    ]
    
    # Add middle positions
    for i in range(1, len(positions) - 1):
        direction = "right" if i % 2 == 1 else "left"
        routine_lines.extend([
            f"*, x={positions[i]}, y={ground_level}, frequency=1, skip=False, adjust=False",
            f"    Ray, direction={direction}, jump=False, attacks=2",
        ])
        
        # Add different skills based on position
        if i == 1:
            routine_lines.append(f"    Pole, direction={direction}, jump=False")
        elif i == 2:
            routine_lines.append(f"    Link, direction={direction}, jump=False")
        elif i == 3:
            routine_lines.append(f"    Antares")
            routine_lines.append(f"    Algol")
        elif i == 4:
            routine_lines.append(f"    Fomalhaut")
            routine_lines.append(f"    Izar")
    
    # Add final position
    direction = "right" if len(positions) % 2 == 0 else "left"
    routine_lines.extend([
        f"*, x={positions[-1]}, y={ground_level}, frequency=1, skip=False, adjust=False",
        f"    Ray, direction={direction}, jump=False, attacks=2",
        f"    Boom, direction={direction}, jump=False, attacks=1",
    ])
    
    # Add buff check
    buff_x = round((positions[0] + positions[-1]) / 2, 3)
    routine_lines.extend([
        f"@, label=BuffCheck",
        f"*, x={buff_x}, y={ground_level}, frequency=10, skip=False, adjust=False",
        f"    Buff",
        f"    FeedPet",
        f"*, x={positions[1]}, y={ground_level}, frequency=1, skip=False, adjust=False",
        f"    Ray, direction=left, jump=False, attacks=1",
        f"    Vega",
        f"    Sadalmelik",
        f">, label=Start"
    ])
    
    return routine_lines

def create_vertical_routine(map_name, ground_level=0.238, platform_levels=[0.150, 0.100]):
    """
    Creates a routine that includes vertical movement for platforms.
    
    Args:
        map_name: Name of the map
        ground_level: Y coordinate for ground level
        platform_levels: List of Y coordinates for platforms
    """
    
    routine_lines = [
        f"@, label=GroundPatrol",
        f"*, x=0.300, y={ground_level}, frequency=1, skip=False, adjust=False",
        f"    Buff",
        f"    Ray, direction=left, jump=False, attacks=2",
        f"    Boom, direction=left, jump=False, attacks=1",
        f"*, x=0.500, y={ground_level}, frequency=1, skip=False, adjust=False",
        f"    Ray, direction=right, jump=False, attacks=2",
        f"    Pole, direction=right, jump=False",
        f"*, x=0.700, y={ground_level}, frequency=1, skip=False, adjust=False",
        f"    Ray, direction=left, jump=False, attacks=2",
        f"    Link, direction=left, jump=False",
    ]
    
    # Add platform positions
    for i, platform_y in enumerate(platform_levels):
        routine_lines.extend([
            f"@, label=Platform{i+1}",
            f"*, x=0.400, y={platform_y}, frequency=1, skip=False, adjust=False",
            f"    Ray, direction=left, jump=False, attacks=2",
            f"    Antares",
            f"    Algol",
            f"*, x=0.600, y={platform_y}, frequency=1, skip=False, adjust=False",
            f"    Ray, direction=right, jump=False, attacks=2",
            f"    Fomalhaut",
            f"    Izar",
        ])
    
    # Add buff check and loop
    routine_lines.extend([
        f"@, label=BuffCheck",
        f"*, x=0.500, y={ground_level}, frequency=10, skip=False, adjust=False",
        f"    Buff",
        f"    FeedPet",
        f">, label=GroundPatrol"
    ])
    
    return routine_lines

def save_routine(routine_lines, map_name, routine_type="adaptive"):
    """Saves the routine to a CSV file."""
    
    # Create routines directory if it doesn't exist
    routines_dir = "resources/routines/astelle"
    os.makedirs(routines_dir, exist_ok=True)
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{routine_type}_{map_name}_{timestamp}.csv"
    filepath = os.path.join(routines_dir, filename)
    
    # Save the routine
    with open(filepath, 'w') as f:
        f.write('\n'.join(routine_lines))
    
    print(f"✅ Routine saved: {filepath}")
    return filepath

def main():
    """Main function to create adaptive routines."""
    
    print("🎯 Astelle Adaptive Routine Generator")
    print("=" * 50)
    
    # Get map information
    map_name = input("Enter map name (e.g., 'fes2', 'clp'): ").strip()
    if not map_name:
        map_name = "generic_map"
    
    print("\n📊 Map Configuration:")
    print("1. Ground-level patrol only (recommended for flat maps)")
    print("2. Multi-platform routine (for maps with platforms)")
    
    choice = input("Choose routine type (1 or 2): ").strip()
    
    if choice == "1":
        # Ground-level patrol
        print("\n🔧 Ground Patrol Configuration:")
        map_width = input("Map width ratio (0.1-1.0, default 0.8): ").strip()
        map_width = float(map_width) if map_width else 0.8
        
        num_positions = input("Number of patrol positions (3-8, default 6): ").strip()
        num_positions = int(num_positions) if num_positions else 6
        
        routine_lines = create_adaptive_routine(
            map_name=map_name,
            map_width_ratio=map_width,
            num_positions=num_positions
        )
        
        filepath = save_routine(routine_lines, map_name, "ground_patrol")
        
    elif choice == "2":
        # Multi-platform routine
        print("\n🔧 Multi-Platform Configuration:")
        ground_level = input("Ground level Y coordinate (default 0.238): ").strip()
        ground_level = float(ground_level) if ground_level else 0.238
        
        platform_input = input("Platform Y coordinates (comma-separated, e.g., 0.150,0.100): ").strip()
        if platform_input:
            platform_levels = [float(x.strip()) for x in platform_input.split(',')]
        else:
            platform_levels = [0.150, 0.100]
        
        routine_lines = create_vertical_routine(
            map_name=map_name,
            ground_level=ground_level,
            platform_levels=platform_levels
        )
        
        filepath = save_routine(routine_lines, map_name, "multi_platform")
    
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    print(f"\n🎉 Routine created successfully!")
    print(f"📁 File: {filepath}")
    print(f"\n📋 Next steps:")
    print(f"1. Load the routine in Auto Maple: File → Load Routine")
    print(f"2. Test on your map and adjust positions if needed")
    print(f"3. Use the Edit tab to fine-tune the routine")

if __name__ == "__main__":
    main() 