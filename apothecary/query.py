import sqlalchemy
import apothecary.singleton


def dict_query(Model, session=None, like=False, any=False):
    """Return an object for querying that accepts keyword arguments
    to directly query.
    """

    def _dict_query(*args, **kwa):
        assert session or args, "`dict_query` requires a SQLA Session argument."
        Session = session or args[0]

        query = Session.query(Model) # Get the query object from the session.

        def build_filters():
            for key, val in kwa.iteritems():
                attr = getattr(Model, key, None)
                if attr is not None:
                    if like is True:
                        yield attr.like(val)
                    else:
                        yield attr == val
                else:
                    raise KeyError("Attribute `%s` does not exist in model `%s`." % 
                                        (key, Model.__name__))
        if any is True: # Process `any` as "or" and default as "and"
            return query.filter(sqlalchemy.or_(*build_filers()))
        else:
            return query.filter(sqlalchemy.and_(*build_filters()))
    return _dict_query
