#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.blog.models import Category, Article, Tag, Comment

def create_sample_data():
    # Create a superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created superuser: admin")

    # Create a regular user
    user, created = User.objects.get_or_create(
        username='blogger',
        defaults={'email': 'blogger@example.com', 'first_name': 'John', 'last_name': 'Doe'}
    )
    if created:
        user.set_password('password123')
        user.save()
        print("Created user: blogger")

    # Create categories
    categories_data = [
        {'name': 'Technology', 'description': 'Latest tech news and insights'},
        {'name': 'Programming', 'description': 'Programming tutorials and tips'},
        {'name': 'Web Development', 'description': 'Web dev best practices'},
        {'name': 'Data Science', 'description': 'Data analysis and machine learning'},
        {'name': 'Django', 'description': 'Django framework specific content'},
    ]

    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")

    # Create tags
    tags_data = [
        'python', 'django', 'javascript', 'react', 'vue', 'web-dev',
        'tutorial', 'tips', 'best-practices', 'machine-learning', 'ai',
        'database', 'api', 'frontend', 'backend', 'devops'
    ]

    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        if created:
            print(f"Created tag: {tag.name}")

    # Create sample articles
    articles_data = [
        {
            'title': 'Getting Started with Django 5.0',
            'excerpt': 'Learn how to build modern web applications with Django 5.0, the latest version of the popular Python web framework.',
            'content': '''Django 5.0 brings exciting new features and improvements to the web development landscape. In this comprehensive guide, we'll explore everything you need to know to get started with this powerful framework.

## What's New in Django 5.0?

Django 5.0 introduces several significant improvements:

1. **Enhanced Performance**: Better caching and query optimization
2. **Improved Admin Interface**: More intuitive and responsive design
3. **Better Security**: Updated security middleware and features
4. **Async Support**: Improved async view handling

## Setting Up Your First Django Project

To create a new Django project, run:

```bash
pip install django
django-admin startproject myproject
cd myproject
python manage.py runserver
```

## Creating Models

Models are the heart of Django applications. Here's an example:

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

## Conclusion

Django 5.0 is an excellent choice for web development, offering a perfect balance between power and simplicity. Start building your next project today!''',
            'category': 'Django',
            'tags': ['python', 'django', 'web-dev', 'tutorial'],
            'read_time': 8,
            'is_featured': True
        },
        {
            'title': 'Python Best Practices for 2024',
            'excerpt': 'Discover the latest Python best practices and patterns that every developer should know in 2024.',
            'content': '''Python continues to evolve as one of the most popular programming languages. Here are the best practices you should follow in 2024.

## 1. Use Type Hints

Type hints make your code more readable and maintainable:

```python
from typing import List, Dict, Optional

def process_data(data: List[Dict[str, str]]) -> Optional[str]:
    return data[0].get('name') if data else None
```

## 2. Follow PEP 8

Always follow the PEP 8 style guide for consistent code formatting.

## 3. Use Virtual Environments

Always use virtual environments for your projects:

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

## 4. Write Tests

Test-driven development is crucial:

```python
import unittest

class TestMyFunction(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(add(2, 3), 5)
```

## Conclusion

Following these best practices will make you a better Python developer.''',
            'category': 'Programming',
            'tags': ['python', 'best-practices', 'tips'],
            'read_time': 6,
            'is_featured': False
        },
        {
            'title': 'Building REST APIs with Django REST Framework',
            'excerpt': 'Learn how to create powerful REST APIs using Django REST Framework with practical examples.',
            'content': '''Django REST Framework (DRF) is a powerful toolkit for building Web APIs. Let's explore how to create a complete API.

## Installation

First, install DRF:

```bash
pip install djangorestframework
```

Add it to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
]
```

## Creating Serializers

Serializers convert complex data types to native Python datatypes:

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at']
```

## Creating Views

DRF provides various view classes:

```python
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

## URL Configuration

Set up your URLs:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## Conclusion

DRF makes it easy to build robust APIs quickly and efficiently.''',
            'category': 'Web Development',
            'tags': ['django', 'api', 'backend', 'tutorial'],
            'read_time': 10,
            'is_featured': True
        },
        {
            'title': 'Introduction to Machine Learning with Python',
            'excerpt': 'A beginner-friendly guide to getting started with machine learning using Python and scikit-learn.',
            'content': '''Machine learning is transforming how we interact with technology. This guide will help you get started.

## What is Machine Learning?

Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## Setting Up Your Environment

Install the necessary libraries:

```bash
pip install numpy pandas scikit-learn matplotlib jupyter
```

## Your First ML Model

Let's create a simple classification model:

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load the dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create and train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, predictions):.2f}")
```

## Key Concepts

1. **Supervised Learning**: Learning from labeled data
2. **Unsupervised Learning**: Finding patterns in unlabeled data
3. **Features**: Input variables used to make predictions
4. **Labels**: The output we want to predict

## Next Steps

- Explore more complex algorithms
- Learn about deep learning with TensorFlow/PyTorch
- Work on real-world projects

## Conclusion

Machine learning opens up exciting possibilities. Start with simple projects and gradually tackle more complex challenges.''',
            'category': 'Data Science',
            'tags': ['machine-learning', 'ai', 'python', 'tutorial'],
            'read_time': 12,
            'is_featured': False
        }
    ]

    for article_data in articles_data:
        category = Category.objects.get(name=article_data['category'])

        article, created = Article.objects.get_or_create(
            title=article_data['title'],
            defaults={
                'slug': article_data['title'].lower().replace(' ', '-').replace('.', ''),
                'author': user,
                'category': category,
                'content': article_data['content'],
                'excerpt': article_data['excerpt'],
                'status': 'published',
                'read_time_minutes': article_data['read_time'],
                'is_featured': article_data['is_featured'],
            }
        )

        if created:
            # Add tags
            for tag_name in article_data['tags']:
                tag = Tag.objects.get(name=tag_name)
                article.tags.add(tag)

            print(f"Created article: {article.title}")

    # Create sample comments
    articles = Article.objects.filter(status='published')[:2]

    for i, article in enumerate(articles):
        comment_texts = [
            "Great article! This really helped me understand the concept better.",
            "Thanks for sharing this. I've been looking for a good tutorial on this topic.",
            "Excellent explanation! The examples were very clear and easy to follow.",
        ]

        for j, comment_text in enumerate(comment_texts):
            commenter = User.objects.create_user(
                username=f'commenter_{i}_{j}',
                email=f'commenter{i}{j}@example.com',
                password='password123'
            )

            Comment.objects.get_or_create(
                article=article,
                author=commenter,
                content=comment_text,
                defaults={'is_approved': True}
            )

        print(f"Created comments for: {article.title}")

    print("\nSample data creation completed!")
    print("You can now:")
    print("1. Visit http://localhost:8001/blog/ to see the blog")
    print("2. Log in as 'blogger' with password 'password123'")
    print("3. Create new articles and comments")
    print("4. Access the admin panel at http://localhost:8001/admin/")

if __name__ == '__main__':
    create_sample_data()