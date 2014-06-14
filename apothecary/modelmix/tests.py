import unittest
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import apothecary.modelmix


Base = sqlalchemy.ext.declarative.declarative_base()


# Test Models
# ===========
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


# Tests
# =====

class TestModelMix(unittest.TestCase):
    # Much more extensive tests needed to test other constructions and
    #   functions available.
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.engine = sqlalchemy.create_engine("sqlite:///tests.db")
        self.session = sqlalchemy.orm.scoped_session(
                            sqlalchemy.orm.sessionmaker(bind=self.engine))

    def setUp(self):
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self):
        self.session.remove()
        Base.metadata.drop_all(bind=self.engine, checkfirst=False)

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
