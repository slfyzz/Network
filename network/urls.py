
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts/<str:following>/<int:page>", views.posts, name="posts"),
    path("profile/<str:username>/posts/<int:page>", views.postsByName, name="postsByName"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("post", views.post, name="post"),
    path("like", views.like, name="like"),
    path("editPost", views.editPost, name="editPost"),
    path("posts/<int:page>", views.showPosts, name="showPost")
]
