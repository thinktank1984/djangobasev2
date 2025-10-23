from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Article


@receiver(post_save, sender=Article)
def article_published(sender, instance, created, **kwargs):
    """
    Signal handler for when an article is published.
    Can be extended to send notifications, update search index, etc.
    """
    if instance.status == 'published' and (created or instance.published_at):
        # Add logic for when an article is published
        # For example: send email notifications, update search index, etc.
        pass