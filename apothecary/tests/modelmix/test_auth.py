import unittest
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.ext.declarative

import apothecary.modelmix.auth

from apothecary.tests import SqlaTestCase

# Multiple bases to separate test schema.
Base = sqlalchemy.ext.declarative.declarative_base()


class UserMixModel(Base, apothecary.modelmix.auth.user_mix()):
    """
    """
    __tablename__ = "test_user_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class UserMixEncModel(Base, apothecary.modelmix.auth.user_mix(binary_encode=True)):
    """
    """
    __tablename__ = "test_user_mix_enc"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class GroupMix(Base, apothecary.modelmix.auth.group_mix()):
    __tablename__ = "test_group_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class TestModelMixAuth(SqlaTestCase):
    __base__ = Base

    def test_user_mix(self):
        user = UserMixModel()
        self.session.add(user)
        self.session.commit()

        queried_user = self.session.query(UserMixModel).first()
        self.assertIs(queried_user, user)

        queried_user._name = u"tester"
        queried_user._password = u"12345"
        self.session.add(queried_user)
        self.session.commit()

        queried_user = self.session.query(UserMixModel).first()
        self.assertIs(queried_user, user)
        self.assertTrue(queried_user._challenge('12345'))
        self.assertFalse(queried_user._challenge('54321'))

    def test_user_mix_binary_encoded(self):
        user = UserMixEncModel()
        self.session.add(user)
        self.session.commit()

        queried_user = self.session.query(UserMixEncModel).first()
        self.assertIs(queried_user, user)

        queried_user._name = u"tester"
        queried_user._password = u"12345"
        self.session.add(queried_user)
        self.session.commit()

        queried_user = self.session.query(UserMixEncModel).first()
        self.assertIs(queried_user, user)
        self.assertTrue(queried_user._challenge('12345'))
        self.assertFalse(queried_user._challenge('54321'))

        print(dir(queried_user))
        print(vars(queried_user))

    def test_group_mix(self):
        group = GroupMix()
        group.name = u"Peasants"
        group.level = 100
        self.session.add(group)
        self.session.commit()

        queried_group = self.session.query(GroupMix).first()
        self.assertIs(queried_group, group)
        self.assertIs(queried_group._name, queried_group.name)
        self.assertIs(queried_group._level, queried_group.level)

        group2 = GroupMix()
        group2.name = u"Royalty"
        group2.level = 1000
        self.session.add(group2)
        self.session.commit()

        queried_group2 = self.session.query(GroupMix).get(group2.id)
        self.assertIs(queried_group2, group2)
        self.assertGreater(queried_group2, queried_group)