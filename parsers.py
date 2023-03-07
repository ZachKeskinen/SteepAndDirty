import numpy as np
import pandas as pd
import geopandas as gpd

def parse_boise(fp):
    
    if fp.suffix == '.xlsx':
        df = pd.read_excel(fp, index_col= 0, na_values = ['NR'])

        # data frames with easting/northing
        if 'Easting' in df.columns:
            # get relevant columns
            df = df[['Easting', 'Northing', 'UTM zone', 'Depth (cm)', 'Measurement Tool', 'Comments', 'Observer Name']]
            # make into UTM based geopandas dataframe
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Easting, df.Northing))
            gdf = gdf.set_crs(epsg = f"326{gdf['UTM zone'].iloc[0].strip('T')}")
            # convert to lat long to match
            gdf = gdf.to_crs('epsg:4326')
            # rename to match
            df = gdf.rename({'Depth (cm)': 'depth', 'Measurement Tool':'instrument', 'Comments':'comments', 'Observer Name': 'observer'}, axis = 1)
            df = df.drop(['Easting', 'Northing', 'UTM zone'], axis = 1)
            # remove date index
            df = df.reset_index(drop = True)
            df['site'] = fp.name.split('_')[0]

        # lat/long - in weird format
        else:
            # get rid of lines that don't have 1,2,3...
            first = df[~pd.to_numeric(df.index, errors = 'coerce').isna()]
            # get first 3 columns
            first = first.iloc[:, :3]
            # get second inset table
            second = df.iloc[:, 4:]
            # remove second inset table values that don't have 1,2,3...
            second = second[~pd.to_numeric(second.iloc[:, 0], errors = 'coerce').isna()].iloc[:,:3]
            # if values in second inset table then concat
            if len(second) > 0:
                df = pd.DataFrame(np.concatenate([first.values, second.values]), columns = ['depth', 'lon', 'lat'])
            # if nothing in firs then rename
            else:
                df = first
                df.columns = ['depth', 'lon', 'lat']
            # no comments, instrument for these ones.
            df['comments'] = np.nan
            df['instrument'] = np.nan
            # this format was all done by B. Minich
            df['observer'] = 'B. Minich'
            # remove erronous values in lat and long
            df = df[~pd.to_numeric(df.lat, errors = 'coerce').isna()]
            df = df[~pd.to_numeric(df.lon, errors = 'coerce').isna()]
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
            df = df.set_crs('EPSG:4326')
            df = df.drop(['lon','lat'], axis = 1)
            df['site'] = [s for s in fp.name.split('_') if 'ID' in s][0]

    # CSV files
    elif fp.suffix == '.csv':
        # read csv
        df = pd.read_csv(fp)
        # convert to gpd df
        df = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude))
        df = df.set_crs('EPSG:4326')
        # rename to match
        df = df.rename({'Depth': 'depth', 'MeasurementTool': 'instrument' , 'Comments':'comments' ,'ObserverName':'observer'}, axis = 1)
        # drop date index
        df = df.reset_index(drop = True)
        # drop unused columns
        df = df.drop(['Date','Time', 'Easting', 'Northing', 'Longitude', 'Latitude', 'UTMzone', 'DepthExtra'], axis = 1)
        df['site'] = fp.name[:6]
    
    else:
        raise ValueError(f'Failed to capture {fp}!')

    # remove values that can't be coerced to numeric
    df = df[~pd.to_numeric(df.depth, errors = 'coerce').isna()]
    # reorder to same order
    df = df[['site','depth','observer','instrument','comments', 'geometry']]
    df['state'] = 'ID'
    return df

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def parse_senator_beck(fp):
    header = pd.read_excel(fp)[:2]
    utm = header.iloc[0, 5]
    observers = header.columns[5]

    df = pd.read_excel(fp, skiprows = 3, index_col= 0)
    df = df[(~df.index.isna()) & (~df['UTM N'].isna()) & (df.index != 'WP')]
    # return df
    # make into UTM based geopandas dataframe
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['UTM E'], df['UTM N']))
    gdf = gdf.set_crs(epsg = f"326{utm.strip('S')}") 
    # convert to lat long to match
    gdf = gdf.to_crs('epsg:4326')
    gdf = gdf.rename({'Depth':'depth', 'Notes':'comments'}, axis = 1)
    # no instrument mentioned
    gdf['instrument'] = np.nan
    gdf['observer'] = observers
    # remove values that can't be coerced to numeric
    gdf = gdf[~pd.to_numeric(gdf.depth, errors = 'coerce').isna()]
    # reorder to same order
    df = gdf[['depth','observer','instrument','comments', 'geometry']]
    # remove waypoint index
    df = df.reset_index(drop = True)
    df['state'] = 'CO'

    return df

def parse_cameron_pass(fp):
    df = pd.read_excel(fp)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))
    gdf = gdf.set_crs('EPSG:4326')
    gdf = gdf.rename({'Depth':'depth','Depth (cm)':'depth', 'Measurement Tool':'instrument','Measurment Tool':'instrument' ,'Location':'comments', 'Description':'comments'}, axis = 1)
    gdf['observer'] = np.nan
    # remove values that can't be coerced to numeric
    gdf = gdf[~pd.to_numeric(gdf.depth, errors = 'coerce').isna()]
    # reorder to same order
    df = gdf[['depth','observer','instrument','comments', 'geometry']]
    # remove waypoint index
    df = df.reset_index(drop = True)
    # add site
    df['site'] = fp.stem.split('_')[1]
    df['state'] = 'CO'
    return df

def parse_fraser(fp):
    df = pd.read_excel(fp).iloc[1:]
    if 'Easting' in df.columns:
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Easting'], df['Northing']))
        gdf = gdf.set_crs(epsg = f"326{df['UTM zone'].iloc[2]}") 
        # convert to lat long to match
        gdf = gdf.to_crs('epsg:4326')
        # rename columns
        gdf = gdf.rename({'Depth': 'depth', 'Measurement Tool': 'instrument' , 'Comments':'comments' ,'Observer Name':'observer'}, axis = 1)
        # remove values that can't be coerced to numeric
        gdf = gdf[~pd.to_numeric(gdf.depth, errors = 'coerce').isna()]
        # reorder to same order
        df = gdf[['depth','observer','instrument','comments', 'geometry']]
        # remove waypoint index
        df = df.reset_index(drop = True)
        df['site'] = fp.stem.split('_')[-1]
        df['state'] = 'CO'
        return df
    else:
        # check to be sure it is just this one file with no coordinates and then ignore
        assert fp.name == '20210203 Radar 2.xlsx'
        return gpd.GeoDataFrame(columns = ['depth','observer','instrument','comments', 'geometry', 'site', 'state'], crs = 'EPSG:4326')