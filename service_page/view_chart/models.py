from django.db import models

import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt

from tensorflow.keras.models import load_model

# Create your models here.

class fitting:
    
    def __init__(self):
        self.model = load_model('./view_chart/data/model.h5')

class MakeSet:
    
    def __init__(self,txt):
        
        n = dt.datetime.now()
        m = dt.timedelta(100)

        self.txt = txt

        self.result = []
        self.arr = [[] for _ in range(4)]

        self.start_date = f'{n-m}'[:10]
        self.end_date = f'{n}'[:10]
        
    def price_list(self):
    
        self.krx = fdr.StockListing('KRX')
        self.symbol = self.krx.loc[self.krx['Name'] == self.txt,'Symbol'].values[0]

        self.stock = fdr.DataReader(self.symbol,self.start_date,self.end_date)['Close'][-50:]
        self.kospi = fdr.DataReader('KS11',self.start_date,self.end_date)['Close'][-50:]
        self.wd_ratio = fdr.DataReader('USD/KRW',self.start_date,self.end_date)['Close']
        self.etf = fdr.DataReader('069500',self.start_date,self.end_date)['Close'][-50:]
        self.us10yt = fdr.DataReader('US10YT=X',self.start_date,self.end_date)['Close']
         
    def price_fix(self):
        
        drop_lst = self.stock.index
        
        for j in [self.wd_ratio,self.us10yt]:
            for i in j.index:
                if i not in drop_lst:
                    del j[i]
                    
        df_concat = pd.concat([self.stock,self.wd_ratio,self.us10yt],axis = 1)
        df_concat.columns=["stock","usd/kr","us10"]
        df_concat.drop(df_concat[np.isnan(df_concat['stock'])].index,inplace=True)
        df_concat.reset_index(inplace=True)
        
        for i in df_concat[np.isnan(df_concat['us10'])].index:
            if i > 0:
                df_concat.loc[i,'us10'] = df_concat.loc[i-1,'us10']
            else:
                df_concat.loc[i,'us10'] = df_concat.loc[i+1,'us10']
        
        for i in df_concat[np.isnan(df_concat['usd/kr'])].index:
            if i > 0:
                df_concat.loc[i,'usd/kr'] = df_concat.loc[i+1,'usd/kr']
            else:
                df_concat.loc[i,'usd/kr'] = df_concat.loc[i-1,'usd/kr']
        
        date_list = self.stock.index
        self.stock = self.stock.to_list()
        self.kospi = self.kospi.to_list()
        self.etf = self.etf.to_list()
        self.wd_ratio = df_concat['usd/kr'].to_list()
        self.us10yt = df_concat['us10'].to_list()
        
        return date_list, self.stock, self.kospi, self.etf, self.wd_ratio, self.us10yt
    
    def all_in_one(self):
        
        self.price_list()
        
        return self.price_fix()
    
lst, stock, kospi, wd_ratio, etf, us10yt = MakeSet('삼성전자').all_in_one()

md = fitting().model

class Stock(models.Model):
    content = models.CharField(max_length = 255)