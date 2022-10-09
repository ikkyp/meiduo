from django.urls import path

from apps.users.views import UsernameCountView, RegisterView, LoginView, LogoutView

urlpatterns = [
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
]
