#績效指標製作
import pandas as pd
# 載入yahoo finance 套件
from FinMind.data import DataLoader
#FinMind資料
FM=DataLoader()
def getDataFM(prod,st,en):
        demodata=FM.taiwan_stock_daily_adj(stock_id=prod,start_date=st,end_date=en)#除息還原股
        demodata=demodata.rename(columns={'max':'high','min':'low','Trading_Volume':'volume',
                                          'Trading_turnover':'turnover'}) #自定義名稱
        # 日期設定為索引
        demodata['date']=pd.to_datetime(demodata['date'])
        demodata=demodata.set_index(demodata['date'])
        demodata=demodata[['date','stock_id','open','high','low','close','volume','turnover']]
        return demodata




