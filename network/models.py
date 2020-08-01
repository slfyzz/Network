from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Post (models.Model):

    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    body = models.TextField(blank=False)
    timeStamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", related_name="likedPosts", blank=True)

    def serialize(self, user):
        return {
            'id' : self.id,
            'owner' : self.owner.username,
            'body' : self.body,
            'timestamp' : self.timeStamp.strftime("%b %d %Y, %I:%M %p"),
            'likes' : [user.username for user in self.likes.all()],
            'liked' : user in self.likes.all(),
            'currentUser' : user.username
        }


class User(AbstractUser):
    followers = models.ManyToManyField("User", related_name="following", blank=True)

    def serialize(self, user):
        return {
            'id' : self.id,
            'userName' : self.username,
            'email' : self.email,
            'followers' : [user.username for user in self.followers.all()],
            'following' : [user.username for user in self.following.all()],
            'posts' : [post.serialize(user) for post in self.posts.all()]
        }

