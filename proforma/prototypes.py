"""Pro-forma prototype base classes."""
import logging

import numpy as np


logger = logging.getLogger(__name__)


class _SharedPrototype:
    """Shared base class."""

    _INCOME_ATTRIBUTE = None
    _PARKING_ATTRIBUTE = None
    LIMITING_FACTOR = None

    def __init__(self, *args, **kwargs):
        """init."""
        parcel = kwargs.pop('parcel', None)
        conversion_rates = kwargs.pop('conversion_rates', None)
        super().__init__(*args, **kwargs)

        self._is_fit = False
        if all(x is not None for x in (parcel, conversion_rates)):
            self.fit(parcel, conversion_rates)

    def __str__(self):
        return '{0}: {1}'.format(self.__class__.__name__, self.name)

    @property
    def rmv_rpv_ratio(self):
        """Real market value to residual property value ratio."""
        rmv = self.parcel.rmv_per_sf
        rpv = self.rpv_per_sf

        if rpv <= 0:
            return None
        return rmv / rpv

    @property
    def redevelopment_rate(self):
        """Redevelopment rate."""
        ratio = self.rmv_rpv_ratio
        if ratio is None:
            return 0

        return self.conversion_rates.get(self.parcel.conversion_rate_region, ratio)

    @property
    def net_redev_rate(self):
        """Redevelopment rate, adjusted for limiting factor."""
        return self.redevelopment_rate * self.LIMITING_FACTOR

    @property
    def max_sf(self):
        """Maximum square feet allowable on prototype."""
        if isinstance(self, (ResidentialOwnershipPrototype, ResidentialRentalPrototype)):
            # Square footage only applies to non-residential prototypes
            return 0
        return self.far * self.parcel.net_no_row

    @property
    def n_sf(self):
        """Determine the number of yielded square feet."""
        if isinstance(self, (ResidentialOwnershipPrototype, ResidentialRentalPrototype)):
            # Square footage only applies to non-residential prototypes
            return 0
        # n_gained * probability
        return (self.max_sf - self.parcel.sf) * self.net_redev_rate

    @property
    def max_units(self):
        """Maximum number of units allowable on prototype."""
        if not isinstance(self, (ResidentialOwnershipPrototype, ResidentialRentalPrototype)):
            # Units only apply to residential prototypes
            return 0
        return self.density / 43560 * self.parcel.net_no_row

    @property
    def n_units(self):
        """Determine the number of yielded units."""
        if not isinstance(self, (ResidentialOwnershipPrototype, ResidentialRentalPrototype)):
            # Units only apply to residential prototypes
            return 0

        # n_gained * probability
        return (self.max_units - self.parcel.units) * self.net_redev_rate


