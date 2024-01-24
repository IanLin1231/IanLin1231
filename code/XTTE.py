import shioaji as sj
from consql import SQL_DATA
import pandas as pd
from talib.abstract import RSI, MACD, EMA, SMA, ATR 
import talib 
from datetime import datetime, timedelta
from consql import SQL_DATA_DAIL

'''
api = sj.Shioaji(simulation=True) # 模擬模式
api.login(
         api_key="6tdnA3hAbKMHtGWNY5pfd6fHrCyUXbP47KN5wUcsuwhL",     # 請修改此處
         secret_key="6wmG6ufQ6djzt18FFSZ4rq1JyZANq6CRyruULnfaHr4V",   # 請修改此處
         contracts_timeout=10000,
         #contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
         )
'''

# 初始資料函數
def RSI_data(data):
    #相對強弱指數:一種動量指標，評估股價價格變動，判斷股票是超買還是超賣。
    data['rsi1'] = RSI(data, timeperiod=120)
    data['rsi2'] = RSI(data, timeperiod=150)
    return data
def MACD_data(data):
    #移動平均收斂擴散指標:一種趨勢跟踪動量指標，顯示兩個移動平均線之間的關係。
    data = data.join(MACD(data, 40, 120, 60))
    return data    
def MA_data(data):
    #加權移動平均線，對最近的數據點給予更多權重。
    data['ema']=EMA(data,timeperiod=120)
    return data    
def Bollinger_data(data):
    #布林通道:衡量市場波動性，一條中央移動平均線和兩條與標準差。
    window = 20  # 布林通道的窗口大小
    std_dev = 2  # 布林通道的標準差倍數
    data['MA'] = data['close'].rolling(window).mean()  # 中軌
    data['Upper'] = data['MA'] + std_dev * data['close'].rolling(window).std()  # 上軌
    data['Lower'] = data['MA'] - std_dev * data['close'].rolling(window).std()  # 下軌
    return data
def MA_array_data(data):
    #簡單移動平均線（SMA），這是一種跟踪資產價格平均值
    data['ma1'] = SMA(data, timeperiod=90)
    data['ma2'] = SMA(data, timeperiod=120)
    data['ma3'] = SMA(data, timeperiod=150)
    return data

def MA_ATR_data(data):
    #指數移動平均線（EMA）和平均真實範圍（ATR）
    data['ema'] = EMA(data, timeperiod=80) #EMA是80天的周期，提供了對價格趨勢的權重評估。
    data['atr1'] = ATR(data, timeperiod=120) #ATR指標用120和200天的平均真實範圍衡量市場波動性
    data['atr2'] = ATR(data, timeperiod=200)
    return data   
def rollBack_data(data):
    data['rsi']=RSI(data,timeperiod=10)
    # 相對強弱指數一種動量指標，用於評估股價的最近價格變動。
    #over_buy=80
    #over_sell=40
    # 這裡可以設置超買和超賣的閾值，例如80和40
    return data
def MACD_SMA_data(data): # 移動平均收斂擴散指標（MACD）和簡單移動平均線（SMA）
    data['macd'], data['macdsignal'], data['macdhist'] = MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    # 12天快速周期、26天慢速周期和9天信號線周期
    data['sma5'] = SMA(data['close'], timeperiod=5)
    # 5天和10天周期的SMA，這有助於分析短期價格趨勢
    data['sma10'] = SMA(data['close'], timeperiod=10)
    return data
def RSI_MACD_SMA_data(data):
    # 計算兩個不同時間週期的相對強弱指數（RSI）值
    data['rsi6'] = RSI(data['close'], timeperiod=6)  # 6日RSI，短期市場趨勢的動量指標
    data['rsi12'] = RSI(data['close'], timeperiod=12) # 12日RSI，相對長期的市場趨勢動量指標

    # 計算移動平均收斂擴散指標（MACD）
    data['macd'], data['macdsignal'], _ = MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    # 這裡的MACD使用12天快速移動平均線和26天慢速移動平均線，以及9天的信號線

    # 計算簡單移動平均線（SMA）
    data['sma5'] = SMA(data['close'], timeperiod=5)  # 5日SMA，用於分析短期價格趨勢
    data['sma10'] = SMA(data['close'], timeperiod=10) # 10日SMA，用於分析中期價格趨勢

    return data
