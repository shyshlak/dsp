"""Pro-forma prototype base classes."""
import numpy as np


class Prototype(object):
    """Prototype base class."""

    def __init__(
        self,
        site_size,
        stories,
        building_sf,
        efficiency_ratio,
        parking_ratio,
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
        capitalization_adjustment_factor
    ):
        """docs."""
        self.site_size = site_size
        self.stories = stories
        self.building_sf = building_sf
        self.efficiency_ratio = efficiency_ratio
        self.parking_ratio = parking_ratio
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
        self.capitalization_adjustment_factor = capitalization_adjustment_factor

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
        parking_per_sf = self.parking_ratio / 1000
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
    def threshold_return_on_cost(self):
        """Return on cost threshold."""
        return self.capitalization_rate * 1.15

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


class ResidentialRentalPrototype(Prototype):
    """Residential rental prototype.

    Note: This is where things get "tricky".
    """


if __name__ == '__main__':
    office_high_rise_assumptions = dict(
        site_size=40000,
        stories=10,
        building_sf=300000,
        efficiency_ratio=0.9,
        parking_ratio=1.5,
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
        capitalization_adjustment_factor=0
    )

    office_high_rise = OfficePrototype(**office_high_rise_assumptions)

    print(office_high_rise.rpv_per_sf)
