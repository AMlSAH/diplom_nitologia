from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'user_type')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'buyer'),
            is_active=False
        )

        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        confirm_url = f"http://localhost:8000/api/v1/accounts/confirm-email/{uid}/{token}/"
        send_mail(
            'Подтверждение регистрации',
            f'Для подтверждения email перейдите по ссылке: {confirm_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

class ConfirmEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Неверная ссылка подтверждения')
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError('Токен недействителен или истёк')
        user.is_active = True
        user.save()
        return attrs
