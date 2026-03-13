from rest_framework import serializers
from .models import Blog, Category, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'blog',
            'user',
            'user_name',
            'content',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user']


class BlogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id',
            'user',
            'user_name',
            'category',
            'category_name',
            'title',
            'content',
            'image',
            'tags',
            'is_ai_generated',
            'created_at',
            'updated_at',
            'comments',
            'comments_count',
        ]
        read_only_fields = ['user']