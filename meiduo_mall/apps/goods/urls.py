from django.urls import path

from apps.goods.views import IndexView, ListView, SKUIndex, DetailView, UserBrowseHistory

urlpatterns = [
    path('index/', IndexView.as_view()),
    path('list/<category_id>/skus/', ListView.as_view()),
    path('search/', SKUIndex()),
    path('detail/<sku_id>/', DetailView.as_view()),
    path('browse_histories/', UserBrowseHistory.as_view()),
]
