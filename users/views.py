from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegistrationSerializer, UserProfileSerializer


@extend_schema(tags=["Users"], summary="Регистрация пользователя")
class RegistrationAPIView(generics.CreateAPIView):
    """Зарегистрируйте пользователя, который впоследствии сможет аутентифицироваться с помощью электронной почты и пароля."""

    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)


@extend_schema(tags=["Users"], summary="Профиль текущего пользователя")
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """Разрешите пользователю просматривать или обновлять только свой идентификатор чата в Telegram."""

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
