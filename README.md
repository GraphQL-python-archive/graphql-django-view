# `graphql-django-view`

[![Build Status](https://travis-ci.org/graphql-python/graphql-django-view.svg?branch=master)](https://travis-ci.org/graphql-python/graphql-django-view) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphql-django-view/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphql-django-view?branch=master) [![PyPI version](https://badge.fury.io/py/graphql-django-view.svg)](https://badge.fury.io/py/graphql-django-view)

A `django` view that will execute a `GraphQLSchema` using a given `Executor`.

## Usage
Use it like you would any other Django View.

```python
urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(schema=Schema)),
]
```

### Supported options
 * `schema`: The `GraphQLSchema` object that you want the view to execute when it gets a valid request.
 * `pretty`: Whether or not you want the response to be pretty printed JSON.
 * `executor`: The `Executor` that you want to use to execute queries.
 * `root_value`: The `root_value` you want to provide to `executor.execute`.

You can also subclass `GraphQLView` and overwrite `get_root_value(self, request)` to have a dynamic root value
per request.

```python
class UserRootValue(GraphQLView):
    def get_root_value(self, request):
        return request.user

```
