from os.path import basename
from mediapipe import Image, ImageFormat
from os import mkdir
from os.path import exists
import os
import numpy as np
from mediapipe import solutions, tasks
from mediapipe.framework.formats import landmark_pb2
from os.path import realpath
import cv2
import csv
import json

allowed_extensions = ["png", "jpeg", "jpg"]


class Utils:

    def __init__(self) -> None:
        pass

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = np.copy(rgb_image)

        # Loop through the detected poses to visualize.
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]

            # Draw the pose landmarks.
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend(
                [
                    landmark_pb2.NormalizedLandmark(
                        x=landmark.x, y=landmark.y, z=landmark.z
                    )
                    for landmark in pose_landmarks
                ]
            )
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                solutions.pose.POSE_CONNECTIONS,
                solutions.drawing_styles.get_default_pose_landmarks_style(),
            )
        return annotated_image

    def get_landmarks_by_size(self, pose_landmarker, width, height):
        return np.array(
            [[lmk.x * width, lmk.y * height, lmk.z * width] for lmk in pose_landmarker],
            dtype=np.float32,
        )

    def pose_landmarker_on_image(
        self, save_file: bool, image_path: str, out_path: str, model_path: str
    ) -> list:

        BaseOptions = tasks.BaseOptions
        PoseLandmarker = tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = tasks.vision.RunningMode

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=realpath(model_path)),
            running_mode=VisionRunningMode.IMAGE,
            num_poses=1,
        )

        with PoseLandmarker.create_from_options(options) as landmarker:
            cv_mat = cv2.imread(image_path)
            rgb_frame = Image(image_format=ImageFormat.SRGB, data=cv_mat)
            pose_landmarker_result = landmarker.detect(rgb_frame)

        if len(pose_landmarker_result.pose_landmarks) == 0:
            return None

        pose_landmarker = pose_landmarker_result.pose_landmarks[0]
        frame_height, frame_width = cv_mat.shape[0], cv_mat.shape[1]
        file_name = basename(image_path)

        if save_file == True:
            annotated_image = self.draw_landmarks_on_image(
                rgb_frame.numpy_view(), pose_landmarker_result
            )
            cv2.imwrite(f"{out_path}/{file_name}", annotated_image)

        return [
            [file_name]
            + self.get_landmarks_by_size(pose_landmarker, frame_width, frame_height)
            .flatten()
            .astype(str)
            .tolist(),
            pose_landmarker,
            frame_width,
            frame_height,
        ]

    def read_landmark_from_json(self, data):
        landmark_array = np.array(data["landmark"], dtype=np.float32)

        reshaped_data = np.reshape(landmark_array, (-1, 3))
        return reshaped_data

    def ValidateDirOrCreate(self, path: str):
        if not exists(path):
            mkdir(path)

    def ReadImagesFromFolder(
        self,
        rootPath: str,
        saveDataAsImage: bool,
        outImagePath: str,
        csvOutPath: str,
        model_path: str,
    ):
        dir = os.listdir(rootPath)

        if saveDataAsImage:
            self.ValidateDirOrCreate(outImagePath)

        for i in range(len(dir)):
            self.ValidateDirOrCreate(csvOutPath)
            imagesFiles = os.listdir(os.path.join(rootPath, dir[i]))
            outSubPath = f"{outImagePath}/{dir[i]}"
            if saveDataAsImage:
                self.ValidateDirOrCreate(f"{outImagePath}/{dir[i]}")
            with open(f"{csvOutPath}/{dir[i]}.csv", "w") as csv_out_file:
                csv_out_writer = csv.writer(
                    csv_out_file,
                    delimiter=",",
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n",
                )
                for j in range(len(imagesFiles)):
                    imageFile = imagesFiles[j]
                    extension = imageFile.split(".")[-1]
                    filePath = realpath(f"{rootPath}/{dir[i]}/{imageFile}")
                    if extension in allowed_extensions:
                        result = self.pose_landmarker_on_image(
                            saveDataAsImage, filePath, outSubPath, model_path
                        )
                        if result is not None and len(result[0]) > 0:
                            csv_out_writer.writerow(result[0])
