from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import time
import random
import math
import serial

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


## vlakno ktore sa spusti nazaciatku
def background_thread(args):
    time.sleep(3)
    count = 0
    y ="0"
    B = 1 #pomocna premena, porovnava sa s A
    print("args")
    print(args)
    def write_read(x):
        if B!=A:
            print("poslana hodnota do arduina")
            arduino.write(bytes(x, 'utf-8'))
            time.sleep(1)
            hodnota = arduino.readline().strip()
            return hodnota
        else:
            #print("vypisuje predosle")
            hodnota = arduino.readline().decode().strip('\r\n')
            hodnota = format(hodnota)
            return hodnota





    while True:
        if args:
          A = dict(args).get('A')#vstup od uzivatela
        else:
          A = 1

        y = dict(args).get('start')#vstup od uzivatela
        A=str(A)

        socketio.sleep(1)#ako casto chceme refreshovat
        count += 1 #zvysujeme pocitadlo pri receive
        print("A=",A)

        #num="200"
        #num = input("Enter a number: ") # Taking input from user
        outa = write_read(A)
        outa = str(outa)
        #print(outa) # printing the value
        B = A
        #print("B",B)
        print("Tlacitko Start",y)#na zaciatku tlacitko start je NONE
        if y =="1":
            socketio.emit('my_response',
                          {'data': outa, 'count': count},
                          namespace='/test')







@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

 ##ak dojde od klienta udalost my_event tak sa urobi funkcia
@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    session['A'] = message['value']
    print("message['value']")
    print(message['value'])
    emit('my_response',
         {'data': ('Nova hodnota je:', message['value']), 'count': session['receive_count']})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('start', namespace='/test')
def db_message(message):
    session['start'] = message['value']

@socketio.on('stop', namespace='/test')
def db_message(message):
    session['start'] = message['value']

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)