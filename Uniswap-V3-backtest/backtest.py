#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import liquidity
import GraphBacktest
import charts
import get_data
import strategy as st


def uniswap_backtest_ETH(start_date,end_date,mini,maxi,target,hold_target):
    pool = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8" # ETH USDC Ethereum
    base = 0
    
    file_path = ".\\" + "graph" + ".csv"
    #get_data.update(file_path)    #更新資料
    data = pd.read_csv(file_path)
    
    filtered_data = get_data.filtered_data(data,start_date,end_date)
    price_data = filtered_data.copy()
    filtered_data = filtered_data[::-1]
    dpd = filtered_data.reset_index(drop=True)
    price_data = price_data.reset_index(drop=True)
    
    decimal0=dpd.iloc[0]['pool.token0.decimals']
    decimal1=dpd.iloc[0]['pool.token1.decimals']
    decimal=decimal1-decimal0
    dpd['fg0']=((dpd['feeGrowthGlobal0X128'])/(2**128))/(10**decimal0)
    dpd['fg1']=((dpd['feeGrowthGlobal1X128'])/(2**128))/(10**decimal1)

    #Calculate F0G and F1G (fee earned by an unbounded unit of liquidity in one period)

    dpd['fg0shift']=dpd['fg0'].shift(-1)
    dpd['fg1shift']=dpd['fg1'].shift(-1)
    dpd['fee0token']=dpd['fg0']-dpd['fg0shift'] 
    dpd['fee1token']=dpd['fg1']-dpd['fg1shift']

    # calculate my liquidity

    SMIN=np.sqrt(mini* 10 ** (decimal))   
    SMAX=np.sqrt(maxi* 10 ** (decimal))  

    if base == 0:
        price0 = dpd['open'].iloc[-1]
        
        sqrt0 = np.sqrt(dpd['open'].iloc[-1]* 10 ** (decimal))
        dpd['price0'] = dpd['open']

    else:
        price0 = 1/dpd['open'].iloc[-1]
        
        sqrt0= np.sqrt(1/dpd['open'].iloc[-1]* 10 ** (decimal))
        dpd['price0']= 1/dpd['open']

    if sqrt0>SMIN and sqrt0<SMAX:

            deltaL = target / ((sqrt0 - SMIN)  + (((1 / sqrt0) - (1 / SMAX)) * (dpd['price0'].iloc[-1]* 10 ** (decimal))))
            amount1 = deltaL * (sqrt0-SMIN)
            amount0 = deltaL * ((1/sqrt0)-(1/SMAX))* 10 ** (decimal)

    elif sqrt0<SMIN:

            deltaL = target / (((1 / SMIN) - (1 / SMAX)) * (dpd['price0'].iloc[-1]))
            amount1 = 0
            amount0 = deltaL * (( 1/SMIN ) - ( 1/SMAX ))

    else:
            deltaL = target / (SMAX-SMIN) 
            amount1 = deltaL * (SMAX-SMIN)
            amount0 = 0


    #print("Amounts:",amount0,amount1)

    #print(dpd['price0'].iloc[-1],mini,maxi)
    #print((dpd['price0'].iloc[-1],mini,maxi,amount0,amount1,decimal0,decimal1))
    myliquidity = liquidity.get_liquidity(dpd['price0'].iloc[-1],mini,maxi,amount0,amount1,decimal0,decimal1)

    #print("OK myliquidity",myliquidity)

    # Calculate ActiveLiq

    dpd['ActiveLiq'] = 0
    dpd['amount0'] = 0
    dpd['amount1'] = 0
    dpd['amount0unb'] = 0
    dpd['amount1unb'] = 0

    if base == 0:

        for i, row in dpd.iterrows():
            if dpd['high'].iloc[i]>mini and dpd['low'].iloc[i]<maxi:
                if dpd['high'].iloc[i]-dpd['low'].iloc[i] == 0:
                    dpd.iloc[i,dpd.columns.get_loc('ActiveLiq')] = 100
                else :
                    dpd.iloc[i,dpd.columns.get_loc('ActiveLiq')] = (min(maxi,dpd['high'].iloc[i]) - max(dpd['low'].iloc[i],mini)) / (dpd['high'].iloc[i]-dpd['low'].iloc[i]) * 100
            else:
                dpd.iloc[i,dpd.columns.get_loc('ActiveLiq')] = 0

            amounts= liquidity.get_amounts(dpd['price0'].iloc[i],mini,maxi,myliquidity,decimal0,decimal1)
            dpd.iloc[i,dpd.columns.get_loc('amount0')] = amounts[1]
            dpd.iloc[i,dpd.columns.get_loc('amount1')]  = amounts[0]

            amountsunb= liquidity.get_amounts((dpd['price0'].iloc[i]),1.0001**(-887220),1.0001**887220,1,decimal0,decimal1)
            dpd.iloc[i,dpd.columns.get_loc('amount0unb')] = amountsunb[1]
            dpd.iloc[i,dpd.columns.get_loc('amount1unb')] = amountsunb[0]
       

    else:

        for i, row in dpd.iterrows():

            if (1/ dpd['low'].iloc[i])>mini and (1/dpd['high'].iloc[i])<maxi:
                if (1/dpd['low'].iloc[i])-(1/dpd['high'].iloc[i]) == 0:
                    dpd.iloc[i,dpd.columns.get_loc('ActiveLiq')] = 100
                else :
                    dpd.iloc[i,dpd.columns.get_loc('ActiveLiq')] = (min(maxi,1/dpd['low'].iloc[i]) - max(1/dpd['high'].iloc[i],mini)) / ((1/dpd['low'].iloc[i])-(1/dpd['high'].iloc[i])) * 100
            else:
                dpd.iloc[i,dpd.columns.get_loc('ActiveLiq')] = 0

            amounts= liquidity.get_amounts((dpd['price0'].iloc[i]*10**(decimal)),mini,maxi,myliquidity,decimal0,decimal1)
            dpd.iloc[i,dpd.columns.get_loc('amount0')] = amounts[0]
            dpd.iloc[i,dpd.columns.get_loc('amount1')] = amounts[1]

            amountsunb= liquidity.get_amounts((dpd['price0'].iloc[i]),1.0001**(-887220),1.0001**887220,1,decimal0,decimal1)
            dpd.iloc[i,dpd.columns.get_loc('amount0unb')] = amountsunb[0]
            dpd.iloc[i,dpd.columns.get_loc('amount1unb')] = amountsunb[1]



    ## Final fee calculation

    dpd['myfee0'] = dpd['fee0token'] * myliquidity * dpd['ActiveLiq'] / 100
    dpd['myfee1'] = dpd['fee1token'] * myliquidity * dpd['ActiveLiq'] / 100
    
    
    #print(dpd)
   
    
    return charts.chart1(dpd,base,myliquidity,hold_target,price0)

