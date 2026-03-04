from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import UserViewset, OrganizationViewset


routers = DefaultRouter()
routers.register(r'user', UserViewset , basename='user' )
routers.register(r'organizatin', OrganizationViewset , basename='organization')

urlpatterns = [
    path('acc/', include(routers.urls))
]