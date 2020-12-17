import logging

from db_manager import conn
from db_manager.db_errors import InsertFartException, CreateChallengeException, AcceptChallengeException, \
    CalculateWinnerException, SetWinnerException, CreateUserException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def insert_fart(owner: str, timestamp: str, url: str = None):
    insert_query = f"""INSERT INTO farts_master.dim_farts (`url`, `owner`, `timestamp`) VALUES ('{url}', '{owner}', '{timestamp}')"""
    with conn.cursor() as cur:
        cur.execute(insert_query)
        conn.commit()
        return cur.lastrowid


def create_challenge(first_fart: int, fart_owner: str, timestamp: str) -> int:
    import random
    with conn.cursor() as cur:
        challenge_created = False
        max_retries = 3
        while max_retries > 0 and not challenge_created:
            try:
                challenge_id = random.randrange(100000, 999999, 1)
                create_challenge_query = f"INSERT INTO farts_master.challenges (`id`, `host`, `participants`, `timestamp`) " \
                                         f"VALUES ('{challenge_id}', '{fart_owner}' ,'{first_fart}', '{timestamp}')"
                cur.execute(create_challenge_query)
                conn.commit()
                challenge_created = True
            except Exception as e:
                logging.error(f"Could'nt create a challenge due to {e}")
                logging.info(f"There are still more {max_retries}")
                max_retries -= 1
                if max_retries <= 0:
                    raise CreateChallengeException(f"Could'nt create challenge due to {e}")
        return challenge_id


def fart_to_challenge(fart_id: int, fart_url: str, timestamp: str):
    with conn.cursor() as cur:
        update_fart_url = f"UPDATE farts_master.dim_farts SET url = '{fart_url}', timestamp  = '{timestamp}' WHERE  id = '{fart_id}'"
        cur.execute(update_fart_url)
        conn.commit()


def set_winner_fart(challenge_id: str, winning_order: str):
    set_winner_query = f"UPDATE farts_master.challenges SET winner = '1', participants = '{winning_order}' WHERE id = '{challenge_id}'"
    try:
        with conn.cursor() as cur:
            cur.execute(set_winner_query)
            conn.commit()

    except Exception as e:
        raise SetWinnerException(e)


def create_user():
    def get_random_string(length):
        import random
        import string
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    with conn.cursor() as cur:
        user_id_created = False
        max_retries = 3
        while max_retries > 0 and not user_id_created:
            potential_user_name = get_random_string(6)
            check_if_id_exists = f"SELECT count(*) FROM farts_master.users WHERE id = '{potential_user_name}'"
            cur.execute(check_if_id_exists)
            conn.commit()
            results = cur.fetchone()
            if results and results[0] == 0:
                user_id_created = True
            max_retries -= 1
        if not user_id_created:
            raise CreateUserException("Could'nt create user")

        insert_user_query = f"INSERT INTO farts_master.users (`id`) VALUES ('{potential_user_name}')"
        cur.execute(insert_user_query)
        conn.commit()
        return potential_user_name


def add_challenge_to_user(user_id: str, challenge: str):
    from models import User

    with conn.cursor() as cur:
        get_user_query = f"SELECT * FROM farts_master.users WHERE id = '{user_id}'"
        cur.execute(get_user_query)
        conn.commit()
        user_row = cur.fetchone()
        if not user_row:
            raise Exception(f"There is no such user {user_id}")
        user = User.from_tuple(user_row)

        check_if_challenge_valid = f"SELECT * FROM farts_master.challenges WHERE id = '{challenge}'"
        cur.execute(check_if_challenge_valid)
        conn.commit()
        challenge_row = cur.fetchone()
        if not challenge_row:
            raise Exception(f"There is no such challenge {challenge}")

        new_challenges_value = f"{user.challenges},{challenge}" if user.challenges else challenge
        updated_challenges_query = f"UPDATE farts_master.users SET challenges = '{new_challenges_value}' WHERE id = '{user_id}'"
        cur.execute(updated_challenges_query)
        conn.commit()


