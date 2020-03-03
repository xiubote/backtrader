from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from backtrader import date2num
from backtrader.feed import DataBase
from backtrader.utils.py3 import filter, string_types, integer_types
import numpy as np
import pymysql
import datetime
import time
from WindPy import w
        

class MySQLData(DataBase):

    params = (
        ('nocase', True),
        ('dataname', 'None'),
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('frequency', 'day'),
        ('security', 'None'),
        ('user', 'root'),
        ('password', '58604496'),
        
    )

    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        self._idx = -1
        s = self.p.dataname
        start_date = str(self.p.fromdate.date())
        end_date = str(self.p.todate.date())
        frequency = self.p.frequency
        user = self.p.user
        sql_password = self.p.password
        c = 'd_' + frequency + ',open,high,low,close,volume'
#        if self.p.security == 'None':
#            #自动识别有bug，正在修复，谨慎使用
#            if self.p.frequency == 'day':
#                if s[0:2] == 'sz' or s[0:2] == 'sh':
#                    sql = "select "+c+" from md_day where stock = '"+ s[2:] +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                    self.security = 'stock'
#                else:
#                    sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                    self.security = 'future'
#            else:
#                if s[0:2] == 'sz' or s[0:2] == 'sh':
#                    sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"  
#                    self.security = 'stock'
#                else:
#                    sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
#                    self.security = 'future'
        if self.p.security == 'stock':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where stock = '"+ s[2:] +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
                self.security = 'stock'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"  
                self.security = 'stock'
        elif self.p.security == 'future':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
                self.security = 'future'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
                self.security = 'future'  
        elif self.p.security == 'index':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
                self.security = 'index'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
                self.security = 'index'
        self.conn = pymysql.connect(user = user, password = sql_password, database = 'md_' + self.security)
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql)
        self.description = self.cursor.description

    def _load(self):
        self._idx += 1
        try:
            bar = self.cursor.fetchone()
            while None in bar:
                bar = self.cursor.fetchone()
            self.lines.datetime[0] = date2num(bar[0])
            self.lines.open[0] = bar[1]
            self.lines.high[0] = bar[2]
            self.lines.low[0] = bar[3]
            self.lines.close[0] = bar[4]
            self.lines.volume[0] = bar[5]
            #self.lines.openinterest[0] = 0
            return True
        except TypeError:
            self.conn.close()
            return False

        

        
class WindDataLive2(DataBase):
    from WindPy import w
