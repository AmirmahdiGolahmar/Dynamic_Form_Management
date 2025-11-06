import graphene
from form.models import Process, Form
from graphene_django import DjangoObjectType


class ProcessType(DjangoObjectType):
    class Meta:
        model = Process
        fields = ('id', 'name', 'description', 'creator', 'forms')


class FormType(DjangoObjectType):
    class Meta:
        model = Form
        fields = ('id', 'title', 'process')


class Query(graphene.ObjectType):
    all_processes_by_user_id = graphene.List(
        ProcessType, 
        user_id=graphene.Int(required=True)
    )
    all_forms = graphene.List(FormType)

    def resolve_all_processes_by_user_id(root, info, user_id):
        return Process.objects.filter(creator__id=user_id)

    def resolve_all_forms(root, info):
        return Form.objects.all()

class CreateProcess(graphene.Mutation):
    class Arguments:
            name = graphene.String(required=True)
            description = graphene.String()
            user_id = graphene.Int(required=True)

    process = graphene.Field(ProcessType)

    @classmethod
    def mutate(cls, root, info, name, description=None, user_id=None):
        process = Process.objects.create(
            name=name, description=description, creator_id=user_id
        )
        return CreateProcess(process=process)
    

class Mutation(graphene.ObjectType):
    create_process = CreateProcess.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
