import time
from phymotion import ThetaMotorController
from theta import ThetaHeidenhainController

class SampleThetaController(object):

    MAX_ANGLE_MOVE = 10
    ANGLE_MIN = -10.0
    ANGLE_MAX = 10.0
    ANGLE_TOL = 0.003
    TOTAL_WAITING_TIME = 100
    WAITING_TIME = 0.5

    def __init__(self):
        self._motor = ThetaMotorController()
        self._encoder = ThetaHeidenhainController()

    def get_angle(self):
        with self._encoder:
            return self._encoder.get_angle()

    def set_angle(self, angle):
        if not (self.ANGLE_MIN <= angle <= self.ANGLE_MAX):
            raise RuntimeError("New angle is not in the allowed angle range [%s, %s]", self.ANGLE_MIN, self.ANGLE_MAX)

        with self._encoder:
            self._move_angle(angle)

    def move_cw(self, angle):
        self.set_angle(abs(angle))

    def move_acw(self, angle):
        self.set_angle(-1.0 * abs(angle))

    def search_reference(self):
        try:
            self._encoder.connect()
            self._motor.get_driver().deactivate_endphase()

            self._encoder.start_reference()
            raw_encoder = self._encoder.get_encoder()
            raw_encoder.clearBuffer()
            while not raw_encoder.receivedReference():
                raw_encoder.read()
                print("At position %s. Reference 1: %s, Reference 2: %s" % (raw_encoder.getPosition(), raw_encoder.getReference1(), raw_encoder.getReference2()))

            self._encoder.stop_reference()

        finally:
            self._encoder.disconnect()
            self._motor.get_driver().activate_endphase()
            
    def _move_angle(self, angle):
        cur_angle = self._encoder.get_angle()
        diff = angle - cur_angle

        steps = self._proposal_steps(diff)
        print("Proposal steps: %s" % steps)
        if steps == 0:
            return

        self._motor.move(steps)
        i = 0
        while True:
            i += self.WAITING_TIME
            if not self._motor.is_moving() or i >= self.TOTAL_WAITING_TIME:
                break

            cur_angle = self._encoder.get_angle()
                
            diff_new = abs(cur_angle - angle)
            if diff_new > diff:
                self._motor.stop()

            print("current angle %s" % cur_angle)
            time.sleep(self.WAITING_TIME)

        self._motor.stop()
        new_angle = self._encoder.get_angle()
        print("Current angle: %s" % new_angle)

        new_diff = abs(angle - new_angle)

        if new_diff > self.ANGLE_TOL:
            print("... move again")
            self._move_angle(angle)

    def _proposal_steps(self, angle_diff):
        return -1 * int(angle_diff * 1250)
