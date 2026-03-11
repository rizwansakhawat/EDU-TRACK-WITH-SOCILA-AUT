from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import UserViewset, OrganizationViewset

from courses.views import CouserViewset
from core.views import InstituteViewset
from enrollments.views import EnrollmentViewSet, PaymentViewSet
from reports.views import CertificateViewSet



routers = DefaultRouter()
routers.register(r'user', UserViewset , basename='user' )
routers.register(r'organizatin', OrganizationViewset , basename='organization')

routers.register(r'courses', CouserViewset, basename="course")
routers.register(r'institute', InstituteViewset, basename='institute')
routers.register(r'enrollment', EnrollmentViewSet, basename='enrollment')
routers.register(r'pyment', PaymentViewSet, basename='payment')
routers.register(r"certificates", CertificateViewSet, basename='certificates')


urlpatterns = [
    path('', include(routers.urls)),
    
]