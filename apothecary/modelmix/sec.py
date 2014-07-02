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
                     tokenfunc=apothecary.util.token, index=True,
                     Type=sqlalchemy.types.String):
    """Random tokens used for ident or other security functionality.
    """

    if length < 6:
        log.warning("`record_token_mix` with a length less than 6 is not "
                    "recomended.")

    _tokenfunc = lambda *a: tokenfunc(length)
    _attr_name = '_' + attr_name
    _col_name = col_name or attr_name

    class RecordTokenMix(object):
        """
        """
        def get_token(self):
            return getattr(self, _attr_name)

        def set_token(self, value):
            assert isinstance(value, basestring), "`value` must be a string."
            setattr(self, _attr_name, value)

        def revoke_token(self):
            self.set_token(_tokenfunc())

    def token_col(**kwa):
        kwa['default'] = _tokenfunc
        if onupdate is True:
            kwa['onupdate'] = _tokenfunc
        kwa['nullable'] = False # not(oncreate or onupdate)
        kwa['index'] = index
        return sqlalchemy.Column(_col_name, Type(length), **kwa)

    setattr(RecordTokenMix, _attr_name, token_col())
    setattr(RecordTokenMix, attr_name,
            sqlalchemy.ext.declarative.declared_attr(lambda cls:
                    sqlalchemy.orm.synonym(_attr_name,
                            descriptor=property(RecordTokenMix.get_token,
                                    RecordTokenMix.set_token,
                                    RecordTokenMix.revoke_token))))
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
            return base64.urlsafe_b64encode(digest).rstrip('=')

        def validate_securl(self, challenge, *namespace):
            """Validates a challenge code"""
            # formerly validate_code
            return self.get_securl(*namespace) == challenge

        securl = property(get_securl)
        securlid = sqlalchemy.ext.declarative.declared_attr(
                        lambda cls: sqlalchemy.orm.synonym(created_col))

    return UrlSecMix
