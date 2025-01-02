# import pytest
# from ariadne import make_executable_schema
# # from ariadne.asgi import TestClient
# from chat.schema import type_defs, query, mutation, subscription

# # Create the executable schema
# schema = make_executable_schema(type_defs, [query, mutation, subscription])


# # @pytest.fixture
# # def gql_client():
# #     """Fixture to create a TestClient for the chat schema."""
# #     app = TestClient(schema)
# #     return app


# class TestChatSchema:

#     def test_query_chat_rooms(self, gql_client):
#         query = """
#         query {
#             chatRooms {
#                 id
#                 name
#                 createdAt
#             }
#         }
#         """
#         response = gql_client.query(query)
#         assert response.status_code == 200
#         assert "errors" not in response.json()

#     def test_query_messages(self, gql_client):
#         query = """
#         query($roomId: ID!) {
#             messages(roomId: $roomId) {
#                 id
#                 content
#                 timestamp
#                 user {
#                     id
#                     username
#                 }
#             }
#         }
#         """
#         variables = {"roomId": 1}
#         response = gql_client.query(query, variables=variables)
#         assert response.status_code == 200
#         assert "errors" not in response.json()

#     def test_create_chat_room_mutation(self, gql_client):
#         mutation = """
#         mutation($name: String!) {
#             createChatRoom(name: $name) {
#                 id
#                 name
#                 createdAt
#             }
#         }
#         """
#         variables = {"name": "Test Room"}
#         response = gql_client.query(mutation, variables=variables)
#         assert response.status_code == 200
#         assert "errors" not in response.json()

#     def test_create_message_mutation(self, gql_client):
#         mutation = """
#         mutation($roomId: ID!, $content: String!) {
#             createMessage(roomId: $roomId, content: $content) {
#                 id
#                 content
#                 timestamp
#                 user {
#                     id
#                     username
#                 }
#             }
#         }
#         """
#         variables = {"roomId": 1, "content": "Hello, world!"}
#         response = gql_client.query(mutation, variables=variables)
#         assert response.status_code == 200
#         assert "errors" not in response.json()

#     def test_subscription_message_added(self, gql_client):
#         subscription = """
#         subscription($roomId: ID!) {
#             messageAdded(roomId: $roomId) {
#                 id
#                 content
#                 timestamp
#                 user {
#                     id
#                     username
#                 }
#             }
#         }
#         """
#         variables = {"roomId": 1}
#         response = gql_client.subscribe(subscription, variables=variables)
#         assert response.status_code == 200
#         assert "errors" not in response.json()