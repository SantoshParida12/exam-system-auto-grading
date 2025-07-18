from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin', RedirectView.as_view(url='/admin/', permanent=True)),  # Redirect /admin to /admin/
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('prof/', include('prof.urls')),
    path('student/', include('student.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
