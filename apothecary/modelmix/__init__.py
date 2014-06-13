
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
          timefunc=_timefunc):
    class TsMix(object):
        """Base Timestamp model mixin.
        `created_key` - Column name for created timestamp.
        `updated_key` - Column name for updated timestamp.
        `defer` - Defer loading of the columns to access time rather
                  than at query."""
        pass

    def created_col(cls):
        return sqlalchemy.Column(sqlalchemy.types.Integer, default=timefunc,
                                 nullable=False)

    def updated_col(cls):
        return sqlalchemy.Column(sqlalchemy.types.Integer, default=timefunc,
                                 onupdate=timefunc, nullable=False)

    if defer is true:
        setattr(TsMix, created_key, sqlalchemy.orm.defered(created_col()))
        setattr(TsMix, updated_key, sqlalchemy.orm.defered(updated_col()))
    else:
        setattr(TsMix, created_key, created_col())
        setattr(TsMix, updated_key, updated_col())

    return TsMix
TsMix = tsmix()


def flagmix(flag_attr='a_flag', default=True, flag=True, inverse=False,
            col_name=None):
    """Allows for the arbitrary creation of flag (boolean) attributes.
    Queries are automatically filtered based on the flag when coupled
    with codalib.alchemy.unique_constructor or
    codalib.alchemy.query_filters.

    `flagattr` - the name of the flag to be used.
        This is also doubles as the table column name unless `columnname` is set.
        Two methods are added based on this name:
            flag_[flagattr] - Sets the flag. (alias of FlagMix._flag)
            unflag_[flagattr] - Unsets the flag. (alias of FlagMix._unflag)

    `default` - This is the default value set upon row insert.

    `flag` - This is the enabled boolean state.

    `inverse` - This inverses the set state of FlagMix._flag() and FlagMix._unflag() 

    `columnname` - This overrides `flagattr`"""
    # Removed the confusion of `inverse`
    
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
            self._flag = not flag if inverse else flag

        def _unset_flag(self):
            self._flag = flag if inverse else not flag

        @property
        def __filter__(self):
            return self._flag == flag

    def flag_col():
        return Column(sqlalchemy.types.Boolean, default=default,
                      nullable=False)

    setattr(FlagMix, '_'.join(['set', flag_attr]), FlagMix._set_flag)
    setattr(FlagMix, '_'.join(['unset', flag_attr]), FlagMix._unset_flag)
    setattr(FlagMix, col_name or flag_attr, flag_col())

    return FlagMix

FlagMix = flagmix()
ActiveMix = flagmix('active')
DeletableMix = flagmix('deleted', default=False, flag=False, inverse=True)