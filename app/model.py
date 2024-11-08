from pydantic import BaseModel, Field
from typing import List

class SurveyResult(BaseModel):
    question_number: int = Field(..., ge=1, le=10)  # Each question_number must be between 1 and 10
    question_value: int = Field(..., ge=1, le=7)    # Each question_value must be between 1 and 7


class Survey(BaseModel):
    user_id: str = Field(..., min_length=5, pattern=r"^\w+$")  # Use `pattern` instead of `regex`
    survey_results: List[SurveyResult] = Field(..., min_length=10, max_length=10)

    def __init__(self, **data):
        super().__init__(**data)

        # Manually perform validation after model initialization

        # Validate survey_results length
        if len(self.survey_results) != 10:
            raise ValueError("survey_results must contain exactly 10 items.")
        
        # Ensure all question numbers from 1 to 10 are present exactly once
        question_numbers = {result.question_number for result in self.survey_results}
        if question_numbers != set(range(1, 11)):
            raise ValueError("Each question_number from 1 to 10 must appear exactly once.")
