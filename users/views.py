from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Owner, Project, LoginLog
from .serializers import (
    UserSerializer, UserCreateSerializer, OwnerSerializer, ProjectSerializer, LoginSerializer
)


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user."""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Owner APIs
class OwnerListCreateView(generics.ListCreateAPIView):
    """GET: List all owners. POST: Insert new owner."""
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer


class OwnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Single owner. PUT/PATCH: Update. DELETE: Delete owner."""
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    lookup_url_kwarg = 'owner_id'


# Project APIs
class ProjectListCreateView(generics.ListCreateAPIView):
    """GET: List all projects. POST: Insert new project."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Single project. PUT/PATCH: Update. DELETE: Delete project."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_url_kwarg = 'project_id'


# Login / Logout APIs
class LoginView(APIView):
    """POST: Login with username and password. Records event in login_log table."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'success': False, 'message': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        login(request, user)
        LoginLog.objects.create(user=user, action=LoginLog.LOGIN)
        return Response({
            'success': True,
            'message': 'Login successful.',
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    """POST: Logout current user. Records event in login_log table."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_authenticated:
            LoginLog.objects.create(user=request.user, action=LoginLog.LOGOUT)
        logout(request)
        return Response({'success': True, 'message': 'Logout successful.'})
