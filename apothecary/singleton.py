from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ('Session',)

Session = scoped_session(sessionmaker())