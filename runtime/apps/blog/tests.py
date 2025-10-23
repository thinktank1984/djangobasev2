from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Article, Category, Comment, Tag


class BlogModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )

    def test_category_creation(self):
        """Test category model creation and string representation"""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(str(self.category), 'Test Category')

    def test_tag_creation(self):
        """Test tag model creation and string representation"""
        self.assertEqual(self.tag.name, 'Test Tag')
        self.assertEqual(self.tag.slug, 'test-tag')
        self.assertEqual(str(self.tag), 'Test Tag')

    def test_article_creation(self):
        """Test article model creation"""
        article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            author=self.user,
            category=self.category,
            content='This is a test article content.',
            excerpt='Test article excerpt.',
            status='published',
            published_at=timezone.now()
        )
        article.tags.add(self.tag)

        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.category, self.category)
        self.assertEqual(article.status, 'published')
        self.assertEqual(str(article), 'Test Article')
        self.assertEqual(article.get_comments_count(), 0)

    def test_article_slug_auto_generation(self):
        """Test that slug is automatically generated from title"""
        article = Article.objects.create(
            title='Test Article Title With Spaces',
            author=self.user,
            content='Test content',
            excerpt='Test excerpt',
            status='draft'
        )
        self.assertEqual(article.slug, 'test-article-title-with-spaces')

    def test_comment_creation(self):
        """Test comment model creation"""
        article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            author=self.user,
            content='Test content',
            excerpt='Test excerpt',
            status='published'
        )
        comment = Comment.objects.create(
            article=article,
            author=self.user,
            content='This is a test comment.'
        )
        self.assertEqual(comment.article, article)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(str(comment), f'Comment by {self.user.username} on {article.title}')


class BlogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.published_article = Article.objects.create(
            title='Published Article',
            slug='published-article',
            author=self.user,
            category=self.category,
            content='Published article content.',
            excerpt='Published article excerpt.',
            status='published',
            published_at=timezone.now()
        )
        self.draft_article = Article.objects.create(
            title='Draft Article',
            slug='draft-article',
            author=self.user,
            content='Draft article content.',
            excerpt='Draft article excerpt.',
            status='draft'
        )

    def test_article_list_view(self):
        """Test article list view shows only published articles"""
        response = self.client.get(reverse('blog:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Article')
        self.assertNotContains(response, 'Draft Article')

    def test_article_detail_view(self):
        """Test article detail view for published article"""
        response = self.client.get(
            reverse('blog:article_detail', kwargs={'slug': 'published-article'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Article')
        self.assertContains(response, 'Published article content.')

    def test_article_detail_view_draft_not_accessible(self):
        """Test that draft articles are not accessible"""
        response = self.client.get(
            reverse('blog:article_detail', kwargs={'slug': 'draft-article'})
        )
        self.assertEqual(response.status_code, 404)

    def test_category_detail_view(self):
        """Test category detail view"""
        response = self.client.get(
            reverse('blog:category_detail', kwargs={'slug': 'test-category'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
        self.assertContains(response, 'Published Article')

    def test_search_view(self):
        """Test search functionality"""
        response = self.client.get(reverse('blog:search'), {'q': 'Published'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Article')

    def test_article_create_view_requires_login(self):
        """Test that article creation requires login"""
        response = self.client.get(reverse('blog:article_create'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login

    def test_article_create_view_logged_in(self):
        """Test article creation view for logged in user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:article_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Article')