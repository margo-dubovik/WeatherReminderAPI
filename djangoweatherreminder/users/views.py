import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import RegistrationSerializer
from .models import CustomUser


class RegistrationView(APIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

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
