from django.urls import path
from .views import (
    PostListView,
    PostDetailview,
    )


urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("post/<slug:slug>/", PostDetailview.as_view(), name="post_detail"),
]