#    w.start()
    params = (
        ('nocase', True),
        ('dataname', 'None'),
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('frequency', 'day'),
        ('security', 'None'),
        ('sleep', 1),
        ('user', 'root'),
        ('password', '58604496'),
    )


    def islive(self):
        '''Returns ``True`` to notify ``Cerebro`` that preloading and runonce
        should be deactivated'''
        return True
    
    def live(self):
        return True


    def __init__(self):
        super().__init__()
        self.backtest = True

    def start(self):
        super().start()
        self._idx = -1
        s = self.p.dataname
        start_date = str(self.p.fromdate.date())
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        frequency = self.p.frequency
            
        if self.p.security == 'stock':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", start_date, end_date, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))                     
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", start_date, end_date, "PriceAdj=B")
            
        elif self.p.security == 'future':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", start_date, end_date, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", start_date, end_date, "PriceAdj=B")
                
        elif self.p.security == 'index':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", start_date, end_date, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", start_date, end_date, "PriceAdj=B")
                
        self.times = data_wind.Times
        self.data = data_wind.Data
        self.count = 0

    def _load(self):
        self._idx += 1
        if self.backtest:
            try:
                bar = [self.times[self.count]]
                for i in self.data:
                    if np.isnan(i[self.count]) == True:
                        self.count += 1
                        return None
                    bar.append(i[self.count])
                self.lines.datetime[0] = date2num(bar[0])
                self.lines.open[0] = bar[1]
                self.lines.high[0] = bar[2]
                self.lines.low[0] = bar[3]
                self.lines.close[0] = bar[4]
                self.lines.volume[0] = bar[5]
                self.temp = bar[0]
                self.count += 1
                return True
            except IndexError:
                self.backtest = False

        if self.p.sleep == 1:
            if datetime.datetime.now().time() > datetime.time(15,1,0):
                market_opentime = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1),datetime.time(9,30,0))
                print('wait for market opening')
                time.sleep((market_opentime-datetime.datetime.now()).seconds)
                
            elif datetime.datetime.now() < datetime.datetime.combine(datetime.date.today(),datetime.time(9,30,0)):
                market_opentime = datetime.datetime.combine(datetime.date.today(),datetime.time(9,30,0))
                print('wait for market opening')
                time.sleep((market_opentime-datetime.datetime.now()).seconds)
            else:
                if self.p.frequency == 'day':
                    time.sleep(19800)
                else:
                    time.sleep(60*int(self.p.frequency[0:-3]))
        elif self.p.sleep == 0:
            pass
                
        s = self.p.dataname
        frequency = self.p.frequency
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.p.security == 'stock':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", str(self.temp), now_time, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))                     
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", str(self.temp), now_time, "PriceAdj=B")
            
        elif self.p.security == 'future':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", str(self.temp), now_time, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", str(self.temp), now_time, "PriceAdj=B")
                
        elif self.p.security == 'index':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", str(self.temp), now_time, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", str(self.temp), now_time, "PriceAdj=B")    
        self.times = data_wind.Times
        self.data = data_wind.Data
        if len(self.times) < 2:
            #print('中午休市，等待数据')
            return None
        bar = [self.times[1]]
        for i in self.data:
            if np.isnan(i[1]) == True:
                #print('停牌了')
                return None
            bar.append(i[1])
        self.lines.datetime[0] = date2num(bar[0])
        self.lines.open[0] = bar[1]
        self.lines.high[0] = bar[2]
        self.lines.low[0] = bar[3]
        self.lines.close[0] = bar[4]
        self.lines.volume[0] = bar[5]
        self.temp = bar[0]
        return True

        
class WindDataLive(DataBase):
    from WindPy import w
    w.start()
    params = (
        ('nocase', True),
        ('dataname', 'None'),
        ('dataname_live', 'None'),
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('frequency', 'day'),
        ('security', 'None'),
        ('sleep', 1),
        ('user', 'root'),
        ('password', '58604496'),
    )


    def islive(self):
        '''Returns ``True`` to notify ``Cerebro`` that preloading and runonce
        should be deactivated'''
        return True
    
    def live(self):
        return True


    def __init__(self):
        super().__init__()
        self.backtest = True

    def start(self):
        super().start()
        self._idx = -1
        s = self.p.dataname
        start_date = str(self.p.fromdate.date())
        frequency = self.p.frequency
        user = self.p.user
        sql_password = self.p.password
        c = 'd_' + frequency + ',open,high,low,close,volume'

        if self.p.security == 'stock':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where stock = '"+ s[2:] +"' and d_day > '"+start_date+"'"
                self.security = 'stock'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"'"  
                self.security = 'stock'
        elif self.p.security == 'future':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"'"
                self.security = 'future'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"'"
                self.security = 'future'  
        elif self.p.security == 'index':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where index = '"+ s[2:] +"' and d_day > '"+start_date+"'"
                self.security = 'index'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"'"
                self.security = 'index'
        self.conn = pymysql.connect(user = user, password = sql_password, database = 'md_' + self.security)
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql)
        self.description = self.cursor.description


    def _load(self):


        self._idx += 1
        if self.backtest:
            try:
                bar = self.cursor.fetchone()
                while None in bar:
                    bar = self.cursor.fetchone()
                self.lines.datetime[0] = date2num(bar[0])
                self.lines.open[0] = bar[1]
                self.lines.high[0] = bar[2]
                self.lines.low[0] = bar[3]
                self.lines.close[0] = bar[4]
                self.lines.volume[0] = bar[5]
                self.temp = bar[0]
                return True
            except TypeError:
                self.backtest = False



        if self.p.sleep == 1:
            if datetime.datetime.now().time() > datetime.time(15,1,0):
                market_opentime = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1),datetime.time(9,30,0))
                print('wait for market opening')
                time.sleep((market_opentime-datetime.datetime.now()).seconds)
                
            elif datetime.datetime.now() < datetime.datetime.combine(datetime.date.today(),datetime.time(9,30,0)):
                market_opentime = datetime.datetime.combine(datetime.date.today(),datetime.time(9,30,0))
                print('wait for market opening')
                time.sleep((market_opentime-datetime.datetime.now()).seconds)
            else:
                if self.p.frequency == 'day':
                    time.sleep(19800)
                else:
                    print('等待数据')
                    time.sleep(60*int(self.p.frequency[0:-3]))
        elif self.p.sleep == 0:
            pass
                
        s = self.p.dataname
        frequency = self.p.frequency
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.p.security == 'stock':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", str(self.temp), now_time, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))                     
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", str(self.temp), now_time, "PriceAdj=B")
            
        elif self.p.security == 'future':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", str(self.temp), now_time, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", str(self.temp), now_time, "PriceAdj=B")
                
        elif self.p.security == 'index':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", str(self.temp), now_time, "BarSize="+frequency+";periodstart=09:00:00;periodend="+datetime.datetime.now().strftime('%H:%M:%S'))
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", str(self.temp), now_time, "PriceAdj=B")    
        self.times = data_wind.Times
        self.data = data_wind.Data
        if len(self.times) < 2:
            #print('中午休市，等待数据')
            return None
        bar = [self.times[1]]
        for i in self.data:
            if np.isnan(i[1]) == True:
                #print('停牌了')
                return None
            bar.append(i[1])
        self.lines.datetime[0] = date2num(bar[0])
        self.lines.open[0] = bar[1]
        self.lines.high[0] = bar[2]
        self.lines.low[0] = bar[3]
        self.lines.close[0] = bar[4]
        self.lines.volume[0] = bar[5]
        self.temp = bar[0]
        return True


            
