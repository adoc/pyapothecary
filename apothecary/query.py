import sqlalchemy
import apothecary.singleton


def dict_query(Model, session=None, query=None, like=False, any=False):
    """Return an object for querying that accepts keyword arguments
    to directly query.
    """

    def _dict_query(*args, **kwa):
        assert session or query or args, "`dict_query` requires a SQLA Session argument."
        if not query:
            Session = session or args[0]
            Query = Session.query(Model)
        else:
            Query = query # Get the query object from the session.

        def build_filters():
            for key, val in kwa.items():
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
            return Query.filter(sqlalchemy.or_(*build_filers()))
        else:
            return Query.filter(sqlalchemy.and_(*build_filters()))
    return _dict_query
