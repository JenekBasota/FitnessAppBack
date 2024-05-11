from flask_socketio import SocketIO, emit
from model.Classes.ClassificationSmoothing import EMADictSmoothing
from model.Classes.FullBodyPoseEmbedder import FullBodyPoseEmbedder
from model.Classes.PoseClassifier import PoseClassifier

pose_samples_folder = "model/fitness_poses_images_csv"

socketio = SocketIO()

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
        if 'landmark' in data:
            result = StartClassifier(data)
            emit('message', {'status': 'success', 'msg': result})
        else:
            emit('message', {'status': 'error', 'message': 'JSON data is missing the landmark key'})
    except:
        emit('message', {'status': 'error', 'msg': 'Invalid message'})