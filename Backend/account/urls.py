from django.urls import path, include
from .views import Register, Login, Logout, GetUserData, UpdateProfile

urlpatterns = [
    path("register", Register.as_view()), # Register new user
    path("login", Login.as_view()), # Login
    path("logout", Logout.as_view()), # Logout
    path("user/<str:username>", GetUserData.as_view()), # Get user data
    path("updateprofile/<str:username>", UpdateProfile.as_view()), # Update profile
]
