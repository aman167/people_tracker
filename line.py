import cv2
import numpy as np
import torch
def get_coordinates(video_path):
    """
    Asks the user to select two points in a video to define a counting line.

    The user is shown the first frame of the video, and can move the mouse to see
    the coordinates of the mouse position displayed in real time. The user can
    click on two points to select them as the start and end points of the counting
    line. The points are stored in a list, and the line is drawn on the frame in
    real time.

    The function returns the list of two coordinates if the user successfully
    selects two points, or None if the user quits or resets the points without
    selecting two points.

    Parameters:
    video_path : str
        The path to the video file to read.

    Returns:
    coordinates : list of two tuples
        The start and end points of the counting line, or None if no points were
        selected.
    """

    coordinates = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            # here we are displaying coordinates 
            frame_copy = frame.copy()
            cv2.putText(frame_copy, f'Coordinates: ({x}, {y})', (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Get Coordinates', frame_copy)
        
        elif event == cv2.EVENT_LBUTTONDOWN:
            # Store coordinates when left mouse button is clicked
            coordinates.append((x, y))
            print(f'Point {len(coordinates)} selected: ({x}, {y})')
            
            # Draw points
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Get Coordinates', frame)
            
            # If we have 2 points, draw the line
            if len(coordinates) == 2:
                cv2.line(frame, coordinates[0], coordinates[1], (0, 255, 0), 2)
                cv2.imshow('Get Coordinates', frame)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Could not open video")
        return None
    
    #first frame
    ret, frame = cap.read()
    if not ret:
        print("Could not read frame")
        return None
    
    cv2.namedWindow('Get Coordinates')
    cv2.setMouseCallback('Get Coordinates', mouse_callback)
    
    print("Click two points to define your entering line.")
    print("Press 'r' to reset points.")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        # Quit
        if key == ord('q'):
            break
        # Reset pointsbutton
        elif key == ord('r'):
            coordinates = []
            ret, frame = cap.read()
            cv2.imshow('Get Coordinates', frame)
            print("Points reset. Select new points.")
    
        # If we have 2 points, we're done
        if len(coordinates) == 2:
            print("Line coordinates selected:")
            print(f"Point 1: {coordinates[0]}")
            print(f"Point 2: {coordinates[1]}")
            cv2.waitKey(2000)  # Show final line for 1 second
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    return coordinates if len(coordinates) == 2 else None

print("Coordinate capture function defined.")
print("Move mouse to see coordinates")
print("Click to set points")
print("Press 'r' to reset points")

def get_inside_outside(video_path, line_coordinates):
    """
    Asks the user to select a point inside the shop area.

    The user is shown the first frame of the video, and can move the mouse to see
    the coordinates of the mouse position displayed in real time. The user can
    click on a point to select it as the inside area. The point is stored in a
    variable, and the point is drawn on the frame in real time.

    The function returns the side of the line that the point is on, relative to the
    line defined by the two points passed in. This is used to determine the
    reference side of the line.

    Parameters:
    video_path : str
        The path to the video file to read.
    line_coordinates : list of two tuples
        The start and end points of the counting line.

    Returns:
    inside_side : int
        The side of the line that the inside point is on, relative to the line.
        This is either 1 (right side) or -1 (left side), or None if no point was
        selected.
    """
    def get_side_of_line(point, line_start, line_end):
        return np.sign((line_end[0] - line_start[0]) * (point[1] - line_start[1]) - 
                      (line_end[1] - line_start[1]) * (point[0] - line_start[0]))
    
    inside_point = None
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal inside_point
        if event == cv2.EVENT_MOUSEMOVE:
            frame_copy = frame.copy()
            cv2.line(frame_copy, line_coordinates[0], line_coordinates[1], (0, 255, 0), 2)
            cv2.putText(frame_copy, f'Position: ({x}, {y})', (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Select Inside Area', frame_copy)
        
        elif event == cv2.EVENT_LBUTTONDOWN:
            inside_point = (x, y)
            print(f'Inside area selected at: ({x}, {y})')
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(frame, 'INSIDE', (x+10, y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Select Inside Area', frame)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Could not open video")
        return None
    
    ret, frame = cap.read()
    if not ret:
        print("Could not read frame")
        return None
    
    cv2.namedWindow('Select Inside Area')
    cv2.setMouseCallback('Select Inside Area', mouse_callback)
    
    # Draw the line
    cv2.line(frame, line_coordinates[0], line_coordinates[1], (0, 255, 0), 2)
    
    print("Click on the INSIDE area of the shop")
    print("Press 'q' when done, 'r' to reset")
    
    while True:
        cv2.imshow('Select Inside Area', frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') and inside_point is not None:
            break
        elif key == ord('r'):
            inside_point = None
            ret, frame = cap.read()
            cv2.line(frame, line_coordinates[0], line_coordinates[1], (0, 255, 0), 2)
            print("Reset selection. Click on the INSIDE area.")
    
    cap.release()
    cv2.destroyAllWindows()
    
    if inside_point is None:
        return None
    
    # Determine the inside
    inside_side = get_side_of_line(inside_point, line_coordinates[0], line_coordinates[1])
    return inside_side