class Prototype(_SharedPrototype):
    """Prototype base class."""

    def __init__(
        self,
        name,
        site_size,
        stories,
        building_sf,
        efficiency_ratio,
        parking_ratio_per_1000_sf,
        pct_structured_parking,
        base_construction_cost_per_sf,
        tenant_improvement_allowance,
        construction_adjustment_factor,
        base_parking_cost_per_space,
        parking_adjustment_factor,
        income_adjustment_factor,
        vacancy_collection_loss,
        base_operating_expenses,
        operating_adjustment_factor,
        base_capitalization_rate,
        capitalization_adjustment_factor,
        threshold_return_on_cost,
        *args,
        **kwargs
    ):
        """docs."""
        self.name = name
        self.site_size = site_size
        self.stories = stories
        self.building_sf = building_sf
        self.efficiency_ratio = efficiency_ratio
        self.parking_ratio_per_1000_sf = parking_ratio_per_1000_sf
        self.pct_structured_parking = pct_structured_parking
        self.base_construction_cost_per_sf = base_construction_cost_per_sf
        self.tenant_improvement_allowance = tenant_improvement_allowance
        self.construction_adjustment_factor = construction_adjustment_factor
        self.base_parking_cost_per_space = base_parking_cost_per_space
        self.parking_adjustment_factor = parking_adjustment_factor
        self.income_adjustment_factor = income_adjustment_factor
        self.vacancy_collection_loss = vacancy_collection_loss
        self.base_operating_expenses = base_operating_expenses
        self.operating_adjustment_factor = operating_adjustment_factor
        self.base_capitalization_rate = base_capitalization_rate
        self.capitalization_adjustment_factor = capitalization_adjustment_factor,
        self.threshold_return_on_cost = threshold_return_on_cost

        super().__init__(*args, **kwargs)

    # Pro forma
    def __getattr__(self, name):
        """Raise a different error if trying to access attributes before the Prototype is fit."""
        fit_attributes = (
            'parcel', 'base_income_per_sf_per_year', 'parking_charges_per_space_per_month'
        )
        if name in fit_attributes and not self._is_fit:
            raise ValueError('{0} cannot be accessed until the Prototype is fit.'.format(name))
        raise AttributeError(
            '{0} object has no attribute {1}'.format(self.__class__.__name__, name)
        )

    def fit(self, parcel, conversion_rates):
        """Fit a prototype."""
        self.parcel = parcel
        self.conversion_rates = conversion_rates
        self.base_income_per_sf_per_year = getattr(parcel, self._INCOME_ATTRIBUTE)
        self.parking_charges_per_space_per_month = getattr(parcel, self._PARKING_ATTRIBUTE)
        self._is_fit = True

    # Property Assumptions
    @property
    def far(self):
        """Floor area ratio."""
        return self.building_sf / self.site_size

    @property
    def leasable_area(self):
        """Leasable square feet."""
        return self.building_sf * self.efficiency_ratio

    @property
    def parking_spaces(self):
        """Number of parking spaces."""
        parking_per_sf = self.parking_ratio_per_1000_sf / 1000
        n_spaces = self.leasable_area * parking_per_sf
        return np.floor(n_spaces)

    @property
    def parking_spaces_surface(self):
        """Number of surface parking spaces."""
        pct_surface = 1 - self.pct_structured_parking
        return self.parking_spaces * pct_surface

    @property
    def parking_spaces_structured(self):
        """Number of structured parking spaces."""
        return self.parking_spaces * self.pct_structured_parking

    # Cost Assumptions
    @property
    def construction_cost_per_sf(self):
        """Construction cost per square foot."""
        unadjusted = self.base_construction_cost_per_sf + self.tenant_improvement_allowance
        return unadjusted * (1 + self.construction_adjustment_factor)

    @property
    def structured_parking_cost_per_space(self):
        """Structured parking cost per space."""
        return self.base_parking_cost_per_space * (1 + self.parking_adjustment_factor)

    # Income Assumptions
    @property
    def achievable_pricing(self):
        """Achievable Pricing."""
        return self.base_income_per_sf_per_year * (1 + self.income_adjustment_factor)

    # Expense Assumptions
    @property
    def operating_expenses(self):
        """Operating expenses."""
        return self.base_operating_expenses * (1 + self.operating_adjustment_factor)

    # Valuation Assumptions
    @property
    def capitalization_rate(self):
        """Capitalization rate."""
        return self.base_capitalization_rate * (1 + self.capitalization_adjustment_factor)

    # Cost
    @property
    def cost_per_construct_without_parking(self):
        """Cost (excluding parking)."""
        return self.building_sf * self.construction_cost_per_sf

    @property
    def parking_costs(self):
        """Cost of parking."""
        return self.parking_spaces_structured * self.structured_parking_cost_per_space

    @property
    def project_cost(self):
        """Estimated project cost."""
        return self.cost_per_construct_without_parking + self.parking_costs

    # Income
    @property
    def annual_base_income(self):
        """Annual base income."""
        return self.leasable_area * self.achievable_pricing

    @property
    def annual_parking_income(self):
        """Annual income from parking."""
        monthly_parking_income = (
            self.parking_spaces_structured
            * self.parking_charges_per_space_per_month
        )
        return monthly_parking_income * 12

    @property
    def gross_annual_income(self):
        """Gross annual income."""
        return self.annual_base_income + self.annual_parking_income

    @property
    def effective_gross_income(self):
        """Gross annual income, less vacancy and collection loss."""
        return self.gross_annual_income * (1 - self.vacancy_collection_loss)

    @property
    def annual_noi(self):
        """Annual net operating income (Effective gross income, less operating expenses)."""
        return self.effective_gross_income * (1 - self.operating_expenses)

    # Property Valuation
    @property
    def return_on_cost(self):
        """Return on cost."""
        return self.annual_noi / self.project_cost

    @property
    def residual_property_value(self):
        """Residual property value."""
        return (self.annual_noi / self.threshold_return_on_cost) - self.project_cost

    @property
    def rpv_per_sf(self):
        """Residual property value per square foot."""
        return self.residual_property_value / self.site_size


