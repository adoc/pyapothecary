"""SQLAlchemy Model Mixins

id_mix
    IdMix
ts_mix
    TsUpdatedMix
    TsCreatedMix
flag_mix
    ActiveMix
    DeletableMix

"""


import logging
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm
import sqlalchemy.ext.hybrid
import sqlalchemy.ext.declarative

import apothecary.util


logger = logging.getLogger(__name__)

__all__ = ("id_mix", "IdMix", "ts_mix")


class ConstructorMix(object):
    """This sets column values using constructor keyword args.
    """
    def __init__(self, *args, **kwa):
        """
        """
        cls = self.__class__
        for key, val in kwa.items():
            # Set primary attribute.
            if self.__table__.columns.has_key(key):
                setattr(self, key, val) # Set
            # Set descriptor attribute.
            elif hasattr(cls, key):
                attr = getattr(cls, key)
                if hasattr(attr, 'descriptor'):
                    if isinstance(getattr(attr, 'descriptor'), property):
                        setattr(self, key, val) # Set
            else:
                # Raise here I think.
                # kwa ignored.
                logger.warning("Key `%s` was not found in model. Ignoring.")


def id_mix(id_attr='id', id_col=None):
    """
    """
    id_col = id_col or id_attr
    class IdMix(object):
        """Integer primary key model mixin."""
        __id_attr__ = id_attr
        pass

    def col(**kwa):
        kwa['primary_key'] = True
        return sqlalchemy.Column(id_col, sqlalchemy.types.Integer, **kwa)

    setattr(IdMix, id_attr, col())
    return IdMix
IdMix = id_mix()


def ts_mix(ts_attr, ts_col=None, oncreate=False, onupdate=False, defer=False,
          timefunc=apothecary.util.time, Type=sqlalchemy.types.Integer):
    """
    `ts_col` - Column name for created timestamp.
    `oncreate` -
    `onupdate` -
    `defer` - Defer loading of the columns to access time rather
              than at query.
    `timefunc` - 
    `Type` -
    """
    ts_col = ts_col or ts_attr
    #assert isinstance(ts_col, basestring), "`ts_col` attribute must be a string."

    class TsMix(object):
        """Timestamp Model Mixin.
        """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _ts(self):
            return getattr(self, ts_attr)

        @_ts.setter
        def _ts(self, value):
            setattr(self, ts_attr, value)

        def _set_now(self):
            self._ts = timefunc()

    def col(**col_kwa):
        # Create the Column object with various options.
        if oncreate is True:
            col_kwa['default'] = timefunc
        if onupdate is True:
            col_kwa['default'] = timefunc #??
            col_kwa['onupdate'] = timefunc
        col_kwa['nullable'] = not(oncreate or onupdate)
        return sqlalchemy.Column(ts_col, Type, **col_kwa)

    setattr(TsMix, '_'.join([ts_attr, 'set_now']), TsMix._set_now)

    if defer is True:
        # Defer loading of column.
        setattr(TsMix, ts_attr, sqlalchemy.orm.defered(col()))
    else:
        # Eager (?) loading of column.
        setattr(TsMix, ts_attr, col())
    return TsMix
TsUpdatedMix = ts_mix('ts_updated', onupdate=True)
TsCreatedMix = ts_mix('ts_created', oncreate=True)


def flag_mix(flag_col, default=True, invert_filter=False,
            Type=sqlalchemy.types.Boolean):
    """Allows for the arbitrary creation of flag (boolean) attributes.
    Queries are automatically filtered based on the flag when coupled
    with .unique_constructor, .query_filters, or .rebase metaclass.

    `flag_col` - the name of the flag attribute.
        This is also doubles as the table column name unless
        `col_name` is set. Two methods are added based on this name:
            flag_[flagattr] - Sets the flag. (alias of FlagMix._flag)
            unflag_[flagattr] - Unsets the flag. (alias of FlagMix._unflag)

    `default` - This is the default value set upon row insert.

    `invert_filter` - This inverts the filter from expecting a True
        value to Fale.

    `Type` - The SQLAlchemy type to use for the column.
    """
    # Removed the confusion of `inverse`. Replaced with `invert_filter`
    # Removed col_name.
    class FlagMix(object):
        """ """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _flag(self):
            return getattr(self, flag_col)

        @_flag.setter
        def _flag(self, value):
            assert isinstance(value, bool), "`value` must be boolean."
            setattr(self, flag_col, value)

        def _set_flag(self):
            self._flag = True

        def _unset_flag(self):
            self._flag = False

        @property
        def __filter__(self):
            return self._flag is False if invert_filter else True

    def col():
        return sqlalchemy.Column(sqlalchemy.types.Boolean, default=default,
                                 nullable=False)

    setattr(FlagMix, '_'.join(['set', flag_col]), FlagMix._set_flag)
    setattr(FlagMix, '_'.join(['unset', flag_col]), FlagMix._unset_flag)
    setattr(FlagMix, flag_col, col())

    return FlagMix
