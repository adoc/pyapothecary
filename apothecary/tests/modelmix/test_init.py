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


class SequenceMixModel(Base, apothecary.modelmix.sequence_mix('sequence')):
    __tablename__ = "test_sequence_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)


class LookupMixModel(Base, apothecary.modelmix.lookup_mix()):
    __tablename__ = "test_lookup_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)

class AssociationLeft(Base):
    __tablename__ = "test_association_left"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.types.String(32), index=True)

class AssociationRight(Base):
    __tablename__ = "test_association_right"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.types.String(32), index=True)

class AssociationMix(Base,
        apothecary.modelmix.association_mix(AssociationLeft, AssociationRight)):
    __tablename__ = "test_association_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)

AssociationMix.init_left_relationship('rights')
AssociationMix.init_right_relationship('lefts')


class AssociationMultPriLeft(Base):
    __tablename__ = "test_association_multipri_left"
    id0 = sqlalchemy.Column(sqlalchemy.types.Boolean, primary_key=True)
    id1 = sqlalchemy.Column(sqlalchemy.types.Boolean, primary_key=True)
    #id2 = sqlalchemy.Column(sqlalchemy.types.Boolean, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.types.String(32), index=True)


class AssociationMultPriRight(Base):
    __tablename__ = "test_association_multipri_right"
    id0 = sqlalchemy.Column(sqlalchemy.types.Boolean, primary_key=True)
    id1 = sqlalchemy.Column(sqlalchemy.types.Boolean, primary_key=True)
    #id2 = sqlalchemy.Column(sqlalchemy.types.Boolean, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.types.String(32), index=True)


class AssociationMultPri(Base,
        apothecary.modelmix.association_mix(AssociationMultPriLeft, 
                                   AssociationMultPriRight)):
    __tablename__ = "test_association_multipri_mix"
    id = sqlalchemy.Column(sqlalchemy.types.Integer, primary_key=True)
#print(vars(AssociationMultPri))
#AssociationMultPri.init_left_relationship('rights')
#AssociationMultPri.init_right_relationship('lefts')


