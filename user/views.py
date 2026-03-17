import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes

from .serializer import UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):

    code = request.data.get("code")

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

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"access_token": access_token},
    ).json()

    email = user_info["email"]
    name = user_info["name"]

    user, created = User.objects.get_or_create(
        username=email,
        defaults={"email": email, "first_name": name},
    )

    login(request, user)

    return Response({
        "message": "Google login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": name,
            "picture": user_info.get("picture"),
        }
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response({
        "id": request.user.id,
        "email": request.user.email,
        "name": request.user.first_name
    })


@api_view(["GET"])
def all_users(request):

    users = User.objects.all()

    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)