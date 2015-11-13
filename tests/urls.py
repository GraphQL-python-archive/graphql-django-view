from django.conf.urls import url
from graphql.core.type.definition import GraphQLObjectType, GraphQLField
from graphql.core.type.scalars import GraphQLString
from graphql.core.type.schema import GraphQLSchema

from graphql_django_view import GraphQLView


def resolve_raises(o, a, i):
    raise Exception("This field raised an exception.")


Query = GraphQLObjectType(
    name='Query', fields={
        'raises': GraphQLField(GraphQLString, resolver=resolve_raises),
        'hello': GraphQLField(GraphQLString, resolver=lambda *_: "Hello World")
    }
)

Schema = GraphQLSchema(Query)

urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(schema=Schema)),
]
