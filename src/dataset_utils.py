import os
import glob
import re

def auto_detect_dataset(data_dir):
    """
    Automatically detect VTK files in a directory and determine:
    - n_term (from folder name or file pattern)
    - initial_step (first step number)
    - step_increment (difference between consecutive steps)
    
    Returns: (n_term_str, initial_step, step_increment)
    """
    # Find all VTK files
    vtk_files = glob.glob(os.path.join(data_dir, "*.vtk"))
    
    if not vtk_files:
        raise ValueError(f"No VTK files found in {data_dir}")
    
    # Extract step numbers from filenames
    # Pattern: tree2D_Nterm0064_step0008.vtk
    step_numbers = []
    n_term_from_file = None
    
    for filepath in vtk_files:
        filename = os.path.basename(filepath)
        # Match pattern: Nterm####_step####
        match = re.search(r'Nterm(\d+)_step(\d+)', filename)
        if match:
            if n_term_from_file is None:
                n_term_from_file = match.group(1)
            step_numbers.append(int(match.group(2)))
    
    if not step_numbers:
        raise ValueError(f"Could not parse VTK filenames in {data_dir}")
    
    # Sort step numbers
    step_numbers.sort()
    
    # Determine increment (difference between first two steps)
    if len(step_numbers) >= 2:
        step_increment = step_numbers[1] - step_numbers[0]
    else:
        step_increment = step_numbers[0]  # Only one file
    
    initial_step = step_numbers[0]
    
    # Try to get n_term from folder name first
    folder_name = os.path.basename(data_dir)
    match = re.search(r'Nterm_(\d+)', folder_name)
    if match:
        n_term_str = match.group(1)
    elif n_term_from_file:
        n_term_str = n_term_from_file
    else:
        # Fallback: use max step number
        n_term_str = str(max(step_numbers))
    
    print(f"Auto-detected: n_term={n_term_str}, initial_step={initial_step}, increment={step_increment}")
    print(f"Found {len(step_numbers)} files: {step_numbers}")
    
    return n_term_str, initial_step, step_increment
