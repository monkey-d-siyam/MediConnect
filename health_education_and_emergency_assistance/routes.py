from flask import Blueprint, request, render_template
from google import genai

education = Blueprint('education', __name__, template_folder='templates/education')

# Initialize Google Gemini client with API key
client = genai.Client(api_key="AIzaSyDVQ8oZIrmO_rPAc6FVTR8W1G9Edj3W6oc")

@education.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    if request.method == 'GET':
        return render_template('symptom_checker.html')

    # Handle POST request
    symptoms = request.form.get('symptoms', '')

    if not symptoms.strip():
        return render_template('symptom_checker.html', error='No symptoms provided.')

    # Call Google Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"The user reports the following symptoms: {symptoms}. What might they be facing?"
        )

        # Extract the response
        suggestion_text = response.text.strip()

        if not suggestion_text:
            suggestion_text = "No meaningful response received from the API. Please try again later."

        # Process the response into a structured format
        suggestion = [line.strip() for line in suggestion_text.split("\n") if line.strip()]
        detailed_explanation = (
            "The suggestions provided are based on the symptoms you entered. "
            "Please consult a healthcare professional for accurate diagnosis and treatment."
        )

    except Exception as e:
        # Log the error for debugging
        print("Error occurred:", str(e))
        if "503" in str(e):
            suggestion = ["The service is currently unavailable. Please try again later."]
        elif "invalid_api_key" in str(e):
            suggestion = ["The API key provided is invalid. Please contact support."]
        else:
            suggestion = [f"An error occurred while connecting to the API: {str(e)}"]
        detailed_explanation = None

    return render_template(
        'symptom_checker.html',
        suggestion=suggestion,
        detailed_explanation=detailed_explanation
    )