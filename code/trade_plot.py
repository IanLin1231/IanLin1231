from consql import SQL_DATA
import pandas as pd
import mplfinance as mpf
from talib.abstract import RSI, MACD, EMA, SMA, ATR 
import talib 
from datetime import datetime, timedelta
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

# 進場邏輯函數
def rsi_entry_logic(data, i, position):
    # 如果RSI1大於RSI2，且目前無持倉，則生成進場信號
    c_rsi1 = data.loc[data.index[i], 'rsi1']
    c_rsi2 = data.loc[data.index[i], 'rsi2']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_rsi1 > c_rsi2:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
        
    return position, indicators

def macd_entry_logic(data, i, position):
    # 如果MACD柱狀圖大於0，且目前無持倉，則生成進場信號
    c_macd = data.loc[data.index[i], 'macdhist']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_macd > 0:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators
    
def ma_entry_logic(data, i, position): #如果收盤價高於EMA的1.01倍，且目前無持倉，則生成進場信號
    c_close = data.loc[data.index[i], 'close']
    c_ema = data.loc[data.index[i], 'ema']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_close > c_ema * 1.01:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators

def bollinger_entry_logic(data, i, position):
    # 如果收盤價高於下軌且開盤價低於下軌，且目前無持倉，則生成進場信號
    c_close = data.loc[data.index[i], 'close']
    c_open = data.loc[data.index[i], 'open']
    c_lower = data.loc[data.index[i], 'Lower']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_close > c_lower and c_open < c_lower:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators
    
def ma_array_entry_logic(data, i, position):
    # 如果短期SMA高於中期SMA且中期SMA高於長期SMA，且目前無持倉，則生成進場信號
    c_ma1 = data.loc[data.index[i], 'ma1']
    c_ma2 = data.loc[data.index[i], 'ma2']
    c_ma3 = data.loc[data.index[i], 'ma3']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_ma1 > c_ma2 > c_ma3:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators

def ma_atr_entry_logic(data, i, position):
    # 如果收盤價高於EMA 1.01倍且短期ATR大於長期ATR，且目前無持倉，則生成進場信號
    c_close = data.loc[data.index[i], 'close']
    c_ema = data.loc[data.index[i], 'ema']
    c_atr1 = data.loc[data.index[i], 'atr1']
    c_atr2 = data.loc[data.index[i], 'atr2']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_close > c_ema * 1.01 and c_atr1 > c_atr2:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators

def rollback_entry_logic(data, i, position, rsi_min, rsi_min_time):
    # 當RSI低於超賣閾值並在短期內反彈時，生成進場信號
    c_rsi = data.loc[data.index[i], 'rsi']
    over_sell = 40
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if c_rsi < over_sell:
    # 檢查RSI是否低於超賣閾值
        if rsi_min > c_rsi:
        # 如果當前RSI低於之前記錄的最低RSI，更新最低RSI值和對應時間
            rsi_min = c_rsi
            rsi_min_time = i
            
    if i <= rsi_min_time + 3 and c_rsi > rsi_min + 10:
    #檢查是否出現反彈，如果自最低RSI值記錄以來（不超過3天），RSI值反彈超過10點，則生成進場信號
        rsi_min = 100
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
        
    return position, indicators, rsi_min, rsi_min_time

def macd_sma_entry_logic(data, i, position):
    # 當MACD高於信號線且短期SMA高於長期SMA時，生成進場信號
    c_macd = data.loc[data.index[i], 'macd']
    c_macdsignal = data.loc[data.index[i], 'macdsignal']
    c_sma5 = data.loc[data.index[i], 'sma5']
    c_sma10 = data.loc[data.index[i], 'sma10']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_macd > c_macdsignal and c_sma5 > c_sma10:
        position = 1
        indicators.append({'type': '進場', 'c_time': data.loc[data.index[i], 'date'], 'order_time': n_time, 'order_price': n_open, 'order_unit': 1})
    return position, indicators

