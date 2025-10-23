from django import forms
from .models import Article, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = 'Comment'


class ArticleForm(forms.ModelForm):
    save_as_draft = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        })
    )

    class Meta:
        model = Article
        fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 'is_featured', 'read_time_minutes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter article title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'content': forms.Textarea(attrs={
                'rows': 15,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Write your article content here...'
            }),
            'excerpt': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Brief description of your article (max 300 characters)'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'read_time_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': 1,
                'max': 60
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['category'].label = 'Category'
        self.fields['content'].label = 'Content'
        self.fields['excerpt'].label = 'Excerpt'
        self.fields['featured_image'].label = 'Featured Image'
        self.fields['is_featured'].label = 'Mark as Featured'
        self.fields['read_time_minutes'].label = 'Estimated Reading Time (minutes)'
        self.fields['save_as_draft'].label = 'Save as Draft'

    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt and len(excerpt) > 300:
            raise forms.ValidationError('Excerpt cannot exceed 300 characters.')
        return excerpt