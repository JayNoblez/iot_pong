
#!/usr/bin/env python3

from time import sleep
import paho.mqtt.client as mqtt
from pixel_art import PixelArt

# Import the fake sense hat module if available
# We do this because we need a pong game to run on non-raspberry devices 
# (using a Tkinter interface) to use it as a debugging platform and because
# sometimes a pi is not available
# If the "fake" module is not found, just import the normal API to se SenseHat
try:
    from fake_sense_hat import SenseHat
except ImportError:
    from sense_hat import SenseHat
    pass

DEBUG_WALLS = False

class Vector_2d(object):
    """Dead simple 2D vector class"""
    x = 0;
    y = 0;

class Ball:
    """ Class that implements the Pong ball"""
    def __init__(self, init_velocity_x, init_velocity_y, hat):
        """Set ball to inital values"""
        self.position = Vector_2d()
        self.velocity = Vector_2d()
        self.velocity.x = init_velocity_x
        self.velocity.y = init_velocity_y
        self.init_velocity_x = init_velocity_x
        self.init_velocity_y = init_velocity_y
        self.position.x = 7
        self.position.y = 3
        self.deflection = 1
        self.hat = hat

    def reinit(self):
        """Re-initialise the ball to the default location"""
        self.velocity.x = self.init_velocity_x
        self.velocity.y = self.init_velocity_y
        self.position.x = 7
        self.position.y = 3
        self.deflection = 1

    def set(self, x_pos, y_pos, x_vel, y_vel):
        self.position.x = x_pos
        self.position.y = y_pos
        self.velocity.x = x_vel
        self.velocity.y = y_vel

    def draw(self):
        self.hat.set_pixel(int(self.position.x), int(self.position.y), 100, 100, 100)

    def move(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

class Paddle():
    def __init__(self, height, hand, hat):
        self.position = Vector_2d()
        self.position.x = 0
        self.position.y = 7
        self.height = height
        self.hand = hand
        self.hat = hat

    def draw(self):
        for pixel in range(self.position.y - self.height, self.position.y):
            self.hat.set_pixel(int(self.position.x), int(pixel), 100, 100, 100)

    def move(self, hat):
        for event in hat.stick.get_events():
            if event.direction == "up":
                self.position.y += 1
            elif event.direction == "down":
                self.position.y -= 1

        if self.position.y - self.height < 0:
            self.position.y  += 1
            print("Paddle limit UP")
        elif self.position.y > 8:
            self.position.y  -= 1
            print("Paddle limit DOWN")

def intra_object_collision_detection(ball, paddle):
    score = False

    if (frange(ball.position.y, paddle.position.y - paddle.height, paddle.position.y)) and (ball.position.x <= 1):
        print("PADDLE COLLISION")
        ball.velocity.x = -ball.velocity.x
    
    elif ball.position.x <= 1:
        print("SCORE")
        score = True 
    elif ball.position.x >= 7:
        print("WALL COLLISION")
        ball.velocity.x = -ball.velocity.x
        return score, True
    
    if not frange(ball.position.y, 0, 7):
        print("SIDEWALL COLLISION")
        ball.velocity.y = -ball.velocity.y

    ball.position.x = realign(ball.position.x, 0, 7)
    ball.position.y = realign(ball.position.y, 0, 7)
    paddle.position.x = realign(paddle.position.x, 0, 7)
    paddle.position.y = realign(paddle.position.y, paddle.height, 7)
    return score, False
    
def realign(value, range_min, range_max):
    if value >= range_max:
        value = range_max
    if value <= range_min:
        value = range_min

    return value

def frange(value, range_min, range_max):
    if (value < range_min) or (value > range_max):
        return False
    return True

def fill_color(hat, color):
    hat.set_pixels([color] * 8 * 8)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("thm_rr_iot_project/#")
    client.connected_flag = True

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    if msg.topic == "thm_rr_iot_project/game" and msg.payload.decode("utf-8") == "new":
        client.new_game_flag = True

    if msg.topic == "thm_rr_iot_project/pass":
        if msg.payload.decode("utf-8") != "":
            client.pass_received_flag = True
            client.initiated, client.pass_value_pos_x, client.pass_value_pos_y, client.pass_value_vel_x, client.pass_value_vel_y = pass_ball_string_decode(msg.payload.decode("utf-8"))

def pass_ball_string(ball, initiator):
    return str(int(initiator)) + "," + str(ball.position.x) + "," + str(ball.position.y) + "," + str(ball.velocity.x) + "," + str(ball.velocity.y)

def pass_ball_string_decode(string):
    print(str(tuple(map(float, string.split(',')))))
    return tuple(map(float, string.split(',')))

def new_game(client, fade):
    hat.set_pixels(pa.fade(pa.make_up_arror(), fade))

    # Client initiated game
    if client.new_game_flag:
        # Reset flag
        client.publish("thm_rr_iot_project/game", payload="")
        return True, False

    for event in hat.stick.get_events():
        if event.direction == "up":
            client.publish("thm_rr_iot_project/game", payload="new")
            return True, True
    return False, False

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connected_flag = False
client.new_game_flag = False
client.pass_received_flag = False

client.initiated = 0
client.pass_value_pos_x = 0
client.pass_value_pos_y = 0
client.pass_value_vel_x = 0
client.pass_value_vel_y = 0

client.connect("iot.eclipse.org", 1883, 60)
client.loop_start()

pa = PixelArt()

hat = SenseHat()

ball = Ball(-1, 0.5, hat)
paddle = Paddle(3, 0, hat)
next_stage = "wait_wait_for_connection"
initiator = False

i = 0;
while True:
    i += 1
    if i == 100:
        i = 0

    print("next_stage: " + next_stage)

    if next_stage == "wait_wait_for_connection":
        hat.set_pixels(pa.fade(pa.loading(), i/100))

        if client.connected_flag:
            next_stage = "new_game"

    elif next_stage == "score":
        fill_color(hat, [255, 0, 0])
        for wait in range(2):
            sleep(1)
        ball.reinit()
        next_stage = "play"

    elif next_stage == "new_game":
        new_game_started, initiator = new_game(client, i/100)

        if new_game_started:
            if initiator:
                next_stage = "play"
            else:
                next_stage = "wait_for_ball"

    elif next_stage == "wait_for_ball":
        if client.pass_received_flag:
            client.pass_received_flag = False
            if client.initiated != initiator:
                ball.set(client.pass_value_pos_x, client.pass_value_pos_y, client.pass_value_vel_x, client.pass_value_vel_y)
                next_stage = "play"

        fill_color(hat, [0, 0, 0])
        paddle.move(hat)
        paddle.draw()

    elif next_stage == "play":
        fill_color(hat, [0, 0, 0])
   
        ball.move()
        paddle.move(hat)

        score, court_change = intra_object_collision_detection(ball, paddle)
        
        if score:
            next_stage = "score"

        if court_change:
            client.publish("thm_rr_iot_project/pass", payload=pass_ball_string(ball, initiator))
            next_stage = "wait_for_ball"
        
        ball.draw()
        paddle.draw()

    sleep(0.10)
