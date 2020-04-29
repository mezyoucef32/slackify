import json


def test_home_page(client):
    rv = client.get('/')
    assert b'Home' in rv.data


def test_redirect_to_command_handler(client):
    """Redirect to /hello based on form command"""
    rv = client.post('/',
                     data={'command': '/chau'},
                     content_type='application/x-www-form-urlencoded')
    assert b'Hello' in rv.data


def test_function_name_gets_overriden_by_decorator_arg(client):
    """Redirect to /hello based on form command"""
    rv = client.post('/',
                     data={'command': '/hello'},
                     content_type='application/x-www-form-urlencoded')
    assert b'Unknown Command' in rv.data


def test_redirect_to_command_handler_fails_on_invalid_command(client):
    """Redirect to /hello based on form command"""
    rv = client.post('/',
                     data={'command': '/Inexistent'},
                     content_type='application/x-www-form-urlencoded')
    assert b'Unknown Command' in rv.data


def test_redirect_to_shortcut_handler(client):
    args = {
        'payload': json.dumps({
            'type': 'shortcut',
            'callback_id': 'my-shortcut'
        })
    }
    rv = client.post('/',
                     data=args,
                     content_type='application/x-www-form-urlencoded')
    assert b'Shortcut' in rv.data


def test_redirect_to_shortcut_handler_invalid_id(client):
    args = {
        'payload': {
            'type': 'shortcut',
            'callback_id': 'not-a-shortcut'
        }
    }
    rv = client.post('/', json=args)
    assert b'Unknown Command' in rv.data


def test_if_exception_is_raised_request_is_redirect_to_error_handler(client):
    args = {
        'payload': "Breaking JSON"
    }
    rv = client.post('/',
                     data=args,
                     content_type='application/x-www-form-urlencoded')
    assert b'Oops..' in rv.data


def test_request_handling_with_no_added_matchers(bare_client):
    rv = bare_client.post('/',
                          json={'data': {'a': 1}},
                          content_type='application/json')
    assert b'Unknown Command' == rv.data


def test_redirect_on_action_id(client):
    payload = {
        "type": "block_actions",
        "actions": [{
            'action_id': 'my-action-id',
            'block_id': 'block-id',
        }],
        "token": "",
        "response_url": "",
        "trigger_id": "",
    }
    rv = client.post('/',
                     data={'payload': json.dumps(payload)},
                     content_type='application/x-www-form-urlencoded')

    assert b'Action' == rv.data


def test_action_redirects_based_on_block_and_action_ids(client):
    payload = {
        "type": "block_actions",
        "actions": [{
            'action_id': 'incorrect-action-id',
            'block_id': 'a-block-id',
        }],
        "token": "",
        "response_url": "",
        "trigger_id": "",
    }
    rv = client.post('/',
                     data={'payload': json.dumps(payload)},
                     content_type='application/x-www-form-urlencoded')

    assert b'Unknown Command' == rv.data

    # Fix payload acion id
    payload['actions'][0]['action_id'] = 'the-id'
    rv = client.post('/',
                     data={'payload': json.dumps(payload)},
                     content_type='application/x-www-form-urlencoded')

    assert b'Complex Action' == rv.data


def test_view_decorator_captures_modal_callbacks(client):
    payload = {
        'type': 'view_submission',
        'user': {'id': 'UG31KD90T', 'name': 'ambro17.1', 'team_id': 'TG4H5ANVC'},
        'view': {'blocks': [{'block_id': 'username_block'},
                            {'block_id': 'password_block'}],
                 'callback_id': 'my-first-view',
                 'state': {'values': {'password_block': {'password_value': {'type': 'plain_text_input',
                                                                            'value': 'eagae'}},
                                      'username_block': {'username_value': {'type': 'plain_text_input',
                                                                            'value': 'aeg'}}}},
                 'type': 'modal'}}
    rv = client.post('/',
                     data={'payload': json.dumps(payload)},
                     content_type='application/x-www-form-urlencoded')

    assert b'View' == rv.data


def test_capture_reaction_event(client, mocker):
    payload = {
        'event': {
            'type': 'reaction_added',
            'text': 'python',
            'user': 'UG31KD90T',
            'ts': '1588116040.001700',
            'team': 'TG4H5ANVC',
            'blocks': [{}],
            'channel': 'CG34PCNRY',
            'event_ts': '1588116040.001700',
            'channel_type': 'channel'
        },
        'type': 'event_callback',
        'event_id': 'Ev0129KEQSS3',
    }
    client.application.emitter = mocker.MagicMock()
    rv = client.post('/slack/events',
                     json=payload,
                     content_type='application/json')

    assert rv.data == b''
    assert rv.status == '200 OK'
    assert client.application.emitter.emit.called
    client.application.emitter.emit.assert_called_with('reaction_added', payload)
