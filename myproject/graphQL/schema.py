import graphene
from graphQL.queries import Query
from graphQL.mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
