from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from server.catflap import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path(
        "catflaps/<int:catflap_id>/inside",
        views.set_catflap_cat_inside,
        name="set-inside",
    ),
    path(
        "catflaps/<int:catflap_id>/outside",
        views.set_catflap_cat_outside,
        name="set-outside",
    ),
]
