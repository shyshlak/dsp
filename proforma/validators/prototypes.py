"""Validate and read prototype data."""
from functools import partial

import engarde.checks as ec
import numpy as np

from . import utils


# READERS

class FlexReader(utils.Reader):
    """Flex prototype reader."""

    DTYPES = {
        'name': np.object,
        'site_size': float,
        'stories': float,
        'building_sf': float,
        'efficiency_ratio': float,
        'parking_ratio_per_1000_sf': float,
        'pct_structured_parking': float,
        'base_construction_cost_per_sf': float,
        'tenant_improvement_allowance': float,
        'construction_adjustment_factor': float,
        'base_parking_cost_per_space': float,
        'parking_adjustment_factor': float,
        'income_adjustment_factor': float,
        'vacancy_collection_loss': float,
        'base_operating_expenses': float,
        'operating_adjustment_factor': float,
        'base_capitalization_rate': float,
        'capitalization_adjustment_factor': float,
        'threshold_return_on_cost': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )


class OfficeReader(utils.Reader):
    """Office prototype reader."""

    DTYPES = {
        'name': np.object,
        'site_size': float,
        'stories': float,
        'building_sf': float,
        'efficiency_ratio': float,
        'parking_ratio_per_1000_sf': float,
        'pct_structured_parking': float,
        'base_construction_cost_per_sf': float,
        'tenant_improvement_allowance': float,
        'construction_adjustment_factor': float,
        'base_parking_cost_per_space': float,
        'parking_adjustment_factor': float,
        'income_adjustment_factor': float,
        'vacancy_collection_loss': float,
        'base_operating_expenses': float,
        'operating_adjustment_factor': float,
        'base_capitalization_rate': float,
        'capitalization_adjustment_factor': float,
        'threshold_return_on_cost': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )


class ResOwnReader(utils.Reader):
    """Residential ownership prototype reader."""

    DTYPES = {
        'name': np.object,
        'site_size': float,
        'density': float,
        'avg_unit_size': float,
        'efficiency_ratio': float,
        'parking_ratio_per_unit': float,
        'pct_structured_parking': float,
        'base_construction_cost_per_sf': float,
        'construction_adjustment_factor': float,
        'base_parking_cost_per_space': float,
        'parking_adjustment_factor': float,
        'income_adjustment_factor': float,
        'sales_commission': float,
        'threshold_return': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )


class ResRentReader(utils.Reader):
    """Residential rental prototype reader."""

    DTYPES = {
        'name': np.object,
        'site_size': float,
        'density': float,
        'avg_unit_size': float,
        'efficiency_ratio': float,
        'parking_ratio_per_unit': float,
        'pct_structured_parking': float,
        'base_construction_cost_per_sf': float,
        'construction_adjustment_factor': float,
        'base_parking_cost_per_space': float,
        'parking_adjustment_factor': float,
        'income_adjustment_factor': float,
        'vacancy_collection_loss': float,
        'base_operating_expenses': float,
        'operating_adjustment_factor': float,
        'base_capitalization_rate': float,
        'capitalization_adjustment_factor': float,
        'threshold_return_on_cost': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )


class RetailReader(utils.Reader):
    """Retail prototype reader."""

    DTYPES = {
        'name': np.object,
        'site_size': float,
        'stories': float,
        'building_sf': float,
        'efficiency_ratio': float,
        'parking_ratio_per_1000_sf': float,
        'pct_structured_parking': float,
        'base_construction_cost_per_sf': float,
        'tenant_improvement_allowance': float,
        'construction_adjustment_factor': float,
        'base_parking_cost_per_space': float,
        'parking_adjustment_factor': float,
        'income_adjustment_factor': float,
        'vacancy_collection_loss': float,
        'base_operating_expenses': float,
        'operating_adjustment_factor': float,
        'base_capitalization_rate': float,
        'capitalization_adjustment_factor': float,
        'threshold_return_on_cost': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )


class WDReader(utils.Reader):
    """Warehouse and distributing prototype reader."""

    DTYPES = {
        'name': np.object,
        'site_size': float,
        'stories': float,
        'building_sf': float,
        'efficiency_ratio': float,
        'parking_ratio_per_1000_sf': float,
        'pct_structured_parking': float,
        'base_construction_cost_per_sf': float,
        'tenant_improvement_allowance': float,
        'construction_adjustment_factor': float,
        'base_parking_cost_per_space': float,
        'parking_adjustment_factor': float,
        'income_adjustment_factor': float,
        'vacancy_collection_loss': float,
        'base_operating_expenses': float,
        'operating_adjustment_factor': float,
        'base_capitalization_rate': float,
        'capitalization_adjustment_factor': float,
        'threshold_return_on_cost': float,
    }

    CHECKS = (
        ec.none_missing,
        partial(ec.is_shape, shape=(-1, len(DTYPES))),
        ec.unique_index,
        partial(ec.has_dtypes, items=DTYPES),
    )