def filtering_data(start_date,end_date):
    #獲得資料
    file_path = ".\\" + "graph" + ".csv"
    #get_data.update(file_path)    #更新資料
    data = pd.read_csv(file_path)
    data = data.copy()
    filtered_data = get_data.filtered_data(data,start_date,end_date)
    df = filtered_data.reset_index(drop=True)
    
    df['date']=pd.to_datetime(df['periodStartUnix'],unit='s')
    df.index = df["date"]
    df.index = pd.to_datetime(df.index)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    df = df.resample('D',on = "date").last()
    
    return df

def range_backtest(start_date,end_date,target_0,investment_method="compound_interest"):
    if investment_method == "compound_interest":
        target = target_0
        df, buy, sell = st.my_strategy(filtering_data(start_date,end_date),start_date,end_date)
        buy_index = list(buy.keys())
        important_sheets = pd.DataFrame()
        hold_target = target
        cumulative_feeV = 0
        for i in range(len(buy)):
            open_position = str(buy_index[i])
            close_position = str(sell[i])
            mini,maxi = buy[buy_index[i]]
            pair_value, total_value, important_sheet = uniswap_backtest_ETH(open_position,close_position,mini,maxi,target,hold_target)
            target = total_value[-1]
            hold_target = important_sheet["hold_strategy_value"].iloc[-1]
            cumulative_feeV += important_sheet["cumulative_feeV"].iloc[-1]
            important_sheets =  pd.concat([important_sheets,important_sheet])  
        #return strategy_return,buy,sell
        lp_return = (target - target_0) / target_0
        fee_return = cumulative_feeV / target_0
        
        important_sheets = important_sheets.resample('D').fillna(None)
        important_sheets["close"] = filtering_data(start_date,end_date)["close"]
        important_sheets['pair_value'].fillna(method='ffill', inplace=True)
        important_sheets['total_value'].fillna(method='ffill', inplace=True)
        important_sheets['hold_strategy_value'].fillna(method='ffill', inplace=True)
        
        important_sheets.to_csv("important_sheets.csv")
        return important_sheets, fee_return

    
    else :
        target = target_0
        df, buy, sell = st.my_strategy(filtering_data(start_date,end_date),start_date,end_date)
        buy_index = list(buy.keys())
        important_sheets = pd.DataFrame()
        hold_target = target
        cumulative_feeV = 0
        for i in range(len(buy)):
            open_position = str(buy_index[i])
            close_position = str(sell[i])
            mini,maxi = buy[buy_index[i]]
            pair_value, total_value, important_sheet = uniswap_backtest_ETH(open_position,close_position,mini,maxi,target,hold_target)
            target = pair_value[-1]
            hold_target = important_sheet["hold_strategy_value"].iloc[-1]
            cumulative_feeV += important_sheet["cumulative_feeV"].iloc[-1]
            important_sheets =  pd.concat([important_sheets,important_sheet])
        #return strategy_return,buy,sell
        lp_return = (target - target_0) / target_0
        fee_return = cumulative_feeV / target_0
        
        important_sheets = important_sheets.resample('D').fillna(None)
        important_sheets["close"] = filtering_data(start_date,end_date)["close"]
        important_sheets['pair_value'].fillna(method='ffill', inplace=True)
        important_sheets['total_value'].fillna(method='ffill', inplace=True)
        important_sheets['hold_strategy_value'].fillna(method='ffill', inplace=True)
        
        important_sheets.to_csv("important_sheets.csv")
        return important_sheets, fee_return

