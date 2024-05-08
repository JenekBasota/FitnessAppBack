from flask_socketio import SocketIO, emit

socketio = SocketIO()

@socketio.on('message')
def handle_message(data):
    try:
        # Пытаемся разобрать JSON-данные
        if 'landmark' in data:
            landmarks = data['landmark']

            for landmark in landmarks:
                print(f"Received landmark data: {landmark}")

            emit('message', {'status': 'success', 'message': 'Data received'})
        else:
            emit('message', {'status': 'error', 'message': 'JSON data is missing the landmark key'})
    except:
        emit('message', {'status': 'error', 'msg': 'Invalid message'})