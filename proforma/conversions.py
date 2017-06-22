"""Conversion rates."""

import numpy as np


def compound_rate(x, n):
    """Compound X for n periods."""
    return ((1 + x) ** n) - 1


class ConversionRates:
    """Conversion rates object."""

    RATIO_LOOKUP = (
        # Cut-off, rate
        (0.75, '<.75'),
        (1.25, '.75-1.25'),
        (2, '1.25-2.0'),
        (4, '2.0-4.0'),
        (np.inf, '>4.0'),
    )

    def __init__(self, df):
        """Initialize."""
        self._df = df

    def _ratio_to_column(self, ratio):
        """Convert ratio to appropriate column name."""
        for cutoff, column in self.RATIO_LOOKUP:
            if ratio < cutoff:
                return column

    def get(self, region, ratio):
        """Get conversion rate based on region and ratio."""
        column = self._ratio_to_column(ratio)
        return self._df.at[region, column]

    def compound(self, n):
        """Return a new ConversionRates instance, compounding the rates for n periods."""
        df = self._df.apply(compound_rate, axis=1, args=(n,))
        return ConversionRates(df)
