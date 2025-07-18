from flask import Blueprint, request, render_template,current_app
from . import education
from google import genai
from extensions import cache  # Import the cache object from extensions
import requests
import random
import os
from googleapiclient.discovery import build


client = genai.Client(api_key="AIzaSyDVQ8oZIrmO_rPAc6FVTR8W1G9Edj3W6oc")

@education.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    if request.method == 'GET':
        return render_template('education/symptom_checker.html')

    # Handle POST request
    symptoms = request.form.get('symptoms', '')

    if not symptoms.strip():
        return render_template('education/symptom_checker.html', error='No symptoms provided.')

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
        'education/symptom_checker.html',
        suggestion=suggestion,
        detailed_explanation=detailed_explanation
    )

@education.route('/health-tips')
@cache.cached(timeout=3600)  # Use the globally initialized cache
def health_tips():
    try:
        # Access the YouTube API keys from the environment variable and select one randomly
        youtube_api_keys = os.getenv('YOUTUBE_API_KEYS').split(',')
        youtube_api_key = random.choice(youtube_api_keys)
        if not youtube_api_key:
            raise ValueError("YouTube API key is not configured.")
        
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        
        # Define search queries based on the provided topics
        search_queries = [
            "health awareness", "public health awareness", "preventive health care",
            "health education", "importance of health checkup", "healthy lifestyle tips",
            "early signs of illness", "World Health Day awareness", "Breast Cancer Awareness Month",
            "mental health awareness week", "covid-19 awareness video"
        ]
        
        # Fetch videos for each query and filter by medium length
        videos = []
        for query in search_queries:
            try:
                search_response = youtube.search().list(
                    part="snippet",
                    q=query,
                    maxResults=5,  # Reduce the number of results fetched
                    type="video",
                    videoDuration="medium",  # Filter for medium-length videos
                    relevanceLanguage="en"  # Ensure videos are in English
                ).execute()
            except Exception as e:
                if "quotaExceeded" in str(e):
                    current_app.logger.error("YouTube API quota exceeded.")
                    videos = [{"title": "Quota Exceeded", "url": ""}]
                    break
                else:
                    raise
            
            # Filter out news channels and limit to 4 videos
            for item in search_response.get('items', []):
                channel_title = item['snippet']['channelTitle'].lower()
                if "news" not in channel_title and len(videos) < 4:
                    videos.append({
                        "title": item['snippet']['title'],
                        "url": f"https://www.youtube.com/embed/{item['id']['videoId']}"
                    })
                if len(videos) == 4:
                    break

        # Fetch videos from trusted channels
        trusted_channels = {
            "Harvard Med": "UC6YGRv5zEveCvdKjvGGsCLA",
            "Mayo Clinic": "UCi7ZkzJM1oJBrIg10Lr24ug",
            "NHS England": "UC4Q4wZxRnm3S2lZcE7bCMAA",
            "CDC": "UCiDKcjK3F6llN7txVkOEZ2g",
            "WHO": "UC07-dOwgza1IguKA86jqxNA"
        }

        for name, channel_id in trusted_channels.items():
            try:
                response = requests.get(
                    f"https://www.googleapis.com/youtube/v3/search"
                    f"?part=snippet&channelId={channel_id}&maxResults=1&type=video&q=awareness&key={youtube_api_key}",
                    timeout=10
                )
                data = response.json()
                for item in data.get("items", []):
                    videos.append({
                        "title": item["snippet"]["title"],
                        "url": f"https://www.youtube.com/embed/{item['id']['videoId']}"
                    })
            except Exception as e:
                current_app.logger.error(f"Error fetching from {name}: {e}")

        if not videos:
            videos = [{"title": "No videos available", "url": ""}]

        # Fetch current disease information using the PubMed API
        articles = []
        try:
            # Define the PubMed API endpoint and parameters
            params = {
                "db": "pubmed",
                "term": "health OR disease OR awareness",  # Search terms
                "retmax": 5,  # Limit to 5 articles
                "retmode": "json",
                "api_key": current_app.config.get('PUBMED_API_KEY')  # Use the environment variable
            }

            # Make the request to the PubMed API
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                article_ids = search_data.get("esearchresult", {}).get("idlist", [])

                # Fetch article details using the PubMed ESummary API
                if article_ids:
                    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                    summary_params = {
                        "db": "pubmed",
                        "id": ",".join(article_ids),
                        "retmode": "json",
                        "api_key": current_app.config.get('PUBMED_API_KEY')
                    }
                    summary_response = requests.get(summary_url, params=summary_params, timeout=10)
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        articles = [
                            {
                                "title": item.get("title", "No title"),
                                "url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/",
                                "source": "PubMed"
                            }
                            for article_id, item in summary_data.get("result", {}).items()
                            if article_id != "uids"  # Exclude metadata
                        ]
            else:
                current_app.logger.error(f"Error fetching articles from PubMed: {response.status_code}")
                articles = [{"title": "Error", "url": "", "source": ""}]
        except Exception as e:
            current_app.logger.error(f"Exception fetching articles from PubMed: {e}")
            articles = [{"title": "Error fetching articles", "url": "", "source": ""}]

    except Exception as e:
        current_app.logger.error(f"Error fetching data: {e}")  # Log the error
        videos = [{"title": "Error", "url": ""}]
        articles = [{"title": "Error fetching articles", "url": "", "source": ""}]

    # Pass a flag to indicate this is the health-tips route
    return render_template('education/health_tips.html', videos=videos, articles=articles, health_tips_page=True)