class OfficePrototype(Prototype):
    """Office prototype."""

    _INCOME_ATTRIBUTE = 'off_rent'
    _PARKING_ATTRIBUTE = 'park_off'
    LIMITING_FACTOR = 1


class RetailPrototype(Prototype):
    """Retail prototype."""

    _INCOME_ATTRIBUTE = 'ret_rent'
    LIMITING_FACTOR = 1

    def fit(self, parcel, conversion_rates):
        """Fit a prototype."""
        self.parcel = parcel
        self.conversion_rates = conversion_rates
        self.base_income_per_sf_per_year = getattr(parcel, self._INCOME_ATTRIBUTE)
        self.parking_charges_per_space_per_month = 0
        self._is_fit = True


class WDPrototype(Prototype):
    """Warehouse and distribution (W&D) industrial prototype."""

    _INCOME_ATTRIBUTE = 'wd_rent'
    LIMITING_FACTOR = 1

    def fit(self, parcel, conversion_rates):
        """Fit a prototype."""
        self.parcel = parcel
        self.conversion_rates = conversion_rates
        self.base_income_per_sf_per_year = getattr(parcel, self._INCOME_ATTRIBUTE)
        self.parking_charges_per_space_per_month = 0
        self._is_fit = True


class FlexPrototype(Prototype):
    """Flex industrial prototype."""

    _INCOME_ATTRIBUTE = 'flex_rent'
    LIMITING_FACTOR = 1

    def fit(self, parcel, conversion_rates):
        """Fit a prototype."""
        self.parcel = parcel
        self.conversion_rates = conversion_rates
        self.base_income_per_sf_per_year = getattr(parcel, self._INCOME_ATTRIBUTE)
        self.parking_charges_per_space_per_month = 0
        self._is_fit = True