# Tests
# =====
class TestModelMix(SqlaTestCase):
    __base__ = Base
    # Much more extensive tests needed to test other constructions and
    #   functions available.

    def test_id_mix(self):
        id_obj = IdModel()
        self.__session__.add(id_obj)
        self.__session__.commit()

        # Query object and check it.
        queried_id_obj = self.__session__.query(IdModel).first()
        self.assertIs(id_obj, queried_id_obj)
        self.assertEqual(id_obj.id, 1)

    def test_ts_mix(self):
        ts_obj = TsModel()
        ts_obj.ts_set_now()
        self.__session__.add(ts_obj)
        self.__session__.commit()

        # Query object and check it.
        queried_ts_obj = self.__session__.query(TsModel).first()
        self.assertIs(ts_obj, queried_ts_obj)
        self.assertGreater(queried_ts_obj.ts, 1402776709)

    def test_flag_mix(self):
        flag_obj = FlagModel()
        self.__session__.add(flag_obj)
        self.__session__.commit()

        queried_flag_obj = self.__session__.query(FlagModel).first()
        self.assertIs(queried_flag_obj, flag_obj)
        self.assertIs(queried_flag_obj.flag, True)

        queried_flag_obj.unset_flag()
        self.__session__.add(queried_flag_obj)
        self.__session__.commit()

        queried_flag_obj = self.__session__.query(FlagModel).first()
        self.assertIs(queried_flag_obj.flag, False)

    def test_flag_ts_mix(self):
        flag_obj = FlagTsModel()
        self.__session__.add(flag_obj)
        self.__session__.commit()

        queried_flag_obj = self.__session__.query(FlagTsModel).first()
        self.assertIs(flag_obj, queried_flag_obj)
        self.assertIs(queried_flag_obj.flag, True)
        self.assertGreater(queried_flag_obj.flag_ts, 1402776709)

    def test_sequence_mix(self):
        seq_obj = SequenceMixModel()
        self.__session__.add(seq_obj)
        self.__session__.commit()

        queried_seq_obj = self.__session__.query(SequenceMixModel).first()
        self.assertIs(seq_obj, queried_seq_obj)
        self.assertEqual(queried_seq_obj.sequence, 0)

        queried_seq_obj._sequence_inc()
        self.__session__.add(queried_seq_obj)
        self.__session__.commit()

        queried_seq_obj = self.__session__.query(SequenceMixModel).first()
        self.assertIs(seq_obj, queried_seq_obj)
        self.assertEqual(seq_obj.sequence, 1)

    def test_lookup_mix(self):
        lookup_obj = LookupMixModel()
        lookup_obj.key = u"test"
        lookup_obj.value = u"This is a test."
        self.__session__.add(lookup_obj)
        self.__session__.commit()

        queried_lookup_obj = self.__session__.query(LookupMixModel).first()
        self.assertIs(lookup_obj, queried_lookup_obj)
        self.assertEqual(queried_lookup_obj.key, u"test")
        self.assertEqual(queried_lookup_obj.value, u"This is a test.")

    def test_association_mix(self):
        left1 = AssociationLeft(name="left1")
        left2 = AssociationLeft(name="left2")
        left3 = AssociationLeft(name="left3")
        left4 = AssociationLeft(name="left4")
        right1 = AssociationRight(name="right1")
        right2 = AssociationRight(name="right2")
        right3 = AssociationRight(name="right3")
        right4 = AssociationRight(name="right4")

        left1.rights.append(right1)
        left1.rights.append(right3)
        left2.rights.append(right2)
        left2.rights.append(right4)
        right3.lefts.append(left3)
        right4.lefts.append(left4)

        self.add(left1)
        self.add(left2)
        self.add(left3)
        self.add(left4)
        self.add(right1)
        self.add(right2)
        self.add(right3)
        self.add(right4)

        qleft1 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left1").one())
        qleft2 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left2").one())
        qleft3 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left3").one())
        qleft4 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left4").one())

        self.assertIs(qleft1.rights[0], right1)
        self.assertIs(qleft1.rights[1], right3)
        self.assertIs(qleft2.rights[0], right2)
        self.assertIs(qleft2.rights[1], right4)
    '''
    def test_association_multipre_mix(self):
        left1 = AssociationMultPriLeft(id0=0, id1=0, name="left1")
        left2 = AssociationMultPriLeft(id0=1, id1=0, name="left2")
        left3 = AssociationMultPriLeft(id0=0, id1=1, name="left3")
        left4 = AssociationMultPriLeft(id0=1, id1=1, name="left4")
        right1 = AssociationMultPriRight(id0=0, id1=0, name="right1")
        right2 = AssociationMultPriRight(id0=1, id1=0, name="right2")
        right3 = AssociationMultPriRight(id0=0, id1=1, name="right3")
        right4 = AssociationMultPriRight(id0=1, id1=1, name="right4")

        left1.rights.append(right1)
        left1.rights.append(right3)
        left2.rights.append(right2)
        left2.rights.append(right4)
        right3.lefts.append(left3)
        right4.lefts.append(left4)

        self.add(left1)
        self.add(left2)
        self.add(left3)
        self.add(left4)
        self.add(right1)
        self.add(right2)
        self.add(right3)
        self.add(right4)

        qleft1 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left1").one())
        qleft2 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left2").one())
        qleft3 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left3").one())
        qleft4 = (self.__session__.query(AssociationLeft)
                    .filter(AssociationLeft.name=="left4").one())

        self.assertIs(qleft1.rights[0], right1)
        self.assertIs(qleft1.rights[1], right3)
        self.assertIs(qleft2.rights[0], right2)
        self.assertIs(qleft2.rights[1], right4)'''