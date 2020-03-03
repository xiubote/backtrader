
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 16:16:26 2020

@author: xiubote
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import numpy as np
from sklearn import linear_model
from sklearn import preprocessing
import datetime

class rsrs_indicator(bt.Indicator):
    lines = ('rsrs','r2',)
    def __init__(self, rsrs_window):
        self.params.rsrs_window = rsrs_window
        self.addminperiod(self.params.rsrs_window)

    def next(self):
        data_serial_high = list(self.data.high.get(size = self.params.rsrs_window))
        data_serial_low = list(self.data.low.get(size = self.params.rsrs_window))
        model = linear_model.LinearRegression()
        model.fit(np.array([data_serial_low]).T, data_serial_high)
        self.lines.rsrs[0] = model.coef_[0]
        self.lines.r2[0] = model.score(np.array([data_serial_low]).T, data_serial_high)

class rsrs_zscore_indicator(bt.Indicator):
    lines = ('zscore',)
    def __init__(self, zscore_window, rsrs_window):
        self.params.zscore_window = zscore_window
        self.params.rsrs_window = rsrs_window
        self.addminperiod(self.params.zscore_window + self.params.rsrs_window)
        self.rsrs = rsrs_indicator(self.data, rsrs_window = self.params.rsrs_window)
        self.r2 = rsrs_indicator(self.data, rsrs_window = self.params.rsrs_window).lines.r2
        
    def next(self):
        self.lines.zscore[0] = preprocessing.scale(list(self.rsrs.get(size = self.params.zscore_window)))[-1]*self.r2[0]*self.rsrs[0]
        
class RSRS_Strategy(bt.Strategy):
    params = (('rsrs_window', 18),('zscore_window', 250),('judge', 0.9),)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        for i in range(0,len(self.datas)):
            self.datas[i].rsrs = rsrs_indicator(self.datas[i],rsrs_window = self.params.rsrs_window)
            self.datas[i].r2 = rsrs_indicator(self.datas[i],rsrs_window = self.params.rsrs_window).lines.r2
            self.datas[i].zscore = rsrs_zscore_indicator(self.datas[i], zscore_window = self.params.zscore_window, rsrs_window = self.params.rsrs_window)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            if self.datas[0].datetime.date(0) < datetime.date.today():
                pass
            else:
                print('发送信号')
                print([str(self.datas[0].datetime.datetime(0)), order.data._name,order.size,self.getposition(order.data).size])
#        if order.status in [order.Completed]:
#            if order.isbuy():
#                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
#                    (order.executed.price,order.executed.value,order.executed.comm))
#                
#            else:  
#                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
#                    (order.executed.price,order.executed.value,order.executed.comm))  


    def next(self):
        
#        self.log('Close, %.2f' % self.data.close[0])
#        self.log('Close, %.2f' % self.datas[1].close[0])
        
        zscore = self.data.zscore[0]
        judge = self.p.judge
        
        if zscore > judge:
            if self.getposition(data=self.datas[1]).size < 0:
                self.order = self.close(self.datas[1])
                self.order = self.buy(self.datas[1])
            elif self.getposition(data=self.datas[1]).size > 0:
                pass
            elif self.getposition(data=self.datas[1]).size == 0:
                self.order = self.buy(self.datas[1])

        elif zscore < -judge:
            if self.getposition(data=self.datas[1]).size > 0:
                self.order = self.close(self.datas[1])
                self.order = self.sell(self.datas[1],size = 1)
            elif self.getposition(data=self.datas[1]).size < 0:
                pass
            elif self.getposition(data=self.datas[1]).size == 0:
                self.order = self.sell(self.datas[1],size=1)

    def stop(self):
        print('Final Portfolio Value: %.2f' % self.broker.getvalue())


class Test_Strategy(bt.Strategy):
    #测试用
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        pass
    def next(self):        
        self.log('Close, %.2f' % self.data.close[0])
        self.log('Close, %.2f' % self.datas[1].close[0])
        
def RSRS_backtest():
    dataname = ['sh000300', 'if00']
    security = ['index','future']
    fromdate = datetime.datetime(2017,2,28)
    todate = datetime.date(2020,2,28)
    frequency = '30min'
    cash = 3200
    commission = 1
    margin = 1
    automargin = 0.15
    RSRS_Strategy.backtest(dataname, fromdate, todate, frequency, security, cash, commission, margin, automargin)
    
        
def RSRS_monitor():
    dataname = ['sh000300', 'if00']
    security = ['index','future']
    dataname_live = ['000300.SH','if.CFE']
    fromdate = datetime.datetime(2017,2,28)
    frequency = '30min'
    cash = 3200
    commission = 1
    margin = 1
    automargin = 0.15
    RSRS_Strategy.monitor(dataname, dataname_live, fromdate, frequency, security, cash, commission, margin, automargin)
    #Test_Strategy.monitor(dataname, dataname_live, fromdate, '1min', security, cash)
    
if __name__ == '__main__':  
    
    RSRS_backtest()
    #RSRS_monitor()
