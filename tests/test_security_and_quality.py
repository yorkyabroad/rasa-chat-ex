import os
import json
import subprocess
import tempfile
import unittest


class TestSecurityAndQuality(unittest.TestCase):
    """Tests for security vulnerabilities and code quality."""

    def test_security_vulnerabilities(self):
        """Test that Python files don't contain security vulnerabilities using Bandit."""
        # Skip test if bandit is not installed
        try:
            subprocess.run(["bandit", "--version"], capture_output=True, shell=False)
        except FileNotFoundError:
            self.skipTest("bandit not installed")
            
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Run bandit on the project, excluding test files
        result = subprocess.run(
            ["bandit", "-r", project_root, "-f", "json", "-x", ".git,__pycache__,.pytest_cache,venv,env,tests,htmlcov"],
            capture_output=True,
            text=True,
            shell=False  # Explicitly set shell=False for security
        )
        
        # Only fail on high and medium severity issues
        try:
            output = json.loads(result.stdout)
            issues = output.get("results", [])
            serious_issues = [
                f"{issue['filename']}:{issue['line_number']} - {issue['issue_text']} (Severity: {issue['issue_severity']})"
                for issue in issues
                if issue['issue_severity'] in ['MEDIUM', 'HIGH']
            ]
            
            if serious_issues:
                self.fail("Security vulnerabilities found:\n" + "\n".join(serious_issues))
        except json.JSONDecodeError:
            if result.returncode not in [0, 1]:  # 1 is for issues found
                self.fail(f"Bandit failed with output: {result.stdout}\n{result.stderr}")

    def test_dependency_vulnerabilities(self):
        """Test that dependencies don't have known vulnerabilities."""
        # Skip test if safety is not installed
        try:
            subprocess.run(["safety", "--version"], capture_output=True, shell=False)
        except FileNotFoundError:
            self.skipTest("safety not installed")
            
        # Run safety check on requirements
        result = subprocess.run(
            ["safety", "check", "--file=requirements.txt", "--json"],
            capture_output=True,
            text=True,
            shell=False  # Explicitly set shell=False for security
        )
        
        try:
            # Parse the JSON output
            output = json.loads(result.stdout)
            vulnerabilities = output.get("vulnerabilities", [])
            
            if vulnerabilities:
                formatted_vulns = [
                    f"{vuln['package_name']} {vuln['vulnerable_spec']}: {vuln['advisory']}"
                    for vuln in vulnerabilities
                ]
                self.fail("Vulnerable dependencies found:\n" + "\n".join(formatted_vulns))
        except json.JSONDecodeError:
            # Safety might not return valid JSON if there are no vulnerabilities
            pass

    def test_license_compliance(self):
        """Test that dependencies comply with allowed licenses."""
        # Skip this test if liccheck is not installed
        try:
            subprocess.run(["liccheck", "--version"], capture_output=True, shell=False)
        except FileNotFoundError:
            self.skipTest("liccheck not installed")
            
        # Create a temporary license configuration file
        license_config = """
[Licenses]
authorized_licenses:
    MIT
    BSD
    Apache Software License
    Python Software Foundation License
    ISC License
    Mozilla Public License 2.0 (MPL 2.0)
    GNU Lesser General Public License v3 (LGPLv3)
    Apache License 2.0
    The Unlicense (Unlicense)

unauthorized_licenses:
    GNU General Public License v2 (GPLv2)
    GNU General Public License v3 (GPLv3)
    Affero General Public License
    """
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write(license_config)
            config_path = temp.name
        
        try:
            # Run liccheck on requirements
            result = subprocess.run(
                ["liccheck", "-s", config_path, "-r", "requirements.txt", "--no-deps"],
                capture_output=True,
                text=True,
                shell=False  # Explicitly set shell=False for security
            )
            
            # Check if there were unauthorized licenses
            if "Unauthorized licenses" in result.stdout:
                self.fail(f"License compliance issues found:\n{result.stdout}")
        finally:
            # Clean up the temporary file
            os.unlink(config_path)


if __name__ == "__main__":
    unittest.main()