ActiveMix = flag_mix('active')
DeletableMix = flag_mix('deleted', default=False, invert_filter=True)


def flag_ts_mix(flag_col, ts_col, default_flag=False, timefunc=apothecary.util.time):
    FlagMix = flag_mix(flag_col, default=default_flag)
    TsMix = ts_mix(ts_col, timefunc=timefunc, oncreate=default_flag is True)

    class FlagTsMix(FlagMix, TsMix):
        """
        """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _flag(self):
            return FlagMix._flag(self)

        @_flag.setter
        def _flag(self, value):
            # Can this be refactored to not repeat what's in FlagMix?
            assert isinstance(value, bool), "`value` must be boolean."
            setattr(self, flag_col, value)

            if value is True:
                setattr(self, ts_col, timefunc())
            else:
                setattr(self, ts_col, None)

    return FlagTsMix


def sequence_mix(sequence_col, default=0, index=True):
    class SequenceMix(object):
        """Base Sequence mixin class """
        
        @sqlalchemy.ext.hybrid.hybrid_property
        def _sequence(self):
            return getattr(self, sequence_col)

        @_sequence.setter
        def _sequence(self, value):
            assert isinstance(value, int), "`value` must be an integer."
            setattr(self, sequence_col, value)

        def _sequence_inc(self):
            self._sequence += 1

        def _sequence_dec(self):
            self._sequence -= 1

    def col(**kwa):
        return sqlalchemy.Column(sqlalchemy.types.Integer, index=index,
                                 nullable=True, default=default)

    setattr(SequenceMix, sequence_col, col())
    return SequenceMix
SequenceMix = sequence_mix('sequence')


def lookup_mix(key_col='key', value_col='desc', ext_col=None,
               index_name=True, key_len=32, value_len=160, ext_len=1024):
    """Provides a simple 'key', 'value', and optionally 'extended'
    columns. While resembling a key/value store, there are better tools
    for that.
    'key' is always required and indexed by default.
    'value' and 'extended value' expect Unicode and are
        nullable.
    """
    class LookupMix(object):
        """Base Simple Lookup model"""
        pass

    setattr(LookupMix, key_col,
                sqlalchemy.Column(sqlalchemy.types.String(length=key_len),
                                  unique=index_name, index=index_name,
                                  nullable=False))
    setattr(LookupMix, value_col,
                sqlalchemy.Column(sqlalchemy.types.Unicode(length=value_len),
                                  nullable=True))
    if ext_col is not None:
        setattr(LookupMix, ext_col,
                    sqlalchemy.Column(sqlalchemy.types.Unicode(length=ext_len),
                                      nullable=True))
    return LookupMix

LookupMix = lookup_mix()
LookupMixExt = lookup_mix(ext_col='ext')

'''
# borked
def association_mix(left_cls, right_cls,
                    left_id_colprefix="left_id",
                    right_id_colprefix="right_id"):
    """
    """# Not working for multi_pri key relationships. Need to check proper
        # usage of `foreign_keys` on relationship.
    left_pri_key_cols = left_cls.__table__.primary_key.columns
    right_pri_key_cols = right_cls.__table__.primary_key.columns

    class AssociationMix(object):
        """
        """
        @classmethod
        def init_left_relationship(cls, attrname, **kwa):
            """
            """
            kwa['secondary'] = cls.__table__
            #kwa['foreign_keys'] = cls.__left_local_keys__
            #print(kwa['foreign_keys'])
            setattr(left_cls, attrname,
                    sqlalchemy.orm.relationship(right_cls, **kwa))

        @classmethod
        def init_right_relationship(cls, attrname, **kwa):
            """
            """
            kwa['secondary'] = cls.__table__
            kwa['foreign_keys'] = cls.__right_local_keys__
            setattr(right_cls, attrname,
                    sqlalchemy.orm.relationship(left_cls, **kwa))

    def apply_col_attrs(columns, prefix):
        local_keys = []
        for n, pack in enumerate(columns.items()):
            key, foreign_column = pack
            colkey = '_'.join([prefix, key]) #and n??
            
            col = sqlalchemy.Column(colkey, 
                            foreign_column.type,
                            sqlalchemy.ForeignKey(foreign_column))

            #column = apothecary.util.column(colkey, 
            #                foreign_column.type,
            #                sqlalchemy.ForeignKey(foreign_column))
            setattr(AssociationMix, colkey, sqlalchemy.ext.declarative.declared_attr(lambda cls: col))
            local_keys.append(col)
        return local_keys

    AssociationMix.__left_local_keys__ = apply_col_attrs(left_pri_key_cols, left_id_colprefix)
    AssociationMix.__right_local_keys__ = apply_col_attrs(right_pri_key_cols, right_id_colprefix)

    return AssociationMix
'''

class UniqueMix(object):
    """
    author: Michael Bayer
    src: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/UniqueObject
    """
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return apothecary.util.unique(
                    session,
                    cls,
                    cls.unique_hash,
                    cls.unique_filter,
                    cls,
                    arg, kw
               )