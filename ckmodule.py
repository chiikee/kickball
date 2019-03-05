"""My own module to organize misc functions."""

import math
import random
import cv2
import pyglet
import pymunk
from pymunk import Vec2d

#This function is from imutils package, copying it out so that i know what it does.
def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized

#This function is from imutils package, copying it out so that i know what it does.
def grab_contours(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
                         "otherwise OpenCV changed their cv2.findContours return "
                         "signature yet again. Refer to OpenCV's documentation "
                         "in that case"))

    # return the actual contours array
    return cnts

def create_ball_sprite(x,y):
    """Modularized ball sprite creation."""
    ball_img = pyglet.resource.image('football100.png')
    ball_img.anchor_x = ball_img.width/2
    ball_img.anchor_y = ball_img.height/2

    mass = 10
    radius = ball_img.width/2

    ball_sprite = pyglet.sprite.Sprite(ball_img)
    ball_sprite.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
    ball_sprite.body.position = x, y
    ball_sprite.body.angle = random.random() * math.pi
    ball_sprite.shape = pymunk.Circle(ball_sprite.body, radius)
    ball_sprite.shape.friction = 0.5
    ball_sprite.shape.elasticity = 0.9

    return ball_sprite

def create_outer_walls(space,width,height):
    """Modularized outer wall creation."""
    static_lines = [pymunk.Segment(space.static_body, (0.0, 0.0), (width, 0.0), 0.0),
                    pymunk.Segment(space.static_body, (width, 0.0), (width, height), 0.0),
                    pymunk.Segment(space.static_body, (width, height), (0.0, height), 0.0),
                    pymunk.Segment(space.static_body, (0.0, 600.0), (0.0, 0.0), 0.0)]
    for line in static_lines:
        line.friction = 0.5
        line.elasticity = 0.9

    return static_lines

def circle_sprite_touch_rect(sprite,rect):
    radius = sprite.shape.radius
    minx = rect[0] - radius
    miny = rect[1] - radius
    maxx = rect[0] + rect[2] + radius
    maxy = rect[1] + rect[3] + radius
    spritex = sprite.body.position.x
    spritey = sprite.body.position.y
    if spritex > minx and spritex < maxx and spritey > miny and spritey < maxy:
        return True
    else:
        return False

def sprite_rect_vector(sprite,rect):
    ball_vec = Vec2d(sprite.body.position.x, sprite.body.position.y)
    rect_x = (rect[0] + rect[2])/2
    rect_y = (rect[1] + rect[3])/2
    rect_vec = Vec2d(rect_x, rect_y)
    return Vec2d.normalized(ball_vec - rect_vec)

def contour_frame_diff(curr_frame, avg_frame, delta_thresh, min_area):
    rect_list = []
    frameDelta = cv2.absdiff(curr_frame, cv2.convertScaleAbs(avg_frame))
    thresh = cv2.threshold(frameDelta, delta_thresh, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = grab_contours(cnts)
    cntssorted = sorted(cnts, key=lambda x: cv2.contourArea(x))

    for cnt in cntssorted:
        if cv2.contourArea(cnt) < min_area:
            continue
        rect_list.append(cv2.boundingRect(cnt))
        #rect_list.append(cv2.fitEllipse(cnt))
    
    return rect_list

class Collider:
    body = None
    shape = None

    def __init__(self, x, y):
        self.body = pymunk.Body(0, 0, pymunk.Body.KINEMATIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, 1.0)

    def move_to_rect(self, delta_time, rect, width_scale, height_scale):
        self.body.position = (rect[0]+rect[2]/2)*width_scale, (rect[1]+rect[3]/2)*height_scale
        #self.shape = pymunk.Circle(self.body, min(rect[2]/2*width_scale, rect[3]/2*height_scale))
        self.shape.unsafe_set_radius(min(rect[2]/2*width_scale, rect[3]/2*height_scale))
        self.shape.friction = 0.5
        self.shape.elasticity = 0.9
        #calculate new radius
        #calculate vector
        #calculate velocity

    def reset(self, index):
        self.body.position = -10.0*index, -10.0*index
        self.shape.unsafe_set_radius(1.0)
        #calculate new radius
        #calculate vector
        #calculate velocity
    

