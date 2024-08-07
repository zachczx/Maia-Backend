from rest_framework.permissions import BasePermission
from rest_framework.request import Request

class IsSuperUser(BasePermission):
    
    def has_permission(self, request: Request) -> bool:
        return request.user and request.user.is_superuser
