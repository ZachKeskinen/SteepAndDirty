from pathlib import Path
import pandas as pd

from parsers import parse_boise, parse_cameron_pass, parse_fraser, parse_senator_beck

res = pd.DataFrame()

raw_dir = Path('SnowEx2021_TimeSeries_DepthTransects/raw')

parser = {'Boise River': parse_boise, 'Senator Beck': parse_senator_beck, \
          'Fraser': parse_fraser, 'Cameron Pass': parse_cameron_pass}

if __name__ == '__main__':

    for loc_dir in raw_dir.glob('*'):
    print(loc_dir)
    # if loc_dir.name != 'Cameron Pass':
    #     continue

    for date_dir in loc_dir.glob('*'):
        for fp in date_dir.joinpath('Depth Transects').glob('*'):
            df = parser[loc_dir.name](fp)
            df['date'] = pd.to_datetime(date_dir.name).strftime('%Y-%m-%d')
            df['Location'] = loc_dir.name
            # print(df['site'])
            res = pd.concat([res, df], ignore_index = True)
    
    res.to_csv('depths.csv')