import json

from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)

# start websocket server
socketio = SocketIO(app, cors_allowed_origins="*")

# TODO: all_possible_cards should be calculated by crew_game logic
# notation could be changed
# when player 
card_max_value = 9
trump_card_max_value = 4
trump_color = 'x'
colors = {'r', 'g', 'b', 'y'}
all_possible_cards = set()

for color in colors:
    for value in range(1, card_max_value + 1):
        all_possible_cards.add(color + str(value))

for value in range(1, trump_card_max_value + 1):
    all_possible_cards.add(trump_color + str(value))
#############################################################################


# all users that have the site open
users = dict()
# users that started a game (empty when no game started)
players = dict()


@socketio.on('connect')
def connect():
    users.update({request.sid: ""})
    emit('user list', json.dumps(users), broadcast=True)
    print('new connection: ', request.sid, ' user count: ' + str(len(users)))
    if (len(players) > 0):
        emit('game started', json.dumps(players), broadcast=True)
        emit('cards updated', json.dumps(list(all_possible_cards)),
             broadcast=True)


@socketio.on('update name')
def update_name(name):
    users.update({request.sid: name})
    emit('user list', json.dumps(users), broadcast=True)


@socketio.on('start game')
def start_game():
    global players
    players = users
    emit('game started', json.dumps(players), broadcast=True)
    emit('cards updated', json.dumps(list(all_possible_cards)), broadcast=True)


@socketio.on('end game')
def end_game():
    global players
    players = dict()
    emit('game ended', broadcast=True)


# when one player adds a card to its deck remove it from possible cards
@socketio.on('card taken')
def card_taken(card):
    print(card)
    all_possible_cards.remove(card)
    emit('cards updated', json.dumps(list(all_possible_cards)), broadcast=True)


@socketio.on('disconnect')
def disconnect():
    users.pop(request.sid)
    emit('user list', json.dumps(users), broadcast=True)
    print('disconnected: ', request.sid, ' user count: ' + str(len(users)))


@app.route('/')
def index():
    return render_template('index.html')


# If you are running it using python <filename> then below command will be used
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True)
