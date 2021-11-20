from os import pipe
import sys
import sqlite3


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)

    return conn

# print(switchstate)
# exit()


database = r'/home/css400.db'
conn = create_connection(database)
cur = conn.cursor()
command = ""

transcript = str(sys.argv[1:][0])
device = str(sys.argv[1:][1])
print(transcript)
# acDeviceId = 2
if device == "pi":
    acDeviceId = 2
elif device == "esp":
    acDeviceId = 3

# acDeviceId = 2
device_id = acDeviceId

# transcript = "pi ac cool mode fan speed auto swing on 27 degrees"
# transcript = "light toggle"
# transcript = "ac cool mode fan speed auto swing off"
# transcript = "ac off"
# transcript = ""

transcript = transcript + " "
transcript = transcript.lower()
# print(transcript)

# params
power = None
mode = None
temp = None
swing = None
fan = None

light = None

tv = None
tvChannel = None
tvPower = None
tvVolume = None


# transcript = input()


def fanSwing(transcript):
    global fan
    global swing
    global power

    if transcript.find("fan") >= 0:
        power = 1
        fanSpeed = transcript[transcript.find("fan"):]
        # print(fanSpeed)

        if fanSpeed.find(" 1 ") >= 0:
            fan = 1

        elif fanSpeed.find(" 2 ") >= 0:
            fan = 2

        elif fanSpeed.find(" 3 ") >= 0:
            fan = 3

        elif fanSpeed.find(" 4 ") >= 0:
            fan = 4

        elif fanSpeed.find(" 5 ") >= 0:
            fan = 5

        elif transcript.find("auto") >= 0:
            fan = 0

    if transcript.find("swing on") >= 0 or transcript.find("on swing") >= 0:
        swing = 1
        power = 1

    elif transcript.find("swing off") >= 0 or transcript.find("off swing") >= 0:
        swing = 0
        power = 1


# control lights
if transcript.find("light") >= 0:

    cur.execute("SELECT state FROM Switchstate")
    light = cur.fetchall()[0][0]
    # print(light)

    if transcript.find("on") >= 0:
        light = "on"

    elif transcript.find("off") >= 0:
        light = "off"

    elif transcript.find("toggle") >= 0:
        if light == 2:
            light = "off"
        else:
            light = "on"

# control tv

if transcript.find("tv") >= 0 or transcript.find("television") >= 0 or transcript.find(
        "volume") >= 0 or transcript.find("mute") >= 0 or transcript.find("unmute") >= 0 or transcript.find("channel") >= 0:
    tv = "on"
    if (transcript.find("tv") >= 0 or transcript.find("television") >= 0) and transcript.find("on") >= 0:
        tvPower = 1

    elif (transcript.find("tv") >= 0 or transcript.find("television") >= 0) and transcript.find("off") >= 0:
        tvPower = 0

    elif transcript.find("volume") >= 0 and (transcript.find("up") >= 0 or transcript.find("increase") >= 0):
        tvVolume = 1

    elif transcript.find("volume") >= 0 and (transcript.find("down") >= 0 or transcript.find("decrease") >= 0):
        tvVolume = 0

    elif transcript.find("unmute") >= 0:
        tvVolume = "unmute"

    elif transcript.find("mute") >= 0:
        tvVolume = "mute"

    elif transcript.find("channel") >= 0:
        numlist = [int(s) for s in transcript.split() if s.isdigit()]
        tvChannel = numlist[0]

# control air conditioner

if (transcript.find("air") >= 0 or transcript.find("air conditioner")
        >= 0 or transcript.find("ac") >= 0) and transcript.find("on") >= 0:
    power = 1

if transcript.find("air off") >= 0 or transcript.find("air conditioner off") >= 0 or transcript.find("ac off") >= 0 or transcript.find("off air") >= 0 or transcript.find(
        "off air conditioner") >= 0 or transcript.find("off ac") >= 0 or transcript.find("off the ac") >= 0 or transcript.find("off the air conditioner") >= 0:
    power = 0

if not light and not tv:

    fanSwing(transcript)

    numlist = [int(s) for s in transcript.split() if s.isdigit()]
    templist = []
    # print(numlist)
    for i in numlist:
        if i >= 18 and i <= 32:
            templist.append(i)
    try:
        temp = templist[0]
        mode = "cool"
        power = 1
    except BaseException:
        next

    if transcript.find("dry") >= 0:
        power = 1
        mode = "dry"
        temp = 0
        swing = 0
        fan = 0

    # elif transcript.find("fan mode")>=0 or transcript.find("mode fan")>=0:
    elif transcript.find("fan mode") >= 0:
        # fanSwing(transcript)
        power = 1
        temp = None
        mode = "fan"

    elif transcript.find("cool") >= 0:
        fanSwing(transcript)
        power = 1
        mode = "cool"


# print(power, mode, temp, swing, fan)
# exit()

cur.execute(
    "SELECT ACcommand.power, ACstate.state_id, ACcommand.mode FROM ACstate, ACcommand WHERE ACstate.state_id=ACcommand.command_id AND ACstate.device_id=?;",
    (device_id,
     ))
