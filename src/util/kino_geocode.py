from geocode.geocode import Geocode
from geocode.flags import flags

from typing import override
import logging

import pandas as pd
import pickle
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)-5.5s] [%(name)-12.12s]: %(message)s')
log = logging.getLogger(__name__)


class KinoGeocode(Geocode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def create_geonames_pickle(self):
        """Create list of place/country data from geonames data and sort according to priorities"""
        def is_ascii(s):
            try:
                s.encode(encoding='utf-8').decode('ascii')
            except UnicodeDecodeError:
                return False
            else:
                return True
        log.info('Reading geo data...')
        df = self.get_geonames_data()

        # Global filtering
        log.info('Reading feature class data...')
        df_features = self.get_feature_names_data()
        df = df.merge(df_features, on='feature_code', how='left')
        df.loc[df.geoname_id == '3355338', 'country_code'] = 'NA' # strangely, Namibia is missing the country_code
        # Apply the following filters:
        # - only keep places with feature class A (admin) and P (place), and CONT (continent)
        df = df[
                (df.feature_code_class.isin(['A', 'P'])) |
                (df.feature_code.isin(['CONT', 'RGN']))
                ]
        # - remove everything below min_population_cutoff
        df = df[
                (df['population'] > self.min_population_cutoff) |
                (df.feature_code.isin(['CONT', 'RGN']))
                ]
        # - get rid of items without a country code, usually administrative zones without country codes (e.g. "The Commonwealth")
        df = df[
                (~df.country_code.isnull()) |
                (df.feature_code.isin(['CONT', 'RGN']))
                ]
        # - remove certain administrative regions (such as zones, historical divisions, territories)
        df = df[~df.feature_code.isin(['ZN', 'PCLH', 'TERR'])]

        # Expansion of altnames
        df['official_name'] = df['name']
        # - expand alternate names
        df.loc[:, 'alternatenames'] = df.alternatenames.str.split(',')
        df['is_altname'] = False
        _df = df.explode('alternatenames')
        _df['name'] = _df['alternatenames']
        _df['is_altname'] = True
        df = pd.concat([df, _df])
        df = df.drop(columns=['alternatenames'])
        log.info(f'... read a total of {len(df):,} location names')

        # Filtering applied to names and altnames
        log.info('Apply filters...')
        # - remove all names that are floats/ints
        df['is_str'] = df.name.apply(lambda s: isinstance(s, str))
        df = df[df['is_str']]
        # - only allow 2 character names if 1) name is non-ascii (e.g. Chinese characters) 2) is an alternative name for a country (e.g. UK)
        #   3) is a US state or Canadian province
        df['is_country'] = df.feature_code.str.startswith('PCL')
        df['is_ascii'] = df.name.apply(is_ascii)
        # add "US" manually since it's missing in geonames
        row_usa = df[df.is_country & (df.name == 'USA')].iloc[0]
        row_usa['name'] = 'US'
        df = pd.concat([df, pd.DataFrame.from_records([row_usa])])
        df = df[
                (~df.is_ascii) |
                (df.name.str.len() > 2) |
                ((df.name.str.len() == 2) & (df.country_code == 'US')) |
                ((df.name.str.len() == 2) & (df.country_code == 'CA')) |
                ((df.name.str.len() == 2) & (df.is_country))
                ]
        # - altnames need to have at least 4 characters (removes e.g. 3-letter codes)
        df = df[~(
                    (~df.is_country) &
                    (~df.country_code.isin(['US', 'CA'])) &
                    (df.is_ascii) &
                    (df.is_altname) &
                    (df.name.str.len() < 4)
                    )]
        # - remove altnames of insignificant admin levels and of places that are very small
        # set admin level
        df['admin_level'] = None
        df.loc[df.feature_code.isin(['PCLI', 'PCLD', 'PCLF', 'PCLS', 'PCLIX', 'PCLX', 'PCL']), 'admin_level'] = 0
        for admin_level in range(1, 6):
            df.loc[df.feature_code.isin([f'ADM{admin_level}', f'ADM{admin_level}H']), 'admin_level'] = admin_level
        df = df[
                ~(
                    ((df.is_altname) & (df.admin_level.isin([3,4,5]))) |
                    ((df.is_altname) & (df.feature_code_class == 'P') & (df.population < 100000))
                    )
                ]

        # Add flags
        df_countries = df[(df.geoname_id.isin([str(v) for v in flags.values()])) & (~df.is_altname)].copy()
        for flag, geoname_id in flags.items():
            try:
                row = df_countries[(df_countries.geoname_id == str(geoname_id))].iloc[0].copy()
            except IndexError:
                pass
            else:
                row['name'] = flag
                df = pd.concat([df, pd.DataFrame.from_records([row])])

        # Sort by priorities and drop duplicate names
        # Priorities
        # 1) Large cities (population size > large_city_population_cutoff)
        # 2) States/provinces (admin_level == 1)
        # 3) Countries (admin_level = 0)
        # 4) Places
        # 5) counties (admin_level > 1)
        # 6) continents
        # 7) regions
        # (within each group we will sort according to population size)
        # Assigning priorities
        df['priority'] = np.nan
        df.loc[(df.feature_code == 'RGN'), 'priority'] = 7
        df.loc[(df.feature_code == 'CONT'), 'priority'] = 6
        df.loc[(df.feature_code_class == 'A') & (df.admin_level > 1), 'priority'] = 5
        df.loc[df.feature_code_class == 'P', 'priority'] = 4
        df.loc[(df.feature_code_class == 'A') & (df.admin_level == 0), 'priority'] = 3
        df.loc[(df.feature_code_class == 'A') & (df.admin_level == 1), 'priority'] = 2
        df.loc[(df.population > self.large_city_population_cutoff) & (df.feature_code_class == 'P') & (~df.is_altname), 'priority'] = 1
        # Sorting
        log.info('Sorting by priority...')
        df.sort_values(by=['priority', 'population'], ascending=[True, False], inplace=True)
        # set location_types
        df['location_type'] = np.nan
        for admin_level in range(1, 6):
            df.loc[df.admin_level == admin_level, 'location_type'] = f'admin{admin_level}'
        df.loc[df.feature_code == 'ADMD', 'location_type'] = 'admin_other'
        df.loc[df.admin_level == 0, 'location_type'] = 'country'
        df.loc[(df.population <= self.large_city_population_cutoff) & (df.feature_code_class == 'P'), 'location_type'] = 'place'
        df.loc[(df.population > self.large_city_population_cutoff) & (df.feature_code_class == 'P'), 'location_type'] = 'city'
        df.loc[df.feature_code == 'CONT', 'location_type'] = 'continent'
        df.loc[df.feature_code == 'RGN', 'location_type'] = 'region'
        if len(df[df.location_type.isna()]) > 0:
            log.warning(f'{len(df[df.location_type.isna()]):,} locations could not be matched to a location_type. These will be ignored.')
        # filter by user-defined location types
        df = df[df.location_type.isin(self.location_types)]
        location_types_counts = dict(df.location_type.value_counts())
        log.info(f'Collected a total of {len(df):,} location names. Breakdown by location types:')
        for loc_type, loc_type_count in location_types_counts.items():
            log.info(f'... type {loc_type}: {loc_type_count:,}')
        # Write as pickled list
        log.info(f'Writing geonames data to file {self.geonames_pickle_path}...')
        df = df[self.geo_data_field_names].values.tolist()
        with open(self.geonames_pickle_path, 'wb') as f:
            pickle.dump(df, f)
