from django.shortcuts import render
from .models import *
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.http import HttpResponse

# Create your views here.

def chart(request):
    
    df = pd.DataFrame([stock,kospi,etf,wd_ratio,us10yt]).T
    df.index = lst.astype(str)
    df.columns = ['주가','코스피','ETF','원달러 환율','미 국채 금리']
    df = df.reset_index()
    
    fig = make_subplots(
        rows=6, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
               [{"type": "scatter"}],
               [{"type": "scatter"}],
               [{"type": "scatter"}],
               [{"type": "scatter"}],
               [{"type": "scatter"}]])
    
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["주가"],
            mode="lines",
            name="주가"
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["코스피"],
            mode="lines",
            name="코스피 지수"
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["ETF"],
            mode="lines",
            name="ETF"
        ),
        row=4, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["원달러 환율"],
            mode="lines",
            name="원/달러 환율"
        ),
        row=5, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["미 국채 금리"],
            mode="lines",
            name="미 국채 10년 금리"
        ),
        row=6, col=1
    )
    
    fig.add_trace(
        go.Table(
            header=dict(
                values=["날짜","주가", "코스피",
                        "ETF", "원/달러 환율", "미 국채 10년 금리"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[df[k].tolist() for k in df.columns],
                align = "left")
        ),
        row=1, col=1
    )
    fig.update_layout(
        height=1000,
        showlegend=False,
        title_text="주가 예측 기반 데이터",
    )
    
    graphs = fig._repr_html_()
    
    return render(
        request,
        'view_chart/chart.html',
        {'graph':graphs}
    )


def calcStock(request):
    input_stock = request.POST['stockName']
    stock_name = Stock('input_stock').all_in_one()[1]
    stock_name.save()
    return HttpResponse("주식 종목 =>"+input_stock)
