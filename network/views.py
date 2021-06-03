from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

import json
from .models import User, Post


def index(request):
    return render(request, "network/index.html") 

@csrf_exempt
@login_required
def post(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Post is required"}, status=400)
    try:
        data = json.loads(request.body)
        postBody = data.get("post")
        if postBody == "":
            return JsonResponse({"error" : "Can't Post empty post"}, status=400)
    except KeyError:
        return JsonResponse({"error" : "Can't Post empty post"}, status=400)

    post = Post(
        owner=request.user,
        body=postBody
    )
    post.save()
    return JsonResponse({'message':"The post has been uploaded Successfully"})


# need a profile page
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("Not found")
    if request.user.is_authenticated:
        context = {
            'profile' : user.serialize(request.user),
            'user' : request.user.username or 'None',
            'followed' : user in request.user.following.all(),
            'login' : request.user.is_authenticated
        }
    else :
        context = {
            'profile' : user.serialize(request.user),   
            'user' : 'None',
            'login' : request.user.is_authenticated
        }
    return JsonResponse(context, safe=False)


def postsByName(request, username, page):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("Not found")
    
    posts = user.posts.order_by('-timeStamp')
    p = Paginator(posts, 10)
    ls = paginator(page, p)
    
    context = {
        'posts' : [post.serialize(request.user) for post in p.page(page).object_list],  
        'paginator' : ls,
        'login' : request.user.is_authenticated
      
    }
    return JsonResponse(context,  safe=False)


#need a post page
def posts(request, page, following):

    if following == "true":
        posts = Post.objects.filter(owner__in=request.user.following.all()).order_by('-timeStamp')
    else:
        posts = Post.objects.order_by('-timeStamp')
        
    p = Paginator(posts, 10)
    if page > p.num_pages:
        return JsonResponse({'error' : "there's no posts in that page"})

    ls = paginator(page, p)
    context = {
        'posts' : [post.serialize(request.user) for post in p.page(page).object_list],
        'paginator' : ls,
        'login' : request.user.is_authenticated
        }

    return JsonResponse(context , safe=False)
 


def showPosts(request, page):
    return HttpResponseRedirect(reverse('posts', args=("false", page,)))

@csrf_exempt
@login_required
def editPost(request):
    if request.method != 'PUT':
        return JsonResponse({'error' : "must be accessed by PUT request"})
    data = json.loads(request.body)
    try:
        postId = data.get('id')
        body = data.get('body')
        post = Post.objects.get(pk=postId)
    except KeyError:
        return JsonResponse({'error' : "some info is missing"})
    except Post.DoesNotExist:
        return JsonResponse({'error' : "No post with such an id"})

    post.body = body
    post.save()
    return JsonResponse({'success' : "Done Successfully"})




@csrf_exempt
@login_required
def follow(request):
    if request.method != 'PUT':
        return JsonResponse({'error' : "must be accessed by PUT request"})
    try :
        data = json.loads(request.body)
        user = int(data.get('user'))
        userAccount = User.objects.get(pk=user)

    except KeyError:
        return JsonResponse({'error' : "id of a user must be sent"})
    except User.DoesNotExist:
        return JsonResponse({'error' : "no user with such that id"})

    userAccount.followers.add(request.user)
    return JsonResponse({'success' : "Done Successfully"})

@csrf_exempt
@login_required
def unfollow(request):
    if request.method != 'PUT':
        return JsonResponse({'error' : "must be accessed by PUT request"})

    try:
        data = json.loads(request.body)
        user = int(data.get('user'))
        userAccount = User.objects.get(pk=user)
    except KeyError:
        return JsonResponse({'error' : "id of a user must be sent"})
    except User.DoesNotExist:
        return JsonResponse({'error' : "no user with such that id"})

    if request.user not in userAccount.followers.all():
        return JsonResponse({'error' : "cant unfollow without following"})

    userAccount.followers.remove(request.user)
    return JsonResponse({'success' : "Done Successfully"})


@csrf_exempt
@login_required
def like(request):
    if request.method != 'PUT':
        return JsonResponse({'error' : "must be accessed by PUT request"})
    
    try:
        data = json.loads(request.body)
        post = int(data.get('postId'))
        postObject = Post.objects.get(pk=post)
    except KeyError:
        return JsonResponse({'error' : "id of a post must be sent"})
    except Post.DoesNotExist:
        return JsonResponse({'error' : "no post with such that id"})
    
    #print(postObject.likes.all())
    #print(request.user)

    if request.user not in postObject.likes.all():
        postObject.likes.add(request.user)
    else:
        postObject.likes.remove(request.user)

    #print(postObject.likes.all())
    postObject.save()
    return JsonResponse({'success' : "Done Successfully"})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def paginator(page, p):

    ls = [page] 
    print(p.num_pages)
    if page + 1  <= p.num_pages:
        ls.append(page + 1)

    if page == 1 and page + 2 <= p.num_pages: 
        ls.append(page + 2)
    elif page == p.num_pages:
        if page - 1 > 0:
            ls.insert(0, page - 1)
        if page - 2 > 0:
            ls.insert(0, page - 2)
    
    elif page > 1 and page < p.num_pages:
        ls.append(page + 1)
        ls.insert(0, page -1)


    return ls
