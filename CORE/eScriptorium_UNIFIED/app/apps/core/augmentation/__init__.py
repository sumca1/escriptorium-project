"""
Data augmentation for OCR/HTR training
Specialized for Hebrew and Arabic historical manuscripts
"""

from .image_augmentor import OCRAugmentor, AugmentedDataset, augment_image

__all__ = ['OCRAugmentor', 'AugmentedDataset', 'augment_image']
