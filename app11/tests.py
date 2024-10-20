from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, Coords, Level, Images, PerevalAdded
from .serializers import PerevalAddedSerializer


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@example.com', fam='Doe', name='John', otc='Smith',
                                        phone='123456789')
        self.coords = Coords.objects.create(latitude='40.7128', longitude='74.0060', height=100)
        self.level = Level.objects.create(winter='cold', summer='hot', autumn='cool', spring='warm')
        self.pereval = PerevalAdded.objects.create(beauty_title='Beautiful', title='Title', other_titles='Others',
                                                   connect='Connection', user=self.user, coords=self.coords,
                                                   level=self.level, status='new')
        self.image = Images.objects.create(data='ImageData', title='ImageTitle', pereval=self.pereval)

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')

    def test_coords_creation(self):
        self.assertEqual(self.coords.height, 100)

    def test_level_creation(self):
        self.assertEqual(self.level.spring, 'warm')

    def test_perevaladded_creation(self):
        self.assertEqual(self.pereval.status, 'new')

    def test_images_creation(self):
        self.assertEqual(self.image.title, 'ImageTitle')


class PerevalAddedSerializerTestCase(TestCase):

    def setUp(self):
        self.user_data = {'email': 'test@test.com', 'phone': '1234567890', 'fam': 'Doe', 'name': 'John',
                          'otc': 'Smith'}
        self.coords_data = {'latitude': 40.7128, 'longitude': -74.0060}
        self.level_data = {'name': 'Beginner'}
        self.images_data = [{'data': 'image1.png', 'title': 'Image 1'}, {'data': 'image2.png', 'title': 'Image 2'}]
        self.pereval_data = {'status': 'Active', 'url': 'example.com', 'beauty_title': 'Beautiful Title',
                             'title': 'Title', 'other_titles': 'Other Titles', 'connect': 'Connected'}

    def test_pereval_serializer_create(self):
        serializer = PerevalAddedSerializer(
            data={**self.pereval_data, 'user': self.user_data, 'coords': self.coords_data, 'level': self.level_data,
                  'images': self.images_data})
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(PerevalAdded.objects.filter(pk=instance.pk).exists(), True)

    def test_pereval_serializer_update(self):
        instance = PerevalAdded.objects.create(**self.pereval_data)
        serializer = PerevalAddedSerializer(instance, data={**self.pereval_data, 'user': self.user_data,
                                                            'coords': self.coords_data, 'level': self.level_data,
                                                            'images': self.images_data}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(updated_instance.pk, instance.pk)


class PerevalAddedViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@test.com', phone='1234567890', fam='Doe', name='John',
                                        otc='Smith')
        self.coords = Coords.objects.create(latitude=40.7128, longitude=-74.0060)
        self.level = Level.objects.create(name='Beginner')
        self.image1 = Images.objects.create(data='image1.png', title='Image 1')
        self.image2 = Images.objects.create(data='image2.png', title='Image 2')
        self.pereval = PerevalAdded.objects.create(status='Active', url='example.com',
                                                   beauty_title='Beautiful Title',
                                                   title='Title', other_titles='Other Titles', connect='Connected',
                                                   user=self.user, coords=self.coords, level=self.level)
        self.pereval.images.add(self.image1, self.image2)

    def test_get_perevaladded_by_id(self):
        url = reverse('perevaladded-detail', kwargs={'pk': self.pereval.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_perevaladded(self):
        data = {'status': 'Active', 'url': 'example.com', 'beauty_title': 'Beautiful Title', 'title': 'Title',
                'other_titles': 'Other Titles', 'connect': 'Connected', 'user': self.user.pk,
                'coords': self.coords.pk,
                'level': self.level.pk, 'images': [self.image1.pk, self.image2.pk]}
        url = reverse('perevaladded-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_perevaladded(self):
        data = {'status': 'Inactive', 'title': 'New Title'}
        url = reverse('perevaladded-detail', kwargs={'pk': self.pereval.pk})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submit_data_by_email(self):
        url = reverse('perevaladded-submitDataByEmail', kwargs={'email': self.user.email})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_highest_pereval(self):
        url = reverse('highest_pereval')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_highest_pereval_no_coords(self):
        url = reverse('highest_pereval')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"message": "No Coords objects found"})


class TestAPIEndpoints(APITestCase):

    def setUp(self):
        Coords.objects.create(latitude=40.7128, longitude=-74.0060, height=100)

    def test_swagger_endpoint(self):
        url = reverse('schema-swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_endpoint(self):
        url = reverse('schema-redoc')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_highest_pereval_endpoint(self):
        url = reverse('highest_pereval')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_endpoint(self):
        url = reverse('create')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DatabaseConnectionTestCase(TestCase):

    def test_database_connection(self):
        from django.db import connection
        self.assertIsNotNone(connection)

    def test_write_to_database(self):
        user = User.objects.create(email='test@example.com', fam='Doe', name='John', otc='Smith', phone='123456789')
        self.assertIsNotNone(user.id)

    def test_read_from_database(self):
        user = User.objects.create(email='test@example.com', fam='Doe', name='John', otc='Smith', phone='123456789')
        retrieved_user = User.objects.get(id=user.id)
        self.assertEqual(user.email, retrieved_user.email)
