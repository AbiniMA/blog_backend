import requests
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import UserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    code = request.data.get("code")

    if not code:
        return Response(
            {"error": "Code is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code",
        },
    )

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return Response(
            {
                "error": "Failed to get access token",
                "details": token_data
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user_info_res = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"access_token": access_token},
    )
    user_info = user_info_res.json()

    email = user_info.get("email")
    name = user_info.get("name", "")
    picture = user_info.get("picture")

    if not email:
        return Response(
            {
                "error": "Failed to get user info",
                "details": user_info
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            "email": email,
            "first_name": name,
        },
    )

    if not created:
        user.email = email
        user.first_name = name
        user.save()

    tokens = get_tokens_for_user(user)

    return Response({
        "message": "Google login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.first_name,
            "picture": picture,
        },
        "tokens": tokens,
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response({
        "id": request.user.id,
        "email": request.user.email,
        "name": request.user.first_name,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)