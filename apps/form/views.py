from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Process
from .serializers import ProcessSettingsSerializer


class ProcessSettingsUpdateView(generics.UpdateAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(creator=user)


class ProcessDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            process = Process.objects.get(pk=pk)
        except Process.DoesNotExist:
            return Response({'error': 'Process not found.'}, status=status.HTTP_404_NOT_FOUND)

        if process.creator != request.user:
            return Response({'error': 'You are not allowed to delete this process.'}, status=status.HTTP_403_FORBIDDEN)

        process.delete()

        return Response({'message': 'Process and its form mappings deleted successfully.'}, status=status.HTTP_200_OK)
