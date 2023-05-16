from flask import Flask, request, jsonify
from settings import handle_exceptions, logger, connection

app = Flask(__name__)


# create character
@app.route("/game/insert", methods=["POST"], endpoint="create_player")
@handle_exceptions
def create_player():
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection")
    if "name" and "strength" and "power" and "intelligence" not in request.json:
        raise Exception("data missing")
    data = request.get_json()
    name = data['name']
    strength = data['strength']
    power = data['power']
    intelligence = data['intelligence']

    cur.execute('INSERT INTO player_data(name, strength, power, intelligence)''VALUES (%s,%s, %s, %s);',
                (name, strength, power, intelligence))
    conn.commit()


# get patient details
@app.route("/player_details/<int:player_id>", methods=["GET"], endpoint="get_player_details")
def get_player_details(player_id):
    cur, conn = connection()
    # Retrieve patient details from the patient_data table
    cur.execute("SELECT name, strength, power, intelligence FROM player_data WHERE player_id = %s", (player_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"message": f"No rows found "})
    data_list = []
    name, strength, power, intelligence = row
    data = {
            "name": name,
            "strength": strength,
            "power": power,
            "intelligence": intelligence
    }
    data_list.append(data)
    return jsonify(data_list), 200


@app.route("/all/player_details", methods=["GET"], endpoint="all_player_details")
def get_player_details():
    cur, conn = connection()
    # Retrieve player details from the player_data table
    cur.execute("SELECT * FROM player_data ")
    rows = cur.fetchall()
    if not rows:
        return jsonify({"message": f"No rows found "})
    data_list = []
    for row in rows:
        player_id, name, strength, power, intelligence = row
        data = {
            "player_id": player_id,
            "name": name,
            "strength": strength,
            "power": power,
            "intelligence": intelligence
        }
        data_list.append(data)
    return jsonify(data_list), 200


# update player details
@app.route("/details/update/<int:player_id>", methods=["PUT"], endpoint="details_update")
def treatment_update(player_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    data = request.get_json()
    name = data['name']
    strength = data['strength']
    power = data['power']
    intelligence = data['intelligence']
    cur.execute('SELECT name,strength,power,intelligence FROM player_data WHERE player_id = %s', (player_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'message': 'player_id is not available'}), 400

    # Update the book's availability
    cur.execute('UPDATE player_data SET name=%s,strength=%s,power=%s,intelligence=%s WHERE player_id = %s', (name, strength, power, intelligence, player_id))
    conn.commit()
    return jsonify({'message': 'updated successfully'}), 200



@app.route('/game/attack', methods=['POST'], endpoint="attack")
def attack():
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection")
    if "attacker" and "defender" not in request.json:
        raise Exception('data missing')
    data = request.get_json()
    attacker = data.get('attacker')
    defender = data.get('defender')
    cur.execute("SELECT * FROM player_data WHERE name=%s;", (attacker,))
    attacker_data = cur.fetchone()
    cur.execute("SELECT * FROM player_data WHERE name=%s;", (defender,))
    defender_data = cur.fetchone()
    if not attacker_data:
        return jsonify({'message': 'Attacker not found in the database'}), 404
    if not defender_data:
        return jsonify({'message': 'Defender not found in the database'}), 404

    damage = attacker_data[2] - defender_data[3]
    if damage < 0:
        damage = 0
    new_intelligence = defender_data[4] - damage
    if new_intelligence <= 0:
        cur.execute("DELETE FROM player_data WHERE name=%s;", (defender,))
        conn.commit()
        return jsonify({'message': 'Attack successful', 'damage': damage, 'defender': defender, 'status': 'dead'}), 200
    else:
        cur.execute("UPDATE player_dara SET intelligence=%s WHERE name=%s;", (new_intelligence, defender,))
        conn.commit()
        return jsonify({'message': 'Attack successful', 'damage': damage, 'defender': defender, 'status': 'alive'}), 200


# delete character
@app.route("/delete/<int:player_id>",methods=["DELETE"],endpoint="delete_character")
def delete_treatment_id(player_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('DELETE FROM player_data WHERE player_id=%s', (player_id,))
    logger(__name__).warning("close the database connection")
    conn.commit()
    if cur.rowcount > 0:
        return jsonify({"message": "deleted successfully"})
    else:
        return jsonify({"message": "player_id  not found"})


# get player with high intellegence
@app.route("/players/highest_intelligence", methods=["GET"], endpoint="get_player_highest_intelligence")
def get_player_highest_intelligence():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")

    # Retrieve player with highest intelligence
    cur.execute("SELECT * FROM player_data WHERE intelligence = (SELECT MAX(intelligence) FROM player_data)")
    row = cur.fetchone()

    if not row:
        return jsonify({"message": "No players found"})

    player_id, name, strength, power, intelligence = row

    data = {
        "player_id": player_id,
        "name": name,
        "strength": strength,
        "power": power,
        "intelligence": intelligence
    }

    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