class WindData(DataBase):
    from WindPy import w
#    w.start()
    params = (
        ('nocase', True),
        ('dataname', 'None'),
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('finishdate', datetime.date(2020,3,15)),
        ('frequency', 'day'),
        ('security', 'None'),
        ('sleep', 1),
    )


    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        self._idx = -1
        s = self.p.dataname
        start_date = str(self.p.fromdate.date())
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        frequency = self.p.frequency

        if self.p.security == 'stock':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", start_date, end_date, "BarSize="+frequency)                     
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", start_date, end_date, "PriceAdj=B")
            
        elif self.p.security == 'future':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", start_date, end_date, "BarSize="+frequency)
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", start_date, end_date, "PriceAdj=B")
                
        elif self.p.security == 'index':
            if frequency != 'day':
                data_wind = w.wsi(s, "open,high,low,close,volume", start_date, end_date, "BarSize="+frequency)
            else:
                data_wind = w.wsd(s, "open,high,low,close,volume", start_date, end_date, "PriceAdj=B")
                
        self.times = data_wind.Times
        self.data = data_wind.Data
        self.count = 0


    def _load(self):

        self._idx += 1
        try:
            bar = [self.times[self.count]]
            for i in self.data:
                if np.isnan(i[self.count]) == True:
                    self.count += 1
                    return None
                bar.append(i[self.count])
            self.lines.datetime[0] = date2num(bar[0])
            self.lines.open[0] = bar[1]
            self.lines.high[0] = bar[2]
            self.lines.low[0] = bar[3]
            self.lines.close[0] = bar[4]
            self.lines.volume[0] = bar[5]
            self.count += 1
            return True
        except TypeError:
            return False            


