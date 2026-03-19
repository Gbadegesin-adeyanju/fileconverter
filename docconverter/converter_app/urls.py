from django.urls import path
from . import views
from .viewset import converterView, emailSubscribeView, imageView

urlpatterns = [
    path('',views.index,name='index'),
    # path('api/',views.apiview,name='api'),
    path('file-upload/', converterView.as_view(), name='file_upload'),
    path('image-upload/', imageView.as_view(), name='image_upload'),
    path('subscribe/', emailSubscribeView.as_view(), name='subscribe')
    
]

    
    