"""Run classes."""

from copy import deepcopy
from functools import lru_cache

from.hbu import HBU


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
    def n_units(self):
        """Total number of units yielded across all highest and best uses."""
        return sum(hbu.n_units for hbu in (self.hbu_1, self.hbu_2, self.hbu_3))

    @property
    def n_sf(self):
        """Total number of square feet yielded across all highest and best uses."""
        return sum(hbu.n_sf for hbu in (self.hbu_1, self.hbu_2, self.hbu_3))
