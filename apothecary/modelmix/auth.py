


try:
    from Crypto import Random
    crypto_random = Random.new().read
except ImportError:
    import os
    import hashlib
    import math
    def crypto_random(length):
        # Don't use for greater than 10,000 bytes.
        passes = int(math.ceil(length/32.0))
        def dopasses():
            for i in range(passes):
                rnd = os.urandom(length*8) # 8x for attempted entropy.
                yield hashlib.sha256(rnd).digest()
        return ''.join(dopasses())[:length]


def user(name_col="user", name_len=32):
    """
    """

    class User(object):
        """
        """
        pass

    setattr(User, name_col, sqlalchemy.Column(
                                sqlalchemy.types.Unicode(length=name_len),
                                unique=True, 
                                ))

    return User
