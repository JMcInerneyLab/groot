"""
Groot test suite.
Includes the automated test generation as well as standalone Python scripts.
This suite tests the groot core commands only - the GUI is excluded.

To use these tests from within the Groot CLI, you can use `import groot_tests`.
"""
from .test_commands import list_tests, reload_test, create_test, run_test 