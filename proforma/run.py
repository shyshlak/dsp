"""Run classes."""
from copy import deepcopy

import pandas as pd


def compound_rate(x, n):
    """Compound X for n periods."""
    return ((1 + x) ** n) - 1


class ModelRun:
    """Model run."""

    def __init__(
        self, parcels, prototypes, base_conversion_rates, screen, n_iterations=5, iteration_length=5
    ):
        """init."""
        conversion_rates = tuple(
            (upper_bound, compound_rate(rate, iteration_length))
            for upper_bound, rate in base_conversion_rates
        )

        self.runs = [
            ParcelRun(parcel, prototypes, conversion_rates, screen, n_iterations)
            for parcel in parcels
        ]

    @property
    def n_sf(self):
        """Total square feet yielded across all model runs."""
        return sum(run.n_sf for run in self.runs)

    @property
    def n_units(self):
        """Total number of units yielded across all model runs."""
        return sum(run.n_units for run in self.runs)

    def _df_rows(self):
        """Generator yielded rows used by to_df()."""
        for run in self.runs:
            for iter_num, iteration in enumerate(run.iterations, start=1):
                for hbu_num, hbu in enumerate(iteration.hbus, start=1):
                    row = {
                        'reference': hbu.parcel.reference,
                        'iteration': iter_num,
                        'hbu': hbu_num,
                        'n_sf': hbu.n_sf,
                        'n_units': hbu.n_units,
                    }
                    yield row

    def to_df(self):
        """Reformat the ModelRun data into a DataFrame."""
        return pd.DataFrame(self._df_rows()).set_index(['reference', 'iteration', 'hbu'])


class ParcelRun:
    """Parcel run."""

    def __init__(self, parcel, prototypes, conversion_rates, screen, n_iterations):
        """init."""
        # Keep only prototypes that pass the entitlement screen
        self._parcel = parcel
        allowed_prototypes = screen.loc[parcel.code].loc[lambda s: s.eq(1)].index.values
        self.prototypes = [p for p in prototypes if p.name in allowed_prototypes]

        self.iterations = list(self._iterations(n_iterations, conversion_rates))

    def _iterations(self, n_iterations, conversion_rates):
        """Run the model for N iterations."""
        self.parcel = self._parcel
        for _ in range(n_iterations):
            iteration = ParcelIteration(self.parcel, self.prototypes, conversion_rates)
            # Set up for next iteration
            self.parcel = deepcopy(self.parcel)
            self.parcel.sf -= iteration.n_sf
            yield iteration

    @property
    def n_sf(self):
        """Number of square feet yielded by parcel run."""
        return sum(iteration.n_sf for iteration in self.iterations)

    @property
    def n_units(self):
        """Number of units yielded by parcel run."""
        return sum(iteration.n_units for iteration in self.iterations)


class ParcelIteration:
    """Parcel iteration."""

    def __init__(self, parcel, prototypes, conversion_rates):
        """init."""
        self.parcel = parcel
        # Only keep prototypes
        self.prototypes = prototypes
        for p in prototypes:
            p.fit(parcel, conversion_rates)
        self.hbus = list(self._hbus())

    def _hbus(self):
        # Three iterations
        prototypes = self.prototypes
        prev_limiting_factor = 1
        for _ in range(3):
            # import pdb; pdb.set_trace()
            if not prototypes:
                # If the list is empty, StopIteration
                raise StopIteration
            hbu = max(prototypes, key=lambda x: x.rpv_per_sf)
            yield hbu
            # Set up next iteration
            prev_limiting_factor *= hbu.LIMITING_FACTOR
            prototypes = [
                self._update(p, prev_limiting_factor)
                for p in prototypes
                if not isinstance(p, type(hbu))
            ]

    def _update(self, prototype, limiting_factor):
        """Update prototype with new limiting factor."""
        prototype = deepcopy(prototype)
        prototype.LIMITING_FACTOR *= limiting_factor
        return prototype

    @property
    def n_sf(self):
        """Number of square feet yielded by all high and best uses."""
        return sum(hbu.n_sf for hbu in self.hbus)

    @property
    def n_units(self):
        """Number of units yielded by all high and best uses."""
        return sum(hbu.n_units for hbu in self.hbus)