class ResidentialRentalPrototype(_SharedPrototype):
    """Residential rental prototype."""

    _INCOME_ATTRIBUTE = 'res_rent'
    _PARKING_ATTRIBUTE = 'park_rent'
    LIMITING_FACTOR = 1

    def __init__(
        self,
        name,
        site_size,
        density,
        avg_unit_size,
        efficiency_ratio,
        parking_ratio_per_unit,
        pct_structured_parking,
        base_construction_cost_per_sf,
        construction_adjustment_factor,
        base_parking_cost_per_space,
        parking_adjustment_factor,
        income_adjustment_factor,
        vacancy_collection_loss,
        base_operating_expenses,
        operating_adjustment_factor,
        base_capitalization_rate,
        capitalization_adjustment_factor,
        threshold_return_on_cost,
        *args,
        **kwargs
    ):
        """docs."""
        self.name = name
        self.site_size = site_size
        self.density = density
        self.avg_unit_size = avg_unit_size
        self.efficiency_ratio = efficiency_ratio
        self.parking_ratio_per_unit = parking_ratio_per_unit
        self.pct_structured_parking = pct_structured_parking
        self.base_construction_cost_per_sf = base_construction_cost_per_sf
        self.construction_adjustment_factor = construction_adjustment_factor
        self.base_parking_cost_per_space = base_parking_cost_per_space
        self.parking_adjustment_factor = parking_adjustment_factor
        self.income_adjustment_factor = income_adjustment_factor
        self.vacancy_collection_loss = vacancy_collection_loss
        self.base_operating_expenses = base_operating_expenses
        self.operating_adjustment_factor = operating_adjustment_factor
        self.base_capitalization_rate = base_capitalization_rate
        self.capitalization_adjustment_factor = capitalization_adjustment_factor
        self.threshold_return_on_cost = threshold_return_on_cost

        super().__init__(*args, **kwargs)

    # Pro forma
    def __getattr__(self, name):
        """Raise a different error if trying to access attributes before the Prototype is fit."""
        fit_attributes = (
            'parcel', 'base_income_per_sf_per_month', 'parking_charges_per_space_per_month'
        )
        if name in fit_attributes and not self._is_fit:
            raise ValueError('{0} cannot be accessed until the Prototype is fit.'.format(name))
        raise AttributeError(
            '{0} object has no attribute {1}'.format(self.__class__.__name__, name)
        )

    def fit(self, parcel, conversion_rates):
        """Fit a prototype."""
        self.parcel = parcel
        self.conversion_rates = conversion_rates
        self.base_income_per_sf_per_month = getattr(parcel, self._INCOME_ATTRIBUTE)
        self.parking_charges_per_space_per_month = getattr(parcel, self._PARKING_ATTRIBUTE)
        self._is_fit = True

    # Property Assumptions
    @property
    def unit_count(self):
        """Unit count."""
        count = self.site_size / 43560 * self.density
        return np.floor(count)

    @property
    def building_sf(self):
        """Building square feet."""
        return self.unit_count * self.avg_unit_size / self.efficiency_ratio

    @property
    def far(self):
        """Floor area ratio."""
        return self.building_sf / self.site_size

    @property
    def parking_spaces(self):
        """Number of parking spaces."""
        n_spaces = self.unit_count * self.parking_ratio_per_unit
        return np.ceil(n_spaces)

    @property
    def parking_spaces_surface(self):
        """Number of surface parking spaces."""
        pct_surface = 1 - self.pct_structured_parking
        return self.parking_spaces * pct_surface

    @property
    def parking_spaces_structured(self):
        """Number of structured parking spaces."""
        return self.parking_spaces * self.pct_structured_parking

    # Cost Assumptions
    @property
    def construction_cost_per_sf(self):
        """Construction cost per square foot."""
        return self.base_construction_cost_per_sf * (1 + self.construction_adjustment_factor)

    @property
    def structured_parking_cost_per_space(self):
        """Structured parking cost per space."""
        return self.base_parking_cost_per_space * (1 + self.parking_adjustment_factor)

    # Income Assumptions
    @property
    def achievable_pricing(self):
        """Achievable Pricing."""
        return self.base_income_per_sf_per_month * (1 + self.income_adjustment_factor)

    # Expense Assumptions
    @property
    def operating_expenses(self):
        """Operating expenses."""
        return self.base_operating_expenses * (1 + self.operating_adjustment_factor)

    # Valuation Assumptions
    @property
    def capitalization_rate(self):
        """Capitalization rate."""
        return self.base_capitalization_rate * (1 + self.capitalization_adjustment_factor)

    # Cost
    @property
    def cost_per_construct_without_parking(self):
        """Cost (excluding parking)."""
        return self.building_sf * self.construction_cost_per_sf

    @property
    def parking_costs(self):
        """Cost of parking."""
        return self.parking_spaces_structured * self.structured_parking_cost_per_space

    @property
    def project_cost(self):
        """Estimated project cost."""
        return self.cost_per_construct_without_parking + self.parking_costs

    # Income
    @property
    def annual_base_income(self):
        """Annual base income."""
        return self.building_sf * self.achievable_pricing * self.efficiency_ratio * 12

    @property
    def annual_parking_income(self):
        """Annual income from parking."""
        monthly_parking_income = (
            self.parking_spaces_structured
            * self.parking_charges_per_space_per_month
        )
        return monthly_parking_income * 12

    @property
    def gross_annual_income(self):
        """Gross annual income."""
        return self.annual_base_income + self.annual_parking_income

    @property
    def effective_gross_income(self):
        """Gross annual income, less vacancy and collection loss."""
        return self.gross_annual_income * (1 - self.vacancy_collection_loss)

    @property
    def annual_noi(self):
        """Annual net operating income (Effective gross income, less operating expenses)."""
        return self.effective_gross_income * (1 - self.operating_expenses)

    # Property Valuation
    @property
    def return_on_cost(self):
        """Return on cost."""
        return self.annual_noi / self.project_cost

    @property
    def residual_property_value(self):
        """Residual property value."""
        return (self.annual_noi / self.threshold_return_on_cost) - self.project_cost

    @property
    def rpv_per_sf(self):
        """Residual property value per square foot."""
        return self.residual_property_value / self.site_size


