import numpy as np
import cv2 as cv
import os
import csv

###USER DEFINED INPUTS###
poly_degree=4
lower_left_point=[-400,10]
upper_right_point=[100,60]
original_image= 'screenshots/AFML_V1_Aluminum_6061_Fsu.png'
######

image_file_name = os.path.splitext(os.path.basename(original_image))[0]
output_folder_name='Output/'

points=[]
dragging_point_index=None
def mouse_callback(event, x, y, flags, param):
    global points, dragging_point_index

    if event == cv.EVENT_LBUTTONDOWN:
        # Check if the click is close to an existing point
        for ii, point in enumerate(points):
            if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                dragging_point_index = ii
                break
        else:
            # If not close to any existing point, add a new point
            points.append((x, y))

    elif event == cv.EVENT_MOUSEMOVE:
            # Check if the mouse is moving
        if dragging_point_index is not None:
            # If dragging is performed, update the coordinates
            points[dragging_point_index] = (x, y)

    elif event == cv.EVENT_LBUTTONUP:
            # If clicking is not performed, stop dragging and updating the coordinates
        dragging_point_index = None
    
    elif event == cv.EVENT_RBUTTONDOWN:
        # Check if the right-click is close to an existing point
        for i, point in enumerate(points):
            if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                # Remove the point
                points.pop(i)
                break

def draw_points(img, points: list):
    #Drawing circles at the selected points
    for pp in points:
        cv.circle(img, pp, 5, (0, 0, 255), -1)

# Reading and opening the original image
img=cv.imread(original_image)
cv.imshow('Original Image',img)
cv.setMouseCallback('Original Image',mouse_callback)

while True:
    # Copy the image to display points
    img_copy = img.copy()
    draw_points(img_copy, points)
    # Display the image
    cv.imshow('Original Image', img_copy)
    if cv.waitKey(1) != -1:
        break
# Converting points' coordinates from pixels to real coordinate values
hor_scale=abs(upper_right_point[0]-lower_left_point[0])
ver_scale=abs(upper_right_point[1]-lower_left_point[1])
horizontal_margin=hor_scale/abs(points[1][0]-points[0][0])
vertical_margin=ver_scale/abs(points[0][1]-points[1][1])
new_points=[]
for i in range(len(points)):
    new_point=(horizontal_margin*(points[i][0]-points[0][0])+lower_left_point[0],vertical_margin*(points[0][1]-points[i][1])+lower_left_point[1])
    new_points.append((new_point))
print("Selected points:",new_points)

#Producing the polynomial fit
xc=[pair[0] for pair in new_points]
yc=[pair[1] for pair in new_points]
poly_coeff=np.polyfit(xc[2:],yc[2:],poly_degree)
print("Polynomial Fit Coefficients:", poly_coeff)
poly_func=np.poly1d(poly_coeff) #POLYFIT FUNCTION TO BE USED FOR DESIRED VALUES
#print("Value at 1000 is:", poly_func(1000))

#Plotting the curve fit and selected points
x_plot_points=np.linspace(min(xc),max(xc),100)
y_plot_points=poly_func(x_plot_points)
x_plot_points=x_plot_points[(y_plot_points>=min(yc))&(y_plot_points<=max(yc))]
y_plot_points=y_plot_points[(y_plot_points>=min(yc))&(y_plot_points<=max(yc))]

x_pixels=(x_plot_points-lower_left_point[0])/horizontal_margin+points[0][0]
y_pixels=-((y_plot_points-lower_left_point[1])/vertical_margin-points[0][1])
x_pixels=x_pixels.astype(np.int32)
y_pixels=y_pixels.astype(np.int32)
img2=cv.imread(original_image)
for i in range(len(x_pixels)-1):
    cv.line(img2,(x_pixels[i],y_pixels[i]),(x_pixels[i+1],y_pixels[i+1]),(0,255,0),2)

for point in points[2:]:
    cv.circle(img2,(point),5,(0,0,255),-1)
cv.imshow('Curve Fit',img2)
cv.waitKey(0)

#Saving the image with a curve fit, coordinates of the selected points and coefficients of the polynomial
os.makedirs(output_folder_name, exist_ok=True)
image_output = os.path.join(output_folder_name, f"{image_file_name}_curve_fit.png")
cv.imwrite(image_output, img2)

csv_file_name_coefficients = os.path.join(output_folder_name, f"{image_file_name}_coefficients.csv")
with open(csv_file_name_coefficients,mode='w',newline='') as file_to_be_opened:
    writer=csv.writer(file_to_be_opened)
    writer.writerow(['degree:',poly_degree])

    coeff_count=poly_degree
    for coefficients in poly_coeff:
        writer.writerow([f"coeff {coeff_count}",coefficients])
        coeff_count-=1

csv_file_name_points = os.path.join(output_folder_name, f"{image_file_name}_points.csv")
with open(csv_file_name_points,mode='w',newline='') as file:
    writer=csv.writer(file)
    writer.writerow(['x','y'])

    for xi,yi in zip(xc[2:],yc[2:]):
        writer.writerow([xi,yi])