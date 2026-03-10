from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_variables
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.parsers import MultiPartParser, FormParser

from .models import User, Owner, Project, Blog, LoginLog, SuperAdmin, UploadFile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserRoleUpdateSerializer,
    UserLoginResponseSerializer,
    OwnerSerializer, ProjectSerializer, BlogSerializer, LoginSerializer,
    SuperAdminSerializer, SuperAdminCreateSerializer, SuperAdminUpdateSerializer,
    UploadFileSerializer,
)

# Common response messages for insert/update/delete
MSG_SUCCESS = 'Successfully'
MSG_ERROR = 'An error occurred'


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user. Returns common success/error message."""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': UserSerializer(serializer.instance).data,
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user. Returns common success/error message."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        try:
            # Always partial=True so only sent fields are validated (username not required)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': serializer.data,
            })
        except ValidationError as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)
        except NotFound:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': 'User not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
            }, status=status.HTTP_200_OK)
        except NotFound:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': 'User not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


class UserRoleUpdateView(APIView):
    """PATCH: Update only the user's role. Returns common success/error message."""

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'message': MSG_ERROR, 'errors': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            serializer = UserRoleUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            user.role = serializer.validated_data['role']
            user.save(update_fields=['role'])
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': UserSerializer(user).data,
            })
        except ValidationError as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)


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
    parser_classes = [MultiPartParser, FormParser]


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Single project. PUT/PATCH: Update. DELETE: Delete project."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_url_kwarg = 'project_id'
    parser_classes = [MultiPartParser, FormParser]


# Blog APIs
class BlogListCreateView(generics.ListCreateAPIView):
    """GET: List all blogs. POST: Insert new blog (with optional image)."""
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    parser_classes = [MultiPartParser, FormParser]


class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Single blog. PUT/PATCH: Update. DELETE: Delete blog."""
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_url_kwarg = 'blog_id'
    parser_classes = [MultiPartParser, FormParser]


class UploadFileView(generics.ListCreateAPIView):
    """GET: List uploaded files. POST: Upload new image/file."""

    queryset = UploadFile.objects.all()
    serializer_class = UploadFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Save original filename for convenience
        if not instance.original_name and instance.file:
            instance.original_name = instance.file.name
            instance.save(update_fields=['original_name'])


# SuperAdmin (admin user) APIs
class SuperAdminDashboardView(generics.ListAPIView):
    """GET /api/superadmin_dashboard/ - List all user login data (User table) for superadmin dashboard."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SuperAdminCreateView(generics.CreateAPIView):
    """POST /api/add_admin_users/ - Add admin user. Returns common success/error message."""
    queryset = SuperAdmin.objects.all()
    serializer_class = SuperAdminCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': SuperAdminSerializer(serializer.instance).data,
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE - alladminuser, update_admin_users, delete_admin_users. Returns common success/error message."""
    queryset = SuperAdmin.objects.all()
    lookup_url_kwarg = 'pk'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return SuperAdminUpdateSerializer
        return SuperAdminSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': serializer.data,
            })
        except NotFound:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': 'Admin user not found.',
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.get('partial', request.method == 'PATCH')
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': SuperAdminSerializer(instance).data,
            })
        except ValidationError as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': e.detail,
            }, status=status.HTTP_400_BAD_REQUEST)
        except NotFound:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': 'Admin user not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
            }, status=status.HTTP_200_OK)
        except NotFound:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': 'Admin user not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


# Login / Logout APIs
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """POST: Login with username and password. Records event in login_log table."""
    permission_classes = [AllowAny]
    authentication_classes = []  # no auth required for login; avoids CSRF block on cross-origin POST

    @sensitive_variables('password')
    def post(self, request):
        # Accept both JSON (request.data) and form data (request.POST)
        data = request.data if request.data else request.POST
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Missing or invalid username or password.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        # If username looks like email, try authenticating by email
        if user is None and '@' in username:
            try:
                u = User.objects.get(email=username)
                if u.check_password(password):
                    user = u
            except User.DoesNotExist:
                pass
        if user is None:
            return Response(
                {'success': False, 'message': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # Only allow login when status is active and user.is_active
        if getattr(user, 'status', 'active') == 'inactive':
            return Response(
                {'success': False, 'message': 'Your username is not active yet.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not user.is_active:
            return Response(
                {'success': False, 'message': 'Your username is not active yet.'},
                status=status.HTTP_403_FORBIDDEN
            )
        # User is active: login and return all stored user data (no password)
        login(request, user)
        LoginLog.objects.create(user=user, action=LoginLog.LOGIN)
        user_data = UserLoginResponseSerializer(user).data
        user_role = getattr(user, 'role', None) or user_data.get('role') or 'user'
        return Response({
            'success': True,
            'message': 'Login successful.',
            'user': user_data,
            'role': user_role,
        })


class LogoutView(APIView):
    """POST: Logout current user. Records event in login_log table."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_authenticated:
            LoginLog.objects.create(user=request.user, action=LoginLog.LOGOUT)
        logout(request)
        return Response({'success': True, 'message': 'Logout successful.'})