def KD_data(data):
    # 計算隨機震盪指標（Stochastic Oscillator），簡稱KD指標
    data['k'], data['d'] = talib.STOCH(data['high'], data['low'], data['close'],
                                       fastk_period=9, slowk_period=3, slowd_period=3)
    # 使用9天的快速K線週期、3天的慢速K線和D線週期，這是一種動量指標，用於識別超買和超賣信號

    return data
def PQ_data(data):
    # 計算簡單移動平均線（SMA）
    data['sma5'] = SMA(data['close'], timeperiod=5)  # 5日SMA
    data['sma20'] = SMA(data['close'], timeperiod=20) # 20日SMA

    # 計算成交量增加的指標
    data['vol_increase'] = data['volume'].diff() > 0  # 檢查當日成交量是否比前一日多，用於評估市場活躍度

    return data
def Turtle_data(data):
    # 計算平均真實範圍（ATR），用於海龜交易系統
    data['ATR'] = ATR(data, timeperiod=14)  # 使用14天的ATR

    # 計算滾動窗口的最高價和最低價
    data['20d_high'] = data['close'].rolling(window=20).max()  # 20天的最高價
    data['10d_low'] = data['close'].rolling(window=10).min()   # 10天的最低價
    data['55d_high'] = data['close'].rolling(window=55).max()  # 55天的最高價
    data['20d_low'] = data['close'].rolling(window=20).min()   # 20天的最低價

    return data
#+++++++++++++++++++++++++++++++++++++++++++++++++
#RSI進場
def rsi_entry_trade(data, position, api, contract):
    c_rsi1 = data['rsi1']
    c_rsi2 = data['rsi2']
    n_open = data['close']
    indicators = []
    #if position == 0 and c_rsi1 > c_rsi2:
    if position == 0:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
        print("下單")
    return position, indicators

def macd_entry_logic(data, position, api, contract):
    # 如果MACD柱狀圖大於0，且目前無持倉，則生成進場信號
    c_macd = data['macdhist']
    n_time= data['date']
    n_open = data['close']
    indicators = []
    if position == 0 and c_macd > 0:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators
    
def ma_entry_logic(data, position, api, contract): #如果收盤價高於EMA的1.01倍，且目前無持倉，則生成進場信號
    c_close = data['close']
    c_ema = data['ema']
    n_open = data['close']
    indicators = []
    if position == 0 and c_close > c_ema * 1.01:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def bollinger_entry_logic(data, position, api, contract):
    # 如果收盤價高於下軌且開盤價低於下軌，且目前無持倉，則生成進場信號
    c_close = data['close']
    c_open = data['open']
    c_lower = data['Lower']
    n_open = data['close']
    indicators = []
    if position == 0 and c_close > c_lower and c_open < c_lower:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators
    
