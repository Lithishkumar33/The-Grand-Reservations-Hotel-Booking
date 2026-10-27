from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('frontend.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', include('adminpanel.urls')),
]

# 🔥 REQUIRED for room image uploads (development only)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
