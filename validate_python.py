#!/usr/bin/env python3
"""
Python validation script for competition submissions.

This script:
1. Finds all Python files in the submission
2. Validates syntax by attempting to compile each file
3. Checks for basic code quality issues
4. Reports any errors found
"""

import sys
import os
import py_compile
import ast
from pathlib import Path


def validate_python_syntax(file_path: Path) -> tuple[bool, str]:
    """
    Validate Python syntax for a single file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to compile the file
        py_compile.compile(str(file_path), doraise=True)
        
        # Try to parse the AST
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            ast.parse(code)
        
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_required_structure(submission_path: Path) -> tuple[bool, list[str]]:
    """
    Check if the submission has the required structure.
    
    Args:
        submission_path: Path to the submission directory
        
    Returns:
        Tuple of (is_valid, list of warnings)
    """
    warnings = []
    
    # Check for at least one Python file
    python_files = list(submission_path.rglob('*.py'))
    if not python_files:
        return False, ["No Python files found in submission"]
    
    # Check for requirements.txt (warning only)
    if not (submission_path / 'requirements.txt').exists():
        warnings.append("No requirements.txt found - make sure all dependencies are documented")
    
    return True, warnings


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("❌ Error: No submission path provided")
        sys.exit(1)
    
    submission_path = Path(sys.argv[1])
    
    if not submission_path.exists():
        print(f"❌ Error: Submission path does not exist: {submission_path}")
        sys.exit(1)
    
    print(f"📁 Path: {submission_path}")
    
    # Check required structure
    is_valid, warnings = check_required_structure(submission_path)
    if not is_valid:
        print("❌ Validation failed:")
        for warning in warnings:
            print(f"  - {warning}")
        sys.exit(1)
    
    # Display warnings
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    # Find all Python files
    python_files = list(submission_path.rglob('*.py'))
    print(f"📝 Found {len(python_files)} Python file(s)")
    print()
    
    # Validate each file
    errors = []
    for py_file in python_files:
        relative_path = py_file.relative_to(submission_path)
        print(f"  Checking {relative_path}...", end=" ")
        
        is_valid, error_msg = validate_python_syntax(py_file)
        if is_valid:
            print("✅")
        else:
            print("❌")
            errors.append((relative_path, error_msg))
    
    print()
    print("=" * 60)
    
    # Report results
    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):")
        print()
        for file_path, error_msg in errors:
            print(f"  {file_path}:")
            print(f"    {error_msg}")
        sys.exit(1)
    else:
        print("✅ All Python files validated successfully!")
        print(f"   {len(python_files)} file(s) checked")
        sys.exit(0)


if __name__ == '__main__':
    main()

