class Fart:

    def __init__(self, fart_id: int, url: str, owner: str, rank: str, timestamp: str):
        self.fart_id = fart_id
        self.url = url
        self.owner = owner
        self.rank = rank
        self.timestamp = str(timestamp)

    @staticmethod
    def from_tuple(row: tuple):
        return Fart(fart_id=row[0], url=row[1], owner=row[2], rank=row[3], timestamp=row[4])


class Challenge:

    def __init__(self, challenge_id: str, host: str, participants: str, winner: str, timestamp: str):
        self.challenge_id = challenge_id
        self.host = host
        self.participants = participants
        self.winner = winner
        self.timestamp = str(timestamp)

    @staticmethod
    def from_tuple(row: tuple):
        return Challenge(challenge_id=row[0], host=row[1], participants=row[2], winner=row[3], timestamp=row[4])


class User:
    def __init__(self, user_id: str, user_name: str, token: str, challenges: str):
        self.user_id = user_id
        self.user_name = user_name
        self.token = token
        self.challenges = challenges

    @staticmethod
    def from_tuple(row: tuple):
        return User(user_id=row[0], user_name=row[1], token=row[2], challenges=row[3])
