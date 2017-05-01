"""Parcel operations."""


class Parcel:
    """Parcel object."""

    def __init__(
        self,
        reference,
        code,
        rmv,
        sf,
        res_rent,
        res_price,
        off_mkt,
        off_rent,
        ret_mkt,
        ret_rent,
        wd_mkt,
        wd_rent,
        flex_mkt,
        flex_rent,
        park_rent,
        park_own,
        park_off
    ):
        """docstring."""
        self.reference = reference
        self.code = code
        self.rmv = rmv
        self.sf = sf
        self.res_rent = res_rent
        self.res_price = res_price
        self.off_mkt = off_mkt
        self.off_rent = off_rent
        self.ret_mkt = ret_mkt
        self.ret_rent = ret_rent
        self.wd_mkt = wd_mkt
        self.wd_rent = wd_rent
        self.flex_mkt = flex_mkt
        self.flex_rent = flex_rent
        self.park_rent = park_rent
        self.park_own = park_own
        self.park_off = park_off

    @property
    def rmv_per_sf(self):
        """Real market value per square foot."""
        return self.rmv / self.sf
