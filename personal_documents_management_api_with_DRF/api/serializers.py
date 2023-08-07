from rest_framework import serializers
from .models import CustomUser, Documents, DocAcess


#================================================================ User Registration Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


#============================================ Documents Model Serializer
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = '__all__'

#==================================================== Document Access Serializer
class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocAcess
        fields = '__all__'