state = cur.fetchall()[0]
# print(state)
acPowerState = state[0]
laststateid = state[1]
currentmode = state[2]
# print(acPowerState)

cur.execute("SELECT channel, power, mute FROM TVstate WHERE device_id=?;", (4,))
tvstate = cur.fetchall()[0]
tvChannelState = tvstate[0]
tvPowerState = tvstate[1]
tvMuteState = tvstate[2]

# light on off
if light == "on":
    cur.execute("SELECT signal from Switchcommand WHERE power = 1;")
    command = cur.fetchall()[0][0]
    cur.execute("UPDATE Switchstate SET state=2 WHERE device_id=?;", (1,))
    conn.commit()


elif light == "off":
    cur.execute("SELECT signal from Switchcommand WHERE power = 0;")
    command = cur.fetchall()[0][0]
    cur.execute("UPDATE Switchstate SET state=1 WHERE device_id=?;", (1,))
    conn.commit()


# tv controls
if tv is not None:
    if tvPower is not None:
        if tvPowerState == 0 and tvPower == 0:
            tvPower = None

        elif tvPowerState == 0 and tvPower == 1:
            cur.execute("SELECT signal from TVcommand WHERE button = 'power';")
            command = cur.fetchall()[0][0]
            cur.execute("UPDATE TVstate SET power=1 WHERE device_id=?;", (4,))
            conn.commit()

        elif tvPowerState == 1 and tvPower == 0:
            cur.execute("SELECT signal from TVcommand WHERE button = 'power';")
            command = cur.fetchall()[0][0]
            cur.execute("UPDATE TVstate SET power=0 WHERE device_id=?;", (4,))
            conn.commit()

        elif tvPowerState == 1 and tvPower == 1:
            tvPower = None

    elif tvVolume is not None:
        if tvVolume == 1:
            cur.execute(
                "SELECT signal from TVcommand WHERE button = 'volume up';")
            command = cur.fetchall()[0][0]

        elif tvVolume == 0:
            cur.execute(
                "SELECT signal from TVcommand WHERE button = 'volume down';")
            command = cur.fetchall()[0][0]

        elif tvVolume == "mute":
            if tvMuteState == 0:
                cur.execute(
                    "SELECT signal from TVcommand WHERE button = 'mute';")
                command = cur.fetchall()[0][0]
                cur.execute(
                    "UPDATE TVstate SET mute=1 WHERE device_id=?;", (4,))
                conn.commit()

        elif tvVolume == "unmute":
            if tvMuteState == 1:
                cur.execute(
                    "SELECT signal from TVcommand WHERE button = 'mute';")
                command = cur.fetchall()[0][0]
                cur.execute(
                    "UPDATE TVstate SET mute=0 WHERE device_id=?;", (4,))
                conn.commit()

    elif tvChannel is not None:
        if tvPowerState == 1:
            command = []
            for i in [int(n) for n in str(tvChannel)]:
                cur.execute(
                    "SELECT signal from TVcommand WHERE button = ?;", (i,))
                command.append(cur.fetchall()[0][0])

            cur.execute(
                "SELECT signal from TVcommand WHERE button = 'ok';")
            command.append(cur.fetchall()[0][0])
            cur.execute("SELECT signal from TVcommand WHERE button = 'back';")
            command.append(cur.fetchall()[0][0])

            cur.execute(
                "UPDATE TVstate SET channel=? WHERE device_id=?;", (tvChannel, 4,))
            conn.commit()


# ac off to on
if not light and acPowerState == 0 and power == 1:
    cur.execute("SELECT ACcommand.power, ACcommand.temp, ACcommand.fan, ACcommand.swing, ACcommand.mode FROM ACcommand, ACstate WHERE ACcommand.command_id=ACstate.laststate_id AND ACstate.device_id=?;", (device_id,))
    lastState = cur.fetchall()[0]
    if power is None:
        power = lastState[0]

    if mode is None:
        mode = lastState[4]

    if temp is None:
        temp = lastState[1]

    if swing is None:
        swing = lastState[3]

    if fan is None:
        fan = lastState[2]

    # print(power, mode, temp, swing, fan)

    cur.execute(
        "SELECT signal, command_id FROM ACcommand WHERE power=? AND temp=? AND fan=? AND swing=? AND mode=? AND device_id=?;",
        (power,
         temp,
         fan,
         swing,
         mode,
         device_id,
         ))
    try:
        signalID = cur.fetchall()[0]
        command = signalID[0]
        commandID = signalID[1]
        # print(command)
    except BaseException:
        print("command not found")

    cur.execute(
        "UPDATE ACstate SET state_id=?, laststate_id=? WHERE device_id=?;",
        (commandID,
         laststateid,
         device_id,
         ))
    conn.commit()


