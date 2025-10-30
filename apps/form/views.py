from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg
from .models import Process, ProcessForm, Form, ResponseSession
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
            process = Process.objects.get(pk=pk, creator=request.user)
        except Process.DoesNotExist:
            return Response({'error': 'No Process matches the given query.'}, status=404)

        process.delete()
        return Response({'message': 'Process and its form mappings deleted successfully.'}, status=200)


class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        processes = Process.objects.filter(creator=user)
        forms = Form.objects.filter(creator=user)
        submissions = ResponseSession.objects.filter(responder=user)

        total_processes = processes.count()
        total_forms = forms.count()
        total_submissions = submissions.count()

        
        public_processes = processes.filter(is_public=True).count()
        private_processes = total_processes - public_processes

        
        avg_forms_per_process = (
            ProcessForm.objects.filter(process__creator=user)
            .values('process')
            .annotate(form_count=Count('form'))
            .aggregate(average=Avg('form_count'))['average'] or 0
        )

        
        most_used_form_data = (
            ProcessForm.objects
            .filter(process__creator=user)
            .values('form__title')
            .annotate(count=Count('process'))
            .order_by('-count')
            .first()
        )
        most_used_form = most_used_form_data['form__title'] if most_used_form_data else None

        data = {
            "overview": {
                "total_processes": total_processes,
                "total_forms": total_forms,
                "total_submissions": total_submissions,
            },
            "visibility": {
                "public_processes": public_processes,
                "private_processes": private_processes,
            },
            "statistics": {
                "avg_forms_per_process": round(avg_forms_per_process, 2),
                "most_used_form": most_used_form,
            },
        }

        return Response(data, status=status.HTTP_200_OK)
