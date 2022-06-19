from django.db import models

import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import datetime as dt

from tensorflow.keras.models import load_model

import re
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
import requests
import pickle

# Create your models here.

with open('./view_chart/data/texts.pkl','rb') as a:
    X_train = pickle.load(a)

# from keras.preprocessing.text import Tokenizer

vocab_size = 40000
tokenizer = Tokenizer(vocab_size+1, oov_token = 'OOV') 
tokenizer.fit_on_texts(X_train)
X_train = tokenizer.texts_to_sequences(X_train)


class NewsAnalysis:
    
    def __init__(self,search_word):
        
        self.client_id = "bzW3U49FrZy_ijT7D5k3" #1.에서 취득한 아이디 넣기
        self.client_secret = "_ojpOWgHKf"  #1. 에서 취득한 키 넣기
        self.search_word = search_word #검색어
        self.encode_type = 'json' #출력 방식 json 또는 xml
        self.max_display = 100 #출력 뉴스 수
        self.sort = 'date' #결과값의 정렬기준 시간순 date, 관련도 순 sim
        self.start = 1 # 출력 위치
        self.url = f"https://openapi.naver.com/v1/search/news.{self.encode_type}?query={search_word}&display={str(int(self.max_display))}&start={str(int(self.start))}&sort={self.sort}"

        
        #헤더에 아이디와 키 정보 넣기 & HTTP요청 보내기
        
    def requestHttp(self):
        
        self.headers = {'X-Naver-Client-Id' : self.client_id,
                   'X-Naver-Client-Secret': self.client_secret
                   }        
        
        self.r = requests.get(self.url, headers=self.headers)
        #요청 결과 보기 200 이면 정상적으로 요청 완료
        return self.r

    def clean_html(self,x):
        self.x = re.sub("\&\w*\;","",x)
        self.x = re.sub("<.*?>","",self.x)
        return self.x
    
    
    def to_dataframe_re_apply(self):
        self.df = pd.DataFrame(self.requestHttp().json()['items']) # 데이터 프레임으로 만들기
        self.df['title'] = self.df['title'].apply(lambda x: self.clean_html(x))
        self.df['description'] = self.df['description'].apply(lambda x: self.clean_html(x))
        return self.df
    

    
    def news_predict(self):
        okt = Okt()
        model = load_model('./view_chart/data/news_predict_v1.h5')
        stopwords = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']
        morphed = []
        dataframe = self.to_dataframe_re_apply()
        for i in range(len(dataframe)):
            new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', dataframe['title'][i])
            new_sentence = re.sub("[\(\[].*?[\)\]]",'', new_sentence)
            new_sentence = okt.morphs(new_sentence, stem=True) # 토큰화
            new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거
            encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
            pad_new = pad_sequences(encoded, maxlen = 30)# 패딩
            score = float(model.predict(pad_new,verbose=0)) # 예측
            if (score > 0.5):
#                 print(dataframe['title'][i])
#                 print("{0:}번 째 기사는 {1:.2f}% 확률로 긍정적 기사입니다.".format((i+1), (score * 100)))
                morphed.append('긍정적인 기사')
            else : 
#                 print(dataframe['title'][i])
#                 print("{0:}번 째 기사는 {1:.2f}% 확률로 부정적 기사입니다.".format((i+1), (1 - score) * 100))
                morphed.append('부정적인 기사')
        dataframe['Prediction'] = morphed
        
        
        return dataframe


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

