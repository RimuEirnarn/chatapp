"""Room related utilities"""

from uuid import uuid4
from secrets import token_hex

# from hashlib import sha256

DM_IDENTIFIER = "DirectMessage/"
GC_IDENTIFIER = "GroupChat/"
PV_IDENTIFIER = "Private/"


def generate_DM_id(uid1: str, uid2: str) -> str:
    """Generate a Direct Message Room ID based on 2 users' id."""
    base_rid = str(uuid4())
    # hexed = hex((uid_1.int * uid_2.int) * randbelow(4096))[2:]
    # return f'{base_rid}/{hexed}/{uid1}:{uid2}'

    # Concatenate user IDs and some random data before hashing
    # data_to_hash = f"{uid1}:{uid2}:{uuid4()}/{token_hex(16)}"

    # Use a cryptographic hash function (SHA-256 in this case)
    # hashed_data = sha256(data_to_hash.encode()).hexdigest()
    hashed_data = "null"

    return f"{DM_IDENTIFIER}{base_rid}/{hashed_data}+{token_hex(8)}/{uid1}:{uid2}"


def generate_groupchat_id(uid1: str) -> str:
    """Generate a Group Chat Room ID based on the creator's id."""
    base_rid = str(uuid4())

    # salt = token_hex(32)
    hashed_token = token_hex(8)

    return f"{GC_IDENTIFIER}{base_rid}/{uid1}${hashed_token}"


def generate_private_rid(uid1: str) -> str:
    """Generate a private room ID based on user's id."""
    base_rid = str(uuid4())

    # salt = token_hex(64)
    hashed_token = token_hex(4)

    return f"{PV_IDENTIFIER}{uid1}/{base_rid}/{'private'}/{hashed_token}"


def identify_room(rid: str):
    """Identify a room by its id."""
    if rid.startswith(DM_IDENTIFIER):
        return "direct"

    if rid.startswith(GC_IDENTIFIER):
        return "groupchat"

    if rid.startswith(PV_IDENTIFIER):
        return "private"

    return "unknown"