def ma_array_entry_logic(data, position, api, contract):
    # 如果短期SMA高於中期SMA且中期SMA高於長期SMA，且目前無持倉，則生成進場信號
    c_ma1 = data['ma1']
    c_ma2 = data['ma2']
    c_ma3 = data['ma3']
    n_open = data['close']
    indicators = []
    if position == 0 and c_ma1 > c_ma2 > c_ma3:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def ma_atr_entry_logic(data, position, api, contract):
    # 如果收盤價高於EMA 1.01倍且短期ATR大於長期ATR，且目前無持倉，則生成進場信號
    c_close = data['close']
    c_ema = data['ema']
    c_atr1 = data['atr1']
    c_atr2 = data['atr2']
    n_open = data['close']
    indicators = []
    if position == 0 and c_close > c_ema * 1.01 and c_atr1 > c_atr2:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def rollback_entry_logic(data, position, api, contract,rsi_min, rsi_min_time):
    # 當RSI低於超賣閾值並在短期內反彈時，生成進場信號
    c_rsi = data['rsi']
    over_sell = 40
    n_open = data['close']
    n_time= data['date']
    indicators = []
    if c_rsi < over_sell:
    # 檢查RSI是否低於超賣閾值
        if rsi_min > c_rsi:
        # 如果當前RSI低於之前記錄的最低RSI，更新最低RSI值和對應時間
            rsi_min = c_rsi
            rsi_min_time = n_time
            
    if n_time <= rsi_min_time + 3 and c_rsi > rsi_min + 10:
    #檢查是否出現反彈，如果自最低RSI值記錄以來（不超過3天），RSI值反彈超過10點，則生成進場信號
        rsi_min = 100
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
        
    return position, indicators, rsi_min, rsi_min_time

def macd_sma_entry_logic(data, position, api, contract):
    # 當MACD高於信號線且短期SMA高於長期SMA時，生成進場信號
    c_macd = data['macd']
    c_macdsignal = data['macdsignal']
    c_sma5 = data['sma5']
    c_sma10 = data['sma10']
    n_open = data['close']
    indicators = []
    if position == 0 and c_macd > c_macdsignal and c_sma5 > c_sma10:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def rsi_macd_sma_entry_logic(data, position, api, contract):
    # 這種進場策略旨在捕捉多個技術指標同時顯示強勢的情況
    # 當短期RSI高於長期RSI，MACD高於其信號線，且短期SMA高於長期SMA時，生成進場信號
    c_rsi_short = data['rsi6']
    c_rsi_long = data['rsi12']
    c_macd = data['macd']
    c_macdsignal = data['macdsignal']
    c_sma5 = data['sma5']
    c_sma10 = data['sma10']
    n_open = data['close']
    
    indicators = []

    if position == 0 and c_rsi_short > c_rsi_long and c_macd > c_macdsignal and c_sma5 > c_sma10:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def kd_entry_logic(data, position, api, contract):
    # 當K線超過D線時，生成進場信號
    c_k = data['k']
    c_d = data['d']
    n_open = data['close']
    indicators = []
    if position == 0 and c_k > c_d:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def pq_entry_logic(data, position, api, contract):
    # 如果目前無持倉，且當日收盤價高於5日和20日SMA，且當日成交量有所增加，則生成進場信號
    c_close = data['close']
    c_sma5 = data['sma5']
    c_sma20 = data['sma20']
    vol_increase = data['vol_increase']
    n_open = data['close']
    indicators = []
    if position == 0 and c_close > c_sma5 and c_close > c_sma20 and vol_increase:
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def turtle_entry_logic(data, position, api, contract):
    # 如果目前無持倉且當日最高價超過20天或55天的最高價，則生成進場信號
    c_20d_high = data['20d_high']
    c_55d_high = data['55d_high']
    n_open = data['close']
    indicators = []
    if position == 0 and (data['high'] > c_20d_high or data['high'] > c_55d_high):
        position = 1
        print("滿足進場條件，生成並執行訂單")
        order = create_buy_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({  
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '買入',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators
#+++++++++++++++++++++++++++++++++++++++++++++++++        
#創建委託單並'買入'
def create_buy_order(api,contract,n_open):
    print("開始購買")
    n_open = n_open.iloc[-1]
    print(n_open)
    order = api.Order(
        price=n_open+0.87, 
        quantity=1, 
        action=sj.constant.Action.Buy, 
        price_type=sj.constant.StockPriceType.LMT, 
        order_type=sj.constant.OrderType.ROD, 
        order_lot=sj.constant.StockOrderLot.Common, 
        # daytrade_short=False,
        custom_field="test",
        account=api.stock_account
    )
    return order
#+++++++++++++++++++++++++++++++++++++++++++++++++
#創建委託單並'賣出'
def create_sell_order(api, contract,n_open):
    n_open = n_open.iloc[-1]
    order = api.Order(
        price=n_open-0.87,  # 設定適當的價格
        quantity=1,
        action=sj.constant.Action.Sell,  # 設定為賣出動作
        price_type=sj.constant.StockPriceType.LMT,
        order_type=sj.constant.OrderType.ROD,
        order_lot=sj.constant.StockOrderLot.Common,
        custom_field="test",
        account=api.stock_account
    )
    return order
#+++++++++++++++++++++++++++++++++++++++++++++++++
#RSI出場
def rsi_exit_trade(data, position, api, contract):
    print("開始出場")
    c_rsi1 = data['rsi1']
    c_rsi2 = data['rsi2']
    n_open = data['close']
    indicators = []
    #if position == 1 and c_rsi1 < c_rsi2 * 0.999:
    if position == 1:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        }) 
        print("下單")
    return position, indicators
