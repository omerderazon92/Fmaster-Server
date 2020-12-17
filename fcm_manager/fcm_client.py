import requests
import json

serverToken = 'AAAAj4dnE0E:APA91bEYpaqROkFACvaELcUGCIJh4e7kNuRsEAGgDuIoKLvMNGwaomLRrwHvVre_LXl6VBIXR9CzO7ggD_8sjcVAkeU0sQjqw8dQtDD6114QcVgAyQ8EZYAgEQPB16dstlEl4eg1Rf-O'


def send_notification_to_users(device_tokens: [str], owner_nick: str, challenge_id: str):
    for token in device_tokens:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        body = {
            'notification':
                {
                    'title': f'{owner_nick} has farted at {challenge_id}',
                    'body': f'Hold your breath and check the room',
                    'sound': 'default'
                },
            'to': token,
            'priority': 'high',
        }
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))


def close_challenge_notifications(device_tokens: [str], challenge_id: str):
    for token in device_tokens:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        body = {
            'notification':
                {
                    'title': f'There is a winner for room number {challenge_id}',
                    'body': f'Hold your breath and check the room',
                    'sound': 'default'
                },
            'to': token,
            'priority': 'high',
        }
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
