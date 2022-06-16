from django.urls import path
from . import views

urlpatterns = [
    path('',views.chart),
    # path('',views.index),
    path('result/',views.inputStock)
]
