from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, ConfirmEmailSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ConfirmEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        serializer = ConfirmEmailSerializer(data={'uid': uidb64, 'token': token})
        if serializer.is_valid():
            return Response({'detail': 'Email подтверждён'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
