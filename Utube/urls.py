from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, routers
from utube_app import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewset)
router.register(r'author', views.AuthorViewset)
router.register(r'subscription', views.SubscriptionViewset)
router.register(r'video', views.VideoViewset)
router.register(r'comment', views.CommentViewset)
router.register(r'like', views.LikeViewset)

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    patterns=[path('api/', include(router.urls)), ],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('utube_app.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include(router.urls)),
    re_path('swagger-ui/',
        TemplateView.as_view(
            template_name='swaggerui/swaggerui.html',
            extra_context={'schema_url': 'openapi-schema'}
        ),
        name='swagger-ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json')
]