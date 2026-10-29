"""Enforce zero actual current, including removal of failed-channel offsets."""
import numpy as np


def outage_offsets(effective_matrices: np.ndarray, offsets: np.ndarray,
                   records: list, failed: int) -> np.ndarray:
    actual_offsets = np.array([r['offset_A'] for r in records])
    gains = np.array([r['gain'] for r in records])
    return offsets-effective_matrices[:, :, failed]*(actual_offsets[:, failed]/(1+gains[:, failed]))[:, None]
