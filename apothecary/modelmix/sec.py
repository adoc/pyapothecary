import base64
import logging
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm
import sqlalchemy.ext.hybrid

import apothecary.util


logger = logging.getLogger(__name__)


# Possibly rename this again.
def record_token_mix(token_col, length=6, oncreate=False, onupdate=False,
                     tokenfunc=apothecary.util.token, index=True,
                     Type=sqlalchemy.types.String):
    """Random tokens used for ident or other security functionality.
    """
    def gentoken():
        # Closure to pass to SQLA events.
        return tokenfunc(length)

    if length < 6:
        log.warning("`record_token_mix` with a length less than 6 is not recomended.")

    class RecordTokenMix(object):
        """
        """
        #@sqlalchemy.ext.hybrid.hybrid_property
        def get_token(self):
            return getattr(self, token_col)

        #@_token.setter
        def set_token(self, value):
            assert isinstance(value, basestring), "`value` must be a string."
            setattr(self, token_col, value)

        def revoke_token(self):
            """
            """
            self.set_token(gentoken())

        token = sqlalchemy.ext.hybrid.hybrid_property(get_token, set_token,
                                                      revoke_token)

    def col(**kwa):
        # Create the Column object with various options.
        if oncreate is True:
            kwa['default'] = gentoken
        if onupdate is True:
            kwa['default'] = gentoken #??
            kwa['onupdate'] = gentoken
        kwa['nullable'] = not(oncreate or onupdate)
        kwa['index'] = index
        return sqlalchemy.Column(Type(length), **kwa)

    setattr(RecordTokenMix, token_col, col())
    return RecordTokenMix


def url_token_mix(created_col='token_created', created_token_size=6,
              updated_token='token_updated', updated_token_size=6,
              hashfunc=apothecary.util.hash):
    """
    """
    CreatedToken = record_token_mix(created_col, length=created_token_size,
                                    oncreate=True, index=True)
    UpdatedToken = record_token_mix(updated_token, length=updated_token_size,
                                    onupdate=True, index=False)

    class UrlSecMix(UpdatedToken, CreatedToken):
        """Provides extra security for urls generated.
        *Defines no columns. Requires the model to also inherit from
        SecMix.
        """

        def get_securl(self, *namespace):
            """Returns hash based on the model's `SecMix.immutid`,
            `SecMix.mutid` and any `args` passed to provide a
            namespace.
            """
            # Formerly get_code
            hashargs = (CreatedToken.get_token(self),
                        UpdatedToken.get_token(self)) + namespace
            digest = hashfunc(*hashargs)
            return base64.urlsafe_b64encode(digest).rstrip('=')

        securl = sqlalchemy.ext.hybrid.hybrid_property(get_securl)

        def get_securlid(self):
            # formerly codeid
            return UpdatedToken.get_token(self)

        securlid = sqlalchemy.ext.hybrid.hybrid_property(get_securlid)

        def validate_securl(self, challenge, *namespace):
            """Validates a challenge code"""
            # formerly validate_code
            return self.get_securl(*namespace) == challenge
            
    return UrlSecMix
