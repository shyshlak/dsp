"""Highest and best use."""
from copy import deepcopy


class HBU:
    """Highest and best use."""

    def __init__(self, parcel, prototypes):
        """Initialize."""
        self.parcel = parcel
        self.prototypes = deepcopy(prototypes)
        for prototype in self.prototypes:
            prototype.prototype.fit(parcel)

        self.hbu = max(self.prototypes, key=lambda x: x.prototype.rpv_per_sf)

    @property
    def rmv_rpv_ratio(self):
        """Real market value to residual property value ratio."""
        rmv = self.parcel.rmv_per_sf
        rpv = self.hbu.prototype.rpv_per_sf

        if rpv == 0:
            return 'NA'
        return rmv / rpv

    @property
    def redevelopment_rate(self):
        """Redevelopment rate."""
        ratio = self.rmv_rpv_ratio
        if ratio == 'NA':
            return 0
        elif ratio < 0.75:
            return 0.0485
        elif 0.75 <= ratio < 1.25:
            return 0.0261
        elif 1.25 <= ratio < 2:
            return 0.0094
        elif 2 <= ratio < 4:
            return 0.0025
        else:
            # >= 4
            return 0.0031

    @property
    def n_units(self):
        """Determine the number of yielded units."""
        if 'residential' in self.hbu.type:
            return 0
        max_units = self.hbu.prototype.density / 43560 * self.parcel.sf
        # Limit
        return max_units * self.redevelopment_rate * self.hbu.prototype.limiting_factor

    @property
    def n_sf(self):
        """Determine the number of yielded square feet."""
        return (
            self.hbu.prototype.far
            * self.parcel.sf
            * self.redevelopment_rate
            * self.hbu.prototype.limiting_factor
        )