class MySQLDataLive(DataBase):

    params = (
        ('nocase', True),
        ('dataname', 'None'),
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('finishdate', datetime.date(2020,3,15)),
        ('frequency', 'day'),
        ('security', 'None'),
        ('password', '58604496'),
    )

    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        self._idx = -1
        s = self.p.dataname
        start_date = str(self.p.fromdate.date())
        end_date = str(self.p.todate.date())
        frequency = self.p.frequency
        sql_password = self.p.password
        c = 'd_' + frequency + ',open,high,low,close,volume'
        if self.p.security == 'stock':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where stock = '"+ s[2:] +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
                self.security = 'stock'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"  
                self.security = 'stock'
        elif self.p.security == 'future':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
                self.security = 'future'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
                self.security = 'future'  
        elif self.p.security == 'index':
            if self.p.frequency == 'day':
                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
                self.security = 'index'
            else:
                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
                self.security = 'index'
        self.conn = pymysql.connect(user = 'root', password = sql_password, database = 'md_' + self.security)
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql)
        self.description = self.cursor.description
        self.live = 2

    def _load(self):
        self._idx += 1
        try:
            bar = self.cursor.fetchone()
            while None in bar:
                bar = self.cursor.fetchone()
            self.lines.datetime[0] = date2num(bar[0])
            self.lines.open[0] = bar[1]
            self.lines.high[0] = bar[2]
            self.lines.low[0] = bar[3]
            self.lines.close[0] = bar[4]
            self.lines.volume[0] = bar[5]
            #self.lines.openinterest[0] = 0
            return True
        except TypeError:
            self.live -= 1
            if self.p.sleep == 0:
                pass
            else:
                time.sleep(3)
            if self.live == 1:
                print('yes'+self.p.dataname)
                self.lines.datetime[0] = date2num(datetime.datetime(2020,3,3,10,0,0))
                self.lines.open[0] = 4000
                self.lines.high[0] = 4010
                self.lines.low[0] = 3990
                self.lines.close[0] = 4001
                self.lines.volume[0] = 100000
                return True
            else:
                self.conn.close()
                return False
           
            
#class MySQLDataLive(DataBase):
#    params = (
#        ('nocase', True),
#        ('dataname', 'None'),
#        ('datetime', None),
#        ('open', -1),
#        ('high', -1),
#        ('low', -1),
#        ('close', -1),
#        ('volume', -1),
#        ('qcheck', 15),
#        ('finishdate', datetime.date(2020,3,15)),
#        ('frequency', 'day'),
#        ('security', 'None'),
#        ('password', '58604496'),
#    )
#
#
#    def islive(self):
#        '''Returns ``True`` to notify ``Cerebro`` that preloading and runonce
#        should be deactivated'''
#        return True
#    
#    def live(self):
#        return True
#
#    def __init__(self):
#
#        super().__init__()
#        self.p.qcheck = 15
#        self.p._qcheck = 15
#        self._qcheck = 15
#
#    def start(self):
#        super().start()
#        self._idx = -1
#        s = self.p.dataname
#        start_date = str(self.p.fromdate.date())
#        end_date = str(self.p.todate.date())
#        frequency = self.p.frequency
#        sql_password = self.p.password
#        c = 'd_' + frequency + ',open,high,low,close,volume'
#        if self.p.security == 'None':
#            #自动识别有bug，正在修复，谨慎使用
#            if self.p.frequency == 'day':
#                if s[0:2] == 'sz' or s[0:2] == 'sh':
#                    sql = "select "+c+" from md_day where stock = '"+ s[2:] +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                    self.security = 'stock'
#                else:
#                    sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                    self.security = 'future'
#            else:
#                if s[0:2] == 'sz' or s[0:2] == 'sh':
#                    sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"  
#                    self.security = 'stock'
#                else:
#                    sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
#                    self.security = 'future'
#        elif self.p.security == 'stock':
#            if self.p.frequency == 'day':
#                sql = "select "+c+" from md_day where stock = '"+ s[2:] +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                self.security = 'stock'
#            else:
#                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"  
#                self.security = 'stock'
#        elif self.p.security == 'future':
#            if self.p.frequency == 'day':
#                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                self.security = 'future'
#            else:
#                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
#                self.security = 'future'  
#        elif self.p.security == 'index':
#            if self.p.frequency == 'day':
#                sql = "select "+c+" from md_day where contract = '"+ s +"' and d_day > '"+start_date+"' and d_day < '"+end_date+"'"
#                self.security = 'index'
#            else:
#                sql = "select "+c+" from md_" + frequency + "_" + s +" where d_"+ frequency+">'"+start_date+"' and d_"+ frequency+"<'"+end_date+"'"
#                self.security = 'index'
#        self.conn = pymysql.connect(user = 'root', password = sql_password, database = 'md_' + self.security)
#        self.cursor = self.conn.cursor()
#        self.cursor.execute(sql)
#        self.description = self.cursor.description
#        self.count = 2
#
#    def _load(self):
#        self._idx += 1
#        try:
#            bar = self.cursor.fetchone()
#            while None in bar:
#                bar = self.cursor.fetchone()
#            self.lines.datetime[0] = date2num(bar[0])
#            self.lines.open[0] = bar[1]
#            self.lines.high[0] = bar[2]
#            self.lines.low[0] = bar[3]
#            self.lines.close[0] = bar[4]
#            self.lines.volume[0] = bar[5]
#            return True
#        except TypeError:
#            self.count -= 1
#            time.sleep(3)
#            if self.count == 1:
#                print('yes')
#                self.lines.datetime[0] = date2num(datetime.datetime(2020,3,3,10,0,0))
#                self.lines.open[0] = 4000
#                self.lines.high[0] = 4010
#                self.lines.low[0] = 3990
#                self.lines.close[0] = 4001
#                self.lines.volume[0] = 100000
#                return True
#            else:
#                return False
        
