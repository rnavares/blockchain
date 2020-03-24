import hashlib
import json


def crypto_hash(*args):
    """
    return ha-256 hash of arguments
    """

    # sort to make sure we have same hash
    # for outputs in different order i.e. 2,3 and 3,2
    stringified_args = sorted(map(lambda data: json.dumps(data), args))

    joined_data = "".join(stringified_args)

    return hashlib.sha256(joined_data.encode("utf-8")).hexdigest()


# print(str(crypto_hash([2, 3], 2, "hello")))
# print(str(crypto_hash(2, [2, 3], "hello")))
