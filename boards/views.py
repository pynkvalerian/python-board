from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from boards.models import Board, Topic, Post
from boards.forms import NewTopicForm, NewPostForm
from django.contrib.auth.decorators import login_required

def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})

@login_required
def board_topics(request, pk):
    board = Board.objects.get(pk=pk)
    form = NewTopicForm()
    return render(request, 'topics.html', {'board': board, 'form': form})

def new_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('board_topics', pk=board.pk)
    else:
        form = NewTopicForm()
    return render(request, 'topics.html', {'form': form, 'board': board})

def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    posts = topic.posts.all()
    form = NewPostForm()
    return render(request, 'topic_posts.html', {'topic': topic, 'posts': posts, 'form': form})

def new_topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=topic.board.pk, topic_pk=topic.pk)
    else:
        form = NewPostForm()
        posts = topic.posts.all()
    return render(request, 'topic_posts.html', {'topic': topic, 'posts': posts, 'form': form})
