import cv2
import pygame
from rover import RoverShell
from pygame.locals import *
from time import sleep
from datetime import date
from random import choice
from string import ascii_lowercase, ascii_uppercase
import cStringIO
import qrtools
import numpy as np

#https://github.com/circleupx/RALVINN2.0/commit/6976987d3cbd0183641eea8059f090a4f41bbed9

def create_opencv_image_from_stringio(img_stream, cv2_img_flag=1):
    img_stream.seek(0)
    img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2_img_flag)


def cvimage_to_pygame(image):
    new_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return pygame.image.frombuffer(new_image.tostring(), new_image.shape[1::-1], "RGB")


class RoverControl():
    def __init__(self):
        pygame.init()
        pygame.display.init()

        self.quit = False
        self.rover = RoverShell()
        self.fps = 48
        self.windowSize = [290, 230]
        self.imageRect = (0, 0, 320, 240)
        self.displayCaption = "RALVINN CAMERA"

        pygame.display.set_caption(self.displayCaption)

        print "Battery: " + str(self.rover.getBatteryPercentage())

        self.screen = pygame.display.set_mode(self.windowSize)
        self.clock = pygame.time.Clock()
        self.run()

    def run(self):
        sleep(1.5)
        while not self.quit:
            self.update_rover_state()
            self.resfresh_video_feed()
            self.qr_code()
        self.rover.quit = True
        pygame.quit()

    def resfresh_video_feed(self):

        """

        """
        self.rover.lock.acquire()
        image = self.rover.currentImage
        self.rover.lock.release()

        cv_image = create_opencv_image_from_stringio(cStringIO.StringIO(image))
        image = cvimage_to_pygame(cv_image)

        # Save the array of bytes into an image file named qr.png
        fname = 'qrimage.png'
        fd = open(fname, 'w')
        fd.write(str(self.rover.currentImage))
        fd.close()

        self.screen.blit(image, (0, 0))
        # Show image array over PyGame display
        pygame.display.update(self.imageRect)

        self.clock.tick(self.fps)

    @staticmethod
    def qr_code():
        # decode the qr image.
        qr = qrtools.QR()
        if qr.decode('qr.png'):
            print qr.data
        else:
            pass

    def update_rover_state(self):
        """

        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True
            elif event.type == KEYDOWN:
                if event.key in (K_j, K_k, K_SPACE, K_u, K_i, K_o):
                    self.updatePeripherals(event.key)
                elif event.key in (K_w, K_a, K_s, K_d, K_q, K_e, K_z, K_c, K_r, K_l):
                    self.updateTreads(event.key)
                else:
                    pass
            elif event.type == KEYUP:
                if event.key in (K_w, K_a, K_s, K_d, K_q, K_e, K_z, K_c, K_r, K_l):
                    self.updateTreads()
                elif event.key in (K_j, K_k):
                    self.updatePeripherals()
                else:
                    pass
            else:
                pass

    def takepicure(self):
        """

        """
        with open(self.newpicturename, 'w') as pic:
            self.rover.lock.acquire()
            pic.write(self.rover.currentImage)
            self.rover.lock.release()

    @property
    def newpicturename(self):
        """

        :return:
        """
        todaysDate = str(date.today())
        uniquekey = ''.join(choice(ascii_lowercase + ascii_uppercase))
        for _ in range(4):
            return todaysDate + '_' + uniquekey + '.jpq'

    def updateTreads(self, key=None):

        # tread speed ranges from 0 (none) to one (full speed) so [.5 ,.5] would be half full speed
        """

        :param key:
        """
        if key is None:
            self.rover.treads = [0, 0]
        elif key is K_w:
            self.rover.treads = [1, 1]
        elif key is K_s:
            self.rover.treads = [-1, -1]
        elif key is K_a:
            self.rover.treads = [-1, 1]
        elif key is K_d:
            self.rover.treads = [1, -1]
        elif key is K_q:
            self.rover.treads = [.1, 1]
        elif key is K_e:
            self.rover.treads = [1, .1]
        elif key is K_z:
            self.rover.treads = [-.1, -1]
        elif key is K_c:
            self.rover.treads = [-1, -.1]
        elif key is K_l:
            pass
        else:
            pass

    def updatePeripherals(self, key=None):
        """

        :param key:
        """
        if key is None:
            self.rover.peripherals['camera'] = 0
        elif key is K_j:
            self.rover.peripherals['camera'] = 1
        elif key is K_k:
            self.rover.peripherals['camera'] = -1
        elif key is K_u:
            self.rover.peripherals['stealth'] = not \
                self.rover.peripherals['stealth']
        elif key is K_i:
            self.rover.peripherals['lights'] = not \
                self.rover.peripherals['lights']
        elif key is K_o:
            self.rover.peripherals['detect'] = not \
                self.rover.peripherals['detect']
        elif key is K_SPACE:
            self.takepicure()
        else:
            pass