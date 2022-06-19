from django.shortcuts import render
from .models import *
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def chart(request):
    
    df = pd.DataFrame([stock,kospi,etf,wd_ratio,us10yt]).T
    df.index = lst.astype(str)
    df.columns = ['주가','코스피','ETF','원달러 환율','미 국채 금리']
    df = df.reset_index()
        
    fig1 = make_subplots(
        horizontal_spacing=0.03,
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.01,
        specs=[[{"type": "table"}]])
    
    
    fig1.add_trace(
        go.Table(
            header=dict(
                values=["날짜","주가", "KOSPI",
                        "ETF", "원/달러 환율", "미 국채 10년 금리"],
                font=dict(size=10),
                align="left",
                fill_color='rgb(248, 232, 249)'
            ),
            cells=dict(
                values=[df[k].tolist() for k in df.columns],
                align = "left",fill_color='rgb(248, 242, 249)')
        ),
        row=1, col=1
    )
    fig1.update_layout(
        height=1000,
        showlegend=True,
    )
    fig1.layout.margin.update({'t':0, 'b':0,'r':0,'l':0})
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(y=df['주가'],x=df['Date'],
                        mode='lines+markers',
                             line_color='green'))
    fig2.layout.margin.update({'t':0, 'b':0,'r':0,'l':0})
    fig2.update_layout({'height':200},plot_bgcolor='rgb(248, 237, 249)'
    )
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(y=df['코스피'],x=df['Date'],
                        mode='lines+markers',
                             line_color='red'))
    fig3.layout.margin.update({'t':0, 'b':0,'r':0,'l':0})
    fig3.update_layout({'height':200},plot_bgcolor='rgb(248, 237, 249)'
    )
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(y=df['ETF'],x=df['Date'],
                        mode='lines+markers',
                             line_color='purple'))
    fig4.layout.margin.update({'t':0, 'b':0,'r':0,'l':0})
    fig4.update_layout({'height':200},plot_bgcolor='rgb(248, 237, 249)'
    )
    
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(y=df['원달러 환율'],x=df['Date'],
                              mode='lines+markers',
                             line_color='blue'))
    fig5.layout.margin.update({'t':0, 'b':0,'r':0,'l':0})
    fig5.update_layout({'height':200},plot_bgcolor='rgb(248, 237, 249)'
    )
    
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(y=df['미 국채 금리'],x=df['Date'],
                        mode='lines+markers',
                             line_color='black'))
    fig6.layout.margin.update({'t':0, 'b':0,'r':0,'l':0})
    fig6.update_layout({'height':200},plot_bgcolor='rgb(248, 237, 249)'
    )
    
    graphs1 = fig1._repr_html_()
    graphs2 = fig2._repr_html_()
    graphs3 = fig3._repr_html_()
    graphs4 = fig4._repr_html_()
    graphs5 = fig5._repr_html_()
    graphs6 = fig6._repr_html_()
    
    stocks = Stock.objects.get(id=1)
    n_texts = NewsText.objects.all()
    
    return render(
        request,
        'view_chart/chart.html',
        {'graph1':graphs1,
         'graph2':graphs2,
         'graph3':graphs3,
         'graph4':graphs4,
         'graph5':graphs5,
         'graph6':graphs6,
         'stock':stocks,
         'texts':n_texts
         }
    )

# def index(request):
#     return render(request, 'view_chart/chart.html')

def inputStock(request):

    input_stock = request.POST['stockName']

    
    dataset, origin, today = PredictSet(input_stock).all_in_one()
    stock_result = origin + md.predict(dataset)[0] * origin
    
    get_df = NewsAnalysis(input_stock)
    pred_df = get_df.news_predict()
    pred_text = pred_df['Prediction'].value_counts()
    text_result = f'긍정적인 기사 : {pred_text[0]} / 부정적인 기사 : {pred_text[1]}'
    
    pleaseplease = Stock(id=1, stock_name=input_stock,
                         stock_price_tm=int(stock_result),
                         stock_price_td=int(today),
                         stock_text=text_result)
    pleaseplease.save()
    
    for i in range(0,100):
        pleaseplease2 = NewsText(id=i+1,
                                 stock_text=input_stock,
                                 stock_title=pred_df.loc[i,'title'],
                                 stock_url=pred_df.loc[i,'link'])
        pleaseplease2.save()

    
    return HttpResponseRedirect('/chart/')