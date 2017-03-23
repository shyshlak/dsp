"""Run classes."""

from copy import deepcopy
from functools import lru_cache

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
