from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('', include('refbooks.urls')),
    path('backend/admin/', admin.site.urls),
    path('backend/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('backend/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
