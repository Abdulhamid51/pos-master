from django.contrib import admin
from django.urls import path, include
from api.routers import router
from main.views import Login, Logout
from api.mobilViewset import login as mlogin, register as mregister
from api.mobilrouter import router as mrouter
from rest_framework.documentation import include_docs_urls
from django.conf.urls.static import static
from django.conf import settings


from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


urlpatterns = [
    # Main app URL-lari
    path('', include('main.urls')),
    path('bot/', include('tg_bot.urls')),

    # Login va Logout
    path('login/', Login, name='login'),
    path('logout/', Logout, name='logout'),

    # Mobile login va register
    path('mlogin/', mlogin, name="mlogin"),
    path('mregister/', mregister, name="mregister"),

    # API va mobil API URL-lari
    path('api/', include(router.urls)),
    path('mapi/', include(mrouter.urls)),

    # Admin paneli URL-lari
    path('admin/', admin.site.urls),

    # API 1 URL-lari (agar bu alohida bo‘lsa)
    path('api1/', include('api.urls')),

    # API hujjatlari URL
    # path('docs/', include_docs_urls(title='API ')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

