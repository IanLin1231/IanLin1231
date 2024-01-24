from PyQt5 import QtCore, QtGui, QtWidgets
from trade_plot import main
from XTTE import trade_main, record_trade, rsi_entry_trade, macd_entry_logic, ma_entry_logic, bollinger_entry_logic, ma_array_entry_logic, ma_atr_entry_logic, rollback_entry_logic, macd_sma_entry_logic, rsi_macd_sma_entry_logic, kd_entry_logic, pq_entry_logic, turtle_entry_logic, rsi_exit_trade, macd_exit_logic, ma_exit_logic, bollinger_exit_logic, ma_array_exit_logic, ma_atr_exit_logic, rollback_exit_logic, macd_sma_exit_logic, rsi_macd_sma_exit_logic, kd_exit_logic, pq_exit_logic, turtle_exit_logic
import shioaji as sj
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates
import pandas as pd
import talib
from datetime import datetime, time
import holidays

class Ui_MainWindow(object):
        # 計算交易績效指標
    def Performance(self, trade=pd.DataFrame(), prodtype='ETF'):
        # 如果沒有交易紀錄 則不做接下來的計算
        if trade.shape[0]==0:
            print('沒有交易紀錄')
            return False
            
        # 交易成本 手續費0.1425%*2 (券商打折請自行計算)
        if prodtype=='ETF':
            cost=0.001 + 0.00285    # ETF稅金 0.1%
        elif prodtype=='Stock':
            cost=0.003 + 0.00285    # 股票的稅金 0.3%
        else:
            return False
        
        # 將物件複製出來，不影響原本的變數內容
        trade1=trade
        trade1=trade1.sort_values("cover_time")
        trade1=trade1.reset_index(drop=True)
        
        # 給交易明細定義欄位名稱
        trade1.columns=['product','bs','order_time','order_price','cover_time','cover_price','order_unit']
        # 計算出每筆的報酬率
        trade1['order_unit'] = trade1['order_unit'].astype(float)
        trade1['ret']=(((trade1['cover_price']-trade1['order_price'])/trade1['order_price'])-cost) *trade1['order_unit']

        # 1. 總報酬率：整個回測期間的總報酬率累加
        sum = '%s'  %( round(trade1['ret'].sum(),4) )
        #print('總績效 '+sum)#%( round(trade1['ret'].sum(),4) ))
        # 2. 總交易次數：代表回測的交易筆數
        trans = '%s' %( trade1.shape[0] )
        #print('交易次數 '+trans)#%( trade1.shape[0] ))
        # 3. 平均報酬率：簡單平均報酬率（扣除交易成本後）
        avgPre = '%s' %( round(trade1['ret'].mean(),4) )
        #print('平均績效 '+avgPre)#%( round(trade1['ret'].mean(),4) ))
        # 4.    平均持有時間：代表平均每筆交易的持有時間
        
        trade1['cover_time'] = pd.to_datetime(trade1['cover_time'])
        trade1['order_time'] = pd.to_datetime(trade1['order_time'])

        onopen_day=(trade1['cover_time']-trade1['order_time']).mean()
        avgTime = '%s' %( onopen_day.days )
        #print('平均持有天數 '+avgTime+' 天')#%( onopen_day.days ))
        # 判斷是否獲利跟虧損都有績效
        earn_trade=trade1[trade1['ret'] > 0]
        loss_trade=trade1[trade1['ret'] <= 0]
        if earn_trade.shape[0]==0 or loss_trade.shape[0]==0: 
            #print('交易資料樣本不足(樣本中需要有賺有賠的)')
            return False        
        # 5. 勝率：代表在交易次數中，獲利次數的佔比（扣除交易成本後）
        earn_ratio=earn_trade.shape[0] / trade1.shape[0]
        winPer = '%s' %( round(earn_ratio ,2) )
        #print('勝率 '+winPer)#%( round(earn_ratio ,2) ))
        # 6. 平均獲利：代表平均每一次獲利的金額（扣除交易成本後）
        avg_earn=earn_trade['ret'].mean()
        avgPro = '%s'%( round(avg_earn,4))
        #print('平均獲利 '+avgPro)#%( round(avg_earn,4)))
        # 7. 平均虧損：代表平均每一次虧損的金額（扣除交易成本後）
        avg_loss=loss_trade['ret'].mean()
        avgLos = '%s'%( round(avg_loss,4))
        #print('平均虧損 '+avgLos)#%( round(avg_loss,4) ))
        # 8. 賺賠比：代表平均獲利 / 平均虧損
        odds=abs(avg_earn/avg_loss)
        od = '%s' %( round(odds,4))
        #print('賺賠比 '+od)#%( round(odds,4) ))
        # 9. 期望值：代表每投入的金額，可能會回報的多少倍的金額
        expct = '%s'%( round(((earn_ratio*odds)-(1-earn_ratio)),4))
        #print('期望值 '+expct)#%( round(((earn_ratio*odds)-(1-earn_ratio)),4) ))
        # 10. 獲利平均持有時間：代表獲利平均每筆交易的持有時間
        earn_onopen_day=(earn_trade['cover_time']-earn_trade['order_time']).mean()
        avgHold_p = '%s'%( earn_onopen_day.days )
        #print('獲利平均持有天數 '+avgHold_p+' 天')#%( earn_onopen_day.days ))
        # 11. 虧損平均持有時間：代表虧損平均每筆交易的持有時間
        loss_onopen_day=(loss_trade['cover_time']-loss_trade['order_time']).mean()
        avgHold_l = '%s'%( loss_onopen_day.days )
        #print('虧損平均持有天數 '+avgHold_l+' 天')#%( loss_onopen_day.days ))
        
        # 12. 最大連續虧損：代表連續虧損的最大幅度
        tmp_accloss=1
        max_accloss=1
        for ret in trade1['ret'].values:
            if ret <= 0:
                tmp_accloss *= ret
                max_accloss= min(max_accloss,tmp_accloss)
            else:
                tmp_accloss = 1
        maxLoss='%s'%(round(max_accloss ,4))
        #print('最大連續虧損',maxLoss)#round(max_accloss ,4))
            
        # 優先計算累計報酬率 並將累計報酬率的初始值改為1 繪圖較容易閱讀
        trade1['acc_ret'] = (1+trade1['ret']).cumprod() 
        trade1.loc[-1,'acc_ret'] = 1 
        trade1.index = trade1.index + 1 
        trade1.sort_index(inplace=True) 
        
        # 13. 最大資金回落：代表資金從最高點回落至最低點的幅度    
        trade1['acc_max_cap'] = trade1['acc_ret'].cummax()
        trade1['dd'] = (trade1['acc_ret'] / trade1['acc_max_cap'])
        trade1.loc[trade1['acc_ret'] == trade1['acc_max_cap'] , 'new_high'] = trade1['acc_ret']
        maxFund='%s'%(round(1-trade1['dd'].min(),4))
        #print('最大資金回落',maxFund)#round(1-trade1['dd'].min(),4))
        
        text='總績效 '+ sum + '\n' + '交易次數 '+ trans + '\n' + '平均績效 ' + avgPre + '\n' + '平均持有天數 ' + avgTime + ' 天\n' + '勝率 ' + winPer + '\n' + '平均獲利 ' + avgPro + '\n' + '平均虧損 ' + avgLos + '\n' + '賺賠比 ' + od + '\n' + '期望值 ' + expct + '\n' + '獲利平均持有天數 ' + avgHold_p + ' 天\n' + '虧損平均持有天數 ' + avgHold_l + ' 天\n'+'最大連續虧損'+maxLoss+'\n'+'最大資金回落'+maxFund
        
        # 14. 繪製資金曲線圖(用幾何報酬計算)
        self.evaluation.figure.clear()
        ax=self.axes_evaluation.figure.add_subplot(111)
        ax.plot( trade1['acc_ret'] , 'b-' ,label='Profit')
        ax.plot( trade1['dd'] , '-' ,color='#FFFF00',label='MDD')
        ax.plot( trade1['new_high'] , 'o' ,color='#FF00FF',label='Equity high')
        ax.legend()
        self.evaluation.draw()
        
        return text
    

    def ChartTrade(self, data, trade=pd.DataFrame(), addp=[], v_enable=True):
        data1 = data
        data1['date'] = pd.to_datetime(data1['date'])  # 將日期列轉換為 datetime
        data1.set_index('date', inplace=True)  # 設定日期為索引
        data1.sort_index(inplace=True)  # 按日期升序排序
        self.candlechart.figure.clear()

        ax_candle = self.candlechart.figure.add_subplot(411)
        ax_rsi = self.candlechart.figure.add_subplot(412, sharex=ax_candle)
        ax_kd = self.candlechart.figure.add_subplot(413, sharex=ax_candle)
        ax_macd_volume = self.candlechart.figure.add_subplot(414, sharex=ax_candle)

        # 計算 RSI, KD, MACD 指標
        data1['RSI'] = talib.RSI(data1['close'])
        data1['K'], data1['D'] = talib.STOCH(data1['high'], data1['low'], data1['close'])
        data1['MACD'], data1['Signal'], _ = talib.MACD(data1['close'])

        # 繪製蠟燭圖
        width = 0.6
        for idx, row in data1.iterrows():
            color = '#FF4500' if row['close'] > row['open'] else '#16982B'
            ax_candle.bar(idx, row['high']-row['low'], width, bottom=row['low'], color=color)
            ax_candle.bar(idx, row['close']-row['open'], width, bottom=min(row['open'], row['close']), color=color)

        # 繪製 RSI 圖
        ax_rsi.plot(data1.index, data1['RSI'], color='b', label='RSI')
        ax_rsi.set_ylabel('RSI')
        ax_rsi.legend()

        # 繪製 KD 圖
        ax_kd.plot(data1.index, data1['K'], color='g', label='K')
        ax_kd.plot(data1.index, data1['D'], color='r', label='D')
        ax_kd.set_ylabel('K/D')
        ax_kd.legend()

        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax_kd.xaxis.set_major_locator(locator)
        ax_kd.xaxis.set_major_formatter(formatter)

        # 繪製 MACD 和成交量
        if v_enable:
            ax_macd = ax_macd_volume.twinx()
            ax_macd_volume.bar(data1.index, data1['volume'], color='k')
            ax_macd.plot(data1.index, data1['MACD'], color='b', label='MACD')
            ax_macd.plot(data1.index, data1['Signal'], color='g', label='Signal')
            ax_macd.set_ylabel('MACD')
            ax_macd.legend()
            ax_macd_volume.set_ylabel('Volume')

        # 繪製買賣點
        if not trade.empty:
            trade1 = trade.copy()
            # 確保交易時間與數據時間格式一致
            trade1['order_time'] = pd.to_datetime(trade1['order_time'])
            trade1['cover_time'] = pd.to_datetime(trade1['cover_time'])

            # 獲取買入和賣出點的數據
            buy_order_trade = trade1[["order_time", "order_price"]].set_index("order_time")
            buy_cover_trade = trade1[["cover_time", "cover_price"]].set_index("cover_time")

            # 繪製買入和賣出點
            ax_candle.plot(buy_order_trade.index, buy_order_trade['order_price'], '^', markersize=5, color='#FF4500', label='Buy')
            ax_candle.plot(buy_cover_trade.index, buy_cover_trade['cover_price'], 'v', markersize=5, color='#16982B', label='Sell')
            ax_candle.legend()
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax_candle.xaxis.set_major_locator(locator)
        ax_candle.xaxis.set_major_formatter(formatter)
        self.candlechart.figure.tight_layout()
        self.candlechart.draw()

    
    def onButtonClick(self): #按下按鈕後
        self.startbutton.setStyleSheet("background-color: red")
        self.startbutton.setText('回測中...')
         # 獲取時間的字串表示
      
        date_start = self.date_First.date().toString("yyyy-MM-dd")
        date_end = self.date_End.date().toString("yyyy-MM-dd")
        
        prod = self.stockname.toPlainText()
        accumulated_data = pd.DataFrame()
        accumulated_trade_df = pd.DataFrame()
        accumulated_indicators = []

        if prod:  #檢查 prod 是否為空
            if prod not in [self.comboBox.itemText(i) for i in range(self.comboBox.count())]:
                self.comboBox.addItem(prod)
        else:
            prod = self.comboBox.currentText()
            self.stockname.setPlainText(prod)
        entry_strategy=self.approach.currentText()
        exit_strategy=self.appearance.currentText()

        prop = self.money.toPlainText()
        if not prod.strip():  # 檢查 prod 是否為空或僅包含空白字符
            self.dataEdit.setPlainText("請輸入商品代碼")
            self.startbutton.setStyleSheet("background-color: white")
            self.startbutton.setText('開始回測')
            return
        elif not prop.strip():  # 檢查 prop 是否為空或僅包含空白字符
            self.dataEdit.setPlainText("請輸入初始資金")
            self.startbutton.setStyleSheet("background-color: white")
            self.startbutton.setText('開始回測')
            return
        elif entry_strategy == ' ':
            self.dataEdit.setPlainText("請選擇進場方式")
            self.trade_sign.setPlainText(" ")
            self.evaluation.figure.clear()
            self.evaluation.draw()
            self.candlechart.figure.clear()
            self.candlechart.draw()
            self.startbutton.setStyleSheet("background-color: white")
            self.startbutton.setText('開始回測')
            return
        elif exit_strategy == ' ':
            self.dataEdit.setPlainText("請選擇出場方式")
            self.trade_sign.setPlainText(" ")
            self.evaluation.figure.clear()
            self.evaluation.draw()
            self.candlechart.figure.clear()
            self.candlechart.draw()
            self.startbutton.setStyleSheet("background-color: white")
            self.startbutton.setText('開始回測')
            return 
            
   
        dataU, trade_dfU, indicatorsU = main(prod, date_start, date_end, entry_strategy, exit_strategy)
        text=self.Performance(trade_dfU,'ETF')
        self.ChartTrade(dataU, trade_dfU, indicatorsU)
        
        # 输出
        self.trade_sign.setPlainText(" ")
        self.dataEdit.setPlainText("Text from stockname:"+str(prod)+"\nText from money:"+str(prop)+"\nSelected Strat Time:"+str(date_start)+"\nSelected End Time:"+str(date_end)+"\n進場:"+entry_strategy+"\n出場:"+exit_strategy+'\n'+str(text)) #改
        for indicator in indicatorsU:
            if indicator['type'] == '進場':
                self.trade_sign.append(f"{indicator['c_time']} 觸發進場訊號 隔日進場 {indicator['order_time']} 進場價 {indicator['order_price']} 進場 {indicator['order_unit']} 單位")
            elif indicator['type'] == '出場':
                self.trade_sign.append(f"{indicator['c_time']} 觸發出場訊號 隔日出場 {indicator['cover_time']} 出場價 {indicator['cover_price']}")

        
        
        self.startbutton.setStyleSheet("background-color: white")
        self.startbutton.setText('開始回測')

        return prod, prop, date_start, date_end


    def checkDateTime(self):
        self.trade_sign.append(f"開始自動交易")
        # 獲取時間的字串表示
        trade_date_start = self.date_First.date().toString("yyyy-MM-dd")
        trade_date_end = self.date_End.date().toString("yyyy-MM-dd")
        print(trade_date_start,trade_date_end)
        trade_prod = self.stockname.toPlainText()
        print(trade_prod)
        if trade_prod:  #檢查 prod 是否為空
            if trade_prod not in [self.comboBox.itemText(i) for i in range(self.comboBox.count())]:
                self.comboBox.addItem(trade_prod)
        else:
            trade_prod = self.comboBox.currentText()
            self.stockname.setPlainText(trade_prod)
        
        trade_prop = self.money.toPlainText()
        
        trade_entry_strategy=self.approach.currentText()
        trade_exit_strategy=self.appearance.currentText()
        print(trade_prop,trade_entry_strategy,trade_exit_strategy)
        if trade_entry_strategy == ' ':
            self.dataEdit.setPlainText("請選擇進場方式")
            self.trade_sign.setPlainText(" ")
            self.evaluation.figure.clear()
            self.evaluation.draw()
            self.candlechart.figure.clear()
            self.candlechart.draw()
            self.startbutton.setStyleSheet("background-color: white")
            self.startbutton.setText('開始回測')
            return
        elif trade_exit_strategy == ' ':
            self.dataEdit.setPlainText("請選擇出場方式")
            self.trade_sign.setPlainText(" ")
            self.evaluation.figure.clear()
            self.evaluation.draw()
            self.candlechart.figure.clear()
            self.candlechart.draw()
            self.startbutton.setStyleSheet("background-color: white")
            self.startbutton.setText('開始回測')
            return 
        
        api = sj.Shioaji(simulation=True) # 模擬模式
        api.login(
                 api_key="6tdnA3hAbKMHtGWNY5pfd6fHrCyUXbP47KN5wUcsuwhL",     # 請修改此處
                 secret_key="6wmG6ufQ6djzt18FFSZ4rq1JyZANq6CRyruULnfaHr4V",   # 請修改此處
                 contracts_timeout=10000,
                 #contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
                 )
        self.trade_sign.append(f"API登陸成功")
        
        position = 0
        
        indicators = []
        new_indicators=[]
        contract = api.Contracts.Stocks[trade_prop]
        start_date = trade_date_start
        trade = pd.DataFrame()
        
        start_date = datetime.strptime(trade_date_start, '%Y-%m-%d').date()
        end_date = datetime.strptime(trade_date_end, '%Y-%m-%d').date()
        target_time = time(14, 30)  # 目標時間為下午 2:30
        tw_holidays = holidays.Taiwan()#台灣休假日
        print(position,'/n',start_date,'/n',end_date,'/n',target_time)
        while True:
            now_datetime = datetime.now()#抓今天日期時間
            now_date = now_datetime.date()#今天日期
            now_time = now_datetime.time()#今天時間

            # 檢查是否在指定日期範圍內
            if start_date <= now_date <= end_date:
                # 檢查是否是休假日
                if now_date in tw_holidays:
                    print("放假")
                else:
                    # 檢查當前時間是否接近下午 2:30
                    if now_time.hour == target_time.hour and now_time.minute == target_time.minute:
                        self.trade_sign.append(f"{target_time} 在下午 2:30。")
                    # 執行你的代碼
                        entry_data,exit_data=trade_main(api, trade_prod, trade_date_start, trade_entry_strategy, trade_exit_strategy, extra_days=200)
                        if position==0:
                            if trade_entry_strategy == 'RSI':
                                position, new_indicators = rsi_entry_trade(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == 'MACD':
                                position, new_indicators = macd_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == '突破均線策略':
                                position, new_indicators = ma_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == '布林函數':
                                position, new_indicators = bollinger_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == '均線排列策略':
                                position, new_indicators = ma_array_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == 'MA+ATR濾網交易策略':
                                position, new_indicators = ma_atr_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == '強勢回檔策略':
                                position, new_indicators, rsi_min, rsi_min_time = rollback_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == 'MACD+SMA':
                                position, new_indicators = macd_sma_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == 'RSI+MACD+SMA':
                                position, new_indicators = rsi_macd_sma_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == 'KD':
                                position, new_indicators = kd_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == 'PQ':
                                position, new_indicators = pq_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_entry_strategy == '海龜':
                                position, new_indicators = turtle_entry_logic(entry_data, position, api, api.Contracts.Stocks[trade_prod])
                            indicators.extend(new_indicators)                  
                        else:    
                         # 出場邏輯
                            if trade_exit_strategy == 'RSI':
                                position, new_indicators = rsi_exit_trade(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == 'MACD':
                                position, new_indicators = macd_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == '突破均線策略':
                                position, new_indicators = ma_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == '布林函數':
                                position, new_indicators = bollinger_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == '均線排列策略':
                                position, new_indicators = ma_array_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == 'MA+ATR濾網交易策略':
                                position, new_indicators = ma_atr_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == '強勢回檔策略':
                                position, new_indicators = rollback_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == 'MACD+SMA':
                                position, new_indicators = macd_sma_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == 'RSI+MACD+SMA':
                                position, new_indicators = rsi_macd_sma_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == 'KD':
                                position, new_indicators = kd_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == 'PQ':
                                position, new_indicators = pq_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            elif trade_exit_strategy == '海龜':
                                position, new_indicators = turtle_exit_logic(exit_data, position, api, api.Contracts.Stocks[trade_prod])
                            indicators.extend(new_indicators)
        
                        trade = record_trade(trade, indicators, trade_prod)
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
                        #印出委託單
                        for indicator in indicators:
                            if indicator[1] == 'Buy':
                                self.trade_sign.append(f"{indicator[0]}  買賣: {indicator[1]} ") 
                                self.trade_sign.append(f"委託時間: {indicator[2]} 委託價: {indicator[3]} 成交時間: {indicator[4]} 成交價: {indicator[5]} 原委託:{indicator[6]} 已成交:{indicator[7]} 委託狀態: {indicator[8]}")
                            elif indicator[1] == 'Sell':
                                self.trade_sign.append(f"商品:{indicator[0]} 買賣: {indicator[1]} ") 
                                self.trade_sign.append(f"委託時間: {indicator[2]} 委託價: {indicator[3]} 成交時間: {indicator[4]} 成交價: {indicator[5]} 原委託:{indicator[6]} 已成交:{indicator[7]} 委託狀態: {indicator[8]}")


                        self.trade_sign.append(f"迴圈執行於")
                        
                    else:
                    # 如果不是目標時間，則等待三十分鐘後再次檢查
                        self.trade_sign.append(f"等待1分鐘")
                        
            else:
                #不在指定的日期範圍內，結束迴圈
                break

        position,trade_data, trade_trade_df, trade_indicators, trade_trade= main(api, contract, trade_prod, trade_date_start, trade_entry_strategy, trade_exit_strategy, position, indicators, new_indicators)
        trade_text=self.Performance(trade_trade_df,'ETF')
        self.ChartTrade(trade_data, trade_trade_df, trade_indicators)
        # 输出
        self.dataEdit.setPlainText("Text from stockname:"+str(trade_prod)+"\nText from money:"+str(trade_prop)+"\nSelected Strat Time:"+str(trade_date_start)+"\nSelected End Time:"+str(trade_date_end)+"\n進場:"+trade_entry_strategy+"\n出場:"+trade_exit_strategy+'\n'+str(trade_text)) #改
        for indicator in trade_indicators:
            if indicator[1] == 'Buy':
                self.trade_sign.append(f"{indicator[0]}  買賣: {indicator[1]} ") 
                self.trade_sign.append(f"委託時間: {indicator[2]} 委託價: {indicator[3]} 成交時間: {indicator[4]} 成交價: {indicator[5]} 原委託:{indicator[6]} 已成交:{indicator[7]} 委託狀態: {indicator[8]}")
            elif indicator[1] == '出場':
                self.trade_sign.append(f"商品:{indicator[0]} 買賣: {indicator[1]} ") 
                self.trade_sign.append(f"委託時間: {indicator[2]} 委託價: {indicator[3]} 成交時間: {indicator[4]} 成交價: {indicator[5]} 原委託:{indicator[6]} 已成交:{indicator[7]} 委託狀態: {indicator[8]}")
        return 0

    def trade_onButtonClick(self): #按下按鈕後
        # 啟動計時器，每半小時檢查一次
        self.timer.start(60000 )  # 1800000 毫秒 = 30 分鐘



    def on_combobox_changed(self):
        prod=self.comboBox.currentText()
        self.stockname.setPlainText(prod)
     


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1159, 696)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(990, 0))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        # 初始化計時器，將 MainWindow 作為父對象
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.checkDateTime)


        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(297, 0))
        self.label.setMaximumSize(QtCore.QSize(99999, 16777215))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        
        self.stockname = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(255)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stockname.sizePolicy().hasHeightForWidth())
        self.stockname.setSizePolicy(sizePolicy)
        self.stockname.setMinimumSize(QtCore.QSize(256, 0))
        self.stockname.setMaximumSize(QtCore.QSize(300, 40))
        self.stockname.setSizeIncrement(QtCore.QSize(0, 20))
        self.stockname.setBaseSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.stockname.setFont(font)
        self.stockname.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.stockname.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.stockname.setMarkdown("")
        self.stockname.setPlaceholderText("請輸入代碼或名稱  ")
        self.stockname.setObjectName("stockname")
        self.horizontalLayout.addWidget(self.stockname)
        
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMinimumSize(QtCore.QSize(101, 0))
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(135, 0))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        
        self.money = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(255)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.money.sizePolicy().hasHeightForWidth())
        self.money.setSizePolicy(sizePolicy)
        self.money.setMinimumSize(QtCore.QSize(256, 0))
        self.money.setMaximumSize(QtCore.QSize(3000, 40))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.money.setFont(font)
        self.money.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.money.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.money.setMarkdown("")
        self.money.setOverwriteMode(False)
        self.money.setObjectName("money")
        self.horizontalLayout.addWidget(self.money)
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(135, 0))
        self.label_2.setBaseSize(QtCore.QSize(40, 0))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        
        self.approach = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.approach.sizePolicy().hasHeightForWidth())
        self.approach.setSizePolicy(sizePolicy)
        self.approach.setMinimumSize(QtCore.QSize(188, 0))
        self.approach.setObjectName("approach")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.approach.addItem("")
        self.horizontalLayout_2.addWidget(self.approach)
        
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setMinimumSize(QtCore.QSize(135, 0))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        
        self.appearance = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.appearance.sizePolicy().hasHeightForWidth())
        self.appearance.setSizePolicy(sizePolicy)
        self.appearance.setMinimumSize(QtCore.QSize(188, 0))
        self.appearance.setObjectName("appearance")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.appearance.addItem("")
        self.horizontalLayout_2.addWidget(self.appearance)
        
        self.startbutton = QtWidgets.QPushButton(self.centralwidget)
        self.startbutton.setMinimumSize(QtCore.QSize(92, 0))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.startbutton.setFont(font)
        self.startbutton.setAutoDefault(False)
        self.startbutton.clicked.connect(self.onButtonClick)#按下按鈕
        self.startbutton.setObjectName("startbutton")
        self.horizontalLayout_2.addWidget(self.startbutton)
        
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(189, 0))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)

        self.date_First = QtWidgets.QDateEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date_First.sizePolicy().hasHeightForWidth())
        self.date_First.setSizePolicy(sizePolicy)
        self.date_First.setMinimumSize(QtCore.QSize(288, 0))
        self.date_First.setObjectName("date_First")
        self.horizontalLayout_3.addWidget(self.date_First)
        
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(189, 0))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        
        self.date_End = QtWidgets.QDateEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date_End.sizePolicy().hasHeightForWidth())
        self.date_End.setSizePolicy(sizePolicy)
        self.date_End.setMinimumSize(QtCore.QSize(288, 0))
        self.date_End.setObjectName("date_End")
        self.horizontalLayout_3.addWidget(self.date_End)
        
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(92, 0))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.clicked.connect(self.trade_onButtonClick)#按下按鈕
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        
        self.dataEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.dataEdit.setStyleSheet("font-size: 20px;")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataEdit.sizePolicy().hasHeightForWidth())
        self.dataEdit.setSizePolicy(sizePolicy)
        self.dataEdit.setMinimumSize(QtCore.QSize(100, 200))
        self.dataEdit.setObjectName("dataEdit")
        self.horizontalLayout_5.addWidget(self.dataEdit)
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        
        
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_6.addLayout(self.verticalLayout_3)
        
        self.candlechart = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        self.axes_candlechart = self.candlechart.figure.add_subplot(111)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.candlechart.sizePolicy().hasHeightForWidth())
        self.candlechart.setSizePolicy(sizePolicy)
        self.candlechart.setMinimumSize(QtCore.QSize(0, 500))
        self.candlechart.setObjectName("candlechart")
        self.verticalLayout_3.addWidget(self.candlechart)
        self.toolbar = NavigationToolbar(self.candlechart, MainWindow)
        self.verticalLayout_3.addWidget(self.toolbar)
        

        
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_6.addLayout(self.verticalLayout_4)

        
        self.evaluation = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        self.axes_evaluation = self.evaluation.figure.add_subplot(111)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.evaluation.sizePolicy().hasHeightForWidth())
        self.evaluation.setSizePolicy(sizePolicy)
        self.evaluation.setMinimumSize(QtCore.QSize(0, 500))
        self.evaluation.setObjectName("evaluation")
        self.verticalLayout_4.addWidget(self.evaluation)
        self.toolbar1 = NavigationToolbar(self.evaluation, MainWindow)
        self.verticalLayout_4.addWidget(self.toolbar1)

        
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.trade_sign = QtWidgets.QTextEdit(self.centralwidget)
        self.trade_sign.setStyleSheet("font-size: 20px;")
        self.trade_sign.setObjectName("trade_sign")
        self.verticalLayout_2.addWidget(self.trade_sign)
        
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1159, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.stockname, self.comboBox)
        MainWindow.setTabOrder(self.comboBox, self.money)
        MainWindow.setTabOrder(self.money, self.approach)
        MainWindow.setTabOrder(self.approach, self.date_First)
        MainWindow.setTabOrder(self.date_First, self.date_End)
        
        
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "請輸入股票區間或代碼："))
        self.label_3.setText(_translate("MainWindow", "初始資金："))
        self.money.setPlaceholderText(_translate("MainWindow", "請輸入金額  "))
        self.label_2.setText(_translate("MainWindow", "入場策略："))
        self.approach.setItemText(0, _translate("MainWindow", " "))
        self.approach.setItemText(1, _translate("MainWindow", "RSI"))
        self.approach.setItemText(2, _translate("MainWindow", "MACD"))
        self.approach.setItemText(3, _translate("MainWindow", "突破均線策略"))
        self.approach.setItemText(4, _translate("MainWindow", "強勢回檔策略"))
        self.approach.setItemText(5, _translate("MainWindow", "布林函數"))
        self.approach.setItemText(6, _translate("MainWindow", "均線排列策略"))
        self.approach.setItemText(7, _translate("MainWindow", "MA+ATR濾網交易策略"))
        self.approach.setItemText(8, _translate("MainWindow", "MACD+SMA"))
        self.approach.setItemText(9, _translate("MainWindow", "RSI+MACD+SMA"))
        self.approach.setItemText(10, _translate("MainWindow", "KD"))
        self.approach.setItemText(11, _translate("MainWindow", "PQ"))
        self.approach.setItemText(12, _translate("MainWindow", "海龜"))
        self.approach.setItemText(13, _translate("MainWindow", "TEXT"))
        self.label_4.setText(_translate("MainWindow", "出場策略："))
        self.appearance.setItemText(0, _translate("MainWindow", " "))
        self.appearance.setItemText(1, _translate("MainWindow", "RSI"))
        self.appearance.setItemText(2, _translate("MainWindow", "MACD"))
        self.appearance.setItemText(3, _translate("MainWindow", "突破均線策略"))
        self.appearance.setItemText(4, _translate("MainWindow", "強勢回檔策略"))
        self.appearance.setItemText(5, _translate("MainWindow", "布林函數"))
        self.appearance.setItemText(6, _translate("MainWindow", "均線排列策略"))
        self.appearance.setItemText(7, _translate("MainWindow", "MA+ATR濾網交易策略"))
        self.appearance.setItemText(8, _translate("MainWindow", "MACD+SMA"))
        self.appearance.setItemText(9, _translate("MainWindow", "RSI+MACD+SMA"))
        self.appearance.setItemText(10, _translate("MainWindow", "KD"))
        self.appearance.setItemText(11, _translate("MainWindow", "PQ"))
        self.appearance.setItemText(12, _translate("MainWindow", "海龜"))
        self.appearance.setItemText(13, _translate("MainWindow", "TEXT"))
        self.startbutton.setText(_translate("MainWindow", "開始回測"))
        self.label_5.setText(_translate("MainWindow", "回測開始時間："))
        self.label_6.setText(_translate("MainWindow", "回測結束時間："))
        self.pushButton.setText(_translate("MainWindow", "開始交易"))
        self.menu.setTitle(_translate("MainWindow", "回測系統"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)  # 创建 QApplication 实例

    # 设置全局字体为 Arial
    font = QtGui.QFont("Arial")
    app.setFont(font)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show() 
    sys.exit(app.exec_())

    




