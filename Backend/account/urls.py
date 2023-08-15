from django.urls import path, include
from .views import Register, Login, Logout, GetProfileData, GetUserData, UpdateProfile

urlpatterns = [
    path("register", Register.as_view()),
    path("login", Login.as_view()),
    path("logout", Logout.as_view()),
    # path("getprofile", GetProfileData.as_view()),
    path("getuser", GetUserData.as_view()),
    path("updateprofile", UpdateProfile.as_view()),
    # TODO:
    # path("<str:username>", GetUserData.as_view()),
]
