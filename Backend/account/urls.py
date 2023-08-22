from django.urls import path, include
from .views import Register, Login, Logout, GetProfileData, GetUserData, UpdateProfile

urlpatterns = [
    path("register", Register.as_view()),
    path("login", Login.as_view()),
    path("logout", Logout.as_view()),
    # path("getprofile", GetProfileData.as_view()),
    path("user/<str:username>", GetUserData.as_view()),
    path("updateprofile/<str:username>", UpdateProfile.as_view()),
]
