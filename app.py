from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    # Here you can pass your astrological calculations as variables
    data = {
        'planet_positions': [
            {'planet': 'Sun', 'position': '15° Aries'},
            {'planet': 'Moon', 'position': '23° Taurus'},
            # Add more planets
        ]
    }
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(port=5000) 