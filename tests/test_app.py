import unittest
from sanic import Sanic
from sanic_testing.testing import SanicTestClient
from sanic import response
from unittest.mock import patch
from statistics import mean
import json

# Assuming your app is in 'main.py' inside the app folder
from app.main import app  # Ensure you import the app correctly


class SurveyProcessorTests(unittest.TestCase):
    def setUp(self):
        """Set up test client and any required mock data"""
        self.app = app
        self.client = SanicTestClient(self.app)

        # Example of valid payload
        self.valid_payload = {
            "survey_results": [
                {"question_number": 1, "question_value": 6},
                {"question_number": 2, "question_value": 7},
                {"question_number": 3, "question_value": 8},
                {"question_number": 4, "question_value": 4},
                {"question_number": 5, "question_value": 5},
                {"question_number": 6, "question_value": 6},
                {"question_number": 7, "question_value": 4},
                {"question_number": 8, "question_value": 6},
                {"question_number": 9, "question_value": 5},
                {"question_number": 10, "question_value": 3}
            ]
        }

        # Example of an invalid payload
        self.invalid_payload = {
            "survey_results": [
                {"question_number": 1, "question_value": "string_instead_of_number"}
            ]
        }

    @patch("app.main.generate_description")
    async def test_process_survey_valid(self, mock_generate_description):
        """Test valid payload processing"""

        # Mock the generate_description method since it uses the Gemini API
        mock_generate_description.return_value = "Generated Description"

        # Call the endpoint with valid payload
        request_data = self.valid_payload
        response = await self.client.post("/process-survey", json=request_data)

        # Check the response status and content
        self.assertEqual(response.status, 200)
        data = response.json()
        self.assertIn("overall_analysis", data)
        self.assertIn("cat_dog", data)
        self.assertIn("fur_value", data)
        self.assertIn("tail_value", data)
        self.assertIn("description", data)
        self.assertIn("mean", data)
        self.assertIn("median", data)
        self.assertIn("std_dev", data)

        # Validate that the description was generated (mocked)
        mock_generate_description.assert_called_once_with(mean([q["question_value"] for q in request_data["survey_results"]]))

    @patch("app.main.generate_description")
    async def test_process_survey_invalid(self, mock_generate_description):
        """Test invalid payload (wrong data type)"""

        # Mock the generate_description method
        mock_generate_description.return_value = "Generated Description"

        # Call the endpoint with invalid payload
        request_data = self.invalid_payload
        response = await self.client.post("/process-survey", json=request_data)

        # Check for error response
        self.assertEqual(response.status, 400)
        data = response.json()
        self.assertIn("error", data)

    @patch("app.main.generate_description")
    async def test_process_survey_edge_case_min_value(self, mock_generate_description):
        """Test edge case: minimum possible values for survey results"""

        # Mock the generate_description method
        mock_generate_description.return_value = "Generated Description"

        # Edge case: Minimum possible values (e.g., all values = 1)
        edge_case_payload = {
            "survey_results": [
                {"question_number": i, "question_value": 1} for i in range(1, 11)
            ]
        }

        # Call the endpoint with edge case payload
        response = await self.client.post("/process-survey", json=edge_case_payload)

        # Check if the response status is 200
        self.assertEqual(response.status, 200)
        data = response.json()

        # Ensure the results reflect the minimum values
        self.assertEqual(data["fur_value"], "short")  # Based on the mean being low
        self.assertEqual(data["tail_value"], "short")  # Based on low values for the tail question

    @patch("app.main.generate_description")
    async def test_process_survey_edge_case_max_value(self, mock_generate_description):
        """Test edge case: maximum possible values for survey results"""

        # Mock the generate_description method
        mock_generate_description.return_value = "Generated Description"

        # Edge case: Maximum possible values (e.g., all values = 7)
        edge_case_payload = {
            "survey_results": [
                {"question_number": i, "question_value": 7} for i in range(1, 11)
            ]
        }

        # Call the endpoint with edge case payload
        response = await self.client.post("/process-survey", json=edge_case_payload)

        # Check if the response status is 200
        self.assertEqual(response.status, 200)
        data = response.json()

        # Ensure the results reflect the maximum values
        self.assertEqual(data["fur_value"], "long")  # Based on the mean being high
        self.assertEqual(data["tail_value"], "long")  # Based on high values for the tail question


if __name__ == "__main__":
    unittest.main()
