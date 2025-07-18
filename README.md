# MediConnect

MediConnect is a web-based healthcare platform built with Flask. It connects patients, doctors, and pharmacies, providing features such as appointment booking, medicine ordering, pharmacy management, health education, and an AI-powered symptom checker.

---

## Features

- **User Authentication:** Register and login as a patient, doctor, or pharmacy.
- **Doctor & Patient Profiles:** Manage and update your medical or professional information.
- **Appointment Booking:** Patients can book appointments with doctors; doctors can manage their schedules.
- **Pharmacy Management:** Pharmacies can manage inventory and approve/cancel medicine orders.
- **Medicine Ordering:** Patients can order medicines and track order status.
- **Health Education:** Access health tips, articles, and an AI-powered symptom checker.
- **Forum & Consultation:** Community forum and video consultation features.
- **Notifications:** Email notifications for appointments and order updates.
- **Real-time Features:** SocketIO for real-time updates (e.g., chat, notifications).

---

## Project Structure

```
MediConnect-4/
│
├── core/
│   ├── routes.py
│   ├── forms.py
│   └── templates/core/
│
├── appointment/
├── consultation/
├── education/
│   └── templates/education/symptom_checker.html
├── forum/
├── pharmacy/
├── hospitals/
├── doctors/
├── extensions.py
├── run.py
└── ...
```

---

## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd MediConnect-4
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure environment variables:**
    - Create a `.env` file in the root directory with your secrets:
      ```
      SECRET_KEY=your_secret_key
      MAIL_USERNAME=your_email@example.com
      MAIL_PASSWORD=your_email_password
      MAIL_DEFAULT_SENDER=your_email@example.com
      ```

4. **Set up the MySQL database:**
    - Create a database named `mediconnect_db`.
    - Import the provided SQL schema (if available) or create tables as required by the models.

5. **Run the application:**
    ```bash
    python run.py
    ```
    The app will be available at [http://localhost:5000](http://localhost:5000).

---

## Symptom Checker

- The symptom checker is available under the Health Education section.
- Users enter symptoms, and the system provides AI-powered suggestions.
- The backend logic for the symptom checker can be found in `education/routes.py`.
- If an external API is used, it will be called from the symptom checker route.

---

## Customization

- Update `extensions.py` to configure database, mail, cache, and SocketIO.
- Modify templates in `core/templates/` and `education/templates/` for UI changes.
- Add new features by creating blueprints and registering them in `run.py`.

---

## License

This project is for educational purposes. Please check individual file headers for additional licensing information.

---

## Credits

- Built with [Flask](https://flask.palletsprojects.com/)
- Uses [Flask-MySQLdb](https://github.com/admiralobvious/flask-mysqldb), [Flask-Mail](https://pythonhosted.org/Flask-Mail/), [Flask-Caching](https://flask-caching.readthedocs.io/), [Flask-SocketIO](https://flask-socketio.readthedocs.io/), and more.

---

## Contact

For questions or support, please open an issue or contact
