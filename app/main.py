import logging
from sanic import Sanic, response
from sanic.request import Request
from motor.motor_asyncio import AsyncIOMotorClient
from app.model import Survey
from statistics import mean, median, stdev
import openai
import os
import google.generativeai as genai

app = Sanic("SurveyProcessor")

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Adjust logging level as needed
logger = logging.getLogger(__name__)

# MongoDB setup
mongo_client = AsyncIOMotorClient("mongodb+srv://premkumarsridharks:Premkumar.2000@cluster0.8psxq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["survey_db"]
collection = db["surveys"]

# Set up OpenAI API key from the environment
genai.configure(api_key="AIzaSyADwknCK9wA-x-pHRAJsvLrMw0i-sFUpvo")

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

async def generate_description(mean_value: float) -> str:
    """Generate a description based on the mean value by selecting an appropriate prompt file."""
    try:
        # Select prompt file based on the mean value
        file_name = "data/the_value_of_short_hair.txt" if mean_value > 4 else "data/the_value_of_long_hair.txt"

        # Read the prompt content from the selected file
        with open(file_name, 'r') as file:
            prompt_content = file.read()

        # Read the system prompt
        with open("data/system_prompt.txt", 'r') as file:
            system_prompt = file.read()

        # Make an asynchronous request to Gemini API
        response = model.generate_content(
            f"{system_prompt}\n\n{prompt_content}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        # Extract and return the generated description
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"Error generating description with Gemini: {str(e)}")
        raise Exception(f"Error generating description with Gemini: {str(e)}")

async def process_survey_data(survey_data):
    survey_results = survey_data["survey_results"]

    overall_analysis = (
        "unsure" if any(q["question_value"] == 7 for q in survey_results if q["question_number"] == 1) and
        any(q["question_value"] < 3 for q in survey_results if q["question_number"] == 4) else "certain"
    )
    cat_dog = (
        "cats" if any(q["question_value"] > 5 for q in survey_results if q["question_number"] == 10) and
        any(q["question_value"] <= 5 for q in survey_results if q["question_number"] == 9) else "dogs"
    )
    fur_value = "long" if mean([q["question_value"] for q in survey_results]) > 5 else "short"
    tail_value = "long" if any(q["question_value"] > 4 for q in survey_results if q["question_number"] == 7) else "short"

    # Generate description based on mean value
    description = await generate_description(mean([q["question_value"] for q in survey_results]))

    processed_data = {
        "overall_analysis": overall_analysis,
        "cat_dog": cat_dog,
        "fur_value": fur_value,
        "tail_value": tail_value,
        "description": description
    }

    return processed_data

async def calculate_statistics(survey_results):
    values = [result["question_value"] for result in survey_results]
    statistics = {
        "mean": mean(values),
        "median": median(values),
        "std_dev": stdev(values) if len(values) > 1 else 0
    }
    return statistics

@app.post("/process-survey")
async def process_survey(request: Request):
    try:
        # Parse and validate request data with Pydantic model
        logger.info("Received survey data for processing.")
        survey_data = Survey(**request.json)
        validated_data = survey_data.dict()
        logger.info("Survey data validated successfully.")
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return response.json({"error": f"Invalid data: {str(e)}"}, status=400)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return response.json({"error": "An unexpected error occurred."}, status=500)

    # Process survey data (Step 1)
    try:
        processed_data = await process_survey_data(validated_data)
        logger.info("Survey data processed successfully.")
    except Exception as e:
        logger.error(f"Error processing survey data: {str(e)}")
        return response.json({"error": f"Error processing survey data: {str(e)}"}, status=500)

    # Insert the initial data into the database
    try:
        insert_result = await collection.insert_one({**validated_data, **processed_data})
        inserted_id = insert_result.inserted_id
        logger.info(f"Survey data inserted with ID: {inserted_id}")
    except Exception as e:
        logger.error(f"Database insert error: {str(e)}")
        return response.json({"error": "Database insertion failed."}, status=500)

    # Calculate statistics (Step 2)
    try:
        statistics = await calculate_statistics(validated_data["survey_results"])
        logger.info("Statistics calculated successfully.")
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        return response.json({"error": f"Error calculating statistics: {str(e)}"}, status=500)

    # Update the document with statistics
    try:
        await collection.update_one(
            {"_id": inserted_id},
            {"$set": statistics}
        )
        logger.info("Survey statistics updated in the database.")
    except Exception as e:
        logger.error(f"Database update error: {str(e)}")
        return response.json({"error": "Database update failed."}, status=500)

    # Return the initial processed data and statistics combined
    logger.info("Returning processed data and statistics.")
    return response.json({**processed_data, **statistics}, status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
