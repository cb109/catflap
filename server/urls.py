from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
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
    # This endpoint serves a service-worker file on root level, so it
    # can control anything below. Why are we using a template here
    # instead of service a static file? Because the file needs to be
    # hosted above the /static/ path for proper scoping.
    path(
        r"service-worker",
        TemplateView.as_view(
            template_name=("service-worker.js"),
            content_type="application/javascript",
        ),
        name="service-worker",
    ),
    path(
        r"manifest",
        views.get_dynamic_manifest_json,
        name="manifest",
    ),
]
