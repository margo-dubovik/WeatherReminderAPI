import json

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import RegistrationSerializer
from .models import CustomUser


class RegistrationView(APIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    @extend_schema(description='### Registration: provide your email and create a password, repeat  your password in '
                               '"password2" parameter',
                   tags=['auth'], )
    def post(self, request):
        request_body = json.loads(request.body)
        serializer = RegistrationSerializer(data=request_body)
        if serializer.is_valid():
            account = serializer.save()
            account.is_active = True
            account.save()
            return Response({'res': 'Registered successfully',
                             'user info': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class DeleteAccount(APIView):
    permission_classes = (IsAuthenticated, )

    @extend_schema(description='### Delete your account',
                   tags=['auth'], )
    def delete(self, request):
        user = request.user
        user.delete()

        return Response({"result": "user deleted"}, status=status.HTTP_200_OK)