def get_user_challenges(user_id: str):
    from models import User, Challenge, Fart
    challenges_obj_list: [Challenge] = []
    with conn.cursor() as cur:
        get_user_query = f"SELECT * FROM farts_master.users WHERE id = '{user_id}'"
        cur.execute(get_user_query)
        conn.commit()
        user_row = cur.fetchone()
        if not user_row:
            raise Exception("User doesn't exist")
        user = User.from_tuple(user_row)

        challenges_ids_list = user.challenges.split(',')
        challenges_ids_list = list(map(lambda id: f"\'{id}\'", challenges_ids_list))
        get_challenge_query = f"SELECT * FROM farts_master.challenges WHERE id in ({','.join(challenges_ids_list)})"
        cur.execute(get_challenge_query)
        conn.commit()
        challenges_rows = cur.fetchall()
        for row in challenges_rows:
            challenges_obj_list.append(Challenge.from_tuple(row).__dict__)

        if not challenges_obj_list:
            raise Exception("There are no challenges")

        for challenge in challenges_obj_list:
            farts: [Fart] = []
            participant_farts = challenge['participants'].split(',')
            participant_farts = list(map(lambda id: f"\'{id}\'", participant_farts))
            get_farts_query = f"SELECT * FROM farts_master.dim_farts WHERE id in ({','.join(participant_farts)})"
            cur.execute(get_farts_query)
            conn.commit()
            farts_rows = cur.fetchall()
            for row in farts_rows:
                fart = Fart.from_tuple(row)
                fart_owner_id = fart.owner
                user_nick = get_user_nick(fart_owner_id)
                setattr(fart, 'owner_nick', user_nick)
                farts.append(fart.__dict__)

            challenge['host_nick'] = get_user_nick(challenge['host'])
            challenge['participants'] = farts

        return challenges_obj_list


def get_user_nick(user_id: str):
    with conn.cursor() as cur:
        get_farts_query = f"SELECT name FROM farts_master.users WHERE id = '{user_id}'"
        cur.execute(get_farts_query)
        conn.commit()
        nick_name_row = cur.fetchone()
        nick_name = nick_name_row[0]
        return nick_name if nick_name else 'Default'


def set_users_nick(user_id: str, user_nick: str):
    with conn.cursor() as cur:
        update_nick_query = f"UPDATE farts_master.users SET name = '{user_nick}' WHERE id = '{user_id}'"
        cur.execute(update_nick_query)
        conn.commit()


def set_user_token(user_id: str, user_token: str):
    with conn.cursor() as cur:
        update_nick_query = f"UPDATE farts_master.users SET token = '{user_token}' WHERE id = '{user_id}'"
        cur.execute(update_nick_query)
        conn.commit()


def get_challenge_user_tokens(challenge_id: str):
    with conn.cursor() as cur:
        get_participants_farts_query = f"SELECT participants FROM farts_master.challenges WHERE id = '{challenge_id}'"
        cur.execute(get_participants_farts_query)
        conn.commit()

        participants_farts = cur.fetchone()
        fart_ids_list = list(map(lambda fart_id: f"{fart_id}", participants_farts))

        get_farts_owner_query = f"SELECT owner FROM farts_master.dim_farts WHERE id in ({','.join(fart_ids_list)})"
        cur.execute(get_farts_owner_query)
        conn.commit()

        user_ids = cur.fetchall()
        users_ids_list = list(map(lambda user_id: f"\"{user_id[0]}\"", user_ids))
        get_tokens_for_users_query = f"SELECT token FROM farts_master.users WHERE id in ({','.join(users_ids_list)})"
        cur.execute(get_tokens_for_users_query)
        conn.commit()
        users_tokens = cur.fetchall()
        users_tokens_list = list(map(lambda users_tokens: f"{users_tokens[0]}", users_tokens))

        return [i for i in users_tokens_list if i != "None"]
