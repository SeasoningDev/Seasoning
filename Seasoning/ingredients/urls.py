from django.conf.urls import url
from ingredients import views

urlpatterns = [
    url(r'^names/$', views.get_ingredient_name_list, name='get_ingredient_name_list'),
]
