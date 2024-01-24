from spider import getDataFM
import pymysql
import pandas as pd

def SQL_DATA(prod, start_time, end_time):
    con = {"host": "140.137.41.140", "port": 3306, "user": "username", "password": "password", "db": "stock_data", "charset": "utf8"}
    try:
        conn = pymysql.connect(**con)
        with conn.cursor() as cursor:
            # 檢查指定日期範圍內的數據是否存在
            cursor.execute("SELECT COUNT(*) FROM shares WHERE stock_id = %s AND date >= %s AND date <= %s", (prod, start_time, end_time))
            count = cursor.fetchone()[0]


            # 如果數據不存在，則調用 getDataFM
            if count == 0:
                data = getDataFM(prod, start_time, end_time)
                command = "INSERT INTO shares(date,stock_id,open,high,low,close,volume,turnover) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                for index, row in data.iterrows():
                    print(index)
                    cursor.execute(command, tuple(row))
                    conn.commit()
                    data = pd.read_sql(f"SELECT * FROM shares WHERE stock_id = '{prod}' AND date >= '{start_time}' AND date <= '{end_time}' ORDER BY date ASC", conn)
            else:
                # 數據已存在，從資料庫讀取數據
                data = pd.read_sql(f"SELECT * FROM shares WHERE stock_id = '{prod}' AND date >= '{start_time}' AND date <= '{end_time}' ORDER BY date ASC", conn)
                # 整理資料庫的資料
                organize="SELECT * FROM shares ORDER BY stock_id ASC, date ASC"
                cursor.execute(organize)
            
            return data
                
    except Exception as e:
        print("發生錯誤：", e)
    finally:
        if conn:
            conn.close()

def SQL_DATA_DAIL(dataframe):
    con = {"host": "140.137.41.140", "port": 3306, "user": "username", "password": "password", "db": "stock_data", "charset": "utf8"}
    try:
        conn = pymysql.connect(**con)
        with conn.cursor() as cursor:
            query_date = dataframe['date'].iloc[0]
            cursor.execute("SELECT COUNT(*) FROM shares WHERE date = %s", (query_date))
            count = cursor.fetchone()[0]
        

            if count == 0:
                command = "INSERT INTO shares(date,stock_id,open,high,low,close,volume,turnover) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                for index, row in dataframe.iterrows():
                    cursor.execute(command, tuple(row))
                    conn.commit()
                print("數據插入成功")
            else:
                print("數據有了")
        return dataframe
    except Exception as e:
        print("發生錯誤：", e)
    finally:
        if conn:
            conn.close()
'''
def DOG(prod, firstTime, endTime, entry_strategy, exit_strategy):
    data = SQL_DATA(prod, firstTime, endTime)
    print("Data Shape:", data.shape)
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
    return (data,trade_df,indicators)

prod = '0050'
firstTime = '2020-01-01'
endTime = '2023-09-01'
entry_strategy='均線排列策略'
exit_strategy="強勢回檔策略"
DOG(prod, firstTime, endTime, entry_strategy, exit_strategy)
'''


