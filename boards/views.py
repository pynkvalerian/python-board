from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from boards.models import Board, Topic, Post
from boards.forms import NewTopicForm, NewPostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'

@login_required
def board_topics(request, pk):
    board = Board.objects.get(pk=pk)
    queryset = board.topics.order_by('-updated_at').annotate(replies=Count('posts')-1)

    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)
    form = NewTopicForm()
    return render(request, 'topics.html', {'board': board, 'topics': topics, 'form': form})

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
    topic.add_views()
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

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
