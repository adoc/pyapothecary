import unittest
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.ext.declarative
import apothecary.modelmix

from apothecary.tests import SqlaTestCase

# Multiple bases to separate test schema.
Base = sqlalchemy.ext.declarative.declarative_base()


class IdModel(Base, apothecary.modelmix.id_mix()):
    __tablename__ = "test_id_mix"


class TsModel(Base, apothecary.modelmix.ts_mix('ts')):
    __tablename__ = "test_ts_mix1"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class TsModel2(Base, apothecary.modelmix.ts_mix('ts_created'),
                 apothecary.modelmix.ts_mix('ts_updated')):
    __tablename__ = "test_ts_mix2"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class FlagModel(Base, apothecary.modelmix.flag_mix('flag')):
    __tablename__ = "test_flag_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class FlagTsModel(Base, apothecary.modelmix.flag_ts_mix('flag', 'flag_ts',
                                default_flag=True)):
    __tablename__ = "test_flag_ts_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class RecordTokenMixModel(Base, apothecary.modelmix.record_token_mix('token')):
    __tablename__ = "test_record_token_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class SequenceMixModel(Base, apothecary.modelmix.sequence_mix('sequence')):
    __tablename__ = "test_sequence_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class LookupMixModel(Base, apothecary.modelmix.lookup_mix()):
    __tablename__ = "test_lookup_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


# Tests
# =====
class TestModelMix(SqlaTestCase):
    __base__ = Base
    # Much more extensive tests needed to test other constructions and
    #   functions available.
    def test__timefunc(self):
        ts_now = apothecary.modelmix._timefunc()
        self.assertIsInstance(ts_now, int)
        self.assertGreater(ts_now, 1402776709)

    def test__tokenfunc(self):
        token = apothecary.modelmix._tokenfunc(64)
        self.assertEqual(len(token), 64)

    def test_id_mix(self):
        id_obj = IdModel()
        self.session.add(id_obj)
        self.session.commit()

        # Query object and check it.
        queried_id_obj = self.session.query(IdModel).first()
        self.assertIs(id_obj, queried_id_obj)
        self.assertEqual(id_obj.id, 1)

    def test_ts_mix(self):
        ts_obj = TsModel()
        ts_obj.ts_set_now()
        self.session.add(ts_obj)
        self.session.commit()

        # Query object and check it.
        queried_ts_obj = self.session.query(TsModel).first()
        self.assertIs(ts_obj, queried_ts_obj)
        self.assertGreater(queried_ts_obj.ts, 1402776709)

    def test_flag_mix(self):
        flag_obj = FlagModel()
        self.session.add(flag_obj)
        self.session.commit()

        queried_flag_obj = self.session.query(FlagModel).first()
        self.assertIs(queried_flag_obj, flag_obj)
        self.assertIs(queried_flag_obj.flag, True)

        queried_flag_obj.unset_flag()
        self.session.add(queried_flag_obj)
        self.session.commit()

        queried_flag_obj = self.session.query(FlagModel).first()
        self.assertIs(queried_flag_obj.flag, False)

    def test_flag_ts_mix(self):
        flag_obj = FlagTsModel()
        self.session.add(flag_obj)
        self.session.commit()

        queried_flag_obj = self.session.query(FlagTsModel).first()
        self.assertIs(flag_obj, queried_flag_obj)
        self.assertIs(queried_flag_obj.flag, True)
        self.assertGreater(queried_flag_obj.flag_ts, 1402776709)

    def test_record_token_mix(self):
        token_obj = RecordTokenMixModel()
        token_obj.revoke_token()
        self.session.add(token_obj)
        self.session.commit()

        queried_token_obj = self.session.query(RecordTokenMixModel).first()
        self.assertIs(token_obj, queried_token_obj)
        self.assertIsInstance(queried_token_obj.token, basestring)
        self.assertEqual(len(queried_token_obj.token), 6)

    def test_sequence_mix(self):
        seq_obj = SequenceMixModel()
        self.session.add(seq_obj)
        self.session.commit()

        queried_seq_obj = self.session.query(SequenceMixModel).first()
        self.assertIs(seq_obj, queried_seq_obj)
        self.assertEqual(queried_seq_obj.sequence, 0)

        queried_seq_obj._sequence_inc()
        self.session.add(queried_seq_obj)
        self.session.commit()

        queried_seq_obj = self.session.query(SequenceMixModel).first()
        self.assertIs(seq_obj, queried_seq_obj)
        self.assertEqual(seq_obj.sequence, 1)

    def test_lookup_mix(self):
        lookup_obj = LookupMixModel()
        lookup_obj.key = u"test"
        lookup_obj.value = u"This is a test."
        self.session.add(lookup_obj)
        self.session.commit()

        queried_lookup_obj = self.session.query(LookupMixModel).first()
        self.assertIs(lookup_obj, queried_lookup_obj)
        self.assertEqual(queried_lookup_obj.key, u"test")
        self.assertEqual(queried_lookup_obj.value, u"This is a test.")