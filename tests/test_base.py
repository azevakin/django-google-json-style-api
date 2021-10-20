from django_google_json_style_api import base


class TestSnakeToCamel:
    """This test covers _snake_to_camel method"""

    def test_snake_string(self):
        assert base._snake_to_camel("snake_case") == "snakeCase"

    def test_empty_string(self):
        assert base._snake_to_camel("") == ""