def macd_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且MACD柱狀圖值下降至-0.005以下
    c_macd = data['macdhist']
    n_open = data['close']
    indicators = []
    if position == 1 and c_macd < -0.005:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators
    
def ma_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且收盤價低於EMA的99.5%
    c_close = data['close']
    c_ema = data['ema']
    n_open = data['close']
    indicators = []
    if position == 1 and c_close < c_ema * 0.995:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def bollinger_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且收盤價低於布林通道上軌而開盤價高於上軌
    c_close = data['close']
    c_open = data['open']
    c_upper = data['Upper']
    n_open = data['close']
    rsi_min = 100
    rsi_min_time = 0
    indicators = []
    if position == 1 and c_close < c_upper and c_open > c_upper:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators
    
def ma_array_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且短期SMA不再高於中期和長期SMA
    c_ma1 = data['ma1']
    c_ma2 = data['ma2']
    c_ma3 = data['ma3']
    n_open = data['close']
    indicators = []
    if position == 1 and not (c_ma1 > c_ma2 > c_ma3):
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def ma_atr_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且收盤價低於EMA的99.5%
    c_close = data['close']
    c_ema = data['ema']
    n_open = data['close']
    indicators = []
    if position == 1 and c_close < c_ema * 0.995:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def rollback_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且RSI值超過80（超買狀態）
    c_rsi = data['rsi']
    over_buy = 80
    n_open = data['close']
    indicators = []
    
    if position == 1 and c_rsi > over_buy:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
        
    return position, indicators

def macd_sma_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且MACD值低於其信號線或5日SMA低於10日SMA
    c_macd = data['macd']
    c_macdsignal = data['macdsignal']
    c_sma5 = data['sma5']
    c_sma10 = data['sma10']
    n_open = data['close']
    indicators = []
    if position == 1 and (c_macd < c_macdsignal or c_sma5 < c_sma10):
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def rsi_macd_sma_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且期RSI低於長期RSI或MACD低於其信號線或短期SMA低於長期SMA
    c_rsi_short = data['rsi6']  # 6 日 RSI
    c_rsi_long = data['rsi12']  # 12 日 RSI
    c_macd = data['macd']
    c_macdsignal = data['macdsignal']
    c_sma5 = data['sma5']
    c_sma10 = data['sma10']
    n_open = data['close']
    indicators = []

    if position == 1 and (c_rsi_short < c_rsi_long or c_macd < c_macdsignal or c_sma5 < c_sma10):
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def kd_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且K線值低於D線值
    c_k = data['k']
    c_d = data['d']
    n_open = data['close']
    indicators = []
    if position == 1 and c_k < c_d:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators

def pq_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且收盤價低於5日SMA
    c_close = data['close']
    c_sma5 = data['sma5']
    n_open = data['close']
    indicators = []
    
    if position == 1 and c_close < c_sma5:
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators


