from os import close
from flask import Flask, url_for, request, redirect
from flask.templating import render_template
import sqlite3
import subprocess
import os
import time


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except Exception as e:
        print(e)

    return conn


database = r'/home/css400.db'
conn = create_connection(database)
cur = conn.cursor()

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    cur.execute("SELECT * FROM room;")
    id = cur.fetchall()

    return render_template('index.html', data=id)


@app.route('/selectRoom', methods=['POST'])
def getroom():
    roomID = request.form['roomID']
    cur.execute("SELECT * FROM device WHERE room_id=?;", (roomID,))
    id = cur.fetchall()
    return render_template("devices.html", devices=id)


@app.route('/selectDevice', methods=['POST'])
def getDevice():
    deviceID = request.form['device']
    cur.execute("SELECT type FROM device WHERE device_id=?;", (deviceID,))
    type = cur.fetchall()[0][0]

    if type == "switch":
        cur.execute("SELECT * FROM Switchstate WHERE device_id=?;", (deviceID,))
        state = cur.fetchall()[0]
        if state[2] == 1:
            info = "off"
        else:
            info = "on"
        return render_template("switch.html", power=info, state=state)

    elif type == "ac":
        cur.execute("SELECT ACcommand.* FROM ACstate,ACcommand WHERE ACstate.device_id=? AND ACstate.state_id=ACcommand.command_id;", (deviceID,))
        state = cur.fetchall()[0]
        return render_template("ac.html", id=deviceID, state=state)

    elif type == "tv":
        cur.execute("SELECT * FROM TVstate WHERE device_id=?;", (deviceID,))
        state = cur.fetchall()[0]
        return render_template("tv.html", id=deviceID, state=state)


@app.route('/switch', methods=['POST'])
def switch():
    power = request.form['switch']
    deviceID = request.form['id']
    if power == "1":
        # print("on")
        subprocess.Popen(["python3", "filter.py", str("light on"), "pi"], cwd=os.getcwd())
    elif power == "0":
        # print("off")
        subprocess.Popen(["python3", "filter.py", str("light off"), "pi"], cwd=os.getcwd())

    time.sleep(1)

    cur.execute("SELECT * FROM Switchstate WHERE device_id=?;", (deviceID,))
    state = cur.fetchall()[0]
    if state[2] == 1:
        info = "off"
    else:
        info = "on"
    return render_template("switch.html", power=info, state=state)


@app.route('/tv', methods=['POST'])
def tv():
    command = request.form['command']
    deviceID = request.form['id']
    print(command)
    if command.isnumeric():
        command = "channel "+command

    subprocess.Popen(["python3", "filter.py", str(command), "esp"], cwd=os.getcwd())
    time.sleep(1)

    cur.execute("SELECT * FROM TVstate WHERE device_id=?;", (deviceID,))
    state = cur.fetchall()[0]
    return render_template("tv.html", id=deviceID, state=state)


@app.route('/ac', methods=['POST'])
def ac():
    command = ""
    deviceID = request.form['id']
    device=""
    if deviceID == '2':
        device = "pi"
    elif deviceID == '3':
        device = "esp"
    print(device)
    power = request.form['power']
    mode = request.form['mode']
    temp = request.form['temp']
    command = "ac "+power+" "+mode+" mode "+temp
    try:
        fan = request.form['fan']
        command = command+" "+fan
    except:
        pass
    try:
        swing = request.form['swing']
        if swing == '1':
            command = command+" swing on"
        elif swing == '0':
            command = command+" swing off"
    except:
        pass
    print(command)
    
    subprocess.Popen(["python3", "filter.py", command, device], cwd=os.getcwd())
    time.sleep(1)

    cur.execute("SELECT ACcommand.* FROM ACstate,ACcommand WHERE ACstate.device_id=? AND ACstate.state_id=ACcommand.command_id;", (deviceID,))
    state = cur.fetchall()[0]
    return render_template("ac.html", id=deviceID, state=state)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    #app.run(debug=True)