class PredictSet:
    
    def __init__(self,txt):

        n = dt.datetime.now()
        m = dt.timedelta(100)

        self.txt = txt

        self.start_date = f'{n-m}'[:10]
        self.end_date = f'{n}'[:10]


        self.krx = fdr.StockListing('KRX')
        self.kospi = fdr.DataReader('KS11',self.start_date,self.end_date)['Close'][-50:]
        self.wd_ratio = fdr.DataReader('USD/KRW',self.start_date,self.end_date)['Close']
        self.etf = fdr.DataReader('069500',self.start_date,self.end_date)['Close'][-50:]
        self.us10yt = fdr.DataReader('US10YT=X',self.start_date,self.end_date)['Close']      
        self.symbol = []
        self.result = []
        self.arr = [[] for _ in range(4)]

          
    def fix_df(self):
        
        df_concat=pd.concat([self.kospi,self.us10yt,self.wd_ratio],axis = 1)
        df_concat.columns=["kospi","us10","usd/kr"]
        df_concat.drop(df_concat[np.isnan(df_concat['kospi'])].index,inplace=True)
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
                
        self.wd_ratio = np.array(df_concat['usd/kr'])
        self.us10yt = np.array(df_concat['us10'])
        self.kospi = np.array(df_concat['kospi'])
        
        return self.kospi, self.wd_ratio, self.us10yt

    def check_symbol(self):
        
        self.symbol = self.krx.loc[self.krx['Name']==self.txt,'Symbol'].values[0]
            
        return self.symbol

    def check_price(self, n=50):
        
        
        stock = fdr.DataReader(self.symbol,self.start_date)['Close']
        self.origin = stock[0]
        self.today = stock[-1]
        
        self.result.append(stock[-50:].to_list())
        
        self.arr[0].append(self.kospi)
        self.arr[1].append(self.wd_ratio)
        self.arr[2].append(self.us10yt)
        self.arr[3].append(self.etf)

        return self.result, self.arr, self.origin, self.today

    def scaling(self):

        normalized_data = []
        
        for window in self.result:
            normalized_window = [((float(p)/float(window[0]))-1) for p in window]
            normalized_data.append(normalized_window)

        self.result = np.array(normalized_data)
        
        for i in range(len(self.arr)):
            
            normalized_data = []
            
            for window in self.arr[i]:
                normalized_window = [((float(p)/float(window[0]))-1) for p in window]
                normalized_data.append(normalized_window)
            
            self.arr[i] = np.array(normalized_data)
            

        return self.result, self.arr
    
    def stock_output(self,):
        
        df = pd.DataFrame(index=range(len(self.result)),
                          columns={'f1','f2','f3','f4','f5'})
        df.columns = ['f1','f2','f3','f4','f5']
        
        for i in range(len(self.result)):
            df.loc[i,'f1'] = self.result[i]
            df.loc[i,'f2'] = self.arr[0][i]
            df.loc[i,'f3'] = self.arr[1][i]
            df.loc[i,'f4'] = self.arr[2][i]
            df.loc[i,'f5'] = self.arr[3][i]
            
        self.df_fix = np.array([i for i in df.loc[0]]).reshape(1,5,50,1)
            
        return self.df_fix

    def all_in_one(self):
        
        self.check_symbol()
        self.fix_df()
        self.check_price()
        self.scaling()
        self.stock_output()
        
        return self.df_fix, self.origin, self.today

    def data_expand(self):
        pass

class Fitting:
    
    def __init__(self):
        self.md = load_model('./view_chart/data/model.h5')
        
md = Fitting().md

lst, stock, kospi, etf, wd_ratio, us10yt = MakeSet('삼성전자').all_in_one()

class Stock(models.Model):
    stock_name = models.CharField(max_length = 255, default='')
    stock_price_tm = models.IntegerField(default='0')
    stock_price_td = models.IntegerField(default='0')
    stock_text = models.CharField(max_length=255, default='')
    
    def __str__(self):
        return f'[{self.stock_name}] {self.stock_price_tm} {self.stock_price_td} {self.stock_text}'

class NewsText(models.Model):
    stock_text = models.CharField(max_length=255,default='')
    stock_title = models.TextField()
    stock_url = models.TextField()
    
    def __str__(self):
        return f'[{self.stock_text}] {self.stock_title} {self.stock_url}'