from django.urls import path
from . import views

urlpatterns = [
    path('',views.chart),
    # path('',views.index),
    path('result2/',views.inputStock)
]
