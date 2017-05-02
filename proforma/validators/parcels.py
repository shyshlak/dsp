"""Validate and read parcel data."""
from functools import partial

import engarde.checks as ec
import numpy as np

from . import utils


# CUSTOM CHECKS

def unique_reference(df):
    """Verify that reference is unique."""
    return df.reference.is_unique


# READER

class ParcelReader(utils.Reader):
    """Parcel reader."""

    DTYPES = {
        'reference': np.object,
        'code': np.object,
        'rmv': float,
        'sf': float,
        'res_rent': float,
        'res_price': float,
        'off_mkt': float,
        'off_rent': float,
        'ret_mkt': float,
        'ret_rent': float,
        'wd_mkt': float,
        'wd_rent': float,
        'flex_mkt': float,
        'flex_rent': float,
        'park_rent': float,
        'park_own': float,
        'park_off': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
        partial(ec.verify, check=unique_reference),
    )

    def get_dtypes(self):
        """Add 'Filter' to dtypes."""
        return {**self.DTYPES, 'Filter': bool}

    def postprocess(self, df):
        """Apply subset."""
        return df.pipe(utils.subset)
