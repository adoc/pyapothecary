import unittest
import sqlalchemy
import sqlalchemy.orm


# Parent test class.
class SqlaTestCase(unittest.TestCase):
    __dburl__ = "sqlite:///tests.db"
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.engine = sqlalchemy.create_engine(self.__dburl__)
        self.session = sqlalchemy.orm.scoped_session(
                            sqlalchemy.orm.sessionmaker(bind=self.engine))

    def setUp(self):
        self.__base__.metadata.create_all(bind=self.engine)

    def tearDown(self):
        self.session.remove()
        self.__base__.metadata.drop_all(bind=self.engine, checkfirst=False)