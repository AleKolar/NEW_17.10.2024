from rest_framework import serializers
from .models import User, Coords, Level, Images, PerevalAdded

from drf_writable_nested.serializers import WritableNestedModelSerializer


class UserSerializer(WritableNestedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CoordsSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Coords
        fields = '__all__'


class LevelSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class ImagesSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Images
        fields = ['data', 'title']


class PerevalAddedSerializer(WritableNestedModelSerializer):
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = ImagesSerializer(many=True)

    class Meta:
        model = PerevalAdded
        fields = ['pk', 'status', 'url', 'beauty_title', 'title', 'other_titles', 'connect', 'add_time', 'user',
                  'coords', 'level', 'images']



        def create(self, validated_data):
            user_data = validated_data.pop('user')
            coords_data = validated_data.pop('coords')
            level_data = validated_data.pop('level')
            images_data = validated_data.pop('images')

            user_instance, created = User.objects.get_or_create(**user_data)
            coords_instance = Coords.objects.create(**coords_data)
            level_instance = Level.objects.create(**level_data)
            pereval = PerevalAdded.objects.create(**validated_data, user=user_instance, coords=coords_instance,
                                                  level=level_instance)

            images_instances = [Images.objects.create(pereval=pereval, **image_data) for image_data in images_data]

            pereval.images.set(images_instances)

            return pereval

        def update(self, instance, validated_data):
            self.update_nested(UserSerializer, instance.user, validated_data.pop('user'))
            self.update_nested(CoordsSerializer, instance.coords, validated_data.pop('coords'))
            self.update_nested(LevelSerializer, instance.level, validated_data.pop('level'))
            self.update_nested(ImagesSerializer, instance.images, validated_data.pop('images'), many=True)

            for field in ['beauty_title', 'title', 'other_titles', 'connect', 'add_time', 'status']:
                setattr(instance, field, validated_data.get(field, getattr(instance, field)))

            instance.save()
            return instance

        # Переопределяем валидацию для доп. проверки на неизменение данных пользователя
        def validate(self, data):
            if self.instance is not None:
                instance_user = self.instance.user
                user_data = data.get('user')
                validating_user_fields = [
                    instance_user.email != user_data['email'],
                    instance_user.phone != user_data['phone'],
                    instance_user.fam != user_data['fam'],
                    instance_user.name != user_data['name'],
                    instance_user.otc != user_data['otc'],
                ]
                if user_data is not None and any(validating_user_fields):
                    raise serializers.ValidationError('Данные пользователя не могут быть изменены')
            return data