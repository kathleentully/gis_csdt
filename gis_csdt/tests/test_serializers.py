from time import sleep
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from gis_csdt.models import Location, GeoCoordinates, DatasetNameField, Dataset, MapPoint, MapElement, Sensor, DataPoint, PhoneNumber, MapPolygon, DataElement, DataField, Tag, TagIndiv
from gis_csdt.views import DataToGSM7
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, TestSerializer, MapPolygonSerializer, CountPointsSerializer, AnalyzeAreaSerializer, AnalyzeAreaNoValuesSerializer, DataPointSerializer, SensorSerializer
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from rest_framework.request import Request
from django.http import HttpRequest, QueryDict
import urllib

User = get_user_model()

class TestDatasetSerializer(TestCase):
	def test_dataset_serializer(self):
		ds = Dataset(name="RPI")
		ds.save()
		data = {'name': 'RPI'}
		serializer = DatasetSerializer(data=data)
		self.assertTrue(serializer.is_valid())
		self.assertEqual(serializer.get_count(ds), 0)
		me = MapElement(dataset=ds)
		me.save()
		self.assertEqual(serializer.get_count(ds), 1)

class TestTestSerializer(TestCase):
	fixtures = ['test_data.json']

	def test_can_create_serializer(self):
		mp = MapPoint.objects.get(pk=1)
		ds = Dataset.objects.get(pk=1)
		me = MapElement(dataset=ds, mappoint=mp)
		me.save()
		df = DataField(dataset=ds, field_type='I', field_name='int_data', field_en='test')
		df.save()
		element = DataElement(mapelement=me, datafield=df, int_data=23)
		element.save()
		request = RequestFactory().put('/?data=all')
		self.user = User.objects.get(username='test')
		request.user = self.user
		# convert the HTTP Request object to a REST framework Request object
		self.request = APIView().initialize_request(request) 
		serializer = TestSerializer(context={'request': self.request})
		expected_address = {"street": "", "city": "Troy", "state": "NY", "zipcode": "", "county": ""}
		self.assertEqual(serializer.get_address(me), expected_address)
		self.assertEqual(serializer.get_data(me), {'test': 23})

class TestCountPointsSerializer(TestCase):
	fixtures = ['test_data.json']

	def test_can_create_serializer(self):
		ds = Dataset.objects.get(pk=1)		
		names = DatasetNameField(field1_en='en1', field2_en='en2')
		setattr(ds, "names", names)
		p1 = Polygon( ((0, 0), (0, 1), (1, 1), (0, 0)) )
 		p2 = Polygon( ((1, 1), (1, 2), (2, 2), (1, 1)) )
		mpoly = MultiPolygon(p1, p2)
		polygon = MapPolygon(lat='42.7302', lon='73.6788', field1=1.0, field2=2.0, mpoly=mpoly, dataset=ds)
		polygon.save()
		# me = MapElement(name='RPI', dataset=ds, mappolygon=polygon)
		# me.save()
		# sleep(1)
		df1 = DataField(dataset=ds, field_type='I', field_name='int_data', field_en='test1')
		df1.save()
		df2 = DataField(dataset=ds, field_type='F', field_name='float_data', field_en='test2')
		df2.save()
		df3 = DataField(dataset=ds, field_type='C', field_name='char_data', field_en='test3')
		df3.save()

		element1 = DataElement(mapelement=polygon, datafield=df1, int_data=23)
		element1.save()
		element2 = DataElement(mapelement=polygon, datafield=df2, float_data=2.34)
		element2.save()
		element3 = DataElement(mapelement=polygon, datafield=df3, char_data='abc')
		element3.save()

		request = RequestFactory().put('/?data=all')
		self.user = User.objects.get(username='test')
		request.user = self.user
		# convert the HTTP Request object to a REST framework Request object
		self.request = APIView().initialize_request(request) 
		serializer = CountPointsSerializer(context={'request': self.request})
		self.assertEqual(serializer.get_count(polygon), 
						 {'test1': 23, 'en1': 1.0, 'en2': 2.0, 'test2': 2.34, 'test3': 'abc'})

