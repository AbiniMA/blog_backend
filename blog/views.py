from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import request, status
from .models import Blog, Category, Comment
from .serializer import BlogSerializer, CategorySerializer, CommentSerializer


@api_view(['GET', 'POST'])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.db.models import Q

@api_view(['GET', 'POST'])
@permission_classes([AllowAny]) 
def blog_list_create(request):

    # -------- GET (FILTER + SEARCH) --------
    if request.method == 'GET':

        category_id = request.GET.get('category')
        search = request.GET.get('search')

        blogs = Blog.objects.all().order_by('-created_at')

        # ✅ filter by category
        if category_id:
            blogs = blogs.filter(category_id=category_id)

        # ✅ search in title + content + tags
        if search:
            blogs = blogs.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )

        serializer = BlogSerializer(
            blogs,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    # -------- POST --------
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    serializer = BlogSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_blogs(request):
    blogs = Blog.objects.filter(user=request.user).order_by('-created_at')
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def blog_detail(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BlogSerializer(blog, context={'request': request})
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    if blog.user != request.user:
        return Response({"error": "You can edit/delete only your own blog"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        blog.delete()
        return Response({"message": "Blog deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def blog_comments(request, blog_id):
    try:
        blog = Blog.objects.get(pk=blog_id)
        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)
        print("COOKIES:", request.COOKIES)
        print("COOKIE HEADER:", request.headers.get("Cookie"))
        print("X-CSRFToken:", request.headers.get("X-CSRFToken"))
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = Comment.objects.filter(blog=blog).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, blog=blog)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    if comment.user != request.user:
        return Response({"error": "You can edit/delete only your own comment"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user, blog=comment.blog)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)