def rsi_macd_sma_entry_logic(data, i, position):
    # 這種進場策略旨在捕捉多個技術指標同時顯示強勢的情況
    # 當短期RSI高於長期RSI，MACD高於其信號線，且短期SMA高於長期SMA時，生成進場信號
    c_rsi_short = data.loc[data.index[i], 'rsi6']
    c_rsi_long = data.loc[data.index[i], 'rsi12']
    c_macd = data.loc[data.index[i], 'macd']
    c_macdsignal = data.loc[data.index[i], 'macdsignal']
    c_sma5 = data.loc[data.index[i], 'sma5']
    c_sma10 = data.loc[data.index[i], 'sma10']

    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []

    if position == 0 and c_rsi_short > c_rsi_long and c_macd > c_macdsignal and c_sma5 > c_sma10:
        position = 1
        indicators.append({
            'type': '進場',
           'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators

def kd_entry_logic(data, i, position):
    # 當K線超過D線時，生成進場信號
    c_k = data.loc[data.index[i], 'k']
    c_d = data.loc[data.index[i], 'd']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_k > c_d:
        position = 1
        indicators.append({'type': '進場','c_time': data.loc[data.index[i], 'date'] , 'order_time': n_time, 'order_price': n_open, 'order_unit': 1})
    return position, indicators

def pq_entry_logic(data, i, position):
    # 如果目前無持倉，且當日收盤價高於5日和20日SMA，且當日成交量有所增加，則生成進場信號
    c_close = data.loc[data.index[i], 'close']
    c_sma5 = data.loc[data.index[i], 'sma5']
    c_sma20 = data.loc[data.index[i], 'sma20']
    vol_increase = data.loc[data.index[i], 'vol_increase']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and c_close > c_sma5 and c_close > c_sma20 and vol_increase:
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1
        })
    return position, indicators

def turtle_entry_logic(data, i, position):
    # 如果目前無持倉且當日最高價超過20天或55天的最高價，則生成進場信號
    c_20d_high = data.loc[data.index[i], '20d_high']
    c_55d_high = data.loc[data.index[i], '55d_high']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 and (data.loc[data.index[i], 'high'] > c_20d_high or data.loc[data.index[i], 'high'] > c_55d_high):
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1  # 或根據ATR調整倉位大小
        })
    return position, indicators

# 出場邏輯函數
def rsi_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且較長時間週期的RSI低於較短時間週期的RSI的99.9%
    c_rsi1 = data.loc[data.index[i], 'rsi1']
    c_rsi2 = data.loc[data.index[i], 'rsi2']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and c_rsi1 < c_rsi2 * 0.999:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators

def macd_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且MACD柱狀圖值下降至-0.005以下
    c_macd = data.loc[data.index[i], 'macdhist']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and c_macd < -0.005:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators
    
def ma_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且收盤價低於EMA的99.5%
    c_close = data.loc[data.index[i], 'close']
    c_ema = data.loc[data.index[i], 'ema']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and c_close < c_ema * 0.995:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators

def bollinger_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且收盤價低於布林通道上軌而開盤價高於上軌
    c_close = data.loc[data.index[i], 'close']
    c_open = data.loc[data.index[i], 'open']
    c_upper = data.loc[data.index[i], 'Upper']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and c_close < c_upper and c_open > c_upper:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators
    
def ma_array_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且短期SMA不再高於中期和長期SMA
    c_ma1 = data.loc[data.index[i], 'ma1']
    c_ma2 = data.loc[data.index[i], 'ma2']
    c_ma3 = data.loc[data.index[i], 'ma3']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and not (c_ma1 > c_ma2 > c_ma3):
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators

def ma_atr_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且收盤價低於EMA的99.5%
    c_close = data.loc[data.index[i], 'close']
    c_ema = data.loc[data.index[i], 'ema']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and c_close < c_ema * 0.995:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators

def rollback_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且RSI值超過80（超買狀態）
    c_rsi = data.loc[data.index[i], 'rsi']
    over_buy = 80
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    
    if position == 1 and c_rsi > over_buy:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
        
    return position, indicators

