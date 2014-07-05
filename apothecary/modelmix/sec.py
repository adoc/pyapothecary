import pprint

import base64
import inspect
import logging
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm
import sqlalchemy.ext.hybrid
import sqlalchemy.ext.declarative

import apothecary.util


logger = logging.getLogger(__name__)


# Possibly rename this again.
def record_token_mix(attr_name, col_name=None, length=6, onupdate=False,
                     index=True, binary_encode=False,
                     tokenfunc=apothecary.util.token,
                     hashfunc=apothecary.util.hash,
                     basefunc=apothecary.util.benc):
    """Random tokens used for ident or other security functionality.
    """

    if length < 6:
        log.warning("`record_token_mix` with a length less than 6 is not "
                    "recomended.")

    #_tokenfunc = lambda *a: tokenfunc(length)
    
    _attr_name = ''.join(['_', attr_name])
    _col_name = col_name or attr_name
    _binary_token_size = basefunc.overhead(length) # Calculate and store overhead.
    
    def encode(value):
        if binary_encode is True and value:
            return basefunc.encode(value)
        return value

    def decode(value):
        if binary_encode is True and value:
            return basefunc.decode(value)
        return value

    def token():
        return hashfunc(tokenfunc(length))[:length]

    class RecordTokenMix(object):
        """
        """
        def get_token(self):
            return decode(getattr(self, _attr_name))

        def set_token(self, value):
            assert isinstance(value, basestring), "`value` must be a string."
            setattr(self, _attr_name, encode(value))

        def revoke_token(self):
            self.set_token(token())

    def col_args(**kwa):
        kwa['default'] = lambda *a: encode(token())
        if onupdate is True:
            kwa['onupdate'] = lambda *a: encode(token())
        kwa['nullable'] = False # not(oncreate or onupdate)
        kwa['index'] = index is True
        return kwa

    if binary_encode is True:
        # Set up a string column for binary encoded values.
        setattr(RecordTokenMix, _attr_name,
                sqlalchemy.Column(_col_name,
                    sqlalchemy.types.String(_binary_token_size), **col_args()))
    else:
        # Set up a binary column.
        setattr(RecordTokenMix, _attr_name,
                sqlalchemy.Column(_col_name,
                    sqlalchemy.types.LargeBinary(length), **col_args()))

    # Set up a synonym for the user defined attribute name.
    setattr(RecordTokenMix, attr_name,
                apothecary.util.synonym(_attr_name, RecordTokenMix.get_token,
                    RecordTokenMix.set_token, RecordTokenMix.revoke_token))

    #setattr(RecordTokenMix, attr_name,
    #        sqlalchemy.ext.declarative.declared_attr(lambda cls:
    #                sqlalchemy.orm.synonym(_attr_name,
    #                        descriptor=property(RecordTokenMix.get_token,
    #                                RecordTokenMix.set_token,
    #                                RecordTokenMix.revoke_token))))
    return RecordTokenMix


def url_token_mix(created_col='token_created', created_token_size=6,
                  updated_token='token_updated', updated_token_size=6,
                  hashfunc=apothecary.util.hash):
    """
    """
    CreatedToken = record_token_mix(created_col, length=created_token_size,
                                    index=True)
    UpdatedToken = record_token_mix(updated_token, length=updated_token_size,
                                    onupdate=True, index=False)

    class UrlSecMix(UpdatedToken, CreatedToken):
        """Provides one-time tokens 
        """
        def get_securl(self, *namespace):
            """Returns hash based on the model's `SecMix.immutid`,
            `SecMix.mutid` and any `args` passed to provide a
            namespaceself.
            """
            hashargs = (CreatedToken.get_token(self),
                        UpdatedToken.get_token(self)) + namespace
            digest = hashfunc(*hashargs)
            return base64.urlsafe_b64encode(digest)#.rstrip('=')

        def validate_securl(self, challenge, *namespace):
            """Validates a challenge code"""
            # formerly validate_code
            return self.get_securl(*namespace) == challenge

        securl = property(get_securl)
        securlid = sqlalchemy.ext.declarative.declared_attr(
                        lambda cls: sqlalchemy.orm.synonym(created_col))

    return UrlSecMix

