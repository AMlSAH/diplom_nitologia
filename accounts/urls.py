from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ConfirmEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm-email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
