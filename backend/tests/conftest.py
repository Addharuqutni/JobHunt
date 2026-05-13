"""
Test configuration and shared fixtures.
"""
import sys
import os

# Ensure the backend app is importable from tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
