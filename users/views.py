from io import BytesIO

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_variables
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from .models import User, Owner, Project, Blog, LoginLog, SuperAdmin, UploadFile, Contact, BillingInvoice, CompanyInfo
from .serializers import (
    UserSerializer, UserCreateSerializer, UserRoleUpdateSerializer,
    UserLoginResponseSerializer,
    OwnerSerializer, ProjectSerializer, BlogSerializer, ContactSerializer, LoginSerializer,
    SuperAdminSerializer, SuperAdminCreateSerializer, SuperAdminUpdateSerializer,
    UploadFileSerializer, BillingInvoiceSerializer, CompanyInfoSerializer,
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
    """GET: List all projects for internal dashboard. POST: Insert new project."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = [MultiPartParser, FormParser]


class ProjectPublicDashboardView(generics.ListAPIView):
    """
    GET: Public project dashboard.
    Read‑only list of all projects for the public frontend.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


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


# Contact APIs
class ContactListCreateView(generics.ListCreateAPIView):
    """GET: List all contact messages. POST: Save new contact message."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetailView(generics.RetrieveDestroyAPIView):
    """GET: Single contact message. DELETE: Delete contact message."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_url_kwarg = 'contact_id'


# BillingInvoice APIs
class BillingInvoiceListCreateView(generics.ListCreateAPIView):
    """GET: List all invoices. POST: Add new invoice (JSON or form + logo file)."""
    queryset = BillingInvoice.objects.all()
    serializer_class = BillingInvoiceSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': serializer.data,
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


class BillingInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Single invoice. PUT/PATCH: Update invoice (JSON or form + logo file). DELETE: Delete invoice."""
    queryset = BillingInvoice.objects.all()
    serializer_class = BillingInvoiceSerializer
    lookup_url_kwarg = 'invoice_id'
    parser_classes = [JSONParser, MultiPartParser, FormParser]

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
                'errors': 'Invoice not found.',
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
                'errors': 'Invoice not found.',
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
                'errors': 'Invoice not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


class InvoiceGeneratePDFView(APIView):
    """GET api/invoice_generate/<invoice_id>/: return PDF, or JSON if client asks for JSON (fixes invalid API call)."""

    permission_classes = [AllowAny]

    def get(self, request, invoice_id):
        try:
            instance = BillingInvoice.objects.get(invoice_id=invoice_id)
        except BillingInvoice.DoesNotExist:
            return Response(
                {'success': False, 'message': MSG_ERROR, 'errors': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        data = BillingInvoiceSerializer(instance, context={'request': request}).data

        # If client expects JSON (e.g. fetch/axios), return JSON so frontend gets valid API response
        accept = request.META.get('HTTP_ACCEPT', '') or ''
        if 'application/json' in accept or request.GET.get('format') == 'json':
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': data,
                'pdf_url': request.build_absolute_uri(request.path) + '?format=pdf',
            })

        # Otherwise generate and return PDF
        buffer = BytesIO()
        p = pdf_canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - inch
        p.setFont('Helvetica-Bold', 16)
        p.drawString(inch, y, 'INVOICE')
        y -= 0.4 * inch
        p.setFont('Helvetica', 10)
        for label, value in [
            ('Invoice No', data.get('invoice_no') or str(data.get('invoice_id', ''))),
            ('Invoice Date', str(data.get('invoice_date') or '')),
            ('Your Company', data.get('own_com_name') or ''),
            ('Tagline', data.get('own_com_title') or ''),
            ('Client Name', data.get('client_name') or ''),
            ('Client ID', data.get('client_id') or ''),
            ('Client Company', data.get('client_company') or ''),
            ('Phone', data.get('client_phone') or ''),
            ('Address', data.get('client_address') or ''),
            ('Description', (data.get('billing_description') or '')[:200]),
            ('Unit Price', str(data.get('unit_price') or '0')),
            ('Subtotal', str(data.get('subtotal') or '0')),
            ('Discount', str(data.get('discount') or '0')),
            ('Total', str(data.get('total_price') or '0')),
        ]:
            if y < inch:
                p.showPage()
                p.setFont('Helvetica', 10)
                y = height - inch
            p.drawString(inch, y, f'{label}: {value}')
            y -= 0.25 * inch
        p.save()
        buffer.seek(0)
        filename = f"invoice_{data.get('invoice_no') or invoice_id}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# CompanyInfo APIs
class CompanyInfoListCreateView(generics.ListCreateAPIView):
    """GET: List all company info. POST: Add new company info."""
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    parser_classes = [MultiPartParser, FormParser]  # accept JSON (default) and form/multipart

    def get_parser_classes(self):
        # Keep JSON parser for POST; list only needs GET
        from rest_framework.parsers import JSONParser
        return [JSONParser, MultiPartParser, FormParser]

    def list(self, request, *args, **kwargs):
        """Return list as { success, message, data } with data a JSON array."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Ensure data is a list so frontend gets an array, not object with numeric keys
        payload = list(serializer.data)
        return Response({
            'success': True,
            'message': MSG_SUCCESS,
            'data': payload,
        })

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': MSG_SUCCESS,
                'data': serializer.data,
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


class CompanyInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Single company info. PUT/PATCH: Update. DELETE: Delete."""
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    lookup_url_kwarg = 'com_id'

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
                'errors': 'Company info not found.',
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
                'errors': 'Company info not found.',
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
                'errors': 'Company info not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': MSG_ERROR,
                'errors': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


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