class ResidentialOwnershipPrototype(_SharedPrototype):
    """Residential ownership prototype."""

    _INCOME_ATTRIBUTE = 'res_price'
    _PARKING_ATTRIBUTE = 'park_own'
    LIMITING_FACTOR = 1

    def __init__(
        self,
        name,
        site_size,
        density,
        avg_unit_size,
        efficiency_ratio,
        parking_ratio_per_unit,
        pct_structured_parking,
        base_construction_cost_per_sf,
        construction_adjustment_factor,
        base_parking_cost_per_space,
        parking_adjustment_factor,
        income_adjustment_factor,
        sales_commission,
        threshold_return,
        *args,
        **kwargs
    ):
        """docs."""
        self.name = name
        self.site_size = site_size
        self.density = density
        self.avg_unit_size = avg_unit_size
        self.efficiency_ratio = efficiency_ratio
        self.parking_ratio_per_unit = parking_ratio_per_unit
        self.pct_structured_parking = pct_structured_parking
        self.base_construction_cost_per_sf = base_construction_cost_per_sf
        self.construction_adjustment_factor = construction_adjustment_factor
        self.base_parking_cost_per_space = base_parking_cost_per_space
        self.parking_adjustment_factor = parking_adjustment_factor
        self.income_adjustment_factor = income_adjustment_factor
        self.sales_commission = sales_commission
        self.threshold_return = threshold_return

        super().__init__(*args, **kwargs)

    # Pro forma
    def __getattr__(self, name):
        """Raise a different error if trying to access attributes before the Prototype is fit."""
        fit_attributes = (
            'parcel', 'base_sale_price_per_sf', 'parking_charges_per_space'
        )
        if name in fit_attributes and not self._is_fit:
            raise ValueError('{0} cannot be accessed until the Prototype is fit.'.format(name))
        raise AttributeError(
            '{0} object has no attribute {1}'.format(self.__class__.__name__, name)
        )

    def fit(self, parcel, conversion_rates):
        """Fit a prototype."""
        self.parcel = parcel
        self.conversion_rates = conversion_rates
        self.base_sale_price_per_sf = getattr(parcel, self._INCOME_ATTRIBUTE)
        self.parking_charges_per_space = getattr(parcel, self._PARKING_ATTRIBUTE)
        self._is_fit = True

    # Property Assumptions
    @property
    def unit_count(self):
        """Unit count."""
        count = self.site_size / 43560 * self.density
        return np.floor(count)

    @property
    def building_sf(self):
        """Building square feet."""
        return self.unit_count * self.avg_unit_size / self.efficiency_ratio

    @property
    def far(self):
        """Floor area ratio."""
        return self.building_sf / self.site_size

    @property
    def parking_spaces(self):
        """Number of parking spaces."""
        n_spaces = self.unit_count * self.parking_ratio_per_unit
        return np.ceil(n_spaces)

    @property
    def parking_spaces_surface(self):
        """Number of surface parking spaces."""
        pct_surface = 1 - self.pct_structured_parking
        return self.parking_spaces * pct_surface

    @property
    def parking_spaces_structured(self):
        """Number of structured parking spaces."""
        return self.parking_spaces * self.pct_structured_parking

    # Cost Assumptions
    @property
    def construction_cost_per_sf(self):
        """Construction cost per square foot."""
        return self.base_construction_cost_per_sf * (1 + self.construction_adjustment_factor)

    @property
    def structured_parking_cost_per_space(self):
        """Structured parking cost per space."""
        return self.base_parking_cost_per_space * (1 + self.parking_adjustment_factor)

    # Income Assumptions
    @property
    def achievable_pricing(self):
        """Achievable Pricing."""
        return self.base_sale_price_per_sf * (1 + self.income_adjustment_factor)

    # Cost
    @property
    def cost_per_construct_without_parking(self):
        """Cost (excluding parking)."""
        return self.building_sf * self.construction_cost_per_sf

    @property
    def parking_costs(self):
        """Cost of parking."""
        return self.parking_spaces_structured * self.structured_parking_cost_per_space

    @property
    def project_cost(self):
        """Estimated project cost."""
        return self.cost_per_construct_without_parking + self.parking_costs

    # Income
    @property
    def gross_income_units(self):
        """Gross income from units."""
        return self.building_sf * self.achievable_pricing * 0.9

    @property
    def gross_income_parking(self):
        """Gross income from parking."""
        return self.parking_spaces_structured * self.parking_charges_per_space

    @property
    def gross_sales_income(self):
        """Total gross income."""
        return self.gross_income_units + self.gross_income_parking

    @property
    def commission(self):  # noqa: D401
        """Sales commission."""
        return self.gross_sales_income * self.sales_commission

    @property
    def effective_gross_income(self):
        """Effective gross income."""
        return self.gross_sales_income - self.commission

    # Property Valuation
    @property
    def return_on_cost(self):
        """Return on cost."""
        return (self.effective_gross_income - self.project_cost) / self.project_cost

    @property
    def residual_property_value(self):
        """Residual property value."""
        return (
            (self.effective_gross_income / (1 + self.threshold_return))
            - self.project_cost
        )

    @property
    def rpv_per_sf(self):
        """Residual property value per square foot."""
        return self.residual_property_value / self.site_size