def macd_sma_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且MACD值低於其信號線或5日SMA低於10日SMA
    c_macd = data.loc[data.index[i], 'macd']
    c_macdsignal = data.loc[data.index[i], 'macdsignal']
    c_sma5 = data.loc[data.index[i], 'sma5']
    c_sma10 = data.loc[data.index[i], 'sma10']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and (c_macd < c_macdsignal or c_sma5 < c_sma10):
        position = 0
        indicators.append({'type': '出場', 'c_time': data.loc[data.index[i], 'date'], 'cover_time': n_time, 'cover_price': n_open})
    return position, indicators

def rsi_macd_sma_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且期RSI低於長期RSI或MACD低於其信號線或短期SMA低於長期SMA
    c_rsi_short = data.loc[data.index[i], 'rsi6']  # 6 日 RSI
    c_rsi_long = data.loc[data.index[i], 'rsi12']  # 12 日 RSI
    c_macd = data.loc[data.index[i], 'macd']
    c_macdsignal = data.loc[data.index[i], 'macdsignal']
    c_sma5 = data.loc[data.index[i], 'sma5']
    c_sma10 = data.loc[data.index[i], 'sma10']

    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []

    if position == 1 and (c_rsi_short < c_rsi_long or c_macd < c_macdsignal or c_sma5 < c_sma10):
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators

def kd_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且K線值低於D線值
    c_k = data.loc[data.index[i], 'k']
    c_d = data.loc[data.index[i], 'd']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and c_k < c_d:
        position = 0
        indicators.append({'type': '出場', 'c_time': data.loc[data.index[i], 'date'], 'cover_time': n_time, 'cover_price': n_open})
    return position, indicators

def pq_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且收盤價低於5日SMA
    c_close = data.loc[data.index[i], 'close']
    c_sma5 = data.loc[data.index[i], 'sma5']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    
    if position == 1 and c_close < c_sma5:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators


def turtle_exit_logic(data, i, position):
    # 條件是當前持倉為1（持有），且當日的最低價低於過去10天或20天的最低價
    c_10d_low = data.loc[data.index[i], '10d_low']
    c_20d_low = data.loc[data.index[i], '20d_low']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 1 and (data.loc[data.index[i], 'low'] < c_10d_low or data.loc[data.index[i], 'low'] < c_20d_low):
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators

# 交易紀錄函數
def record_trade(trade, indicators, prod):
    new_trade_data_list = []
    
    for ind in indicators:
        order_unit = ind.get('order_unit', 1)  # 假設默認的 order_unit 是 1
        if ind['type'] == '進場':
            new_trade_data = pd.Series([
                prod,
                'Buy',
                ind['order_time'],
                ind['order_price'],
                None,  # cover_time 為 None
                None,  # cover_price 為 None
                order_unit
            ])
        elif ind['type'] == '出場':
            new_trade_data = pd.Series([
                prod,
                'Sell',
                ind['cover_time'],  # 這裡用 cover_time
                ind['cover_price'],  # 這裡用 cover_price
                None,  # order_time 為 None
                None,  # order_price 為 None
                order_unit
            ])
        
        new_trade_data_list.append(new_trade_data)
    
    if new_trade_data_list:
        trade = pd.concat([trade, pd.DataFrame(new_trade_data_list)], ignore_index=True)
    #print(new_trade_data_list)   
    return trade

def text_entry_logic(data, i, position):
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if position == 0 :
        position = 1
        indicators.append({
            'type': '進場',
            'c_time': data.loc[data.index[i], 'date'],
            'order_time': n_time,
            'order_price': n_open,
            'order_unit': 1  # 或根據ATR調整倉位大小
        })
    return position, indicators

