from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsSuperUser
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username for the new user'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the new user'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the new user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the new user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the new user'),
                'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the user should have staff privileges'),
            }
        ),
        responses={
            201: openapi.Response(
                description='Registration successful.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        is_staff = request.data.get('is_staff')

        if email is None or password is None or username is None:
            return Response({"error": "Username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not email.endswith('@mindef.gov.sg'):
            return Response({"error": "Only @mindef.gov.sg email addresses are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_staff=is_staff)
        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username for login'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for login'),
            }
        ),
        responses={
            200: openapi.Response(
                description='Successful login',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
                    }
                )
            ),
            401: openapi.Response(
                description='Unauthorized',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'first_name': user.first_name,
                'last_name': user.last_name
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)