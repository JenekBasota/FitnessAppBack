from flask_socketio import SocketIO, emit, join_room, leave_room
from model.Classes.ClassificationSmoothing import EMADictSmoothing
from model.Classes.FullBodyPoseEmbedder import FullBodyPoseEmbedder
from model.Classes.PoseClassifier import PoseClassifier
from datetime import datetime

pose_samples_folder = "model/fitness_poses_images_csv"

socketio = SocketIO()
room_data = {}

def StartClassifier(data):
    pose_embedder = FullBodyPoseEmbedder()
    pose_classifier = PoseClassifier(
        pose_samples_folder=pose_samples_folder,
        pose_embedder=pose_embedder,
        top_n_by_max_distance=30,
        top_n_by_mean_distance=10,
    )

    transformedLandmarks = pose_embedder.get_landmark_from_json(data)

    if transformedLandmarks is not None:
        if transformedLandmarks.shape != (33,3): 
            return f"Unexpected landmarks shape: {transformedLandmarks.shape}"

        pose_classification = pose_classifier(transformedLandmarks)

        classification_filter = EMADictSmoothing(window_size=10, alpha=0.2)

        pose_classification_filtered = classification_filter(pose_classification)

        return pose_classification_filtered

@socketio.on('message')
def handle_message(data):
    try:
        if 'room_id' not in data or data['room_id'] not in room_data:
            emit('message', {'status': 'error', 'msg': "Room identifier not found"})
            return 0
        
        if 'exercise' not in data:
            emit('message', {'status': 'error', 'msg': "Exercise not found"})
            return 0

        if 'landmark' not in data:
            emit('message', {'status': 'error', 'message': 'JSON data is missing the landmark key'})
            return 0
        
        room_id = data['room_id']
        room_data[room_id]['exercise'] = data['exercise']

        result = StartClassifier(data)
        current_phase_values = list(result.values())
        current_phase_keys = list(result.keys())
        if room_data[room_id]['current phase'] is None:
            room_data[room_id]['current phase'] = current_phase_keys[0]
        else:
            if len(current_phase_values) == 1 or current_phase_values[0] >= current_phase_values[1]:
                target_phase = current_phase_keys[0]
            else:
                target_phase = current_phase_keys[1]
                
            if room_data[room_id]['current phase'] != target_phase:
                room_data[room_id]['current phase'] = target_phase
                if "up" not in target_phase:
                    room_data[room_id]['count'] += 1


        emit('message', {'status': 'success', 'count': room_data[room_id]['count']}, room=room_id)
    except:
        emit('message', {'status': 'error', 'msg': 'Invalid message'})

@socketio.on('connect')
def create_room():
    room_id = 'room_' + datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    room_data[room_id] = {
        'start': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'exercise' : None,
        'count': 0,
        'current phase': None,
        'end': None}
    join_room(room_id)
    emit('message', {'room_id': room_id}, room=room_id)

@socketio.on('exit_room')
def exit_room(data):
    if 'room_id' not in data:
        emit('message', {'status': 'error', 'msg': "Room identifier not found"})
        return 0
    
    room_id = data['room_id']
    room_data[room_id]['end'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    emit('message', {'status': 'success', 'msg': "Leave room"}, room=room_id)
    
    leave_room(room_id)
    del room_data[room_id]
    