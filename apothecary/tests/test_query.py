"""
"""
import random
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm.query
import sqlalchemy.ext.declarative

import apothecary.query

from apothecary.tests import SqlaTestCase


try:
    range = xrange
except NameError:
    pass


Base = sqlalchemy.ext.declarative.declarative_base()


class TestModel(Base):
    __tablename__ = "test_model"
    id = sqlalchemy.Column(sqlalchemy.types.Integer(), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.types.Unicode(32), index=True)
    desc = sqlalchemy.Column(sqlalchemy.types.Unicode(128))
    status = sqlalchemy.Column(sqlalchemy.types.Integer())


class TestDictQuery(SqlaTestCase):
    """
    """
    __base__ = Base
    names = [u'Rudy', u'John', u'Jill', u'Jane', u'George', u'Peter']
    desc = [u'Pretty cool.', u'Does this and that.', u'Wants something.']

    def setUp(self):
        SqlaTestCase.setUp(self)
        # Add some dummy data.
        for i in range(100):
            test = TestModel()
            test.name = random.choice(self.names)
            test.desc = random.choice(self.desc)
            test.status = int(random.random()*10000)
            self.__session__.add(test)
        self.__session__.commit()

    def test_dict_query_closure(self):
        self.assertRaises(AssertionError, apothecary.query.dict_query(TestModel))

        query = apothecary.query.dict_query(TestModel,
                                            session=self.__session__)
        self.assertTrue(callable(query))
        self.assertIsInstance(query(), sqlalchemy.orm.query.Query)

    def test_dict_query_execution(self):
        query = apothecary.query.dict_query(TestModel,
                                            session=self.__session__)

        self.assertEqual(len(query().all()), 100)

        first = self.__session__.query(TestModel).first()
        self.assertGreater(len(query(name=first.name).all()), 0)
        self.assertGreater(len(query(desc=first.desc).all()), 0)
        self.assertGreater(len(query(status=first.status).all()), 0)
