from django.urls import path, re_path
from . import views
from django.views.generic import RedirectView
from . import dash_plots
from . import dash_table

urlpatterns = [
    path('', views.start, name='start'),
    path('home', views.home, name='home'),
    path('premier_league', views.premier_league, name='premier_league'),
    path('serie_a', views.serie_a, name='serie_a'),
    path('la_liga', views.la_liga, name='la_liga'),
    path('regression', views.regression, name='regression'),
    path('random_forst', views.random_forest, name='random_forest'),
    path('neural_network', views.neural_network, name='neural_network'),
    path('training', views.training, name='training'),
    path('predicting', views.predicting, name='predicting'),
    path('visualisation', views.visualisation, name='visualisation'),
    path('table', views.table, name='table'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico'))
]
