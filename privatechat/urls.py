from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'msglist', views.PrivateMessageViewset)


urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.userlist, name = 'userlist'),
    path('<int:id>/', views.privatechat, name = 'privatechat'),
]