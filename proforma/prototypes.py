"""Pro-forma prototype base classes."""
import logging

import numpy as np


logger = logging.getLogger(__name__)


class Prototype(object):
    """Prototype base class."""

    def __init__(
        self,
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
        base_income_per_sf_per_year,
        income_adjustment_factor,
        parking_charges_per_space_per_month,
        vacancy_collection_loss,
        base_operating_expenses,
        operating_adjustment_factor,
        base_capitalization_rate,
        capitalization_adjustment_factor,
        threshold_return_on_cost
    ):
        """docs."""
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
        self.base_income_per_sf_per_year = base_income_per_sf_per_year
        self.income_adjustment_factor = income_adjustment_factor
        self.parking_charges_per_space_per_month = parking_charges_per_space_per_month
        self.vacancy_collection_loss = vacancy_collection_loss
        self.base_operating_expenses = base_operating_expenses
        self.operating_adjustment_factor = operating_adjustment_factor
        self.base_capitalization_rate = base_capitalization_rate
        self.capitalization_adjustment_factor = capitalization_adjustment_factor,
        self.threshold_return_on_cost = threshold_return_on_cost

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


class RetailPrototype(Prototype):
    """Retail prototype."""


class IndustrialPrototype(Prototype):
    """Industrial prototype."""


class ResidentialRentalPrototype(object):
    """Residential rental prototype."""

    def __init__(
        self,
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
        base_income_per_sf_per_month,
        income_adjustment_factor,
        parking_charges_per_space_per_month,
        vacancy_collection_loss,
        base_operating_expenses,
        operating_adjustment_factor,
        base_capitalization_rate,
        capitalization_adjustment_factor,
        threshold_return_on_cost
    ):
        """docs."""
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
        self.base_income_per_sf_per_month = base_income_per_sf_per_month
        self.income_adjustment_factor = income_adjustment_factor
        self.parking_charges_per_space_per_month = parking_charges_per_space_per_month
        self.vacancy_collection_loss = vacancy_collection_loss
        self.base_operating_expenses = base_operating_expenses
        self.operating_adjustment_factor = operating_adjustment_factor
        self.base_capitalization_rate = base_capitalization_rate
        self.capitalization_adjustment_factor = capitalization_adjustment_factor
        self.threshold_return_on_cost = threshold_return_on_cost

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


class ResidentialOwnershipPrototype(object):
    """Residential ownership prototype."""

    def __init__(
        self,
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
        base_sale_price_per_sf,
        income_adjustment_factor,
        parking_charges_per_space,
        sales_commission_pct,
        threshold_return_on_sales
    ):
        """docs."""
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
        self.base_sale_price_per_sf = base_sale_price_per_sf
        self.income_adjustment_factor = income_adjustment_factor
        self.parking_charges_per_space = parking_charges_per_space
        self.sales_commission_pct = sales_commission_pct
        self.threshold_return_on_sales = threshold_return_on_sales

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
        return self.gross_sales_income * self.sales_commission_pct

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
            (self.effective_gross_income / (1 + self.threshold_return_on_sales))
            - self.project_cost
        )

    @property
    def rpv_per_sf(self):
        """Residual property value per square foot."""
        return self.residual_property_value / self.site_size


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    office_high_rise_assumptions = dict(
        site_size=40000,
        stories=10,
        building_sf=300000,
        efficiency_ratio=0.9,
        parking_ratio_per_1000_sf=1.5,
        pct_structured_parking=1,
        base_construction_cost_per_sf=210,
        tenant_improvement_allowance=45,
        construction_adjustment_factor=0,
        base_parking_cost_per_space=55000,
        parking_adjustment_factor=0,
        base_income_per_sf_per_year=24,
        income_adjustment_factor=0,
        parking_charges_per_space_per_month=120,
        vacancy_collection_loss=0.1,
        base_operating_expenses=0.05,
        operating_adjustment_factor=0,
        base_capitalization_rate=0.08,
        capitalization_adjustment_factor=0,
        threshold_return_on_cost=0.092
    )

    rental_high_rise_assumptions = dict(
        site_size=40000,
        density=400,
        avg_unit_size=725,
        efficiency_ratio=0.85,
        parking_ratio_per_unit=1,
        pct_structured_parking=1,
        base_construction_cost_per_sf=275,
        construction_adjustment_factor=0,
        base_parking_cost_per_space=55000,
        parking_adjustment_factor=0,
        base_income_per_sf_per_month=2.1,
        income_adjustment_factor=0,
        parking_charges_per_space_per_month=100 / 1.85 * 2.1,
        vacancy_collection_loss=0.05,
        base_operating_expenses=0.33,
        operating_adjustment_factor=0,
        base_capitalization_rate=0.07,
        capitalization_adjustment_factor=0,
        threshold_return_on_cost=0.077
    )

    condo_residential_high_rise_assumptions = dict(
        site_size=40000,
        density=400,
        avg_unit_size=775,
        efficiency_ratio=0.83,
        parking_ratio_per_unit=1.25,
        pct_structured_parking=1,
        base_construction_cost_per_sf=288.75,
        construction_adjustment_factor=0,
        base_parking_cost_per_space=55000,
        parking_adjustment_factor=0,
        base_sale_price_per_sf=260,
        income_adjustment_factor=0,
        parking_charges_per_space=16250,
        sales_commission_pct=0.04,
        threshold_return_on_sales=0.2
    )

    office_high_rise = OfficePrototype(**office_high_rise_assumptions)
    rental_high_rise = ResidentialRentalPrototype(**rental_high_rise_assumptions)
    condo_residential_high_rise = ResidentialOwnershipPrototype(
        **condo_residential_high_rise_assumptions
    )
    msg = '{obj.__class__.__name__}: {obj.rpv_per_sf}'
    logger.debug(msg.format(obj=office_high_rise))
    logger.debug(msg.format(obj=rental_high_rise))
    logger.debug(msg.format(obj=condo_residential_high_rise))
