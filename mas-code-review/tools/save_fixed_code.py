# tools/save_fixed_code.py
import os
from datetime import datetime


def save_fixed_code(
    fixed_code: str,
    original_file_name: str
) -> str:
    """
    Saves the LLM-generated fixed Python code to the
    outputs/ directory with a timestamped filename.

    Args:
        fixed_code (str): The corrected Python source code.
        original_file_name (str): Original file path, used
                                  to derive output filename.

    Returns:
        str: The full path to the saved fixed file.

    Raises:
        ValueError: If fixed_code is empty or whitespace only.
        IOError: If the file cannot be written to disk.
    """
    if not fixed_code or not fixed_code.strip():
        raise ValueError("Fixed code cannot be empty.")

    os.makedirs("outputs", exist_ok=True)

    # Extract just the base filename
    base_name = os.path.basename(original_file_name)

    # Remove .py extension, add timestamp, re-add .py
    name_without_ext = os.path.splitext(base_name)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/fixed_{timestamp}_{name_without_ext}.py"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(fixed_code)

    return output_path