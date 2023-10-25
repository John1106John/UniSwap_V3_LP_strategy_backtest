import json, math
import urllib.request
import pandas as pd
import os
import datetime
import time

URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

def graph(POOL_ID,fromdate):
    query = """
    query pools($pool_id: ID!, $fromdate: Int!) {
      poolHourDatas(where: { pool: $pool_id,periodStartUnix_gt: $fromdate},orderBy:periodStartUnix,orderDirection:asc,first:1000)
        {
        periodStartUnix
        liquidity
        high
        low
        pool{

            totalValueLockedUSD
            totalValueLockedToken1
            totalValueLockedToken0
            token0
                {decimals
                }
            token1
                {decimals
                }
            }
        close
        feeGrowthGlobal0X128
        feeGrowthGlobal1X128
        }
        }
    """
        # Query the subgraph
    req = urllib.request.Request(URL)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = {"query": query, "variables": {"pool_id": POOL_ID, "fromdate": fromdate}}
    jsondataasbytes = json.dumps(jsondata).encode('utf-8')
    req.add_header('Content-Length', len(jsondataasbytes))
    response = urllib.request.urlopen(req, jsondataasbytes)
    assert response.status == 200, "Bad response"

    data = json.load(response)
    poolHourDatas = data['data']['poolHourDatas']

    dpd = pd.json_normalize(poolHourDatas)
    dpd = dpd.astype(float)
    return dpd

def update(address):
    if os.path.isfile(address) :
        df = pd.read_csv(address)

    else :
        date_string = '1970-07-03 20:00:00'  # 西元格式日期和時間字符串
        # 轉換為 datetime 對象
        datetime_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        # 轉換為 UNIX 時間戳記
        timestamp = datetime_obj.timestamp()
        df = graph('0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',int(timestamp))  ##pool可換
        
    last_timestamp = df["periodStartUnix"].iloc[-1]   #資料最後一項時間

    current_timestamp = int(time.time())
    rounded_timestamp = current_timestamp - (current_timestamp % 3600)  #最接近的整點時間

    while int(last_timestamp) != int(rounded_timestamp) :
        new_df = graph('0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',int(last_timestamp))
        df = df.append(new_df)
        last_timestamp = df["periodStartUnix"].iloc[-1]   #資料最後一項時間
        
    df = df.loc[:,"periodStartUnix":]    
    df.to_csv(address)   
        

def filtered_data(data,start_date,end_date) :
    df = data
    datetime_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    start_timestamp = datetime_obj.timestamp()
    datetime_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    end_timestamp = datetime_obj.timestamp()
    filtered_df = df[(df['periodStartUnix'] >= start_timestamp) & (df['periodStartUnix'] <= end_timestamp)]
    filtered_df
    
