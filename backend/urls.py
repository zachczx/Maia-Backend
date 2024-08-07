from django.contrib import admin
from django.urls import path, include
from document_processor import urls as document_processor_urls
from response_generator import urls as response_generator_urls
from query_classifier import urls as query_classifier_urls
from customer_profiler import urls as customer_profiler_urls
from core import urls as core_urls
from account import urls as account_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Maia API",
        default_version='v1',
        description="Description of APIs in Maia Backend",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(document_processor_urls)),
    path('api/', include(response_generator_urls)),
    path('api/', include(customer_profiler_urls)),
    path('api/', include(query_classifier_urls)),
    path('api/', include(core_urls)),
    path('api/', include(account_urls)),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
