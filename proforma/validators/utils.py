"""Utility module for validators."""
import os

import numpy as np
import pandas as pd


def get_ext(filename):
    """Extract the extension from a filename."""
    _, ext = os.path.splitext(filename)

    if ext == '':
        raise ValueError('filename does not contain an extension: {0}'.format(filename))

    return ext


def to_converters(dtypes):
    """Convert dtypes into converters for Excel file parsing."""
    def convert(dtypes):
        for column, dtype in dtypes.items():
            conversions = {np.object: str}
            try:
                dtype = conversions[dtype]
            except KeyError:
                pass

            yield (column, dtype)

    return dict(convert(dtypes))


def read_csv(filename, dtypes, **kwargs):
    """Read CSV with dtypes."""
    return pd.read_csv(filename, dtype=dtypes, **kwargs)


def read_excel(filename, dtypes, **kwargs):
    """Read Excel with converters."""
    converters = to_converters(dtypes)
    return pd.read_excel(filename, converters=converters, **kwargs)


def get_parser(filename):
    """Choose parser based on extension."""
    parsers = {
        # TODO: Add more extensions
        '.csv': read_csv,
        '.xlsx': read_excel,
        '.xls': read_excel,
    }

    ext = get_ext(filename)
    return parsers[ext]


def subset(df):
    """Filter out bad rows and drop the 'filter' column."""
    return df.loc[~df['filter']].drop('filter', axis=1)


class Reader(object):
    """Generic reader class (should be subsetted)."""

    DTYPES = {}
    CHECKS = ()

    def __init__(self, dtypes=None, checks=None):
        """Ability to overwrite class attributes DTYPES and CHECKS."""
        if dtypes is not None:
            self.DTYPES = dtypes
        if checks is not None:
            self.CHECKS = checks

    def get_dtypes(self):
        """Customizable way to get dtypes. Defaults to self.DTYPES."""
        return self.DTYPES

    def get_checks(self):
        """Customizable way to get checks. Defaults to self.CHECKS."""
        return self.CHECKS

    def postprocess(self, df):
        """Customizable post-processing of df. Defaults to no changes."""
        return df

    def read(self, filename):
        """Read data from filename."""
        dtypes = self.get_dtypes()
        parser = get_parser(filename)
        df = parser(filename, dtypes).pipe(self.postprocess)

        for check in self.get_checks():
            check(df)

        return df
