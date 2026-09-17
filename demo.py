#!/usr/bin/env python3
"""Root entry-point wrapper for Linear Algebra Library Prototype Demo.

Runs the narrated end-to-end walkthrough per PRD requirements D-1, D-2, D-3.
Can be executed with:
    python3 demo.py
Or with optional flags:
    python3 demo.py --prime 1009 --parties 4 --explain
"""

import sys
import os

# Ensure prototype package is in python search path
workspace_dir = os.path.dirname(os.path.abspath(__file__))
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from prototype.demo import main

if __name__ == "__main__":
    main()
