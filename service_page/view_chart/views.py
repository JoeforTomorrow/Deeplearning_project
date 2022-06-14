from django.shortcuts import render
from .models import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create your views here.

def chart(request):
    
    sns.set_theme(style="whitegrid")
    data = pd.DataFrame(np.array([stock]).reshape(50,1), lst, columns = ['stock'])
    sns.lineplot(data=data, palette="tab10", linewidth=2.5)
    
    pass
    
    # # graphs = _OBJECT._repr_html_()
    
    # return render(
    #     request,
    #     'view_chart/chart.html',
    #     {'graph':graphs}
    # )