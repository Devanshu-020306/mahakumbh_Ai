from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash

# --- AI Core Imports ---
from ai_core.itinerary_planner import generate_itinerary, find_alternative_event
from ai_core.navigation import get_route_suggestion
from ai_core.assistant import answer_question
from ai_core.safety_monitor import analyze_post
from ai_core.notification_engine import generate_notifications

app = Flask(__name__)
app.secret_key = 'hackathon-super-secret-key-12345'

USERS = { "devotee": "password123", "test": "test" }

# --- Login/Register/Logout Routes (No Change) ---
@app.route('/')
def home():
    if 'username' in session: return redirect(url_for('companion'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('companion'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS:
            flash('Username already exists.', 'error')
        elif not username or not password:
            flash('Username and password cannot be empty.', 'error')
        else:
            USERS[username] = password
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/companion')
def companion():
    if 'username' not in session:
        flash('You must be logged in.', 'error')
        return redirect(url_for('login'))
    return render_template('companion.html')

# --- API Endpoint (THIS IS WHERE THE FIX IS) ---
@app.route('/api/get_recommendations', methods=['POST'])
def get_recommendations():
    if 'username' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        data = request.json
        profile = {
            'age_group': data.get('age_group'),
            'interests': data.get('interests', []),
            'budget': data.get('budget')
        }
        
        itinerary = generate_itinerary(profile)
        community_post = data.get('community_post', '')
        safety_analysis = analyze_post(community_post) if community_post else {
            "status": "Normal", "message": "No community post submitted."
        }
        
        itinerary_update = None
        if safety_analysis.get('status') == 'ALERT' and safety_analysis.get('location'):
            unsafe_location = safety_analysis['location']
            original_events = list(itinerary['suggested_events']) 
            itinerary['suggested_events'] = [e for e in itinerary['suggested_events'] if e['location'] != unsafe_location]
            if len(itinerary['suggested_events']) < len(original_events):
                alternative = find_alternative_event(profile, [unsafe_location])
                if alternative:
                    itinerary['suggested_events'].append(alternative)
                    itinerary_update = {"unsafe_location": unsafe_location, "new_suggestion": alternative}
        
        # ===================================================
        # START OF THE FIX
        # ===================================================
        
        # --- FIX: Defensively get the first event location ---
        # This new block of code safely handles the case where the event list might be empty.
        if itinerary['suggested_events']:
            first_event_location = itinerary['suggested_events'][0]['location']
        else:
            first_event_location = "Mela Grounds" # Use a safe fallback if no events are left
        
        # ===================================================
        # END OF THE FIX
        # ===================================================

        navigation_suggestion = get_route_suggestion(first_event_location)
        user_question = data.get('question', '')
        assistant_response = answer_question(user_question) if user_question else "Ask me a question to get help."
        notifications = generate_notifications(profile, itinerary)
        
        response = {
            "itinerary": itinerary,
            "navigation": navigation_suggestion,
            "assistant": { "user_question": user_question, "answer": assistant_response },
            "safety_analysis": safety_analysis,
            "itinerary_update": itinerary_update,
            "notifications": notifications
        }
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc() # This will print the detailed error to your terminal for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
