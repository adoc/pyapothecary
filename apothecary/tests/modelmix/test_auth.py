import unittest
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.ext.declarative

import apothecary.modelmix.auth

from apothecary.tests import SqlaTestCase


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
    __id_attr__ = "id"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class PermissionMix(Base, apothecary.modelmix.auth.permission_mix()):
    __tablename__ = "test_permission_mix"
    __id_attr__ = "id"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


# Working straight example.
#class GroupPermissionMix(Base):
#    __tablename__ = "test_group_permission_mix"
#    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)
#    group_id = sqlalchemy.Column(sqlalchemy.types.Integer,
#                                 sqlalchemy.ForeignKey(GroupMix.id))
#    permission_id = sqlalchemy.Column(sqlalchemy.types.Integer,
#                                 sqlalchemy.ForeignKey(PermissionMix.id))
#GroupMix._permissions = sqlalchemy.orm.relationship(PermissionMix,
#                    secondary=GroupPermissionMix.__table__)


class GroupPermissionMix(Base,
        apothecary.modelmix.auth.group_permission_mix(GroupMix, PermissionMix)):
    __tablename__ = "test_group_permission_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)

GroupPermissionMix.init_group_relationship()


class TestModelMixAuth(SqlaTestCase):
    __base__ = Base

    def test_user_mix(self):
        user = UserMixModel(name="first")
        self.add(user)

        queried_user = self.query(UserMixModel).first()
        self.assertIs(queried_user, user)

        queried_user.name = u"tester"
        queried_user.password = u"12345"
        self.add(queried_user)

        queried_user = self.query(UserMixModel).first()
        self.assertIs(queried_user, user)
        self.assertTrue(queried_user.challenge('12345'))
        self.assertFalse(queried_user.challenge('54321'))

    def test_user_mix_binary_encoded(self):
        user = UserMixEncModel(name="first")
        self.add(user)

        queried_user = self.query(UserMixEncModel).first()
        self.assertIs(queried_user, user)

        queried_user.name = u"tester"
        queried_user.password = u"12345"
        self.add(queried_user)

        queried_user = self.query(UserMixEncModel).first()
        self.assertIs(queried_user, user)
        self.assertTrue(queried_user.challenge('12345'))
        self.assertFalse(queried_user.challenge('54321'))

    def test_group_mix(self):
        group = GroupMix()
        group.name = u"Peasants"
        group.level = 100
        self.add(group)

        queried_group = self.query(GroupMix).get(group.id)
        self.assertIs(queried_group, group)
        self.assertIs(queried_group._name, queried_group.name)
        self.assertIs(queried_group._level, queried_group.level)

        queried_group._level = 101
        queried_group._name = u"Serfs"
        self.add(queried_group)

        queried_group = self.query(GroupMix).get(queried_group.id)
        self.assertIs(queried_group, group)
        self.assertEqual(queried_group.name, u"Serfs")
        self.assertEqual(queried_group.level, 101)

        group2 = GroupMix()
        group2.name = u"Royalty"
        group2.level = 1000
        self.add(group2)

        queried_group2 = self.query(GroupMix).get(group2.id)
        self.assertIs(queried_group2, group2)
        self.assertGreater(queried_group2, queried_group)

    def test_permission_mix(self):
        permission = PermissionMix()
        permission.name = u"perm"
        self.add(permission)

        queried_permission = self.query(PermissionMix).get(permission.id)
        self.assertIs(queried_permission, permission)

    def test_group_permission_mix(self):
        permission = PermissionMix(name="PERM")
        group = GroupMix(name="group")
        
        self.add(permission)
        
        group.permissions.append(permission)
        self.add(group)

