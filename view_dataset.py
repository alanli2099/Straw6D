import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def draw_box_3d(ax, corners, color, text, line_thickness):
    '''Draw 3d bounding box in image using matplotlib
    corners: (8,2) array of vertices for the 3d box in following order:
        1 -------- 0
       /|         /|
      2 -------- 3 .
      | |        | |
      . 5 -------- 4
      |/         |/
      6 -------- 7
    x: 1->0, y:4->0, z:3->0
    '''
    face_idx = [[0, 1, 5, 4],
                [1, 2, 6, 5],
                [2, 3, 7, 6],
                [3, 0, 4, 7]]
    for ind_f in face_idx:
        poly = Polygon(corners[ind_f], closed=True, edgecolor=color, fill=False, linewidth=line_thickness)
        ax.add_patch(poly)
    
    # for ind_f in face_idx:
    #     poly = Polygon(corners[ind_f][:8], closed=True, edgecolor=color, fill=False, linewidth=line_thickness)
    #     ax.add_patch(poly)
        
    # Calculate and draw axes from the origin to specified directions
    # X-axis from origin to direction parallel to 1->0 in red
    # x_direction = corners[0] - corners[1] + corners[8]
    # ax.plot([corners[8][0], x_direction[0]], [corners[8][1], x_direction[1]], 'r-', linewidth=line_thickness)

    # # Y-axis from origin to direction parallel to 4->0 in green
    # y_direction = corners[0] - corners[4] + corners[8]
    # ax.plot([corners[8][0], y_direction[0]], [corners[8][1], y_direction[1]], 'g-', linewidth=line_thickness)

    # # Z-axis from origin to direction parallel to 3->0 in blue
    # z_direction = corners[0] - corners[3] + corners[8]
    # ax.plot([corners[8][0], z_direction[0]], [corners[8][1], z_direction[1]], 'b-', linewidth=line_thickness)

    # Add text label
    text_x, text_y = corners[8][0] + 5, corners[8][1] +5  # Adjust text position as needed
    ax.text(text_x, text_y, text, color=color, fontsize=6)

def euler_to_rotation(theta):
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(theta[0]), -np.sin(theta[0])],
                    [0, np.sin(theta[0]), np.cos(theta[0])]])

    R_y = np.array([[np.cos(theta[1]), 0, np.sin(theta[1])],
                    [0, 1, 0],
                    [-np.sin(theta[1]), 0, np.cos(theta[1])]])

    R_z = np.array([[np.cos(theta[2]), -np.sin(theta[2]), 0],
                    [np.sin(theta[2]), np.cos(theta[2]), 0],
                    [0, 0, 1]])

    R = np.dot(R_z, np.dot(R_y, R_x))
    return R

# Assuming these paths are correctly set up for your dataset
path = ''
imageDir = os.path.join(path, "images")
boxesDir = os.path.join(path, "boxes")

imagesPaths = sorted(os.listdir(imageDir))
boxesPaths = sorted(os.listdir(boxesDir))

imagesPaths = [os.path.join(imageDir, path) for path in imagesPaths]
boxesPaths = [os.path.join(boxesDir, path) for path in boxesPaths]

for imagePath, boxesPath in zip(imagesPaths, boxesPaths):
    image = Image.open(imagePath)
    dpi = 100
    fig, ax = plt.subplots(figsize=(800/dpi, 600/dpi), dpi=dpi)
    ax.imshow(image)
    
    with open(boxesPath) as boxesFile:
        boxesLines = boxesFile.readlines()

    del boxesLines[0]  # Assuming the first line is not needed
    for box in boxesLines:
        box = box.strip().split(',')
        label = float(box[0])
        x, y, z = float(box[1]), float(box[2]), float(box[3])
        w, h, l = float(box[4]), float(box[5]), float(box[6])
        roll, pitch, yaw = float(box[7]), float(box[8]), float(box[9])

        R = euler_to_rotation([roll, pitch, yaw])

        x_corners = [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2, 0]
        y_corners = [h / 2, h / 2, h / 2, h / 2, -h / 2, -h / 2, -h / 2, -h / 2, 0]
        z_corners = [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2, 0]

        corners = np.array([x_corners, y_corners, z_corners], dtype=np.float32)
        corners_3d = np.dot(R, corners) + np.array([x, y, z], dtype=np.float32).reshape(3, 1)
        corners_3d = corners_3d.transpose(1, 0)

        pts_2d = []
        for i in range(9):
            X, Y, Z = corners_3d[i][0], -corners_3d[i][1], -corners_3d[i][2]
            u, v = 400.32 * X / Z + 400, 400.32 * Y / Z + 300  # Assuming these are your camera parameters
            pts_2d.append([u, v])

        color, text = ('red', 'Ripe') if label == 250 else ('green', 'Unripe')
        if (0 <= pts_2d[8][0] < 800 and 0 <= pts_2d[8][1] < 600):
            draw_box_3d(ax, np.array(pts_2d).astype(np.int32), color, text, line_thickness=1.0)

    plt.axis('off')  # Hide axes
    plt.tight_layout(pad=0)  # Minimize padding
    plt.savefig('figure.png',dpi=dpi, bbox_inches='tight',pad_inches=0)
    plt.show()
    break  # Remove or modify this depending on whether you want to process more images
