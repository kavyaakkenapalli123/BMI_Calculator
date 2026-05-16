from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)


# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect('bmi.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT,
            date TEXT
        )
    ''')

    conn.commit()

    conn.close()


init_db()


# ================= BMI FUNCTIONS =================

def calculate_bmi(weight, height):

    return round(weight / (height ** 2), 2)


def get_category(bmi):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal Weight"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obese"


def get_suggestion(category):

    suggestions = {
        "Underweight": "Increase healthy nutritional intake.",
        "Normal Weight": "Maintain your healthy lifestyle.",
        "Overweight": "Exercise regularly and maintain a balanced diet.",
        "Obese": "Consult a healthcare professional."
    }

    return suggestions.get(category)


# ================= HOME PAGE =================

@app.route('/', methods=['GET', 'POST'])

def index():

    bmi = None
    category = None
    suggestion = None
    error = None

    if request.method == 'POST':

        try:

            name = request.form['name']

            weight = float(request.form['weight'])

            height = float(request.form['height'])

            # Validation

            if not name:

                error = "Please enter your name"

            elif weight <= 0 or height <= 0:

                error = "Weight and height must be positive"

            else:

                bmi = calculate_bmi(weight, height)

                category = get_category(bmi)

                suggestion = get_suggestion(category)

                # Store Data

                conn = sqlite3.connect('bmi.db')

                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO bmi_records
                    (name, weight, height, bmi, category, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (

                    name,
                    weight,
                    height,
                    bmi,
                    category,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                ))

                conn.commit()

                conn.close()

        except ValueError:

            error = "Please enter valid numeric values"

    return render_template(

        'index.html',

        bmi=bmi,

        category=category,

        suggestion=suggestion,

        error=error
    )


# ================= HISTORY PAGE =================

@app.route('/history')

def history():

    conn = sqlite3.connect('bmi.db')

    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, weight, height, bmi, category, date
        FROM bmi_records
        ORDER BY id DESC
    ''')

    records = cursor.fetchall()

    conn.close()

    return render_template(

        'history.html',

        records=records
    )


# ================= GRAPH =================

@app.route('/graph')

def graph():

    conn = sqlite3.connect('bmi.db')

    cursor = conn.cursor()

    cursor.execute('SELECT name, bmi FROM bmi_records')

    data = cursor.fetchall()

    conn.close()

    if data:

        names = [row[0] for row in data]

        bmi_values = [row[1] for row in data]

        plt.figure(figsize=(8, 5))

        plt.plot(names, bmi_values, marker='o')

        plt.title('BMI Trend Analysis')

        plt.xlabel('Users')

        plt.ylabel('BMI')

        plt.grid(True)

        plt.tight_layout()

        plt.savefig('static/graph.png')

        plt.close()

    return redirect('/static/graph.png')


# ================= RUN APP =================

if __name__ == '__main__':

    app.run(debug=True)