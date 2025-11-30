"""
TABA Pipeline Settings
Add these to your main settings.py or local_settings.py
"""

import tempfile
from pathlib import Path

# TABA Pipeline Configuration
# ============================

# Path to TABA pipeline installation
# Example: '/home/user/TABA-Groundtruth-Alignment-Pipeline'
TABA_PIPELINE_PATH = None  # Set to actual path

# Working directory for TABA jobs
# Security: Use secure temp directory instead of hardcoded /tmp
# nosec B108: Using tempfile.gettempdir() for cross-platform secure temp
TABA_WORK_DIR = str(Path(tempfile.gettempdir()) / 'taba_work')  # nosec B108

# Output directory for TABA results
# Security: Use secure temp directory instead of hardcoded /tmp
# nosec B108: Using tempfile.gettempdir() for cross-platform secure temp
TABA_OUTPUT_DIR = str(Path(tempfile.gettempdir()) / 'taba_output')  # nosec B108

# Conda environment for TABA
TABA_CONDA_ENV = 'taba_alignment'

# Passim default settings
TABA_DEFAULT_PASSIM_N = 5
TABA_DEFAULT_PASSIM_CORES = 4
TABA_DEFAULT_PASSIM_MEMORY = 4
TABA_DEFAULT_PASSIM_DRIVER_MEMORY = 2

# Levenshtein threshold default
TABA_DEFAULT_LEVENSHTEIN_THRESHOLD = 0.8

# Maximum job execution time (seconds)
TABA_MAX_EXECUTION_TIME = 3600  # 1 hour

# Cleanup old job directories after (days)
TABA_CLEANUP_AFTER_DAYS = 7
