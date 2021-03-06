import cv2
from tkinter import *
import numpy as np
import json
from math import pi, atan2

# Create a settings window
settings_window = Tk()

# Set a title for the settings window
settings_window.title("Settings")

hsv_option = StringVar(settings_window)  # set a variable for the pick from the option menu
hsv_option.set("default")  # set the default option for the option menu

data_to_show_option = StringVar(settings_window)  # set a variable for the pick from the option menu
data_to_show_option.set("Angle")  # set the default option for the option menu

hsv_option_menu = OptionMenu(settings_window, hsv_option, "default", "saved", "fuel") # Create an option menu
hsv_option_menu.pack()


data_to_show_option_menu = OptionMenu(settings_window, data_to_show_option, "Angle", "Distance") # Create an option menu
data_to_show_option_menu.pack()


# Create a dictionary for the HSV default values
hsv = {'ilowH': 0, 'ihighH': 179, 'ilowS': 0, 'ihighS': 255, 'ilowV': 0, 'ihighV': 255} #

# get HSV saved values
settings_file = open("settings.txt", "r+")
hsv_saved_settings = eval(settings_file.read())


def set_hsv_values():  # read hsv settings from the settings file

    print(hsv_option.get())
    option = hsv_option.get()
    global hsv

    if hsv_saved_settings is not '':

        if option == "default":

            hsv = {'ilowH': 0, 'ihighH': 179, 'ilowS': 0, 'ihighS': 255, 'ilowV': 0, 'ihighV': 255}

        elif option == "saved":

            hsv = hsv_saved_settings

        elif option == "fuel":

            hsv = {'ilowH': 10, 'ihighH': 43, 'ilowS': 145, 'ihighS': 255, 'ilowV': 147, 'ihighV': 255}

    else:

        if option == "default":

            hsv = {'ilowH': 0, 'ihighH': 179, 'ilowS': 0, 'ihighS': 255, 'ilowV': 0, 'ihighV': 255}

        elif option == "fuel":

            hsv = {'ilowH': 10, 'ihighH': 43, 'ilowS': 145, 'ihighS': 255, 'ilowV': 147, 'ihighV': 255}

    cv2.setTrackbarPos('lowH', 'image', hsv['ilowH'])
    cv2.setTrackbarPos('highH', 'image', hsv['ihighH'])
    cv2.setTrackbarPos('lowS', 'image', hsv['ilowS'])
    cv2.setTrackbarPos('highS', 'image', hsv['ihighS'])
    cv2.setTrackbarPos('lowV', 'image', hsv['ilowV'])
    cv2.setTrackbarPos('highV', 'image', hsv['ihighV'])


change_button = Button(settings_window, text="change", command=set_hsv_values)
change_button.pack()

# put -1/0/1 in VideoCapture()
cap = cv2.VideoCapture(1)
cv2.namedWindow('image')


def callback(x):
    pass


# count the amount of balls
counter = 0

# create trackbars for color change
cv2.createTrackbar('lowH', 'image', hsv['ilowH'], 179, callback)
cv2.createTrackbar('highH', 'image', hsv['ihighH'], 179, callback)

cv2.createTrackbar('lowS', 'image', hsv['ilowS'], 255, callback)
cv2.createTrackbar('highS', 'image', hsv['ihighS'], 255, callback)

cv2.createTrackbar('lowV', 'image', hsv['ilowV'], 255, callback)
cv2.createTrackbar('highV', 'image', hsv['ihighV'], 255, callback)


while True:

    ret, frame = cap.read()
    original = frame.copy()
    # grab the frame
    frame = original.copy()

    # get trackbars position
    hsv['ilowH'] = cv2.getTrackbarPos('lowH', 'image')
    hsv['ihighH'] = cv2.getTrackbarPos('highH', 'image')
    hsv['ilowS'] = cv2.getTrackbarPos('lowS', 'image')
    hsv['ihighS'] = cv2.getTrackbarPos('highS', 'image')
    hsv['ilowV'] = cv2.getTrackbarPos('lowV', 'image')
    hsv['ihighV'] = cv2.getTrackbarPos('highV', 'image')

    # save HSV dictionary as a txt file
    with open('settings.txt', 'w') as settings:
        json.dump(hsv, settings)

    # get "mode" trackbar position
    mode = data_to_show_option.get()

    # create a mask
    hsv_colors = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([hsv['ilowH'], hsv['ilowS'], hsv['ilowV']])
    higher_hsv = np.array([hsv['ihighH'], hsv['ihighS'], hsv['ihighV']])
    mask = cv2.inRange(hsv_colors, lower_hsv, higher_hsv)

    frame = cv2.bitwise_and(frame, frame, mask=mask)

    # create a cross kernel
    kernel = np.array([[0, 1, 0],
                       [1, 1, 1],
                       [0, 1, 0]],
                      dtype=np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    ret, mask = cv2.threshold(mask, 127, 255, 0)

    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours is not None:
        for cnt in contours:
            if len(cnt) > 50:

                x, y, w, h = cv2.boundingRect(cnt)
                ratio = w / h

                area_circle_from_rect = pi * ((w / 2) ** 2)

                (a, b), radius = cv2.minEnclosingCircle(cnt)
                center = (int(a), int(b))

                area_circle = pi * (radius ** 2)

                area_ratio = area_circle / area_circle_from_rect

                if 0.75 < ratio < 1.25 and 0.75 < area_ratio < 1.25 and radius > 5:
                    cv2.circle(original, center, int(radius), (255, 255, 0), 5)
                    # cv2.rectangle(original, (x, y), (x + w, y + h), (255, 255, 0), 2)
                    counter += 1
                    (xtarget, y), _ = cv2.minEnclosingCircle(cnt)
                    xframe = frame.shape[1] / 2

                    # focal calculator
                    object_distance_from_camera = 10  # in cm
                    object_width = 12  # in cm
                    object_width_pixels = 60  # in pixels

                    # known focals
                    calc_focal = (object_width_pixels * object_distance_from_camera) / object_width
                    note8_focal = 538.5826771653543
                    yoga_focal = 540

                    # set which focal to use
                    f = yoga_focal

                    # find the angle and the  distance from the object
                    angle = atan2((xtarget - xframe), f) * (180 / pi)
                    distance = (f * 12.7) / (2 * radius)

                    # choose what to display according to the trackbar data
                    if mode == "Distance":
                        data = distance
                    elif mode == "Angle":
                        data = angle

                    cv2.putText(original, str(int(data)), (int(x), int(y + 2 * radius)), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                (0, 0, 0), 3)

    # show thresholded image
    cv2.putText(original, "Fuels: " + str(counter), (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imshow('mask', frame)
    cv2.imshow('original', original)
    counter = 0
    k = cv2.waitKey(1) & 0xFF  # large wait time to remove freezing
    if k == 113 or k == 27:
        settings_window.destroy()
        break
    else:
        settings_window.update_idletasks()
        settings_window.update()

