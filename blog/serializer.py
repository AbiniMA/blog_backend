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

    user_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    image = serializers.SerializerMethodField()   # ✅ important

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

    # ✅ FULL NAME (or fallback)
    def get_user_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name if name else obj.user.email

    # ✅ FULL IMAGE URL
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None