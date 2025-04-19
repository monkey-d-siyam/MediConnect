from flask import Blueprint, render_template, request

general_bp = Blueprint('general', __name__, url_prefix='')

@general_bp.route('/')
@general_bp.route('/home',endpoint='home')
def home():
    return render_template('home.html')

@general_bp.route('/about')
def about():
    return render_template('about.html')

@general_bp.route('/health_tips')
def health_tips():
    articles = [
        {"title": "10 Tips for a Healthy Lifestyle", "content": "Eat healthy, exercise regularly, and sleep well."},
        {"title": "The Importance of Hydration", "content": "Drinking enough water is essential for your body."},
        {"title": "Managing Stress Effectively", "content": "Practice mindfulness and relaxation techniques."}
    ]
    videos = [
        {"title": "Yoga for Beginners", "url": "https://www.youtube.com/embed/v7AYKMP6rOE"},
        {"title": "Healthy Eating Habits", "url": "https://www.youtube.com/embed/dBnniua6-oM"}
    ]
    return render_template('health_tips.html', articles=articles, videos=videos)

@general_bp.route('/symptom_checker', methods=['GET', 'POST'])
def symptom_checker():
    suggestion = None
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '').lower()
        if "fever" in symptoms or "cough" in symptoms:
            suggestion = "You may have a viral infection. Please consult a doctor if symptoms persist."
        elif "chest pain" in symptoms or "shortness of breath" in symptoms:
            suggestion = "This could be a serious condition. Seek immediate medical attention."
        else:
            suggestion = "Your symptoms are not recognized. Please consult a doctor for a proper diagnosis."
    return render_template('symptom_checker.html', suggestion=suggestion)

@general_bp.route('/emergency_contacts')
def emergency_contacts():
    # Placeholder content
    return render_template('emergency_contacts.html')

@general_bp.route('/first_aid')
def first_aid():
    # Placeholder content
    return render_template('first_aid.html')

@general_bp.route('/forum', methods=['GET', 'POST'])
def forum():
    # Placeholder content
    return render_template('forum.html')
