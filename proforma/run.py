"""Run classes."""
from copy import deepcopy
from multiprocessing import Pool

import pandas as pd


class ModelRun:
    """Model run."""

    def __init__(
        self,
        parcels,
        prototypes,
        conversion_rates,
        screen,
        n_iterations,
        iteration_length,
        parallel=True
    ):
        """init."""
        # Compound
        self.conversion_rates = conversion_rates.compound(iteration_length)

        if parallel:
            with Pool() as p:
                self.runs = p.map(
                    ParcelRun.init_parallel,
                    [
                        (parcel, prototypes, self.conversion_rates, screen, n_iterations)
                        for parcel in parcels
                    ]
                )
        else:
            self.runs = [
                ParcelRun(parcel, prototypes, self.conversion_rates, screen, n_iterations)
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
        """Yield rows used by to_df()."""
        for run in self.runs:
            for iter_num, iteration in enumerate(run.iterations, start=1):
                for hbu_num, hbu in enumerate(iteration.hbus, start=1):
                    yield {
                        'reference': run.reference,
                        'iteration': iter_num,
                        'hbu': hbu_num,
                        'prototype': hbu.name,
                        'prototype_class': hbu.__class__.__name__,
                        'code': hbu.parcel.code,
                        'code_general': hbu.parcel.code_general,
                        'tract': hbu.parcel.tract,
                        'ezone': hbu.parcel.ezone,
                        'design_type': hbu.parcel.design_type,
                        'vac_dev': hbu.parcel.vac_dev,
                        'sfr_infill': hbu.parcel.sfr_infill,
                        'jurisdiction': hbu.parcel.jurisdiction,
                        'n_sf': hbu.n_sf,
                        'n_units': hbu.n_units,
                        'n_sf_start': hbu.parcel.sf,
                        'n_units_start': hbu.parcel.units,
                        'max_sf': hbu.max_sf,
                        'max_units': hbu.max_units,
                        'redevelopment_rate': hbu.redevelopment_rate,
                        'net_redev_rate': hbu.net_redev_rate,
                    }

    def to_df(self):
        """Reformat the ModelRun data into a DataFrame."""
        return (
            pd
            .DataFrame(self._df_rows())
            .set_index(['reference', 'iteration', 'hbu'])
            .sort_index()
        )


class ParcelRun:
    """Parcel run."""

    def __init__(self, parcel, prototypes, conversion_rates, screen, n_iterations):
        """init."""
        # Keep only prototypes that pass the entitlement screen
        self._parcel = parcel
        self.reference = parcel.reference
        allowed_prototypes = screen.loc[parcel.code].loc[lambda s: s.eq(1)].index.values
        self.prototypes = [p for p in prototypes if p.name in allowed_prototypes]

        self.iterations = list(self._iterations(n_iterations, conversion_rates))

    @classmethod
    def init_parallel(cls, args):
        """Initialize when running in parallel."""
        return cls(*args)

    def _iterations(self, n_iterations, conversion_rates):
        """Run the model for N iterations."""
        parcel = self._parcel
        for _ in range(n_iterations):
            iteration = ParcelIteration(parcel, self.prototypes, conversion_rates)
            yield iteration
            # Set up for next iteration
            parcel = deepcopy(parcel)
            parcel.sf += iteration.n_sf
            parcel.units += iteration.n_units

    @property
    def n_sf(self):
        """Return the number of square feet yielded by parcel run."""
        return sum(iteration.n_sf for iteration in self.iterations)

    @property
    def n_units(self):
        """Return the number of units yielded by parcel run."""
        return sum(iteration.n_units for iteration in self.iterations)


class ParcelIteration:
    """Parcel iteration."""

    def __init__(self, parcel, prototypes, conversion_rates):
        """init."""
        self.parcel = parcel
        # Only keep prototypes
        self.prototypes = deepcopy(prototypes)
        for p in self.prototypes:
            p.fit(parcel, conversion_rates)
        self.hbus = list(self._hbus())

    def _hbus(self):
        # Three iterations
        prototypes = self.prototypes
        prev_limiting_factor = 1
        for _ in range(3):
            # import pdb; pdb.set_trace()
            if not prototypes:
                # If the list is empty, break
                break
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
        """Return the number of square feet yielded by all high and best uses."""
        return sum(hbu.n_sf for hbu in self.hbus)

    @property
    def n_units(self):
        """Return the number of units yielded by all high and best uses."""
        return sum(hbu.n_units for hbu in self.hbus)
