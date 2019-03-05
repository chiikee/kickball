"""Show a ball and try to move it with the webcam."""

__version__ = "$Id:$"
__docformat__ = "reStructuredText"

import math
import random
import json
#import datetime
import sys

import cv2
import pyglet
from pyglet.window import key
import pymunk
import pymunk.pyglet_util
from pymunk import Vec2d

import ckmodule

CONF = json.load(open("conf.json"))

avg = None
LONG_TERM_BUFFER = None
cap = cv2.VideoCapture(0)
FRAME_DIM = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Camera Capture Resolution",FRAME_DIM)
rect_list = []

window = pyglet.window.Window(width=640, height=360)
fps_display = pyglet.clock.ClockDisplay()
ball_sprite = ckmodule.create_ball_sprite(window.width/2, window.height/2)
draw_options = pymunk.pyglet_util.DrawOptions()

PADDING = math.sqrt(CONF["min_area"])
PADDED_WIDTH = window.width + PADDING * 2
PADDED_HEIGHT = window.height + PADDING * 2
SHIFT_SCALE = (-PADDING, -PADDING, PADDED_WIDTH/FRAME_DIM[0], PADDED_HEIGHT/FRAME_DIM[1])
CAM_FLIP_X = True
CAM_FLIP_Y = True

### Physics stuff
space = pymunk.Space()
space.damping = 0.9

### Static line
static_lines = ckmodule.create_outer_walls(space, window.width, window.height)

### Static Colliders
# colliders = []
# for index in range(1,5):
#     colliders.append(ckmodule.Collider(-10*index,-10*index))

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.P:
        pyglet.image.get_buffer_manager().get_color_buffer().save('kickball.png')
    elif symbol == key.ESCAPE:
        cap.release()
        cv2.destroyAllWindows()
        sys.exit()

@window.event
def on_draw():
    window.clear()

    fps_display.draw()

    for line in static_lines:
        body = line.body

        pv1 = body.position + line.a.rotated(body.angle)
        pv2 = body.position + line.b.rotated(body.angle)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                             ('v2f', (pv1.x, pv1.y, pv2.x, pv2.y)),
                             ('c3f', (.8, .8, .8)*2)
                             )

    ball_sprite.draw()

    for rect in rect_list:
        pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
                             ('v2f', (rect[0], rect[1], 
                                      rect[0]+rect[2], rect[1],
                                      rect[0]+rect[2], rect[1]+rect[3],
                                      rect[0], rect[1]+rect[3])),
                             ('c3f', (.8, .8, .8, .8, .8, .8, .8, .8, .8, .8, .8, .8,))
                             )

    space.debug_draw(draw_options)

def shift_colliders(colliders, rects):
    i = 1
    for collider in colliders:
        if len(rects) > i:
            #update collider
            pass
        else:
            pass 
        i = i + 1

def update(dt):
    dt = 1.0/60. #override dt to keep physics simulation stable
    #step the simulation
    space.step(dt)
    #update the sprite to match the new physics simulation
    ball_sprite.rotation = math.degrees(-ball_sprite.body.angle)+180
    ball_sprite.set_position(ball_sprite.body.position.x, ball_sprite.body.position.y)

def kick_ball(dt):
    impulse = 10000 * Vec2d(1,0)
    impulse.rotate_degrees(random.randint(0,360))
    ball_sprite.body.apply_impulse_at_local_point(impulse)

def kick_ball_cv(dt):
    global avg, rect_list, FRAME_DIM, LONG_TERM_BUFFER

    rect_list = []
    ret, frame = cap.read()
    frame = ckmodule.resize(frame, width=640)
    if CAM_FLIP_X:
        frame = cv2.flip(frame, 1)
    if CAM_FLIP_Y:
        frame = cv2.flip(frame, 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        LONG_TERM_BUFFER = gray.copy().astype("float")
    else:
        cv2.accumulateWeighted(gray, avg, 0.5)
        rect_list = ckmodule.contour_frame_diff(gray, avg, CONF["delta_thresh"], CONF["min_area"])

        for rect in rect_list:
            #fix rect position
            shift_rect = ((rect[0] * SHIFT_SCALE[2]) + SHIFT_SCALE[0],
                          (rect[1] * SHIFT_SCALE[3]) + SHIFT_SCALE[1],
                          rect[2] * SHIFT_SCALE[2],
                          rect[3] * SHIFT_SCALE[3])
            if ckmodule.circle_sprite_touch_rect(ball_sprite, shift_rect):
                ball_sprite.body.apply_impulse_at_local_point(ckmodule.sprite_rect_vector(ball_sprite, shift_rect) * 1000)

        cv2.accumulateWeighted(gray, LONG_TERM_BUFFER, 0.001)
        rect_list = ckmodule.contour_frame_diff(gray, LONG_TERM_BUFFER, CONF["delta_thresh"], CONF["min_area"])

        # count = 0
        # for collider in colliders:
        #     len_of_rect = len(rect_list)
        #     if len_of_rect > 0 and count < len_of_rect:
        #         (h, w) = frame.shape[:2]
        #         collider.move_to_rect(dt, rect_list[count], window.width/w, window.height/h)
        #     else:
        #         collider.reset(count+1)
        #         pass
        #     count = count + 1

def main():    
    space.add(ball_sprite.body, ball_sprite.shape)
    space.add(static_lines)
    # for collider in colliders:
    #     space.add(collider.body, collider.shape)

    pyglet.clock.schedule_interval(update, 1/60.0)
    #pyglet.clock.schedule_interval(kick_ball, 10/6.0)
    pyglet.clock.schedule_interval(kick_ball_cv, 1/30.0)
    pyglet.app.run()

if __name__ == "__main__":
    main()
