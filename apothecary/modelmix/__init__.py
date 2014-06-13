
from sqlalchemy.types import Boolean, Integer, String, Unicode, DateTime

import time
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm


__all__ = (idmix, IdMix, tsmix, TsMix)


def _timefunc():
    return int(time.time())


def idmix(id_key='id'):
    class IdMix(object):
        """Integer primary key model mixin."""
        pass
    setattr(IdMix, id_key, Column(Integer, primary_key=True))
    return IdMix
IdMix = idmix()


def tsmix(created_key='ts_created', updated_key='ts_updated', defer=True,
          timefunc=_timefunc, Type=sqlalchemy.types.Integer):
    class TsMix(object):
        """Base Timestamp model mixin.
        `created_key` - Column name for created timestamp.
        `updated_key` - Column name for updated timestamp.
        `defer` - Defer loading of the columns to access time rather
                  than at query."""
        pass

    def created_col(cls):
        return sqlalchemy.Column(Type, default=timefunc,
                                 nullable=False)

    def updated_col(cls):
        return sqlalchemy.Column(Type, default=timefunc,
                                 onupdate=timefunc, nullable=False)

    if defer is true:
        setattr(TsMix, created_key, sqlalchemy.orm.defered(created_col()))
        setattr(TsMix, updated_key, sqlalchemy.orm.defered(updated_col()))
    else:
        setattr(TsMix, created_key, created_col())
        setattr(TsMix, updated_key, updated_col())

    return TsMix
TsMix = tsmix()


def flagmix(flag_attr='a_flag', default=True, col_name=None,
            invert_filter=False, Type=sqlalchemy.types.Boolean):
    """Allows for the arbitrary creation of flag (boolean) attributes.
    Queries are automatically filtered based on the flag when coupled
    with .unique_constructor, .query_filters, or .rebase metaclass.

    `flag_attr` - the name of the flag attribute.
        This is also doubles as the table column name unless
        `col_name` is set. Two methods are added based on this name:
            flag_[flagattr] - Sets the flag. (alias of FlagMix._flag)
            unflag_[flagattr] - Unsets the flag. (alias of FlagMix._unflag)

    `default` - This is the default value set upon row insert.

    `invert_filter` - This inverts the filter from expecting a True
        value to Fale.
    """
    # Removed the confusion of `inverse`. Replaced with `invert_filter`
    # Removed col_name.
    class FlagMix(object):
        """ """
        @property
        def _flag(self):
            return getattr(self, flag_attr)

        @_flag.setter
        def _flag(self, value):
            assert isinstance(value, bool), "`value` must be boolean."
            setattr(self, flag_attr, value)

        def _set_flag(self):
            self._flag = True

        def _unset_flag(self):
            self._flag = False

        @property
        def __filter__(self):
            return self._flag is False if invert_filter else True

    def flag_col():
        return sqlalchemy.Column(sqlalchemy.types.Boolean, default=default,
                                 nullable=False)

    setattr(FlagMix, '_'.join(['set', flag_attr]), FlagMix._set_flag)
    setattr(FlagMix, '_'.join(['unset', flag_attr]), FlagMix._unset_flag)
    setattr(FlagMix, flag_attr, flag_col())

    return FlagMix

FlagMix = flagmix()
ActiveMix = flagmix('active')
DeletableMix = flagmix('deleted', default=False, invert_filter=True)