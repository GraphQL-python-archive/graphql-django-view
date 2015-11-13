from django.conf.urls import url
from graphql_django_view import GraphQLView
from .schema import Schema

urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(schema=Schema, pretty=True)),
]
