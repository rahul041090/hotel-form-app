from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
from datetime import datetime
import json

app = Flask(__name__)

# ✅ DB INIT
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        registration_id TEXT,
        reference_number TEXT,

        hotel_name TEXT,
        city TEXT,
        address TEXT,
        website TEXT,
        star_category TEXT,
        state TEXT,
        gst TEXT,

        checkin TEXT,
        checkout TEXT,

        amenities TEXT,

        contact_data TEXT,      -- ✅ ADD THIS

        bank_details TEXT,
        policies TEXT,
        authorization TEXT,

        season_data TEXT,
        rate_data TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ✅ ROUTES
@app.route('/')
def form():
    return render_template("form.html")

@app.route('/search')
def search():
    return render_template("search.html")


@app.route('/submit', methods=['POST'])
def submit():

    data = request.json

    # ✅ DEBUG
    print("Amenities:", data.get('amenities'))
    print("Seasons:", data.get('seasons'))
    print("Rates:", data.get('rates'))
    print("Contacts:", data.get('contacts'))  # ✅ NEW

    # ✅ Generate IDs
    registration_id = "REG-" + datetime.now().strftime("%Y%m%d%H%M%S")
    reference_number = "REF-" + uuid.uuid4().hex[:6].upper()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO hotels (

        registration_id,
        reference_number,

        hotel_name,
        city,
        address,
        website,
        star_category,
        state,
        gst,

        checkin,
        checkout,

        amenities,

        contact_data,      -- ✅ NEW
        bank_details,
        policies,
        authorization,

        season_data,
        rate_data

    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (

        registration_id,
        reference_number,

        data.get('hotel_name'),
        data.get('city'),
        data.get('address'),
        data.get('website'),
        data.get('star_category'),
        data.get('state'),
        data.get('gst'),

        data.get('checkin'),
        data.get('checkout'),

        # ✅ SECTION 6
        json.dumps(data.get('amenities', [])),

        # ✅ SECTION 2 (NEW ✅)
        json.dumps(data.get('contacts', {})),

        # ✅ SECTION 7
        json.dumps(data.get('bank', {})),

        # ✅ SECTION 5
        json.dumps(data.get('policies', {})),

        # ✅ SECTION 8
        json.dumps(data.get('authorization', {})),

        # ✅ SECTION 4
        json.dumps(data.get('seasons', [])),

        # ✅ SECTION 3
        json.dumps(data.get('rates', []))
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Saved successfully ✅",
        "registration_id": registration_id,
        "reference_number": reference_number
    })


# ✅ SEARCH API
@app.route('/get-hotels', methods=['GET'])
def get_hotels():

    name = request.args.get('name', '')
    city = request.args.get('city', '')
    state = request.args.get('state', '')

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
    SELECT id, registration_id, reference_number, hotel_name, city, state
    FROM hotels
    WHERE hotel_name LIKE ? AND city LIKE ? AND state LIKE ?
    '''

    cursor.execute(query, (
        f"%{name}%",
        f"%{city}%",
        f"%{state}%"
    ))

    rows = cursor.fetchall()
    conn.close()

    result = [dict(row) for row in rows]
    return jsonify(result)


# ✅ VIEW PAGE (FIXED ✅ SAFE JSON HANDLING)
@app.route('/view/<int:id>')
def view_hotel(id):

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hotels WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Hotel not found"

    data = dict(row)

    # ✅ SAFE parsing (no crash)
    data['amenities'] = json.loads(data.get('amenities') or "[]")
    data['bank'] = json.loads(data.get('bank_details') or "{}")
    data['policies'] = json.loads(data.get('policies') or "{}")
    data['authorization'] = json.loads(data.get('authorization') or "{}")
    data['seasons'] = json.loads(data.get('season_data') or "[]")
    data['rates'] = json.loads(data.get('rate_data') or "[]")
    data['contacts'] = json.loads(data.get('contact_data') or "{}")

    return render_template("view.html", data=data)


# ✅ EDIT (placeholder)
@app.route('/edit/<int:id>')
def edit_hotel(id):

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hotels WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Hotel not found"

    data = dict(row)

    # ✅ Parse JSON
    data['amenities'] = json.loads(data.get('amenities') or "[]")
    data['bank'] = json.loads(data.get('bank_details') or "{}")
    data['policies'] = json.loads(data.get('policies') or "{}")
    data['authorization'] = json.loads(data.get('authorization') or "{}")
    data['seasons'] = json.loads(data.get('season_data') or "[]")
    data['rates'] = json.loads(data.get('rate_data') or "[]")
    data['contacts'] = json.loads(data.get('contact_data') or "{}")

    return render_template("edit.html", data=data)


@app.route('/update/<int:id>', methods=['POST'])
def update_hotel(id):

    data = request.json

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE hotels SET

        hotel_name=?,
        city=?,
        address=?,
        website=?,
        star_category=?,
        state=?,
        gst=?,
        contact_data=?,

        checkin=?,
        checkout=?,

        amenities=?,
        bank_details=?,
        policies=?,
        authorization=?,
        season_data=?,
        rate_data=?

    WHERE id=?
    ''', (

        data.get('hotel_name'),
        data.get('city'),
        data.get('address'),
        data.get('website'),
        data.get('star_category'),
        data.get('state'),
        data.get('gst'),

        data.get('checkin'),
        data.get('checkout'),

        json.dumps(data.get('amenities', [])),
        json.dumps(data.get('bank', {})),
        json.dumps(data.get('policies', {})),
        json.dumps(data.get('authorization', {})),
        json.dumps(data.get('seasons', [])),
        json.dumps(data.get('rates', [])),
        json.dumps(data.get('contacts', {})),

        id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "✅ Updated successfully"})


# ✅ RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)