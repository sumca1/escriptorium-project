"""
OCR/HTR Data Augmentation
Specialized for Hebrew and Arabic historical manuscripts

This module provides image augmentation specifically designed for:
- Hebrew manuscripts (printed and handwritten)
- Arabic manuscripts (various scripts)
- Ancient/historical documents
- Poor quality scans

Author: BiblIA Project
Date: October 22, 2025
"""

import logging
from typing import Optional, Union, Tuple, List

import albumentations as A
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class OCRAugmentor:
    """
    Data augmentation pipeline for OCR/HTR training
    
    Designed specifically for Hebrew and Arabic historical manuscripts.
    Includes transformations that simulate real-world document conditions:
    - Aging (faded ink, yellowed paper)
    - Scanning artifacts (rotation, distortion, blur)
    - Physical damage (wrinkles, stains, torn edges)
    - Morphological variations (thick/thin strokes)
    
    Usage:
        augmentor = OCRAugmentor(level='medium')
        augmented_image = augmentor.augment(original_image)
    """
    
    def __init__(self, level: str = 'medium', seed: Optional[int] = None):
        """
        Initialize augmentor with specified intensity level
        
        Args:
            level: Augmentation intensity level
                   'light'  - Minimal augmentation (5-10% variations)
                   'medium' - Moderate augmentation (10-20% variations) - recommended
                   'heavy'  - Aggressive augmentation (20-40% variations)
            seed: Random seed for reproducibility (optional)
        """
        self.level = level
        self.seed = seed
        self.transform = self._build_pipeline()
        
        logger.info(f'🎨 OCRAugmentor initialized with level="{level}"')
    
    def _build_pipeline(self) -> A.Compose:
        """Build augmentation pipeline based on intensity level"""
        
        if self.level == 'light':
            return self._light_pipeline()
        elif self.level == 'medium':
            return self._medium_pipeline()
        elif self.level == 'heavy':
            return self._heavy_pipeline()
        else:
            logger.warning(f'Unknown level "{self.level}", using medium')
            return self._medium_pipeline()
    
    def _light_pipeline(self) -> A.Compose:
        """
        Light augmentation - minimal changes
        Best for: good quality scans, large datasets
        """
        return A.Compose([
            # Slight rotation (documents not perfectly aligned)
            A.Rotate(limit=2, border_mode=0, p=0.4),
            
            # Minimal noise (scanner artifacts)
            A.GaussNoise(std_range=(0.01, 0.03), p=0.3),
            
            # Slight brightness/contrast (different lighting)
            A.RandomBrightnessContrast(
                brightness_limit=0.1,
                contrast_limit=0.1,
                p=0.4
            ),
        ])
    
    def _medium_pipeline(self) -> A.Compose:
        """
        Medium augmentation - balanced approach (RECOMMENDED)
        Best for: typical manuscripts, moderate datasets
        """
        return A.Compose([
            # Rotation (documents not straight)
            A.Rotate(limit=5, border_mode=0, p=0.5),
            
            # Noise (scanner artifacts, paper texture)
            A.OneOf([
                A.GaussNoise(std_range=(0.02, 0.06), p=1.0),
                A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.3), p=1.0),
            ], p=0.5),
            
            # Brightness/contrast (lighting variations, aging)
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.6
            ),
            
            # Blur (focus issues, camera shake)
            A.OneOf([
                A.MotionBlur(blur_limit=3, p=1.0),
                A.GaussianBlur(blur_limit=3, p=1.0),
                A.MedianBlur(blur_limit=3, p=1.0),
            ], p=0.3),
            
            # Morphology (ink spread, fading) - using Morphological transform
            A.Morphological(scale=(2, 3), operation='erosion', p=0.1),   # Thin strokes
            A.Morphological(scale=(2, 3), operation='dilation', p=0.1),  # Thick strokes
            
            # Distortion (wrinkled paper, curved pages)
            A.GridDistortion(
                num_steps=5,
                distort_limit=0.1,
                border_mode=0,
                p=0.3
            ),
        ])
    
    def _heavy_pipeline(self) -> A.Compose:
        """
        Heavy augmentation - aggressive transformations
        Best for: poor quality scans, very small datasets
        """
        return A.Compose([
            # Significant rotation
            A.Rotate(limit=10, border_mode=0, p=0.7),
            
            # Heavy noise
            A.OneOf([
                A.GaussNoise(std_range=(0.04, 0.1), p=1.0),
                A.ISONoise(color_shift=(0.02, 0.1), intensity=(0.2, 0.5), p=1.0),
                A.MultiplicativeNoise(multiplier=(0.9, 1.1), p=1.0),
            ], p=0.6),
            
            # Strong brightness/contrast variations
            A.RandomBrightnessContrast(
                brightness_limit=0.3,
                contrast_limit=0.3,
                p=0.7
            ),
            
            # Various blur effects
            A.OneOf([
                A.MotionBlur(blur_limit=5, p=1.0),
                A.GaussianBlur(blur_limit=5, p=1.0),
                A.MedianBlur(blur_limit=5, p=1.0),
                A.Defocus(radius=(1, 3), alias_blur=(0.1, 0.3), p=1.0),
            ], p=0.5),
            
            # Morphology - using Morphological transform
            A.Morphological(scale=(2, 4), operation='erosion', p=0.2),
            A.Morphological(scale=(2, 4), operation='dilation', p=0.2),
            
            # Strong distortions (damaged documents)
            A.OneOf([
                A.GridDistortion(
                    num_steps=5,
                    distort_limit=0.2,
                    border_mode=0,
                    p=1.0
                ),
                A.ElasticTransform(
                    alpha=1,
                    sigma=20,
                    border_mode=0,
                    p=1.0
                ),
                A.OpticalDistortion(
                    distort_limit=0.3,
                    border_mode=0,
                    p=1.0
                ),
            ], p=0.5),
            
            # Perspective changes (angle shots)
            A.Perspective(scale=(0.02, 0.05), p=0.3),
            
            # Shadow/lighting effects (uneven lighting)
            A.RandomShadow(
                shadow_roi=(0, 0, 1, 1),
                num_shadows_limit=(1, 2),
                p=0.2
            ),
            
            # JPEG compression artifacts (low quality scans)
            A.ImageCompression(
                quality_range=(60, 100),
                p=0.2
            ),
        ])
    
    def augment(self, image: Union[Image.Image, np.ndarray]) -> np.ndarray:
        """
        Apply augmentation to a single image
        
        Args:
            image: PIL Image or numpy array (RGB or grayscale)
            
        Returns:
            Augmented image as numpy array
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Ensure image is in correct format
        if len(image.shape) == 2:
            # Grayscale - add channel dimension
            image = np.expand_dims(image, axis=-1)
        
        # Apply augmentation
        augmented = self.transform(image=image)
        
        return augmented['image']
    
    def augment_batch(
        self,
        images: List[Union[Image.Image, np.ndarray]],
        n_augmentations: int = 2
    ) -> List[np.ndarray]:
        """
        Apply augmentation to a batch of images
        
        Args:
            images: List of PIL Images or numpy arrays
            n_augmentations: Number of augmented versions per image
                           (original is always included)
            
        Returns:
            List of augmented images (original + augmented versions)
            
        Example:
            >>> augmentor = OCRAugmentor()
            >>> images = [img1, img2, img3]
            >>> # Returns 9 images: 3 original + 6 augmented (2 per original)
            >>> augmented = augmentor.augment_batch(images, n_augmentations=2)
        """
        result = []
        
        for img in images:
            # Add original
            if isinstance(img, Image.Image):
                result.append(np.array(img))
            else:
                result.append(img)
            
            # Add augmented versions
            for _ in range(n_augmentations):
                aug_img = self.augment(img)
                result.append(aug_img)
        
        logger.debug(
            f'Augmented {len(images)} images → {len(result)} total '
            f'(x{1 + n_augmentations} multiplier)'
        )
        
        return result


class AugmentedDataset:
    """
    Wrapper for applying augmentation to dataset during training
    
    This class wraps an existing dataset and applies augmentation
    on-the-fly during training iterations.
    
    Usage:
        original_dataset = YourDataset()
        augmentor = OCRAugmentor(level='medium')
        augmented_dataset = AugmentedDataset(
            original_dataset,
            augmentor,
            augment_prob=0.7
        )
    """
    
    def __init__(
        self,
        dataset,
        augmentor: OCRAugmentor,
        augment_prob: float = 0.5
    ):
        """
        Initialize augmented dataset wrapper
        
        Args:
            dataset: Original dataset to wrap
            augmentor: OCRAugmentor instance
            augment_prob: Probability of applying augmentation (0.0-1.0)
                         0.0 = never augment
                         0.5 = augment 50% of samples
                         1.0 = always augment
        """
        self.dataset = dataset
        self.augmentor = augmentor
        self.augment_prob = augment_prob
        
        logger.info(
            f'📦 AugmentedDataset created: '
            f'{len(dataset)} samples, '
            f'augment_prob={augment_prob:.1%}'
        )
    
    def __len__(self):
        """Return length of original dataset"""
        return len(self.dataset)
    
    def __getitem__(self, idx):
        """
        Get item from dataset with optional augmentation
        
        Args:
            idx: Index of item to retrieve
            
        Returns:
            Dataset item with augmented image (if augmentation is applied)
        """
        item = self.dataset[idx]
        
        # Apply augmentation with specified probability
        if np.random.random() < self.augment_prob:
            # Augment the image
            if 'image' in item:
                item['image'] = self.augmentor.augment(item['image'])
            elif isinstance(item, (tuple, list)) and len(item) > 0:
                # Assume first element is the image
                item = list(item)
                item[0] = self.augmentor.augment(item[0])
                item = tuple(item)
        
        return item


# Convenience function for quick augmentation
def augment_image(
    image: Union[Image.Image, np.ndarray],
    level: str = 'medium'
) -> np.ndarray:
    """
    Quick augmentation of a single image
    
    Args:
        image: PIL Image or numpy array
        level: Augmentation level ('light', 'medium', 'heavy')
        
    Returns:
        Augmented image as numpy array
        
    Example:
        >>> from core.augmentation import augment_image
        >>> augmented = augment_image(original_image, level='medium')
    """
    augmentor = OCRAugmentor(level=level)
    return augmentor.augment(image)
