"""Run classes."""

from copy import deepcopy
from functools import lru_cache

import pandas as pd

from.hbu import HBU


class ModelRun:
    """Model run."""

    def __init__(self, parcels, prototypes, screen, n_iterations=5):
        """init."""
        self.parcels = deepcopy(parcels)
        self.prototypes = deepcopy(prototypes)
        self.screen = screen

        self.iterations = []
        parcels_new = self.parcels
        for _ in range(n_iterations):
            iteration = ModelIteration(parcels_new, self.prototypes, self.screen)
            self.iterations.append(iteration)
            parcels_new = iteration.parcels_new

    @property
    def n_sf(self):
        """Total number of square feet yielded across all iterations."""
        return sum(iteration.n_sf for iteration in self.iterations)

    @property
    def n_units(self):
        """Total number of units yielded across all iterations."""
        return sum(iteration.n_units for iteration in self.iterations)

    def _df_rows(self):
        """Generator yielded rows used by to_df()."""
        for iter_num, iteration in enumerate(self.iterations):
            for parcel_run in iteration.parcel_runs:
                for hbu_num in range(1, 4):
                    hbu_name = 'hbu_{0}'.format(hbu_num)
                    hbu = getattr(parcel_run, hbu_name)
                    row = {
                        'reference': hbu.parcel.reference,
                        'iteration': iter_num,
                        'hbu': hbu_num,
                        'n_sf': hbu.n_sf,
                        'n_units': hbu.n_units
                    }
                    yield row

    def to_df(self):
        """Reformat the ModelRun data into a DataFrame."""
        return pd.DataFrame(self._df_rows()).set_index(['reference', 'iteration', 'hbu'])


class ModelIteration:
    """Model iteration."""

    def __init__(self, parcels, prototypes, screen):
        """init."""
        self.parcels = deepcopy(parcels)
        self.prototypes = deepcopy(prototypes)
        self.screen = screen

        self.parcel_runs = [ParcelRun(parcel, prototypes, screen) for parcel in self.parcels]

        self.parcels_new = []
        for pr in self.parcel_runs:
            parcel_new = deepcopy(pr.parcel)
            parcel_new.sf -= pr.n_sf
            self.parcels_new.append(parcel_new)

    @property
    def n_sf(self):
        """Total number of square feet yielded across all parcels."""
        return sum(pr.n_sf for pr in self.parcel_runs)

    @property
    def n_units(self):
        """Total number of units yielded across all parcels."""
        return sum(pr.n_units for pr in self.parcel_runs)


class ParcelRun:
    """Parcel run."""

    def __init__(self, parcel, prototypes, screen):
        """init."""
        self.parcel = parcel
        self.prototypes = deepcopy(prototypes)
        self.screen = screen

    @property
    @lru_cache()
    def hbu_1(self):
        """Highest and best use #1."""
        return HBU(self.parcel, self.prototypes, self.screen)

    @property
    @lru_cache()
    def hbu_2(self):
        """Highest and best use #2."""
        prototypes = [p for p in self.prototypes if not isinstance(p, type(self.hbu_1.hbu))]
        return HBU(self.parcel, prototypes, self.screen, prev_hbu=self.hbu_1)

    @property
    @lru_cache()
    def hbu_3(self):
        """Highest and best use #3."""
        prototypes = [
            p
            for p in self.prototypes
            if not isinstance(p, (type(self.hbu_1.hbu), type(self.hbu_2.hbu)))
        ]

        return HBU(self.parcel, prototypes, self.screen, prev_hbu=self.hbu_2)

    @property
    def n_sf(self):
        """Total number of square feet yielded across all highest and best uses."""
        return sum(hbu.n_sf for hbu in (self.hbu_1, self.hbu_2, self.hbu_3))

    @property
    def n_units(self):
        """Total number of units yielded across all highest and best uses."""
        return sum(hbu.n_units for hbu in (self.hbu_1, self.hbu_2, self.hbu_3))
