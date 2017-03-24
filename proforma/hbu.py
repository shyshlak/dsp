"""Highest and best use."""
from copy import deepcopy

from . import prototypes


class HBU:
    """Highest and best use."""

    def __init__(self, parcel, prototypes, screen, conversion_rates, prev_hbu=None):
        """Initialize."""
        self.parcel = parcel
        self.prototypes = deepcopy(prototypes)
        for prototype in self.prototypes:
            prototype.fit(parcel)
            # Does zoning allow this prototype?
            prototype.is_allowed = bool(screen.loc[parcel.code, prototype.name])
            prototype.rpv_per_sf_screen = prototype.rpv_per_sf * prototype.is_allowed

        self.hbu = max(self.prototypes, key=lambda x: x.rpv_per_sf_screen)

        self.limiting_factor = self.hbu.limiting_factor
        if prev_hbu is not None:
            self.limiting_factor *= prev_hbu.limiting_factor

        self.conversion_rates = conversion_rates

    @property
    def rmv_rpv_ratio(self):
        """Real market value to residual property value ratio."""
        rmv = self.parcel.rmv_per_sf
        rpv = self.hbu.rpv_per_sf_screen

        if rpv <= 0:
            return 'NA'
        return rmv / rpv

    @property
    def redevelopment_rate(self):
        """Redevelopment rate."""
        ratio = self.rmv_rpv_ratio
        if ratio == 'NA':
            return 0

        for upper_bound, rate in self.conversion_rates:
            if ratio < upper_bound:
                return rate

    @property
    def n_units(self):
        """Determine the number of yielded units."""
        if not isinstance(
            self.hbu,
            (prototypes.ResidentialOwnershipPrototype, prototypes.ResidentialRentalPrototype)
        ):
            # Units only apply to residential prototypes
            return 0
        max_units = self.hbu.density / 43560 * self.parcel.sf
        # Limit
        return max_units * self.redevelopment_rate * self.limiting_factor

    @property
    def n_sf(self):
        """Determine the number of yielded square feet."""
        return self.hbu.far * self.parcel.sf * self.redevelopment_rate * self.limiting_factor
