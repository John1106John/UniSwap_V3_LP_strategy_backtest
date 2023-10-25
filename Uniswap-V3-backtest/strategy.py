#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def my_strategy(df,start_date,end_date):
    ##strategy計算
    # 計算布林帶的中軌、上軌和下軌
    period = 14  # 布林帶期間大小
    df["SMA"] = df["close"].rolling(period).mean()
    df["std"] = df["close"].rolling(period).std()
    df["upper_band"] = df["SMA"] + 2 * df["std"]
    df["lower_band"] = df["SMA"] - 2 * df["std"]
    df["BB%B"] = (df["close"] - df["lower_band"]) / (df["upper_band"] - df["lower_band"])
    overbought_threshold = 1
    oversold_threshold = 0
    df["position"] = None
     
    buy = {}  
    sell = [] 
    
    # 遍歷每一天的數據
    for i in range(2, len(df)):
        if df.loc[df.index[i-2], "BB%B"] <= oversold_threshold and df.loc[df.index[i-1], "BB%B"] > oversold_threshold :
            if df.loc[df.index[i-1], "position"] is None: 
                df.loc[df.index[i]:,"position"] = "long"
                stop_ls  = df.loc[df.index[i-1],"SMA"] - 3 * df.loc[df.index[i-1],"std"]
                stop_pt  = df.loc[df.index[i-1],"SMA"] + 3 * df.loc[df.index[i-1],"std"]  
                buy[df.index[i]] = (stop_ls, stop_pt)
                             
        if df.loc[df.index[i-1], "position"] == "long":
            
            if df.loc[df.index[i-1], "close"] <= stop_ls or df.loc[df.index[i-1], "close"] >= stop_pt :  
                df.loc[df.index[i]:,"position"] = None
                sell.append(df.index[i]) 
    
            else :
                # 超買反轉時賣出
                if df.loc[df.index[i-2], "BB%B"] >= overbought_threshold and df.loc[df.index[i-1], "BB%B"] < overbought_threshold : 
                    df.loc[df.index[i]:,"position"] = None
                    sell.append(df.index[i])

  
    return df, buy, sell

