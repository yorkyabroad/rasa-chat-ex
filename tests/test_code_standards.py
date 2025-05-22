import os
import unittest
import glob

class TestCodeStandards(unittest.TestCase):
    def test_copyright_notice(self):
        """Test that all Python files contain the required copyright notice."""
        # Define the notice that should be in all Python files
        required_notice = "# See this guide on how to implement these action:"
        
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Find all Python files in the project (excluding tests and certain directories)
        python_files = []
        for root, dirs, files in os.walk(project_root):
            # Skip directories we don't want to check
            if any(excluded in root for excluded in [".git", "__pycache__", ".pytest_cache", "venv", "env", "tests"]):
                continue
                
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        # Check each file for the required notice
        files_without_notice = []
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if required_notice not in content:
                    files_without_notice.append(file_path)
        
        # Assert that all files have the notice
        if files_without_notice:
            relative_paths = [os.path.relpath(path, project_root) for path in files_without_notice]
            self.fail(f"The following files are missing the required notice: {', '.join(relative_paths)}")

    def test_no_print_statements(self):
        """Test that Python files don't contain print statements (except in tests)."""
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Find all Python files in the project (excluding tests and certain directories)
        python_files = []
        for root, dirs, files in os.walk(project_root):
            # Skip test directories and other excluded directories
            if any(excluded in root for excluded in [".git", "__pycache__", ".pytest_cache", "venv", "env", "tests"]):
                continue
                
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        # Check each file for print statements
        files_with_print = []
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    # Skip commented lines
                    stripped_line = line.strip()
                    if stripped_line.startswith("#"):
                        continue
                    
                    # Check for print statements
                    if "print(" in stripped_line:
                        files_with_print.append((file_path, i, stripped_line))
        
        # Assert that no files have print statements
        if files_with_print:
            error_messages = [f"{os.path.relpath(path, project_root)}:{line_num}: {line_content}" 
                             for path, line_num, line_content in files_with_print]
            self.fail(f"The following files contain print statements:\n" + "\n".join(error_messages))

    def test_naming_conventions(self):
        """Test that functions and classes follow naming conventions."""
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Find all Python files in the project (excluding tests and certain directories)
        python_files = []
        for root, dirs, files in os.walk(project_root):
            # Skip directories we don't want to check
            if any(excluded in root for excluded in [".git", "__pycache__", ".pytest_cache", "venv", "env", "tests"]):
                continue
                
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        # Patterns for naming conventions
        import re
        # Look for class definitions but avoid false positives in comments and strings
        class_pattern = re.compile(r"^[^#]*class\s+([A-Za-z0-9_]+)", re.MULTILINE)  # Classes should be CamelCase
        function_pattern = re.compile(r"^[^#]*def\s+([A-Za-z0-9_]+)\s*\(", re.MULTILINE)  # Functions should be snake_case
        
        # Check each file for naming conventions
        violations = []
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Check class names (should be CamelCase)
                for match in class_pattern.finditer(content):
                    class_name = match.group(1)
                    # For stricter CamelCase (must have at least two uppercase letters)
                    if not (class_name[0].isupper() and "_" not in class_name and sum(1 for c in class_name if c.isupper()) >= 2):
                    #if not (class_name[0].isupper() and "_" not in class_name):
                        violations.append(f"{os.path.relpath(file_path, project_root)}: Class '{class_name}' should be CamelCase")
                
                # Check function names (should be snake_case)
                for match in function_pattern.finditer(content):
                    function_name = match.group(1)
                    # Skip special methods like __init__
                    if function_name.startswith("__") and function_name.endswith("__"):
                        continue
                    # For stricter snake_case (must have underscores for multi-word names)
                    if not (function_name.islower() and function_name.isidentifier() and (len(function_name) < 12 or "_" in function_name)):
                    #if not (function_name.islower() and function_name.isidentifier()):
                        violations.append(f"{os.path.relpath(file_path, project_root)}: Function '{function_name}' should be snake_case")
        
        # Assert that there are no violations
        if violations:
            self.fail("Naming convention violations found:\n" + "\n".join(violations))

if __name__ == "__main__":
    unittest.main()