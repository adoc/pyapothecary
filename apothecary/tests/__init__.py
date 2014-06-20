import unittest
import sqlalchemy
import sqlalchemy.orm


# Parent test class.
class SqlaTestCase(unittest.TestCase):
    __dburl__ = "sqlite:///tests.db"
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.__engine__ = sqlalchemy.create_engine(self.__dburl__)
        self.__session__ = sqlalchemy.orm.scoped_session(
                            sqlalchemy.orm.sessionmaker(bind=self.__engine__))

    def setUp(self):
        self.__base__.metadata.create_all(bind=self.__engine__)

    def tearDown(self):
        self.__session__.remove()
        self.__base__.metadata.drop_all(bind=self.__engine__, checkfirst=False)

    def query(self, obj):
        return self.__session__.query(obj)

    def add(self, obj):
        self.__session__.add(obj)
        self.__session__.commit()