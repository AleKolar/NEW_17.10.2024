import os

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Max
from django.http import HttpResponse
from django.template import loader

from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Level, Coords, Images, PerevalAdded
from .serializers import UserSerializer, CoordsSerializer, LevelSerializer, ImagesSerializer, PerevalAddedSerializer




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CoordsViewSet(viewsets.ModelViewSet):
    queryset = Coords.objects.all()
    serializer_class = CoordsSerializer


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer


class ImagesViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer


class PerevalAddedViewSet(viewsets.ModelViewSet):
    serializer_class = PerevalAddedSerializer
    queryset = PerevalAdded.objects.all()

    def get_serializer_context(self):
        context = super(PerevalAddedViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def retrieve(self, request, pk=None):
        if pk:
            try:
                pereval = PerevalAdded.objects.get(pk=pk)
                serializer = PerevalAddedSerializer(pereval, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PerevalAdded.DoesNotExist:
                return Response({"message": "PerevalAdded not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "ID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request):
    #     serializer = PerevalAddedSerializer(data=request.data, context={'request': request})
    #     if serializer.is_valid():
    #         instance = serializer.save()
    #         response_data = {
    #             "status": 200,
    #             "message": "Объект успешно создан",
    #             "id": instance.id
    #         }
    #         return Response(response_data, status=status.HTTP_200_OK)
    #     else:
    #         response_data = {
    #             "status": 400,
    #             "message": "Bad Request (при нехватке полей)",
    #             "id": None
    #         }
    #         return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        user_data = request.data.get('user')
        user_email = user_data.get('email')

        try:
            user_instance = User.objects.get(email=user_email)
        except User.DoesNotExist:
            user_instance = User.objects.create(**user_data)
        except MultipleObjectsReturned:
            user_instance = User.objects.filter(email=user_email).first()

        coords_data = request.data.get('coords')
        level_data = request.data.get('level')
        images_data = request.data.get('images')

        coords_instance = Coords.objects.create(**coords_data)
        level_instance = Level.objects.create(**level_data)

        pereval_data = {
            "user": user_instance,
            "coords": coords_instance,
            "level": level_instance,
        }

        pereval = PerevalAdded.objects.create(**pereval_data)

        images_instances = [Images.objects.create(pereval=pereval, **image_data) for image_data in images_data]

        pereval.images.set(images_instances)

        response_data = {
            "status": 200,
            "message": "Объект успешно создан",
            "id": pereval.id
        }
        return Response(response_data, status=status.HTTP_200_OK)


    def update(self, request, pk=None, partial=False):
        pereval = PerevalAdded.objects.get(pk=pk)
        serializer = PerevalAddedSerializer(pereval, data=request.data, partial=partial, context={'request': request})

        if serializer.is_valid():
            user_data = request.data.get('user')
            if user_data is not None:
                instance_user = pereval.user
                validating_user_fields = [
                    instance_user.email != user_data.get('email'),
                    instance_user.phone != user_data.get('phone'),
                    instance_user.fam != user_data.get('fam'),
                    instance_user.name != user_data.get('name'),
                    instance_user.otc != user_data.get('otc'),
                ]
                if any(validating_user_fields):
                    return Response({"state": 0, "message": "Данные пользователя не могут быть изменены"},
                                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({"state": 1, "message": "Запись успешно отредактирована"}, status=status.HTTP_200_OK)

        return Response({"state": 0, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def submitDataByEmail(self, request, email=None):
        if email:
            perevaladded_items = PerevalAdded.objects.filter(user__email=email)
            serializer = PerevalAddedSerializer(perevaladded_items, many=True, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Введите email пользователя в URL"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def highest_pereval(self, request):
        max_height_obj = Coords.objects.order_by('-height').first()

        if max_height_obj is not None:
            max_height = max_height_obj.height
            coords_objs = Coords.objects.filter(height=max_height)
            serializer = CoordsSerializer(coords_objs, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No Coords objects found"}, status=status.HTTP_404_NOT_FOUND)

