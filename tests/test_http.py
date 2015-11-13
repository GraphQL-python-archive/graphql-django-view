import json

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


def url_string(**url_params):
    string = '/graphql'

    if url_params:
        string += '?' + urlencode(url_params)

    return string


def response_json(response):
    return json.loads(response.content.decode())


def test_allows_get_with_query_param(client):
    response = client.get(url_string(query='{test}'))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello World"}
    }


def test_allows_get_with_variable_values(client):
    response = client.get(url_string(
        query='query helloWho($who: String){ test(who: $who) }',
        variables=json.dumps({'who': "Dolly"})
    ))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello Dolly"}
    }


def test_allows_get_with_operation_name(client):
    response = client.get(url_string(
        query='''
        query helloYou { test(who: "You"), ...shared }
        query helloWorld { test(who: "World"), ...shared }
        query helloDolly { test(who: "Dolly"), ...shared }
        fragment shared on QueryRoot {
          shared: test(who: "Everyone")
        }
        ''',
        operationName='helloWorld'
    ))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {
            'test': 'Hello World',
            'shared': 'Hello Everyone'
        }
    }


def test_reports_validation_errors(client):
    response = client.get(url_string(
        query='{ test, unknownOne, unknownTwo }'
    ))

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Cannot query field "unknownOne" on "QueryRoot".',
                'locations': [{'line': 1, 'column': 9}]
            },
            {
                'message': 'Cannot query field "unknownTwo" on "QueryRoot".',
                'locations': [{'line': 1, 'column': 21}]
            }
        ]
    }


def test_errors_when_missing_operation_name(client):
    response = client.get(url_string(
        query='''
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        '''
    ))

    assert response.status_code == 400
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Must provide operation name if query contains multiple operations.'
            }
        ]
    }


def test_errors_when_sending_a_mutation_via_get(client):
    response = client.get(url_string(
        query='''
        mutation TestMutation { writeTest { test } }
        '''
    ))
    assert response.status_code == 405
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Can only perform a mutation operation from a POST request.'
            }
        ]
    }


def test_errors_when_selecting_a_mutation_within_a_get(client):
    response = client.get(url_string(
        query='''
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        ''',
        operationName='TestMutation'
    ))

    assert response.status_code == 405
    assert response_json(response) == {
        'errors': [
            {
                'message': 'Can only perform a mutation operation from a POST request.'
            }
        ]
    }


def test_allows_mutation_to_exist_within_a_get(client):
    response = client.get(url_string(
        query='''
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        ''',
        operationName='TestQuery'
    ))

    assert response.status_code == 200
    assert response_json(response) == {
        'data': {'test': "Hello World"}
    }
