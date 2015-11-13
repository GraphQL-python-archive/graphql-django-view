from django.conf.urls import url
from graphql.core.type.definition import GraphQLArgument, GraphQLField, GraphQLNonNull, GraphQLObjectType
from graphql.core.type.scalars import GraphQLString
from graphql.core.type.schema import GraphQLSchema

from graphql_django_view import GraphQLView


def resolve_raises(o, a, i):
    raise Exception("Throws!")


QueryRootType = GraphQLObjectType(
    name='QueryRoot',
    fields={
        'thrower': GraphQLField(GraphQLNonNull(GraphQLString), resolver=resolve_raises),
        'test': GraphQLField(
            type=GraphQLString,
            args={
                'who': GraphQLArgument(GraphQLString)
            },
            resolver=lambda obj, args, info: 'Hello %s' % (args.get('who') or 'World')
        )
    }
)

MutationRootType = GraphQLObjectType(
    name='MutationRoot',
    fields={
        'writeTest': GraphQLField(
            type=QueryRootType,
            resolver=lambda *_: QueryRootType
        )
    }
)

Schema = GraphQLSchema(QueryRootType)

urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(schema=Schema)),
]