class TestAnalyzeAreaSerializer(TestCase):
	fixtures = ['test_data.json']

	def setUp(self):
		ds = Dataset(name="census2016")
		ds.save()
		self.mp = MapPoint.objects.get(pk=1)
		self.mp.dataset = ds
		self.mp.point = Point(5, 23)
		MapPoint(lat=23.41, lon=98.0, dataset=ds, point=Point(5, 23)).save()
		tag1 = Tag(dataset=ds, tag='tag1', approved=True, count=1)
		tag1.save()
		tag2 = Tag(dataset=ds, tag='tag2', approved=True, count=1)
		tag2.save()
		tagindiv1 = TagIndiv(tag=tag1, mapelement=self.mp)
		tagindiv1.save()
		tagindiv2 = TagIndiv(tag=tag2, mapelement=self.mp)
		tagindiv2.save()
		# p1 = Polygon( ((0, 0), (3, 7), (10, 10), (0, 0)) )
 	# 	p2 = Polygon( ((1, 1), (1, 4), (15, 15), (1, 1)) )
		# mpoly = MultiPolygon(p1, p2)
		# polygon = MapPolygon(lat='50.2340', lon='28.3282', field1=1.0, field2=2.0, mpoly=mpoly, dataset=ds, remote_id=1)
		# polygon.save()
	
		self.request = HttpRequest()
		qdict = QueryDict('', mutable=True)
		qdict.update({'year': '2014'})
		qdict.update({'year': '2016'})
		qdict.update({'unit': 'km'})
		self.request.GET = qdict
		self.serializer = AnalyzeAreaSerializer(context={'request': self.request})
	
	def test_can_get_areaAroundPoint(self):
		data = self.serializer.get_areaAroundPoint(self.mp)
		self.assertEqual(data['point id(s)'], '2')
		self.assertTrue(data.get('1.000000 km'))
		self.assertTrue(data.get('3.000000 km'))
		self.assertTrue(data.get('5.000000 km'))

	def test_can_get_areaAroundPoint2(self):
		data = self.serializer.get_areaAroundPoint2(self.mp)
		self.assertTrue(data.get('1.000000 km'))
		self.assertTrue(data.get('3.000000 km'))
		self.assertTrue(data.get('5.000000 km'))

class TestAnalyzeAreaNoValuesSerializer(TestCase):
	fixtures = ['test_data.json']

	def setUp(self):
		ds = Dataset(name="census2016")
		ds.save()
		self.mp = MapPoint.objects.get(pk=1)
		self.mp.dataset = ds
		self.mp.point = Point(5, 23)
		MapPoint(lat=23.41, lon=98.0, dataset=ds, point=Point(5, 23), state='NY', city='NYC').save()
		tag1 = Tag(dataset=ds, tag='tag1', approved=True, count=1)
		tag1.save()
		tag2 = Tag(dataset=ds, tag='tag2', approved=True, count=1)
		tag2.save()
		tagindiv1 = TagIndiv(tag=tag1, mapelement=self.mp)
		tagindiv1.save()
		tagindiv2 = TagIndiv(tag=tag2, mapelement=self.mp)
		tagindiv2.save()
		# p1 = Polygon( ((0, 0), (3, 7), (10, 10), (0, 0)) )
 	# 	p2 = Polygon( ((1, 1), (1, 4), (15, 15), (1, 1)) )
		# mpoly = MultiPolygon(p1, p2)
		# polygon = MapPolygon(lat='50.2340', lon='28.3282', field1=1.0, field2=2.0, mpoly=mpoly, dataset=ds, remote_id=1)
		# polygon.save()
	
		self.request = HttpRequest()
		qdict = QueryDict('', mutable=True)
		qdict.update({'year': '2014'})
		qdict.update({'year': '2016'})
		qdict.update({'unit': 'km'})
		self.request.GET = qdict
		self.serializer = AnalyzeAreaNoValuesSerializer(context={'request': self.request})
	
	def test_can_get_areaAroundPoint(self):
		data = self.serializer.get_areaAroundPoint(self.mp)
		self.assertEqual(data['1.000000 km'], {})
		self.assertEqual(data['points'][0]['state'], 'NY')
		self.assertEqual(data['points'][0]['city'], 'NYC')