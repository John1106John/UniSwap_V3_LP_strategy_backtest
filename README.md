# UniSwap_V3_LP_strategy_backtest

## 回測邏輯說明
按照策略根據價格所設定的買入賣出時機，提供流動性(在開倉時就提供流動性區間)，賺取手續費，並將手續費一同投入(也可以不將手續費投入)。  
可以分析該策略提供流動性的收益、標準差、夏普值等等。  
可以分析該策略的PNL(如果只是持有幣對，純粹幣對上漲下跌的收益量)，IL(因提供流動性，相對持有的損失，總和必為負值)，手續費收入(因提供流動性賺取的手續費收入)  

也可以比較同樣策略，並按照開倉時比例的持有策略(不提供流動性)的各項指標(較不重要，可忽略)  

## 操作說明
1. **編輯strategy.py(請閱讀下方說明)**
2. 自由更改main.py的參數
3. 執行main.py(需等待約15秒)，將會有 分析結果(直接顯示)、important_sheets(檔案)，其解釋於下方段落說明

### 關於strategy.py編輯方式:
你必須在這裡寫下你的策略，該策略須包含，買入賣出訊號、提供流動性區間，可以參考我寫好的策略。  
請編輯my_strategy函數，其函數會自動引入價格資料(df)，資料index為日期(日資料)，欄位包含但不僅限於'high', 'low', 'close'。  
可以根據自己的策略找出買入賣出訊號!  
ps : 賣出可以考慮停損停利，如我寫的方式。  

**請注意buy、sell的格式!!!**
buy 格式為類似dictionary的格式，key值為買入時機，value為(mini,maxi)，mini為流動性區間低點， maxi為流動性區間高點。ps : 我的策略區間設為和停損停利相同，實際上可以自由設定!
sell 格式為list，賣出時機  

### 關於main.py的參數 :
只有四個參數，基本上可以不用改
start_date = '2021-08-01 00:00:00'
end_date = '2023-07-31 00:00:00'
target = 1000 #初始投入金額(USDC)
investment_method = "compound_interest"

investment_method為投資方式，有兩種模式，"compound_interest"和"simple_interest"，"compound_interest"指的是每次提供流動性獲得的手續費和本金一起投入下一次的提供流動性，而"simple_interest"則是只投入本金
基本上用"compound_interest"即可

## 輸出結果解釋
如果直接跑程式會有以下輸出  
投資金額 : 1000   
PNL : -132.04085018893886           #該值代表幣對如果不提供流動性，按照開倉比例持有的總收益(損失)  
IL : -416.19179200712756            #相對持有，提供流動性的幣對數量變化所造成的總損失  
手續費收入 : 387.94421300465996      #提供流動性賺到的手續費 PS:比較IL是挺有意義的  
手續費報酬率 : 38.79%  
總收益:-16.03%                      #沒有年化  
年化標準差：35.55%                   #時間總長度為第一次開倉到最後一次平倉時間，實際值應該會更小  
最大回檔：-53.72%  
夏普比率：-0.32  
索提諾比率：-4.91                    #可能是錯的  

純持有策略分析  
總收益:-13.43%  
年化標準差：33.95%  
最大回檔：-51.67%  
夏普比率：-0.29  
索提諾比率：-5.01  
  
PS : 純持有策略分析，應該不是很重要，可以忽略，以下解釋也可以忽略  
純持有策略和PNL計算，所使用的策略完全不同  
純持有策略指的是，按照和LP一樣的買入賣出時間點，按照同樣幣對比例分配，計算持有價值，並投入下一次的買入賣出  
而PNL是，按照和LP一樣的買入賣出時間點，按照同樣幣對比例分配，但每次的投入金額是上次LP的總價值(包含幣對以及手續費)  

## 輸出檔案(important_sheets)解釋
important_sheets.csv會自動匯出  
可以觀察欄位變化，也可檢查是否算錯  
  
以下為部分欄位說明  
"close" : 收盤價  
"pair_value" :幣對價值(USDC計價，未開倉時維持不變)  
"total_value" : 總價值(USDC計價) = 幣對價值 + 累積手續費，未開倉時維持不變，並且為下次投入的金額(compound_interest方式)  
"hold_value_compare": 以上次平倉total_value的價值，持有和LP一樣的幣對比例，的價值，用來計算PNL，IL  
"hold_strategy_value" :　純持有策略的價值，單獨計算若是都是按照LP投入的幣對比例進行投資的價值(買入賣出時間點一樣)  
"amount0" : USDC數量  
"amount" : ETH數量  
"cumulative_feeV" : 累積手續費(USDC計價)  
"PNL" : "hold_value_compare" 的價值變化  
"IL_change" : IL的變化量，可能為正數，IL是pair_value - hold_value_compare，必為負
 


