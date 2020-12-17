import json
import logging
import datetime

import db_manager.db_api as api
from fcm_manager import fcm_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_challenge_lambda(event, context):
    request_body = event['body']
    request_body = json.loads(request_body)

    fart_url = request_body['fart_url']
    fart_owner = request_body['fart_owner']

    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    try:
        fart_id = api.insert_fart(url=fart_url, owner=fart_owner, timestamp=timestamp)
        challenge_id = api.create_challenge(first_fart=fart_id, fart_owner=fart_owner, timestamp=timestamp)
        api.add_challenge_to_user(user_id=fart_owner, challenge=str(challenge_id))
        return {
            'statusCode': 200,
            'body': json.dumps({
                'challenge_id': challenge_id
            })
        }
    except Exception as e:
        logging.error(f"Could'nt complete the process due to {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }


def accept_challenge_lambda(event, context):
    request_body = event['body']
    request_body = json.loads(request_body)

    fart_owner = request_body['fart_owner']
    challenge_id = request_body['challenge_id']

    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    try:
        api.add_challenge_to_user(user_id=fart_owner, challenge=challenge_id)
        fart_id = api.insert_fart(url=None, owner=fart_owner, timestamp=timestamp)
        api.fart_to_
        challenge(challenge_id=challenge_id, fart_id=fart_id)
    except Exception as e:
        logging.error(f"Couldn't complete the process due to {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully updated challenge!')
    }


def fart_to_challenge_lambda(event, context):
    request_body = event['body']
    request_body = json.loads(request_body)

    fart_id = request_body['fart_id']
    fart_url = request_body['fart_url']
    owner_nick = request_body['fart_owner']
    challenge_id = request_body['challenge_id']

    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    try:
        api.fart_to_challenge(fart_id=fart_id, fart_url=fart_url, timestamp=timestamp)
        user_tokens = api.get_challenge_user_tokens(challenge_id=challenge_id)
        if user_tokens:
            fcm_client.send_notification_to_users(device_tokens=user_tokens, owner_nick=owner_nick,
                                                  challenge_id=challenge_id)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'challenge_id': challenge_id
            })
        }
    except Exception as e:
        logging.error(f"Could'nt complete the process due to {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }


def calculate_winner_lambda(event, context):
    request_body = event['body']
    request_body = json.loads(request_body)
    challenge_id = request_body['challenge_id']
    winning_order = request_body['winning_order']

    try:
        api.set_winner_fart(challenge_id=challenge_id, winning_order=winning_order)
        user_tokens = api.get_challenge_user_tokens(challenge_id=challenge_id)
        if user_tokens:
            fcm_client.close_challenge_notifications(device_tokens=user_tokens, challenge_id=challenge_id)
        return {
            'statusCode': 200
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }


def create_user_lambda(event, context):
    try:
        new_user_id = api.create_user()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'user_id': new_user_id
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }


def get_user_challenges(event, context):
    request_body = event['queryStringParameters']
    user_id = request_body['user_id']
    try:
        challenges_list = api.get_user_challenges(user_id=user_id)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'challenges_list': challenges_list
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }


def set_users_nick_lambda(event, context):
    request_body = event['body']
    request_body = json.loads(request_body)
    user_id = request_body['user_id']
    nick = request_body['nick']
    token = request_body.get('user_token')
    try:
        api.set_users_nick(user_id=user_id, user_nick=nick)
        if token:
            api.set_user_token(user_id=user_id, user_token=token)
        return {
            'statusCode': 200
        }
    except Exception:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Couldn't complete the process due to {e}")
        }