# 出場邏輯函數
def text_exit_logic(data, i, position):
    t_open = data.loc[data.index[i], 'open']
    n_time= data.loc[data.index[i+1], 'date']
    n_open = data.loc[data.index[i+1], 'open']
    indicators = []
    if (position == 1 and t_open<n_open) or position == 3:
        position = 0
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[i], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    return position, indicators
# 主函數
def main(prod, firstTime, endTime, entry_strategy, exit_strategy, extra_days=200):
    SQL_DATA(prod, firstTime, endTime)
    new_firstTime = datetime.strptime(firstTime, '%Y-%m-%d') - timedelta(days=extra_days)
    new_firstTime = new_firstTime.strftime('%Y-%m-%d')
    data = SQL_DATA(prod, new_firstTime, endTime)
    
    position = 0
    trade = pd.DataFrame()

    # 獲取所有需要的資料
    data_rsi = RSI_data(data.copy())
    data_macd = MACD_data(data.copy())
    
    data_ma = MA_data(data.copy())
    data_bollinger = Bollinger_data(data.copy())
    
    data_ma_array = MA_array_data(data.copy())
    data_ma_atr = MA_ATR_data(data.copy())
    
    data_rollBack = rollBack_data(data.copy())
    rsi_min = 100
    rsi_min_time = 0
    
    data_MACD_SMA = MACD_SMA_data(data.copy())
    data_RSI_MACD_SMA = RSI_MACD_SMA_data(data.copy())
    data_kd = KD_data(data.copy())
    data_pq = PQ_data(data.copy())
    data_turtle = Turtle_data(data.copy())
    


    indicators = []
    new_indicators=[]
    
    for i in range(len(data) - 3):
        
        current_date = data.loc[data.index[i], 'date']
        if firstTime <= current_date <= endTime:
        # 進場邏輯
            if entry_strategy == 'RSI':
                position, new_indicators = rsi_entry_logic(data_rsi, i, position)
            elif entry_strategy == 'MACD':
                position, new_indicators = macd_entry_logic(data_macd, i, position)
            elif entry_strategy == '突破均線策略':
                position, new_indicators = ma_entry_logic(data_ma, i, position)
            elif entry_strategy == '布林函數':
                position, new_indicators = bollinger_entry_logic(data_bollinger, i, position)
            elif entry_strategy == '均線排列策略':
                position, new_indicators = ma_array_entry_logic(data_ma_array, i, position)
            elif entry_strategy == 'MA+ATR濾網交易策略':
                position, new_indicators = ma_atr_entry_logic(data_ma_atr, i, position)
            elif entry_strategy == '強勢回檔策略':
                position, new_indicators, rsi_min, rsi_min_time = rollback_entry_logic(data_rollBack, i, position, rsi_min, rsi_min_time)
            elif entry_strategy == 'MACD+SMA':
                position, new_indicators = macd_sma_entry_logic(data_MACD_SMA, i, position)
            elif entry_strategy == 'RSI+MACD+SMA':
                position, new_indicators = rsi_macd_sma_entry_logic(data_RSI_MACD_SMA, i, position)
            elif entry_strategy == 'KD':
                position, new_indicators = kd_entry_logic(data_kd, i, position)
            elif entry_strategy == 'PQ':
                position, new_indicators = pq_entry_logic(data_pq, i, position)
            elif exit_strategy == '海龜':
                position, new_indicators = turtle_entry_logic(data_turtle, i, position)
            elif exit_strategy == 'TEXT':
                position, new_indicators = text_entry_logic(data_turtle, i, position)
            indicators.extend(new_indicators)
        

            # 出場邏輯
            if exit_strategy == 'RSI':
                position, new_indicators = rsi_exit_logic(data_rsi, i, position)
            elif exit_strategy == 'MACD':
                position, new_indicators = macd_exit_logic(data_macd, i, position)
            elif exit_strategy == '突破均線策略':
                position, new_indicators = ma_exit_logic(data_ma, i, position)
            elif exit_strategy == '布林函數':
                position, new_indicators = bollinger_exit_logic(data_bollinger, i, position)
            elif exit_strategy == '均線排列策略':
                position, new_indicators = ma_array_exit_logic(data_ma_array, i, position)
            elif exit_strategy == 'MA+ATR濾網交易策略':
                position, new_indicators = ma_atr_exit_logic(data_ma_atr, i, position)
            elif exit_strategy == '強勢回檔策略':
                position, new_indicators = rollback_exit_logic(data_rollBack, i, position)
            elif exit_strategy == 'MACD+SMA':
                position, new_indicators = macd_sma_exit_logic(data_MACD_SMA, i, position)
            elif exit_strategy == 'RSI+MACD+SMA':
                position, new_indicators = rsi_macd_sma_exit_logic(data_RSI_MACD_SMA, i, position)
            elif exit_strategy == 'KD':
                position, new_indicators = kd_exit_logic(data_kd, i, position)
            elif exit_strategy == 'PQ':
                position, new_indicators = pq_exit_logic(data_pq, i, position)
            elif exit_strategy == '海龜':
                position, new_indicators = turtle_exit_logic(data_turtle, i, position)
            elif exit_strategy == 'TEXT':
                position, new_indicators = text_exit_logic(data_turtle, i, position)
            indicators.extend(new_indicators)
        
    if position==1:
        n_time= data.loc[data.index[-1], 'date']
        n_open = data.loc[data.index[-1], 'open']
        indicators.append({
            'type': '出場',
            'c_time': data.loc[data.index[-2], 'date'],
            'cover_time': n_time,
            'cover_price': n_open
        })
    


    trade = record_trade(trade, indicators, prod)
    #print('a',trade)    
    # Initialize an empty DataFrame
    trade_df = pd.DataFrame()


    combined_records = []
    for i in range(0, len(trade) - 1, 2):  # 注意這裡是 len(trade) - 1
        buy_row = trade.iloc[i]
        if i + 1 < len(trade):  # 檢查索引是否超出範圍
            sell_row = trade.iloc[i + 1]
    
    # Create a new combined record
        combined_record = {
            "prod": buy_row[0],
            'Buy': buy_row[1],
            "order_time": buy_row[2],
            "order_price": buy_row[3],
            "cover_time": sell_row[2],
            "cover_price": sell_row[3],
            "order_unit": "1"
        }
        combined_records.append(combined_record)

    trade_df = pd.DataFrame(combined_records)
    #print('b',trade_df)
    return (data,trade_df,indicators)


