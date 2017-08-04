#!/usr/bin/env python
"""CLI for DSP."""

import argparse
from os import path
from sys import exit

import numpy as np

import proforma.prototypes as ptypes
from proforma.conversions import ConversionRates
from proforma.parcels import Parcel
from proforma.run import ModelRun
from proforma.validators import conversions as cv, parcels as pav, prototypes as pov, screen as sv


def parser_factory():
    """Parser factory."""
    parser = argparse.ArgumentParser(
        description=(
            'Command-line interface to the Developer Supply Preprocessor.\n\n'
            'The data directory must contain these eight (8) files:\n'
            '\t* parcels.csv\n'
            '\t* entitlement_screen.xlsx\n'
            '\t* conversion_rates.xlsx\n'
            '\t* prototypes/flex.xlsx\n'
            '\t* prototypes/office.xlsx\n'
            '\t* prototypes/residential_ownership.xlsx\n'
            '\t* prototypes/residential_rental.xlsx\n'
            '\t* prototypes/retail.xlsx\n'
            '\t* prototypes/wd.xlsx\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-d', '--data-dir',
        default='./data',
        help='Data directory, defaults to ./data'
    )
    parser.add_argument(
        '-o', '--output-file',
        default=open('./output.csv', 'w'),
        type=argparse.FileType('w'),
        help='Output file location, defaults to ./output.csv',
    )
    parser.add_argument(
        '-l', '--iteration-length',
        default=5, type=int, help='Iteration length, defaults to 1'
    )
    parser.add_argument(
        '-n', '--n-iterations',
        default=1, type=int, help='Number of iterations, defaults to 1'
    )
    return parser


def build_parcels(data_dir):
    """Convert parcels from DataFrame to list of Parcel objects."""
    filename = path.join(data_dir, 'parcels.csv')
    df = pav.ParcelReader().read(filename)
    return [Parcel(**row.to_dict()) for _, row in df.iterrows()]


def build_prototypes(data_dir):
    """Convert and combine prototypes from DataFrames to list of Prototype objects."""
    directory = path.join(data_dir, 'prototypes')
    data = {
        ptypes.FlexPrototype: pov.FlexReader().read(path.join(directory, 'flex.xlsx')),
        ptypes.OfficePrototype: pov.OfficeReader().read(path.join(directory, 'office.xlsx')),
        ptypes.ResidentialOwnershipPrototype: (
            pov.ResOwnReader().read(path.join(directory, 'residential_ownership.xlsx'))
        ),
        ptypes.ResidentialRentalPrototype: (
            pov.ResRentReader().read(path.join(directory, 'residential_rental.xlsx'))
        ),
        ptypes.RetailPrototype: pov.RetailReader().read(path.join(directory, 'retail.xlsx')),
        ptypes.WDPrototype: pov.WDReader().read(path.join(directory, 'wd.xlsx')),
    }

    return [
        cls(**row.to_dict())
        for cls, df in data.items()
        for _, row in df.iterrows()
    ]


def build_screen(data_dir, parcels, prototypes):
    """Prepare entitlement screen."""
    filename = path.join(data_dir, 'entitlement_screen.xlsx')
    return sv.ScreenReader(parcels, prototypes).read(filename)


def build_conversion_rates(data_dir):
    """Prepare the conversion rates."""
    filename = path.join(data_dir, 'conversion_rates.xlsx')
    df = cv.ConversionRatesReader().read(filename)
    return ConversionRates(df)


def main():
    """Run CLI."""
    parser = parser_factory()
    args = parser.parse_args()
    data_dir = path.abspath(args.data_dir)

    print('Gathering parcels...')
    parcels = build_parcels(data_dir)
    print('Gathering prototypes...')
    prototypes = build_prototypes(data_dir)
    print('Gathering screen...')
    screen = build_screen(data_dir, parcels, prototypes)
    print('Gathering conversion rates...')
    conversion_rates = build_conversion_rates(data_dir)

    # Model run
    print('Starting run...')
    model_run = ModelRun(
        parcels, prototypes, conversion_rates, screen, args.n_iterations, args.iteration_length
    )
    print('Compiling data...')
    df = model_run.to_df()

    # To CSV
    print('Saving data...')
    df.to_csv(args.output_file)

    # Summary stats
    print('\nCalculating summary statistics...', end='\n\n')
    print('Number of parcels\t{0}'.format(len(parcels)))
    print('Total commercial square footage yielded\t{0}'.format(df.n_sf.sum()))
    print('Total residential units yielded\t{0}'.format(df.n_units.sum()), end='\n\n')
    print(
        (
            df
            .groupby('prototype')
            .n_sf
            .sum()
            .sort_values(ascending=False)
            .rename_axis('Commercial square footage by prototype:')
            .to_string()
        ),
        end='\n\n'
    )
    print(
        (
            df
            .groupby('prototype')
            .n_units
            .sum()
            .sort_values(ascending=False)
            .rename_axis('Residential units by prototype:')
            .to_string()
        ),
        end='\n\n'
    )

    print('Done!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('Quitting')
