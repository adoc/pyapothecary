import unittest
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.ext.declarative

import apothecary.modelmix.auth

from apothecary.tests import SqlaTestCase

# Multiple bases to separate test schema.
Base = sqlalchemy.ext.declarative.declarative_base()


class User(Base, apothecary.modelmix.auth.user_mix()):
    """
    """
    __tablename__ = "test_user1"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class UserBinenc(Base, apothecary.modelmix.auth.user_mix(binary_encode=True)):
    """
    """
    __tablename__ = "test_user2"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class TestModelMixAuth(SqlaTestCase):
    __base__ = Base


    def test_base_user(self):
        user = User()
        self.session.add(user)
        self.session.commit()

        queried_user = self.session.query(User).first()
        self.assertIs(queried_user, user)

        queried_user._name = u"tester"
        queried_user._password = u"12345"
        self.session.add(queried_user)
        self.session.commit()

        queried_user = self.session.query(User).first()
        self.assertIs(queried_user, user)
        self.assertTrue(queried_user._challenge('12345'))
        self.assertFalse(queried_user._challenge('54321'))

    def test_base_user_binary_encoded(self):
        user = UserBinenc()
        self.session.add(user)
        self.session.commit()

        queried_user = self.session.query(UserBinenc).first()
        self.assertIs(queried_user, user)

        queried_user._name = u"tester"
        queried_user._password = u"12345"
        self.session.add(queried_user)
        self.session.commit()

        queried_user = self.session.query(UserBinenc).first()
        self.assertIs(queried_user, user)
        self.assertTrue(queried_user._challenge('12345'))
        self.assertFalse(queried_user._challenge('54321'))

        print(dir(queried_user))
        print(vars(queried_user))

        assert False