def analyze(df,target_0):
    
    total_return = (df.iloc[-1] - target_0 )/ target_0
    num_years = len(df) / 365  
    annualized_return = (1 + total_return) ** (1 / num_years) - 1

    df['daily_returns'] = df.pct_change()
    std_dev = df['daily_returns'].std()
    annualized_std_dev = std_dev * np.sqrt(365)
    total_std_dev = std_dev * np.sqrt(len(df))
    
    # 計算最大回檔
    cum_returns = (1 + df['daily_returns']).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    max_drawdown = drawdown.min()

    # 計算夏普比率
    risk_free_rate = 0.02  # 假設無風險利率
    excess_returns = annualized_return - risk_free_rate
    sharpe_ratio = excess_returns / annualized_std_dev

    # 計算索提諾比率
    downside_returns = df['daily_returns'][df['daily_returns'] < 0]
    sortino_ratio = excess_returns.mean() / downside_returns.std()

    # 顯示結果
    print(f"總收益:{total_return * 100 :.2f}%")
    print(f"年化標準差：{annualized_std_dev * 100 :.2f}%")
    print(f"最大回檔：{max_drawdown * 100 :.2f}%")
    print(f"夏普比率：{sharpe_ratio:.2f}")
    print(f"索提諾比率：{sortino_ratio:.2f}")

def show_analysis(important_sheets,target_0,fee_return,investment_method="compound_interest"):
    print("------分析結果------")
    PNL = important_sheets["PNL"].sum()
    IL = important_sheets["IL_change"].sum()
    print(f"投資金額 : {target_0}")
    print(f"PNL : {PNL}")
    print(f"IL : {IL}")
    print(f"手續費收入 : {fee_return * target_0}")
    print(f"手續費報酬率 : {fee_return*100:.2f}%")
    if investment_method == "compound_interest":
        analyze(important_sheets["total_value"],target_0)
    else :
        print("註記:以下為幣對分析，不含手續費")
        analyze(important_sheets["pair_value"],target_0)
        
    print("===========================================")
    print("純持有策略分析")
    analyze(important_sheets["hold_strategy_value"],target_0)
    


