from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from server.catflap import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path(
        "catflaps/<uuid:catflap_uuid>/inside",
        views.set_catflap_cat_inside,
        name="set-inside",
    ),
    path(
        "catflaps/<uuid:catflap_uuid>/outside",
        views.set_catflap_cat_outside,
        name="set-outside",
    ),
    path(
        "catflaps/<uuid:catflap_uuid>/status",
        views.get_catflap_status,
        name="status",
    ),
]
