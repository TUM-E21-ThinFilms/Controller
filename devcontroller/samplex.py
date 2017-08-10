from controllers.baur.factory import *
from theta import ThetaHeidenhainController

class SampleThetaController(object):

    MAX_ANGLE_MOVE = 10
    ANGLE_MIN = -10.0
    ANGLE_MAX = 10.0
    ANGLE_TOL = 0.001
    WAITING_TIME = 100

    def __init__(self):
        self._motor = BaurFactory().create_x_stage()
        self._encoder = ThetaHeidenhainController()