# ac on to on
if not light and acPowerState == 1 and power == 1:
    if mode == "cool" and currentmode != "cool":
        cur.execute(
            "SELECT ACcommand.power, ACcommand.temp, ACcommand.fan, ACcommand.swing, ACcommand.mode FROM ACcommand, ACstate WHERE ACcommand.command_id=ACstate.laststateCool_id AND ACstate.device_id=?;",
            (device_id,
             ))
        lastState = cur.fetchall()[0]

        if power is None:
            power = lastState[0]

        if mode is None:
            mode = lastState[4]

        if temp is None:
            temp = lastState[1]

        if swing is None:
            swing = lastState[3]

        if fan is None:
            fan = lastState[2]

    elif mode == "fan" and currentmode != "fan":
        cur.execute(
            "SELECT ACcommand.power, ACcommand.temp, ACcommand.fan, ACcommand.swing, ACcommand.mode FROM ACcommand, ACstate WHERE ACcommand.command_id=ACstate.laststateFan_id AND ACstate.device_id=?;",
            (device_id,
             ))
        lastState = cur.fetchall()[0]

        if power is None:
            power = lastState[0]

        if mode is None:
            mode = lastState[4]

        if temp is None:
            temp = lastState[1]

        if swing is None:
            swing = lastState[3]

        if fan is None:
            fan = lastState[2]

    else:
        cur.execute(
            "SELECT ACcommand.power, ACcommand.temp, ACcommand.fan, ACcommand.swing, ACcommand.mode FROM ACcommand, ACstate WHERE ACcommand.command_id=ACstate.state_id AND ACstate.device_id=?;",
            (device_id,
             ))
        lastState = cur.fetchall()[0]

        if power is None:
            power = lastState[0]

        if mode is None:
            mode = lastState[4]

        if temp is None:
            temp = lastState[1]

        if swing is None:
            swing = lastState[3]

        if fan is None:
            fan = lastState[2]

    # print(power, mode, temp, swing, fan)

    cur.execute(
        "SELECT signal, command_id FROM ACcommand WHERE power=? AND temp=? AND fan=? AND swing=? AND mode=? AND device_id=?;",
        (power,
         temp,
         fan,
         swing,
         mode,
         device_id,
         ))
    try:
        signalID = cur.fetchall()[0]
        command = signalID[0]
        commandID = signalID[1]
    except BaseException:
        print("command not found")

    if mode == "cool":
        cur.execute(
            "UPDATE ACstate SET state_id=?, laststate_id=?, laststateCool_id=? WHERE device_id=?;",
            (commandID,
             laststateid,
             commandID,
             device_id,
             ))
        conn.commit()

    elif mode == "fan":
        cur.execute(
            "UPDATE ACstate SET state_id=?, laststate_id=?, laststateFan_id=? WHERE device_id=?;",
            (commandID,
             laststateid,
             commandID,
             device_id,
             ))
        conn.commit()

    else:
        cur.execute(
            "UPDATE ACstate SET state_id=?, laststate_id=? WHERE device_id=?;",
            (commandID,
             laststateid,
             device_id,
             ))
        conn.commit()


# ac on to off
# print(acPowerState)
if not light and acPowerState == 1 and power == 0:

    cur.execute(
        "SELECT signal, command_id FROM ACcommand WHERE power=0 AND device_id=?;",
        (device_id,
         ))
    try:
        command = cur.fetchall()[0]
        # print(command)
    except BaseException:
        print("command not found")

    cur.execute(
        "UPDATE ACstate SET state_id=?, laststate_id=? WHERE device_id=?;",
        (command[1],
         laststateid,
         device_id,
         ))
    conn.commit()

    command = command[0]

    # print(power, mode, temp, swing, fan)

# ac off to off
if not light and acPowerState == 0 and power == 0:

    cur.execute(
        "SELECT signal, command_id FROM ACcommand WHERE power=0 AND device_id=?;",
        (device_id,
         ))
    try:
        command = cur.fetchall()[0]
        # print(command)
    except BaseException:
        print("command not found")

    command = command[0]


cur.close()
conn.close()

# print(power, mode, temp, swing, fan)
# print(light)


if light is not None:
    print(light)
    # print(command)
    import broadlink
    devices = broadlink.discover(
        timeout=0.2, discover_ip_address='192.168.1.111')
    devices[0].auth()
    devices[0].send_data(command)

elif tv is not None:
    print(tvPower, tvChannel, tvVolume)
    import broadlink
    from time import sleep
    devices = broadlink.discover(
        timeout=0.2, discover_ip_address='192.168.1.123')
    devices[0].auth()

    if tvChannel is None:
        devices[0].send_data(command)

    elif tvChannel is not None:
        # print(command)
        for i in command:
            # print(i)
            devices[0].send_data(i)
            sleep(0.5)

elif power is not None:
    print(power, mode, temp, swing, fan)
    # print(command)
    import broadlink
    if device == "esp":
        devices = broadlink.discover(timeout=0.2, discover_ip_address='192.168.1.123')
    elif device == "pi":
        devices = broadlink.discover(timeout=0.2, discover_ip_address='192.168.1.111')
    devices[0].auth()
    devices[0].send_data(command)
