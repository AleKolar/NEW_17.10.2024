from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, Coords, Level, Images, PerevalAdded
from .serializers import PerevalAddedSerializer


class ModelsTestCase(TestCase):

    def test_user_creation(self):
        user = User.objects.create(email='test@example.com', fam='Doe', name='John', otc='Smith', phone='123456789')
        self.assertEqual(user.email, 'test@example.com')

    def test_coords_creation(self):
        coords = Coords.objects.create(latitude='40.7128', longitude='74.0060', height=100)
        self.assertEqual(coords.height, 100)

    def test_level_creation(self):
        level = Level.objects.create(winter='cold', summer='hot', autumn='cool', spring='warm')
        self.assertEqual(level.spring, 'warm')

    def test_perevaladded_creation(self):
        user = User.objects.create(email='test@example.com', fam='Doe', name='John', otc='Smith', phone='123456789')
        coords = Coords.objects.create(latitude='40.7128', longitude='74.0060', height=100)
        level = Level.objects.create(winter='cold', summer='hot', autumn='cool', spring='warm')
        pereval = PerevalAdded.objects.create(beauty_title='Beautiful', title='Title', other_titles='Others',
                                              connect='Connection', user=user, coords=coords, level=level, status='new')
        self.assertEqual(pereval.status, 'new')

    def test_images_creation(self):
        user = User.objects.create(email='test@example.com', fam='Doe', name='John', otc='Smith', phone='123456789')
        coords = Coords.objects.create(latitude='40.7128', longitude='74.0060', height=100)
        level = Level.objects.create(winter='cold', summer='hot', autumn='cool', spring='warm')
        pereval = PerevalAdded.objects.create(beauty_title='Beautiful', title='Title', other_titles='Others',
                                              connect='Connection', user=user, coords=coords, level=level, status='new')
        image = Images.objects.create(data='ImageData', title='ImageTitle', pereval=pereval)
        self.assertEqual(image.title, 'ImageTitle')


class PerevalAddedSerializerTestCase(TestCase):
    def setUp(self):
        self.user_data = {'email': 'test@test.com', 'phone': '1234567890', 'fam': 'Doe', 'name': 'John', 'otc': 'Smith'}
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
        self.user = User.objects.create(email='test@test.com', phone='1234567890', fam='Doe', name='John', otc='Smith')
        self.coords = Coords.objects.create(latitude=40.7128, longitude=-74.0060)
        self.level = Level.objects.create(name='Beginner')
        self.image1 = Images.objects.create(data='image1.png', title='Image 1')
        self.image2 = Images.objects.create(data='image2.png', title='Image 2')
        self.pereval = PerevalAdded.objects.create(status='Active', url='example.com', beauty_title='Beautiful Title',
                                                   title='Title', other_titles='Other Titles', connect='Connected',
                                                   user=self.user, coords=self.coords, level=self.level)
        self.pereval.images.add(self.image1, self.image2)

    def test_get_perevaladded_by_id(self):
        url = reverse('perevaladded-detail', kwargs={'pk': self.pereval.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_perevaladded(self):
        data = {'status': 'Active', 'url': 'example.com', 'beauty_title': 'Beautiful Title', 'title': 'Title',
                'other_titles': 'Other Titles', 'connect': 'Connected', 'user': self.user.pk, 'coords': self.coords.pk,
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