"""Prespecified features; exact bit extraction and bounded coordinate conversion."""
import numpy as np


def correlation(x, y):
    dx, dy = x - x.mean(), y - y.mean()
    denominator = np.sqrt(np.dot(dx, dx) * np.dot(dy, dy))
    return float(np.dot(dx, dy) / denominator) if denominator else None


def features(raw, p, bins=32):
    width = (p.bit_length() + 7) // 8
    encoded = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 2, width)
    # Each floating approximation has <= a few ulps error. Recompute any bin
    # near a boundary with exact integer division, so bin assignments are exact.
    weights = np.exp2(-8.0 * np.arange(1, width + 1))
    normalized = (encoded.astype(np.float64) @ weights) / (p / 2**(8*width))
    scaled = bins * normalized[:, 0]
    indices = np.floor(scaled).astype(np.int64)
    near = np.flatnonzero(np.abs(scaled - np.rint(scaled)) < 1e-12)
    for i in near:
        indices[i] = bins * int.from_bytes(encoded[i, 0].tobytes(), 'big') // p
    counts = np.bincount(indices, minlength=bins)
    expected = len(indices) / bins
    dispersion = float(((counts - expected)**2 / expected).sum() / (bins - 1))
    result = {'points': len(indices), 'x_bin_counts': counts.tolist(),
              'x_bin_dispersion': dispersion,
              'xy_correlation': correlation(normalized[:, 0], normalized[:, 1]),
              'x_lag1': correlation(normalized[:-1, 0], normalized[1:, 0])}
    for bit in (64, 96):
        if bit >= 8 * width:
            result[f'bit{bit}_lag1'] = None
        else:
            values = ((encoded[:, 0, width - 1 - bit // 8] >> (bit % 8)) & 1).astype(float)
            result[f'bit{bit}_lag1'] = correlation(values[:-1], values[1:])
    return result, normalized
