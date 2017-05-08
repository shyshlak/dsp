"""Validate and read parcel data."""
from functools import partial

import engarde.checks as ec
import numpy as np

from . import utils


# CUSTOM CHECKS

def unique_reference(df):
    """Verify that reference is unique."""
    return df.reference.is_unique


def clean_design_type(df):
    """Replace missing design_type with 'None'."""
    return df.design_type.fillna('None')


# READER

class ParcelReader(utils.Reader):
    """Parcel reader."""

    DTYPES = {
        'reference': np.object,
        'code': np.object,
        'code_general': np.object,
        'tract': np.object,
        'ezone': np.object,
        'design_type': np.object,
        'vac_dev': np.object,
        'sfr_infill': bool,
        'jurisdiction': np.object,
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
        """Add 'filter' to dtypes."""
        return {**self.DTYPES, 'filter': bool}

    def postprocess(self, df):
        """Apply subset."""
        return df.pipe(utils.subset).assign(design_type=clean_design_type)