#class WindData(DataBase):
#
##    w.start()
#    params = (
#        ('nocase', True),
#        ('dataname', 'None'),
#        ('datetime', None),
#        ('open', -1),
#        ('high', -1),
#        ('low', -1),
#        ('close', -1),
#        ('volume', -1),
#        ('frequency', 'day'),
#        ('security', 'None'),
#    )
#
#
#    def __init__(self):
#        super().__init__()
#
#    def start(self):
#        super().start()
#        self._idx = -1
#        s = self.p.dataname
#        start_date = self.p.fromdate.date()
#        end_date = self.p.todate.date()
#        frequency = self.p.frequency
#
#        if self.p.security == 'None':
#            if frequency != 'day':
#                if s[0:2] == 'sz' or s[0:2] == 'sh':
#                    data_wind = w.wsi(s[2:]+'.'+s[0:2], "close,high,low,open,volume,oi", start_date, end_date, "BarSize="+frequency)                     
#                else:
#                    data_wind = w.wsi(s+'.CFE', "close,high,low,open,volume,oi", start_date, end_date, "BarSize="+frequency)
#            else:
#                if s[0:2] == 'sz' or s[0:2] == 'sh':
#                    data_wind = w.wsd(s[2:]+'.'+s[0:2], "open,high,low,close,volume,oi", start_date, end_date, "PriceAdj=B")                
#                else:
#                    data_wind = w.wsd(s+'.CFE', "open,high,low,close,volume,oi", start_date, end_date, "PriceAdj=B")
#            
#        elif self.p.security == 'stock':
#            if frequency != 'day':
#                data_wind = w.wsi(s[2:]+'.'+s[0:2], "close,high,low,open,volume,oi", start_date, end_date, "BarSize="+frequency)                     
#            else:
#                data_wind = w.wsd(s[2:]+'.'+s[0:2], "open,high,low,close,volume,oi", start_date, end_date, "PriceAdj=B")
#            
#        elif self.p.security == 'future':
#            if frequency != 'day':
#                data_wind = w.wsi(s, "close,high,low,open,volume,oi", start_date, end_date, "BarSize="+frequency)
#            else:
#                data_wind = w.wsd(s, "open,high,low,close,volume,oi", start_date, end_date, "PriceAdj=B")
#        self.times = data_wind.Times
#        self.data = data_wind.Data
#        self.count = 0
#
#    def _load(self):
#        print(9)
#        self._idx += 1
#        try:
#            bar = [self.data.Times[self.count]]
#            for i in self.data:
#                bar.append(i[self.count])
#            self.lines.datetime[0] = date2num(bar[0])
#            self.lines.open[0] = bar[1]
#            self.lines.high[0] = bar[2]
#            self.lines.low[0] = bar[3]
#            self.lines.close[0] = bar[4]
#            self.lines.volume[0] = bar[5]
#            return True
#        except IndexError:
#            return False   