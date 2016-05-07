import json
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http.response import HttpResponseBadRequest
from django.views.generic import View
from graphql import Source, parse, execute, validate
from graphql.error import GraphQLError, format_error as format_graphql_error
from graphql.execution import ExecutionResult
from graphql.type.schema import GraphQLSchema
from graphql.utils.get_operation_ast import get_operation_ast
import six


class HttpError(Exception):
    def __init__(self, response, message=None, *args, **kwargs):
        self.response = response
        self.message = message = message or response.content.decode()
        super(HttpError, self).__init__(message, *args, **kwargs)


class GraphQLView(View):
    schema = None
    executor = None
    root_value = None
    pretty = False

    def __init__(self, **kwargs):
        super(GraphQLView, self).__init__(**kwargs)
        assert isinstance(self.schema, GraphQLSchema), 'A Schema is required to be provided to GraphQLView.'

    # noinspection PyUnusedLocal
    def get_root_value(self, request):
        return self.root_value

    def get_context(self, request):
        return request

    def dispatch(self, request, *args, **kwargs):
        try:
            if request.method.lower() not in ('get', 'post'):
                raise HttpError(HttpResponseNotAllowed(['GET', 'POST'], 'GraphQL only supports GET and POST requests.'))

            execution_result = self.execute_graphql_request(request)
            response = {}

            if execution_result.errors:
                response['errors'] = [self.format_error(e) for e in execution_result.errors]

            if execution_result.invalid:
                status_code = 400
            else:
                status_code = 200
                response['data'] = execution_result.data

            return HttpResponse(
                status=status_code,
                content=self.json_encode(request, response),
                content_type='application/json'
            )

        except HttpError as e:
            response = e.response
            response['Content-Type'] = 'application/json'
            response.content = self.json_encode(request, {
                'errors': [self.format_error(e)]
            })
            return response

    def json_encode(self, request, d):
        if not self.pretty and not request.GET.get('pretty'):
            return json.dumps(d, separators=(',', ':'))

        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))

    # noinspection PyBroadException
    def parse_body(self, request):
        content_type = self.get_content_type(request)

        if content_type == 'application/graphql':
            return {'query': request.body.decode()}

        elif content_type == 'application/json':
            try:
                request_json = json.loads(request.body.decode('utf-8'))
                assert isinstance(request_json, dict)
                return request_json
            except:
                raise HttpError(HttpResponseBadRequest('POST body sent invalid JSON.'))

        elif content_type in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            return request.POST

        return {}

    def execute(self, *args, **kwargs):
        return execute(self.schema, *args, **kwargs)

    def execute_graphql_request(self, request):
        query, variables, operation_name = self.get_graphql_params(request, self.parse_body(request))

        if not query:
            raise HttpError(HttpResponseBadRequest('Must provide query string.'))

        source = Source(query, name='GraphQL request')

        try:
            document_ast = parse(source)
            validation_errors = validate(self.schema, document_ast)
            if validation_errors:
                return ExecutionResult(
                    errors=validation_errors,
                    invalid=True,
                )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

        if request.method.lower() == 'get':
            operation_ast = get_operation_ast(document_ast, operation_name)
            if operation_ast and operation_ast.operation != 'query':
                raise HttpError(HttpResponseNotAllowed(
                    ['POST'], 'Can only perform a {} operation from a POST request.'.format(operation_ast.operation)
                ))

        try:
            return self.execute(
                document_ast,
                root_value=self.get_root_value(request),
                variable_values=variables,
                operation_name=operation_name,
                context_value=self.get_context(request)
            )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

    @staticmethod
    def get_graphql_params(request, data):
        query = request.GET.get('query') or data.get('query')
        variables = request.GET.get('variables') or data.get('variables')

        if variables and isinstance(variables, six.text_type):
            try:
                variables = json.loads(variables)
            except:
                raise HttpError(HttpResponseBadRequest('Variables are invalid JSON.'))

        operation_name = request.GET.get('operationName') or data.get('operationName')

        return query, variables, operation_name

    @staticmethod
    def format_error(error):
        if isinstance(error, GraphQLError):
            return format_graphql_error(error)

        return {'message': six.text_type(error)}

    @staticmethod
    def get_content_type(request):
        meta = request.META
        content_type = meta.get('CONTENT_TYPE', meta.get('HTTP_CONTENT_TYPE', ''))
        return content_type.split(';', 1)[0].lower()
