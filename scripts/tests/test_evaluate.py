from datetime import timedelta

import requests

from scripts.evaluate import send_question_to_target


def test_send_question_to_target_valid():
    # Test case 1: Valid response
    response = {
        "choices": [
            {
                "message": {"content": "This is the answer"},
                "context": {"data_points": {"text": ["Context 1", "Context 2"]}},
            }
        ]
    }
    requests.post = lambda url, headers, json: MockResponse(response)
    result = send_question_to_target("Question 1", "http://example.com")
    assert result["question"] == "Question 1"
    assert result["answer"] == "This is the answer"
    assert result["context"] == "Context 1\n\nContext 2"
    assert result["latency"] == 1


def test_send_question_to_target_missing_error_store():
    # Test case 2: Missing 'choices' key in response
    response = {}
    requests.post = lambda url, headers, json: MockResponse(response)
    result = send_question_to_target("Question", "http://example.com")
    assert result["question"] == "Question"
    assert result["answer"] == (
        "Response does not adhere to the expected schema. "
        "Either adjust the app response or adjust send_question_to_target() "
        "in evaluate.py to match the actual schema.\n"
        "Response: {}"
    )
    assert result["context"] == (
        "Response does not adhere to the expected schema. "
        "Either adjust the app response or adjust send_question_to_target() "
        "in evaluate.py to match the actual schema.\n"
        "Response: {}"
    )


def test_send_question_to_target_missing_choices():
    # Test case 2: Missing 'choices' key in response
    response = {}
    requests.post = lambda url, headers, json: MockResponse(response)
    try:
        send_question_to_target("Question", "http://example.com", raise_error=True)
    except Exception as e:
        assert str(e) == (
            "Response does not adhere to the expected schema. "
            "Either adjust the app response or adjust send_question_to_target() "
            "in evaluate.py to match the actual schema.\n"
            "Response: {}"
        )


def test_send_question_to_target_missing_content():
    # Test case 4: Missing 'content' key in response['choices'][0]['message']
    response = {"choices": [{"message": {}, "context": {"data_points": {"text": ["Context 1", "Context 2"]}}}]}
    requests.post = lambda url, headers, json: MockResponse(response)
    try:
        send_question_to_target("Question", "http://example.com", raise_error=True)
    except Exception as e:
        assert str(e) == (
            "Response does not adhere to the expected schema. "
            "Either adjust the app response or adjust send_question_to_target() "
            "in evaluate.py to match the actual schema.\n"
            "Response: {'choices': [{'message': {}, 'context': {'data_points': {'text': ['Context 1', 'Context 2']}}}]}"
        )


def test_send_question_to_target_missing_context():
    # Test case 5: Missing 'context' key in response['choices'][0]
    response = {"choices": [{"message": {"content": "This is the answer"}}]}
    requests.post = lambda url, headers, json: MockResponse(response)
    try:
        send_question_to_target("Question", "http://example.com", raise_error=True)
    except Exception as e:
        assert str(e) == (
            "Response does not adhere to the expected schema. "
            "Either adjust the app response or adjust send_question_to_target() "
            "in evaluate.py to match the actual schema.\n"
            "Response: {'choices': [{'message': {'content': 'This is the answer'}}]}"
        )


class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data
        self.elapsed = timedelta(seconds=1)

    def json(self):
        return self.json_data
