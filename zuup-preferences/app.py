"""
Hugging Face Spaces entry point for Zuup Preference Collection.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from collection.app import PreferenceStore, create_collection_ui

# Initialize store and create app
store = PreferenceStore("preference_data")
demo = create_collection_ui(store)

if __name__ == "__main__":
    demo.launch()

