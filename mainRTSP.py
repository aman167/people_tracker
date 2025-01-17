import cv2
import numpy as np
from ultralytics import YOLO
import torch
import time  
from line import get_coordinates, get_inside_outside

def count_people_video(video_path, line_coordinates=None):
    '''
    This function is used to calculate the number of people 
    entering and exiting a shop based on a line drawn on the video.
    
    Parameters:
    video_path (str): The path to the video file.
    line_coordinates (tuple): The coordinates of the line drawn on the video.
    
    Returns:
    None
    '''
    if line_coordinates is None:
        line_coordinates = get_coordinates(video_path)
        if line_coordinates is None:
            print("No line coordinates provided")
            return
    
    inside_side = get_inside_outside(video_path, line_coordinates)
    if inside_side is None:
        print("Inside area not selected")
        return
    
    model = YOLO('yolo11s.pt')
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Could not open video file: {video_path}")
        return
    
    entering = 0  # to store the number of people entering
    exiting = 0 #to sotre the number of people exiting
    people_tracks = {}  # Dictionary to store the tracks of people
    
    def get_side_of_line(point, line_start, line_end):
        """
        calculate the relative position of a center of bounding box
        with respect to a directed line segment.

        Parameters:
        point (tuple): The (x, y) coordinates of the point.
        line_start (tuple): The (x, y) coordinates of the starting point of the line segment.
        line_end (tuple): The (x, y) coordinates of the ending point of the line segment.

        Returns:
        int: A positive value if the point is on one side of the line, a negative value if it is on the other side,
        and zero if the point lies exactly on the line.
        """

        return np.sign((line_end[0] - line_start[0]) * (point[1] - line_start[1]) - 
                      (line_end[1] - line_start[1]) * (point[0] - line_start[0]))
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video file.")
                break
            
            cv2.line(frame, line_coordinates[0], line_coordinates[1], (0, 255, 0), 2)
            
            with torch.no_grad():
                results = model.track(frame, persist=True, classes=0,conf=0.5, device='cpu')
                
            
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None and boxes.id is not None:
                    xyxy = boxes.xyxy.cpu().numpy()
                    track_ids = boxes.id.cpu().numpy().astype(int)
                    
                    for box, track_id in zip(xyxy, track_ids):
                        center_x = (box[0] + box[2]) / 2
                        center_y = (box[1] + box[3]) / 2
                        center_point = (int(center_x), int(center_y))
                        
                        if track_id not in people_tracks:
                            people_tracks[track_id] = center_point
                        else:
                            prev_point = people_tracks[track_id]
                            
                            prev_side = get_side_of_line(prev_point, line_coordinates[0], line_coordinates[1])
                            curr_side = get_side_of_line(center_point, line_coordinates[0], line_coordinates[1])
                            
                            if prev_side != curr_side:          # Line crossed
                                if curr_side == inside_side:    # going inside
                                    entering += 1
                                else:                           #going outside
                                    exiting += 1
                            
                            people_tracks[track_id] = center_point
                        
                        cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                        
                        cv2.putText(frame, f"ID: {track_id}", (int(box[0]), int(box[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.circle(frame, center_point, 4, (0, 0, 255), -1)
            
            cv2.putText(frame, f"Entering: {entering}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Exiting: {exiting}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            total = entering + exiting
            cv2.putText(frame, f"Total: {total}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("People Counter", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error processing video: {str(e)}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
        print(f"Entering: {entering}")
        print(f"Exiting: {exiting}")
        print(f"Total: {entering + exiting}")

# The program will now open 3 windows:
# Window 1: draw the enterence line
# Window 2: click on the INSIDE area of the shop
# Window 3: Start counting based on your selections

count_people_video("people.avi")
#count_people_video("  --  add the RTSP link  --  ")