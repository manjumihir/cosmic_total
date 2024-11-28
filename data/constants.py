# Constants and configuration data
PROFILE_PATH = "profiles.json"
EPHEMERIS_PATH = './ephemeris'
POSITIONSTACK_API_KEY = 'df58d69f3a320dd1da9f2e805bacf8c9'

# Nakshatra data
nakshatra_list = [
    {"name": "Ashwini", "start": 0.0, "lord": "Ketu"},
    {"name": "Bharani", "start": 13.3333, "lord": "Venus"},
    # ... rest of nakshatra list ...
]

dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

dasha_periods = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'] 