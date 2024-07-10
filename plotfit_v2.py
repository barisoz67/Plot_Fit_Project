import numpy as np
#import matplotlib.pyplot as plt
import cv2 as cv

points=[]
dragging_point_index=None
def mouse_callback(event, x, y, flags, param):
    global points, dragging_point_index

    if event == cv.EVENT_LBUTTONDOWN:
        # Check if the click is close to an existing point
        for i, point in enumerate(points):
            if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                dragging_point_index = i
                break
        else:
            # If not close to any existing point, add a new point
            points.append((x, y))
        #print("Left button down at:", (x, y))

    elif event == cv.EVENT_MOUSEMOVE:
        if dragging_point_index is not None:
            points[dragging_point_index] = (x, y)

    elif event == cv.EVENT_LBUTTONUP:
        dragging_point_index = None
    
    elif event == cv.EVENT_RBUTTONDOWN:
        # Check if the right-click is close to an existing point
        for i, point in enumerate(points):
            if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                # Remove the point
                points.pop(i)
                print("Right button down at:", (x, y), "- Point removed:", point)
                break

def draw_points(img, points):
    for point in points:
        cv.circle(img, point, 5, (0, 0, 255), -1)

img=cv.imread('Photos/Plot1.png') #CUSTOM
cv.imshow('Image',img)
cv.setMouseCallback('Image',mouse_callback)

while True:
    # Copy the image to display points
    img_copy = img.copy()
    draw_points(img_copy, points)
    # Display the image
    cv.imshow('Image', img_copy)
    if cv.waitKey(1) != -1:
        break

print("Selected points:",points)

offset1=[0,10] #CUSTOM
offset2=[1000,14] #CUSTOM
hor_scale=offset2[0]-offset1[0]
ver_scale=offset2[1]-offset1[1]
horizontal_margin=hor_scale/(points[1][0]-points[0][0])
vertical_margin=ver_scale/(points[0][1]-points[1][1])
new_points=[]
for i in range(len(points)):
    new_point=(horizontal_margin*(points[i][0]-points[0][0])+offset1[0],vertical_margin*(points[0][1]-points[i][1])+offset1[1])
    new_points.append((new_point))
print("New Selected points:",new_points)

rem_points=new_points[2:]
xc=[pair[0] for pair in rem_points]
yc=[pair[1] for pair in rem_points]

poly_degree=3 #CUSTOM
poly_coeff=np.polyfit(xc,yc,poly_degree)
poly_func=np.poly1d(poly_coeff) #POLYFIT FUNCTION TO BE USED FOR DESIRED VALUES
#print("Value at 1000 is:", poly_func(1000))
x_plot_points=np.linspace(offset1[0],offset2[0],100)
y_plot_points=poly_func(x_plot_points)
x_pixels=(x_plot_points-offset1[0])/horizontal_margin+points[0][0]
y_pixels=-((y_plot_points-offset1[1])/vertical_margin-points[0][1])
x_pixels=x_pixels.astype(np.int32)
y_pixels=y_pixels.astype(np.int32)
img2=cv.imread('Photos/Plot1.png')
for i in range(len(x_pixels)-1):
    cv.line(img2,(x_pixels[i],y_pixels[i]),(x_pixels[i+1],y_pixels[i+1]),(0,255,0),2)

for point in points[2:]:
    cv.circle(img2,(point),5,(0,0,255),-1)
cv.imshow('Curve Fit',img2)
cv.waitKey(0)