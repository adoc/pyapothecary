import unittest
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.ext.declarative
import apothecary.modelmix.sec

from apothecary.tests import SqlaTestCase

# Multiple bases to separate test schema.
Base = sqlalchemy.ext.declarative.declarative_base()


class RecordTokenMixModel(Base, apothecary.modelmix.sec.record_token_mix('token')):
    __tablename__ = "test_record_token_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class UrlTokenMixModel(Base, apothecary.modelmix.sec.url_token_mix()):
    __tablename__ = "test_url_token_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)
    upd = sqlalchemy.Column(sqlalchemy.types.String(16))

class TestSecModelMix(SqlaTestCase):
    __base__ = Base

    def test_record_token_mix(self):
        token_obj = RecordTokenMixModel()
        token_obj.revoke_token()
        self.__session__.add(token_obj)
        self.__session__.commit()

        queried_token_obj = self.__session__.query(RecordTokenMixModel).first()
        self.assertIs(token_obj, queried_token_obj)
        self.assertIsInstance(queried_token_obj.token, basestring)
        self.assertEqual(len(queried_token_obj.token), 6)

    def test_url_token_mix(self):
        url_token_obj = UrlTokenMixModel()
        url_token_obj.upd = "test"
        self.__session__.add(url_token_obj)
        self.__session__.commit()

        queried_obj = self.__session__.query(UrlTokenMixModel).first()
        securl = queried_obj.securl
        #print(queried_obj.token_created)
        #print(queried_obj.token_updated)
        #print(queried_obj.securl)
        #print(queried_obj.securlid)

        self.assertTrue(queried_obj.validate_securl(securl))

        #assert False