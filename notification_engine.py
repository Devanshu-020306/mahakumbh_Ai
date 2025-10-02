# A simple rule-based engine to generate relevant notifications.

def generate_notifications(profile, itinerary):
    """
    Generates a list of personalized notifications based on user profile and itinerary.
    """
    notifications = []
    interests = profile.get('interests', [])
    suggested_events = itinerary.get('suggested_events', [])

    # Notification 1: Based on primary interest
    if 'spiritual' in interests:
        notifications.append({
            "emoji": "🔔",
            "title": "Spiritual Alert",
            "message": "The mesmerizing Ganga Aarti at Har Ki Pauri starts in the evening. Don't miss this divine experience!"
        })
    elif 'cultural' in interests:
        notifications.append({
            "emoji": "🎸",
            "title": "Cultural Vibe",
            "message": "A Music & Dance festival is happening tonight at Mela Grounds Stage. A perfect way to end your day!"
        })
    elif 'historical' in interests:
        notifications.append({
            "emoji": "🏛️",
            "title": "History Buff Alert",
            "message": "The Heritage Walk through the Old City Zone is highly recommended to explore ancient architecture."
        })
    
    # Notification 2: A practical tip based on a suggested event
    for event in suggested_events:
        if "Shahi Snan" in event['name']:
            notifications.append({
                "emoji": "⚠️",
                "title": "Crowd Warning",
                "message": "Your plan includes the Shahi Snan. It will be extremely crowded. Please keep your belongings safe and stay with your group."
            })
            break # Only add this once
    
    # Notification 3: General helpful tip
    notifications.append({
        "emoji": "🍲",
        "title": "Food Tip",
        "message": "Remember to visit a 'Bhandara' (community kitchen) near an ashram for a free, blessed meal (prasad)."
    })

    return notifications[:3] # Return a max of 3 notifications