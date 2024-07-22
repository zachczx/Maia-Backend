from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsSuperUser
from rest_framework.permissions import IsAuthenticated

class RegisterAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def post(self, request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        is_staff = request.data.get('is_staff')

        if not email or not password or not username:
            return Response({"error": "Username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not email.endswith('@mindef.gov.sg'):
            return Response({"error": "Only @mindef.gov.sg email addresses are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_staff=is_staff)
        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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