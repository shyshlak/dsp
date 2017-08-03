"""Parcel operations."""


class Parcel:
    """Parcel object."""

    def __init__(
        self,
        reference,
        code,
        code_general,
        tract,
        ezone,
        design_type,
        vac_dev,
        sfr_infill,
        jurisdiction,
        rmv,
        sf,
        net_no_row,
        units,
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
        park_off,
        conversion_rate_region,
    ):
        """docstring."""
        self.reference = reference
        self.code = code
        self.code_general = code_general
        self.tract = tract
        self.ezone = ezone
        self.design_type = design_type
        self.vac_dev = vac_dev,
        self.sfr_infill = sfr_infill
        self.jurisdiction = jurisdiction
        self.rmv = rmv
        # Commercial square footage (i.e., what's already built)
        self.sf = sf
        # Buildable square footage. Should always be less than self.sf
        # TODO: Add validation check that this value is always less than self.rmv.
        self.net_no_row = net_no_row
        self.units = units
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
        self.conversion_rate_region = conversion_rate_region

    @property
    def rmv_per_sf(self):
        """Real market value per square foot."""
        if self.sf !=0:
            return self.rmv / self.sf
        else:
        return 0
