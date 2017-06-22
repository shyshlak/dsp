"""Validate and read conversion rate data."""

from functools import partial

import engarde.checks as ec
import numpy as np

from . import utils


class ConversionRatesReader(utils.Reader):
    """Conversion rate reader."""

    DTYPES = {
        '<.75': float,
        '.75-1.25': float,
        '1.25-2.0': float,
        '2.0-4.0': float,
        '>4.0': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )

    def get_dtypes(self):
        """Add region to dtypes."""
        return {**self.DTYPES, 'region': np.object}

    def postprocess(self, df):
        """Set region as the index."""
        return df.set_index('region')