def turtle_exit_logic(data, position, api, contract):
    # 條件是當前持倉為1（持有），且當日的最低價低於過去10天或20天的最低價
    c_10d_low = data['10d_low']
    c_20d_low = data['20d_low']
    n_open = data['close']
    indicators = []
    if position == 1 and (data['low'] < c_10d_low or data['low'] < c_20d_low):
        position = 0
        print(" 滿足出場條件，生成並執行賣出訂單")
        order = create_sell_order(api, contract, n_open)
        trade = api.place_order(contract, order)
        trades = api.list_trades()
        latest_trade = trades[-1] if trades else None
        deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
        deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
        indicators.append({
            '委託時間: ' : latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            '成交時間: ' : deal_time,
            '委託書號: ' : latest_trade.order.id,
            '買賣: ' : '賣出',
            '原委託: ' : str(latest_trade.order.quantity),
            '已成交: ' : str(latest_trade.status.deal_quantity),
            '委託狀態: ' : str(latest_trade.status.status),
            '委託價: ' : str(latest_trade.order.price),
            '成交價: ' : deal_prices
        })
    return position, indicators
#+++++++++++++++++++++++++++++++++++++++++++++++++
# 交易紀錄函數
def record_trade(trade, indicators, prod):
    new_trade_data_list = []
    
    # 处理買入指标
    for ind in indicators:
        
        order_time_str = ind.get('委託時間: ')
        if order_time_str and order_time_str != '未成交':
            order_time = datetime.strptime(order_time_str, '%Y-%m-%d %H:%M:%S')
        else:
            order_time = None
        
        # 處理委託價
        order_price_str = ind.get('委託價: ')
        if order_price_str and order_price_str != '未成交':
            order_price = float(order_price_str)
        else:
            order_price = None
            
         # 處理成交时间
        deal_time_str = ind.get('成交時間: ')
        if deal_time_str and deal_time_str != '未成交':
            deal_time = datetime.strptime(deal_time_str, '%Y-%m-%d %H:%M:%S')
        else:
            deal_time = None
         # 處理成交價
        deal_prices_str = ind.get('成交價: ')
        if deal_prices_str and deal_prices_str != '未成交':
            deal_prices = [float(price.strip()) for price in deal_prices_str.split(',') if price.strip().isdigit()]
        else:
            deal_prices = None
            
        original_quantity = int(ind.get('原委託: ', '0'))
        deal_quantity = int(ind.get('已成交: ', '0'))
        status = ind.get('委託狀態: ')
        
        # 新增買入交易數據
        new_trade_data = pd.Series([
            prod,
            'Buy',
            order_time,
            order_price,
            deal_time,# 成交时间
            deal_prices, # 成交价
            original_quantity,# 原委托数量
            deal_quantity, # 已成交数量
            status, # 委托状态
        ])
        
        new_trade_data_list.append(new_trade_data)
    
    # 處理卖出指标
    for ind in indicators:

        # 處理成交时间
        deal_time_str = ind.get('成交時間: ')
        if deal_time_str and deal_time_str != '未成交':
            deal_time = datetime.strptime(deal_time_str, '%Y-%m-%d %H:%M:%S')
        else:
            deal_time = None

        # 處理成交價
        deal_prices_str = ind.get('成交價: ')
        if deal_prices_str and deal_prices_str != '未成交':
            deal_prices = [float(price.strip()) for price in deal_prices_str.split(',') if price.strip().isdigit()]
        else:
            deal_prices = None

        # 處理其他交易數據
        original_quantity = int(ind.get('原委託: ', '0'))
        deal_quantity = int(ind.get('已成交: ', '0'))
        status = ind.get('委託狀態: ')

        # 新增賣出交易數據
        new_trade_data = pd.Series([
            prod,
            'Sell',
            order_time,# 委托时间
            order_price,# 委托价
            deal_time,
            deal_prices,
            original_quantity,
            deal_quantity,
            status,
        ])
        
        new_trade_data_list.append(new_trade_data)
    
    if new_trade_data_list:
        trade = pd.concat([trade, pd.DataFrame(new_trade_data_list)], ignore_index=True)
        
    return trade
