import time
from devcontroller.encoder.z import ZEncoder
from controllers.baur.factory import *

class SampleZController(object):

    MAX_ANGLE_MOVE = 10
    Z_MIN = -10.0
    Z_MAX = 10.0
    Z_TOL = 2.5e-3
    TOTAL_WAITING_TIME = 100
    WAITING_TIME = 0.5

    def __init__(self):
        self._motor = BaurFactory().create_z_stage()
        self._encoder = ZEncoder()

    def get_encoder(self):
        return self._encoder

    def get_motor(self):
        return self._motor

    def stop(self):
        self._motor.stop()

    def get_position(self):
        with self._encoder:
            return self._encoder.get_position()

    def set_position(self, pos):
        if not (self.Z_MIN <= pos <= self.Z_MAX):
            raise RuntimeError("New position is not in the allowed angle range [%s, %s]", self.Z_MIN, self.Z_MAX)

        with self._encoder:
            self._move_position(pos)

    def move_up(self, position):
        self.set_position(self.get_position() + abs(position))

    def move_down(self, position):
        self.set_position(self.get_position() - abs(position))

    def search_reference(self):
        try:
            self._encoder.connect()

            self._encoder.start_reference()
            raw_encoder = self._encoder.get_encoder()
            raw_encoder.clearBuffer()
            while not raw_encoder.receivedReference():
                raw_encoder.read()
                print("At position %s. Reference 1: %s, Reference 2: %s" % (raw_encoder.getPosition(), raw_encoder.getReference1(), raw_encoder.getReference2()))

            self._encoder.stop_reference()

        finally:
            self._encoder.disconnect()

    def _move_position(self, position):
        current_position = self._encoder.get_position()
        diff = position - current_position

        steps = self._proposal_steps(diff)
        print("Proposal steps: %s" % steps)
        if steps == 0:
            return

        try:
            self._move_motor(steps)
            self._motor.stop()
            new_position = self._encoder.get_position()
            print("Current position: %s" % new_position)

            new_diff = abs(position - new_position)
        except BaseException as e:
            self._motor.stop()
            raise e

        if new_diff > self.Z_TOL:
            print("... move again")
            self._move_position(position)

    def _move_motor(self, diff_steps):
        cur_steps = self._motor.getPosition()
        desired_position = cur_steps + diff_steps

        self._motor.move_abs(desired_position)
        i = 0
        while True:
            i += self.WAITING_TIME
            if self._motor.getPosition() == desired_position or i >= self.TOTAL_WAITING_TIME:
                break

            current_position = self._encoder.get_position()

            if not (self.Z_MIN <= current_position <= self.Z_MAX):
                raise RuntimeError("z-position not in allowed range anymore. STOP.")

            print("current position %s" % current_position)
            time.sleep(self.WAITING_TIME)


    def _proposal_steps(self, angle_diff):
        return -1 * int(angle_diff * 5000)
