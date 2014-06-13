
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