#+++++++++++++++++++++++++++++++++++++++++++++++++
def NewData(api,prod):
   
    snapshots = api.snapshots([api.Contracts.Stocks[prod]])

    df = pd.DataFrame(s.__dict__ for s in snapshots)
    df.ts = pd.to_datetime(df.ts)
    df = df.rename(columns={'code':'stock_id','ts':'date','volume':'Volume','amount':'volume','total_volume':'turnover'})
    df = df[['date','stock_id', 'open', 'high', 'low', 'close','volume','turnover']]
    print(df)
    return df

#+++++++++++++++++++++++++++++++++++++++++++++++++
def trade_main(api, prod, firstTime, entry_strategy, exit_strategy, extra_days=200):
    shape_data=NewData(api,prod)
    SQL_DATA_DAIL(shape_data)
    new_firstTime = datetime.strptime(firstTime, '%Y-%m-%d') - timedelta(days=extra_days)
    new_firstTime = new_firstTime.strftime('%Y-%m-%d')
    data = SQL_DATA(prod, new_firstTime, firstTime)
    trade = pd.DataFrame() 
    #需要的資料

     # 獲取所有需要的資料
    data_rsi = RSI_data(data.copy())
    data_macd = MACD_data(data.copy())
     
    data_ma = MA_data(data.copy())
    data_bollinger = Bollinger_data(data.copy())
     
    data_ma_array = MA_array_data(data.copy())
    data_ma_atr = MA_ATR_data(data.copy())
     
    data_rollBack = rollBack_data(data.copy())

     
    data_MACD_SMA = MACD_SMA_data(data.copy())
    data_RSI_MACD_SMA = RSI_MACD_SMA_data(data.copy())
    data_kd = KD_data(data.copy())
    data_pq = PQ_data(data.copy())
    data_turtle = Turtle_data(data.copy())


    if entry_strategy == 'RSI':
        entry_data=data_rsi
    elif entry_strategy == 'MACD':
        entry_data=data_macd
    elif entry_strategy == '突破均線策略':
        entry_data=data_ma
    elif entry_strategy == '布林函數':
        entry_data=data_bollinger
    elif entry_strategy == '均線排列策略':
        entry_data=data_ma_array
    elif entry_strategy == 'MA+ATR濾網交易策略':
        entry_data=data_ma_atr
    elif entry_strategy == '強勢回檔策略':
        entry_data=data_rollBack
    elif entry_strategy == 'MACD+SMA':
        entry_data=data_MACD_SMA
    elif entry_strategy == 'RSI+MACD+SMA':
        entry_data=data_RSI_MACD_SMA
    elif entry_strategy == 'KD':
        entry_data=data_kd
    elif entry_strategy == 'PQ':
        entry_data=data_pq
    elif exit_strategy == '海龜':
        entry_data=data_turtle


    # 出場邏輯
    if exit_strategy == 'RSI':
        exit_data=data_rsi
    elif exit_strategy == 'MACD':
        entry_data=data_macd
    elif exit_strategy == '突破均線策略':
        entry_data=data_ma
    elif exit_strategy == '布林函數':
        entry_data=data_bollinger
    elif exit_strategy == '均線排列策略':
        entry_data=data_ma_array
    elif exit_strategy == 'MA+ATR濾網交易策略':
        entry_data=data_ma_atr
    elif exit_strategy == '強勢回檔策略':
        entry_data=data_rollBack,
    elif exit_strategy == 'MACD+SMA':
        entry_data=data_MACD_SMA
    elif exit_strategy == 'RSI+MACD+SMA':
        entry_data=data_RSI_MACD_SMA
    elif exit_strategy == 'KD':
        entry_data=data_kd
    elif exit_strategy == 'PQ':
        entry_data=data_pq
    elif exit_strategy == '海龜':
        entry_data=data_turtle   
        
        
        


    return(entry_data,exit_data)





