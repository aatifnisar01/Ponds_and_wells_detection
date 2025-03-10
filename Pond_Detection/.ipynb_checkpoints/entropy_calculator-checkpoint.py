# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 14:14:07 2025

@author: Aatif
"""

import cv2
import numpy as np
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.util import img_as_ubyte

def get_entropy(img, mask):
    """
    Calculate the entropy of an image within a masked region.

    Parameters:
    - img: Input image (BGR format).
    - mask: Binary mask (same spatial dimensions as img).

    Returns:
    - Entropy value of the masked region.
    """
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)  # Convert to grayscale
    mask[mask > 0] = 1  # Ensure mask is binary

    if mask.shape[:2] != img_gray.shape:
        print("Mask shape does not match image shape")
        return 0

    # Normalize the grayscale image to [0, 1]
    img_gray = (img_gray - img_gray.min()) / (img_gray.max() - img_gray.min())

    # Convert to uint8 after normalization
    img_gray = img_as_ubyte(img_gray)

    # Compute entropy
    ent = entropy(img_gray.copy(), disk(5), mask=mask)
    ent = ent[ent > 5.2]

    # Compute average entropy over masked area
    if np.sum(mask) > 0:
        ent = np.sum(ent) / np.sum(mask)  # Average entropy based on the mask area
    else:
        ent = 0

    return ent
