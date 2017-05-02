"""Validate and read entitlement screen data."""
from functools import partial

import engarde.checks as ec

from . import utils


# READER

class ScreenReader(utils.Reader):
    """Entitlement screen reader."""

    def __init__(self, parcels, prototypes):
        """Initialize entitlement screen reader.

        Requires parcels and prototypes, list of Parcel and Prototype objects, respectively.
        """
        self.parcels = parcels
        self.prototypes = prototypes

    def _codes_in_index(self, df):
        index = set(df.index)
        codes = set(parcel.code for parcel in self.parcels)

        # Codes should be a subset of index.
        return codes <= index

    def get_dtypes(self):
        """Columns should match the prototype names and should all be bool."""
        return {
            prototype.name: bool
            for prototype in self.prototypes
        }

    def get_checks(self):
        """Build entitlement screen checks (require local arguments)."""
        # NOTE: Adding all screens here instead of splitting between CHECKS and here for clarity.
        return {
            ec.none_missing,
            partial(ec.is_shape, shape=(-1, len(self.get_dtypes()))),
            ec.unique_index,
            partial(ec.has_dtypes, items=self.get_dtypes()),
            partial(ec.verify, check=self._codes_in_index),
        }

    def postprocess(self, df):
        """Set 'Zone Class' as index."""
        return df.set_index('Zone Class')