# 使用示例
prod = '0050'
firstTime = '2007-01-01'
endTime = '2022-09-01'
entry_strategy="RSI"
exit_strategy="RSI"
dataU, trade_dfU, indicatorsU = main(prod, firstTime, endTime, entry_strategy, exit_strategy)
'''
def mainaa(prod, todayTime, endTime, entry_strategy, exit_strategy):
    data = 及時
    
    position = 0
    trade = pd.DataFrame()

    # 獲取所有需要的資料
    data_rsi = RSI_data(data.copy())
    data_macd = MACD_data(data.copy())
    
    data_ma = MA_data(data.copy())
    data_bollinger = Bollinger_data(data.copy())
    
    data_ma_array = MA_array_data(data.copy())
    data_ma_atr = MA_ATR_data(data.copy())
    
    data_rollBack = rollBack_data(data.copy())
    rsi_min = 100
    rsi_min_time = 0
    
    data_MACD_SMA = MACD_SMA_data(data.copy())
    data_RSI_MACD_SMA = RSI_MACD_SMA_data(data.copy())
    data_kd = KD_data(data.copy())
    data_pq = PQ_data(data.copy())
    data_turtle = Turtle_data(data.copy())
    


    indicators = []
    new_indicators=[]
    
    for i in range(len(data) - 1):
        
        # 進場邏輯
        if entry_strategy == 'RIS':
            position, new_indicators = rsi_entry_logic(data_rsi, i, position)
        elif entry_strategy == 'MACD':
            position, new_indicators = macd_entry_logic(data_macd, i, position)
        elif entry_strategy == '突破均線策略':
            position, new_indicators = ma_entry_logic(data_ma, i, position)
        elif entry_strategy == '布林函數':
            position, new_indicators = bollinger_entry_logic(data_bollinger, i, position)
        elif entry_strategy == '均線排列策略':
            position, new_indicators = ma_array_entry_logic(data_ma_array, i, position)
        elif entry_strategy == 'MA+ATR濾網交易策略':
            position, new_indicators = ma_atr_entry_logic(data_ma_atr, i, position)
        elif entry_strategy == '強勢回檔策略':
            position, new_indicators, rsi_min, rsi_min_time = rollback_entry_logic(data_rollBack, i, position, rsi_min, rsi_min_time)
        elif entry_strategy == 'MACD+SMA':
            position, new_indicators = macd_sma_entry_logic(data_MACD_SMA, i, position)
        elif entry_strategy == 'RSI+MACD+SMA':
            position, new_indicators = rsi_macd_sma_entry_logic(data_RSI_MACD_SMA, i, position)
        elif entry_strategy == 'KD':
            position, new_indicators = kd_entry_logic(data_kd, i, position)
        elif entry_strategy == 'PQ':
            position, new_indicators = pq_entry_logic(data_pq, i, position)
        elif exit_strategy == '海龜':
            position, new_indicators = turtle_entry_logic(data_turtle, i, position)
        indicators.extend(new_indicators)
        

        # 出場邏輯
        if exit_strategy == 'RIS':
            position, new_indicators = rsi_exit_logic(data_rsi, i, position)
        elif exit_strategy == 'MACD':
            position, new_indicators = macd_exit_logic(data_macd, i, position)
        elif exit_strategy == '突破均線策略':
            position, new_indicators = ma_exit_logic(data_ma, i, position)
        elif exit_strategy == '布林函數':
            position, new_indicators = bollinger_exit_logic(data_bollinger, i, position)
        elif exit_strategy == '均線排列策略':
            position, new_indicators = ma_array_exit_logic(data_ma_array, i, position)
        elif exit_strategy == 'MA+ATR濾網交易策略':
            position, new_indicators = ma_atr_exit_logic(data_ma_atr, i, position)
        elif exit_strategy == '強勢回檔策略':
            position, new_indicators = rollback_exit_logic(data_rollBack, i, position)
        elif exit_strategy == 'MACD+SMA':
            position, new_indicators = macd_sma_exit_logic(data_MACD_SMA, i, position)
        elif exit_strategy == 'RSI+MACD+SMA':
            position, new_indicators = rsi_macd_sma_exit_logic(data_RSI_MACD_SMA, i, position)
        elif exit_strategy == 'KD':
            position, new_indicators = kd_exit_logic(data_kd, i, position)
        elif exit_strategy == 'PQ':
            position, new_indicators = pq_exit_logic(data_pq, i, position)
        elif exit_strategy == '海龜':
            position, new_indicators = turtle_exit_logic(data_turtle, i, position)
        indicators.extend(new_indicators)
    
    trade = record_trade(trade, indicators, prod)
        
    # Initialize an empty DataFrame
    trade_df = pd.DataFrame()


    combined_records = []
    for i in range(0, len(trade) - 1, 2):  # 注意這裡是 len(trade) - 1
        buy_row = trade.iloc[i]
        if i + 1 < len(trade):  # 檢查索引是否超出範圍
            sell_row = trade.iloc[i + 1]
    
    #for i in range(0, len(trade), 2):
     #   buy_row = trade.iloc[i]
    #    sell_row = trade.iloc[i + 1]
    
    # Create a new combined record
        combined_record = {
            "prod": buy_row[0],
            'Buy': buy_row[1],
            "order_time": buy_row[2],
            "order_price": buy_row[3],
            "cover_time": sell_row[2],
            "cover_price": sell_row[3],
            "order_unit": "1"
        }
        combined_records.append(combined_record)
    
    trade_df = pd.DataFrame(combined_records)
    #Performance(trade_df,'ETF')
    #ChartTrade(data,trade_df,indicators)
    if(endTime==todayTime):
        return (data,trade_df,indicators)
    else:
        return(mainaa(prod, todayTime+1, endTime, entry_strategy, exit_strategy))
    #trade_df.to_csv('7878.csv', index=False)
    #indicators_df = pd.DataFrame(indicators)
    #indicators_df.to_csv('indicators1.csv', index=False)
'''