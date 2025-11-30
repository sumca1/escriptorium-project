"""
CERberus Integration App for eScriptorium
==========================================

This app integrates CERberus (Character Error Rate analysis) with eScriptorium,
providing advanced OCR quality metrics, confusion matrices, and Unicode-aware
character-level analysis.

Features:
- CER calculation with customizable options
- Character-level statistics
- Unicode block analysis (essential for Hebrew/Arabic)
- Confusion matrices
- Integration with OCR Comparison module
"""

default_app_config = 'apps.cerberus_integration.apps.CerberusIntegrationConfig'