accumulated_data = pd.DataFrame()
accumulated_trade_df = pd.DataFrame()
accumulated_indicators = []

# 在程序开始时运行
'''
prod="0050"
#trade = pd.DataFrame()        
contract = api.Contracts.Stocks[prod]
indicators = [] 
new_indicators=[]
oldposition = 0
a=0
b=0
firstTime = '2023-12-21'
entry_strategy = 'RSI'
exit_strategy = 'RSI'
position = '0'

b,data, trade_df, indicators = trade_main(api, contract, prod, firstTime, entry_strategy, exit_strategy, oldposition, indicators, new_indicators)
'''
'''   
def scheduled_task(api, contract, prod, firstTime, end_date, entry_strategy, exit_strategy, position, indicators, new_indicators):
    current_date = datetime.now().date()
    if current_date <= datetime.strptime(end_date, "%Y-%m-%d").date():
        df = NewData(api, prod, contract)
        SQL_DATA_DAIL(df)
        main(api, contract, prod, firstTime, entry_strategy, exit_strategy, position, indicators, new_indicators)
        
        # 获得下一个交易日
        next_firstTime = get_next_trading_day(current_date, end_date)
        if next_firstTime:
            return next_firstTime
    return firstTime

def start_scheduled_task(api, contract, prod, start_date, end_date, entry_strategy, exit_strategy, position, indicators, new_indicators):
    firstTime = start_date
    schedule.every().day.at("17:02").do(scheduled_task, api, contract, prod, firstTime, end_date, entry_strategy, exit_strategy, position, indicators, new_indicators)

    while True:
        schedule.run_pending()
        time.sleep(1)
'''


'''
#輸出狀態
trades = api.list_trades()
latest_trade = trades[-1] if trades else None
txt = (
        '交易所: ' + str(trade.contract.exchange) + '\n' +
        '商品代號: ' + trade.contract.code + '\n' +
        '商品名稱: ' + trade.contract.name + '\n' +
        '單位: ' + str(trade.contract.unit) + '\n' +
        '漲停價: ' + str(trade.contract.limit_up) + '\n' +
        '跌停價: ' + str(trade.contract.limit_down) + '\n' +
        '參考價: ' + str(trade.contract.reference) + '\n' +
        '更新日期: ' + trade.contract.update_date + '\n'
        )
if latest_trade:
    deal_prices = ", ".join([str(deal.price) for deal in latest_trade.status.deals]) if latest_trade.status.deals else "未成交"
    deal_time = latest_trade.status.order_datetime.fromtimestamp(latest_trade.status.deals[0].ts).strftime('%Y-%m-%d %H:%M:%S') if latest_trade.status.deals else "未成交"
    latest_trade_txt = (
            '委託時間: ' + latest_trade.status.order_datetime.strftime('%Y-%m-%d %H:%M:%S') + '\n' +
            '成交時間: ' + deal_time + '\n' +
            '委託書號: ' + latest_trade.order.id + '\n' +
            '買賣: ' + ('買入' if latest_trade.order.action == sj.constant.Action.Buy else '賣出') + '\n' +
            '原委託: ' + str(latest_trade.order.quantity) + '\n' +
            '已成交: ' + str(latest_trade.status.deal_quantity) + '\n' +
            '委託狀態: ' + str(latest_trade.status.status) + '\n' +
            '委託價: ' + str(latest_trade.order.price) + '\n' +
            '成交價: ' + deal_prices + '\n'
        )
    print(latest_trade_txt)
else:
    no_trade_txt = "沒有交易記錄"
    print(no_trade_txt)
'''

