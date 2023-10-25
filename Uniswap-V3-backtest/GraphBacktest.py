import json, math
import urllib.request
import pandas as pd

URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

def graph(POOL_ID,fromdate):
    query = """
    query pools($pool_id: ID!, $fromdate: Int!) {
      poolHourDatas(where: { pool: $pool_id,periodStartUnix_gt: $fromdate},orderBy:periodStartUnix,orderDirection:desc,first:1000)
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

