from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.db.models import Q, Count
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Article, Category, Comment, Tag
from .forms import CommentForm, ArticleForm


class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        queryset = Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()

        # Category filter
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Tag filter
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # Featured articles filter
        is_featured = self.request.GET.get('featured')
        if is_featured == 'true':
            queryset = queryset.filter(is_featured=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(article_count=Count('article')).filter(article_count__gt=0)
        context['tags'] = Tag.objects.annotate(article_count=Count('articles')).filter(article_count__gt=0)[:20]
        context['featured_articles'] = Article.objects.filter(status='published', is_featured=True)[:3]
        context['current_category'] = self.kwargs.get('category_slug')
        context['current_tag'] = self.kwargs.get('tag_slug')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ArticleDetailView(FormMixin, DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    form_class = CommentForm

    def get_object(self):
        slug = self.kwargs.get('slug')
        article = get_object_or_404(Article, slug=slug, status='published')

        # Increment view count
        article.views_count += 1
        article.save(update_fields=['views_count'])

        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True, parent=None).order_by('created_at')
        context['related_articles'] = Article.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid() and request.user.is_authenticated:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object
        comment.author = self.request.user

        # Handle reply to parent comment
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            parent_comment = get_object_or_404(Comment, pk=parent_id, article=self.object)
            comment.parent = parent_comment

        comment.save()
        messages.success(self.request, 'Your comment has been posted successfully!')
        return redirect('blog:article_detail', slug=self.object.slug)


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('blog:article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.cleaned_data['save_as_draft']:
            form.instance.status = 'draft'
        else:
            form.instance.status = 'published'
            form.instance.published_at = timezone.now()

        messages.success(self.request, f'Article "{form.instance.title}" has been {"published" if form.instance.status == "published" else "saved as draft"}!')
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def form_valid(self, form):
        if form.cleaned_data['save_as_draft']:
            form.instance.status = 'draft'
        elif form.instance.status == 'draft' and not form.cleaned_data['save_as_draft']:
            form.instance.status = 'published'
            form.instance.published_at = timezone.now()

        messages.success(self.request, f'Article "{form.instance.title}" has been updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.object.slug})


@login_required
def like_article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if request.method == 'POST':
        # Toggle like functionality (simplified version)
        # In a real implementation, you'd have a separate Like model
        data = {
            'status': 'success',
            'message': 'Article liked!'
        }
        return JsonResponse(data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


class CategoryDetailView(ListView):
    model = Article
    template_name = 'blog/category_detail.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        self.category = get_object_or_404(Category, slug=category_slug)
        return Article.objects.filter(category=self.category, status='published').select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.annotate(article_count=Count('article')).filter(article_count__gt=0)
        return context


class TagDetailView(ListView):
    model = Article
    template_name = 'blog/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        tag_slug = self.kwargs.get('slug')
        self.tag = get_object_or_404(Tag, slug=tag_slug)
        return Article.objects.filter(tags=self.tag, status='published').select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['tags'] = Tag.objects.annotate(article_count=Count('articles')).filter(article_count__gt=0)
        return context


def search_articles(request):
    query = request.GET.get('q')
    articles = []

    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(tags__name__icontains=query)
        ).filter(status='published').select_related('author', 'category').distinct()

    context = {
        'articles': articles,
        'search_query': query or '',
        'categories': Category.objects.annotate(article_count=Count('article')).filter(article_count__gt=0),
        'tags': Tag.objects.annotate(article_count=Count('articles')).filter(article_count__gt=0)[:20],
    }

    return render(request, 'blog/search_results.html', context)