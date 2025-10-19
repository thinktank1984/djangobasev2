from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Article URLs
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('article/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('article/<slug:slug>/like/', views.like_article, name='like_article'),

    # Category URLs
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/<slug:slug>/articles/', views.CategoryDetailView.as_view(), name='category_articles'),

    # Tag URLs
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('tag/<slug:slug>/articles/', views.TagDetailView.as_view(), name='tag_articles'),

    # Search URL
    path('search/', views.search_articles, name='search'),

    # Featured articles
    path('featured/', views.ArticleListView.as_view(), name='featured_articles'),
]