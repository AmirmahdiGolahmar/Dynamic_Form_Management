from rest_framework import generics, permissions
from .models import Process
from .serializers import ProcessSettingsSerializer

class ProcessSettingsUpdateView(generics.UpdateAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        
        user = self.request.user
        return Process.objects.filter(creator=user)
