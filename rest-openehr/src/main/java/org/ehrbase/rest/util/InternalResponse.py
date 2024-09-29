from typing import Generic, TypeVar
from fastapi import Response
from pydantic.generics import GenericModel


# from pydantic import BaseModel, GenericModel
# from typing import TypeVar, Generic

# T = TypeVar('T')

# class MyModel(GenericModel, Generic[T]):
#     data: T

# class MyModel(GenericModel, Generic[T]):
#     data: T

# # Example of using MyModel with different types
# int_model = MyModel[int](data=123)
# str_model = MyModel[str](data="Hello")

# print(int_model)
# print(str_model)




# Define a generic type T to handle different response data types
T = TypeVar('T')

# Generic class for handling internal responses with headers
class InternalResponse(GenericModel, Generic[T]):
    def __init__(self, response_data: T, headers: dict):
        """
        :param response_data: The data associated with the response.
        :param headers: HTTP headers for the response.
        """
        self.response_data: T = response_data
        self.headers: dict = headers

    def get_response_data(self) -> T:
        """
        :return: The response data of the internal response.
        """
        return self.response_data

    def set_response_data(self, response_data: T):
        """
        Set the response data of the internal response.
        :param response_data: The new response data.
        """
        self.response_data = response_data

    def get_headers(self) -> dict:
        """
        :return: The headers associated with the internal response.
        """
        return self.headers

    def set_headers(self, headers: dict):
        """
        Set the headers for the internal response.
        :param headers: The new headers.
        """
        self.headers = headers

    def to_fastapi_response(self) -> Response:
        """
        Convert the internal response to a FastAPI response.
        :return: A FastAPI Response object with data and headers.
        """
        return Response(
            content=self.response_data.json(), 
            headers=self.headers
        )
