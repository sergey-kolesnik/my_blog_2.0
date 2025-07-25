from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import (
    Post,
    Category,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.formats import date_format
from django.utils.timezone import localtime



from .forms import PostCreateForm, PostUpdateForm, CommentCreateForm
from services.mixins import AuthorRequiredMixin

class PostListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 2
    queryset = Post.custom.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        return context


class PostFromCategory(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    category = None
    paginate_by = 1

    def get_queryset(self):
        # pylint: disable=E1101
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        queryset = Post.objects.filter(category=self.category)
        if not queryset:
            sub_cat = Category.objects.filter(parent=self.category)
            queryset = Post.objects.filter(category__in=sub_cat)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Записи из категории: {self.category.title}"
        return context
    


class PostCreateView(CreateView, LoginRequiredMixin):
    """
    Представление: создание материалов на сайте
    """
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление статьи на сайт'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Представление: обновления материала на сайте
    """
    model = Post
    template_name = 'blog/post_update.html'
    context_object_name = 'post'
    form_class = PostUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление статьи: {self.object.title}'
        return context

    def form_valid(self, form):
        form.instance.updater = self.request.user
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': date_format(
                    localtime(comment.time_create),
                    format='DATETIME_FORMAT',
                    use_l10n=True,
                ),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)

        return redirect(comment.post.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)
