from django.urls import path

from apps.oauth.views import LoginUrlView, OauthQQView

urlpatterns = [
    path('qq/authorization/', LoginUrlView.as_view()),
    path('oauth_callback/', OauthQQView.as_view()),
]
