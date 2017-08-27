from e21_util.interruptor import Interruptor, InterruptableTimer
from devcontroller.encoder.theta import ThetaEncoder
from phymotion import ThetaMotorController
from devcontroller.misc.logger import LoggerFactory

class SampleThetaController(object):

    MAX_ANGLE_MOVE = 10
    ANGLE_MIN = -10.0
    ANGLE_MAX = 10.0
    ANGLE_TOL = 0.003
    TOTAL_WAITING_TIME = 60
    WAITING_TIME = 0.25
    HYSTERESIS_OFFSET = 160

    def __init__(self, interruptor=None, timer=None, logger=None):
        self._motor = ThetaMotorController()
        self._encoder = ThetaEncoder()
        self._moving = False
        self._last_steps = 0

        if logger is None:
            logger = LoggerFactory().get_sample_theta_logger()

        self._logger = logger

        if interruptor is None:
            interruptor = Interruptor()

        self._interruptor = interruptor

        if timer is None:
            timer = InterruptableTimer(self._interruptor)

        self._timer = timer

    def set_interrupt(self, interruptor):
        assert isinstance(interruptor, Interruptor)
        self._interruptor = interruptor

    def get_motor(self):
        return self._motor

    def interrupt(self):
        self._interruptor.stop()

    def get_encoder(self):
        return self._encoder

    def stop(self):
        self._motor.stop()

    def get_angle(self):
        if not self._moving is False:
            return self._moving

        with self._encoder:
            return self._encoder.get_angle()

    def set_angle(self, angle):
        if not (self.ANGLE_MIN <= angle <= self.ANGLE_MAX):
            raise RuntimeError("New angle is not in the allowed angle range [%s, %s]", self.ANGLE_MIN, self.ANGLE_MAX)
        try:
            self._moving = 0
            with self._encoder:
                self._move_angle(angle)
        finally:
            self._moving = False

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
                self._interruptor.stoppable()
                raw_encoder.read()
                self._logger.info("At position %s. Reference 1: %s, Reference 2: %s", raw_encoder.getPosition(), raw_encoder.getReference1(), raw_encoder.getReference2())

            self._encoder.stop_reference()

        finally:
            self._encoder.disconnect()
            self._motor.get_driver().activate_endphase()

    def _move_angle(self, angle):
        cur_angle = self._encoder.get_angle()
        self._moving = cur_angle
        diff = angle - cur_angle

        steps = self._proposal_steps(diff)
        self._logger.info("Moving to angle %s", angle)
        self._logger.info("--> Proposal steps: %s" % steps)
        if steps == 0:
            return

        try:
            self._motor.move(steps)
            i = 0
            while True:
                self._interruptor.stoppable()
                i += self.WAITING_TIME
                if not self._motor.is_moving() or i >= self.TOTAL_WAITING_TIME:
                    self._logger.info("---> Motor stopped or waiting time exceeded")
                    break

                cur_angle = self._encoder.get_angle()
                self._moving = cur_angle
                if not (self.ANGLE_MIN <= cur_angle <= self.ANGLE_MAX):
                    self._logger.error("---> Motor not in allowed range. STOP")
                    raise RuntimeError("Angle not in allowed position anymore. STOP.")

                #diff_new = abs(cur_angle - angle)
                #if diff_new > abs(diff):
                #    self._motor.stop()
                #    self._logger.warning("---> Motor stopped, probably moved in the wrong direction")
                #    break

                self._logger.info("--> Current angle %s",  cur_angle)
                self._timer.sleep(self.WAITING_TIME)

            self._motor.stop()
            new_angle = self._encoder.get_angle()
            self._moving = new_angle
            self._logger.info("---> Current angle %s", new_angle)

            new_diff = abs(angle - new_angle)
        except BaseException as e:
            self._motor.stop()
            raise e

        if new_diff > self.ANGLE_TOL:
            self._logger.info("Goal: %s, current: %s, difference: %s", angle, new_angle, new_diff)
            self._move_angle(angle)


    def _proposal_steps(self, angle_diff):

        new_proposal = -1 * int(angle_diff * 1200)

        hysteresis_correction = 0
        if not self._last_steps == 0:
            sig_new = self.signum(new_proposal)
            sig_old = self.signum(self._last_steps)
            if not sig_new == sig_old:
                hysteresis_correction = sig_new * self.HYSTERESIS_OFFSET

        self._logger.info("Last steps: %s, new proposal: %s + hysteresis offset %s", self._last_steps, new_proposal, hysteresis_correction)
        self._last_steps = new_proposal + hysteresis_correction
        return new_proposal

    def signum(self, value):
        if value > 0:
            return +1
        if value < 0:
            return -1
        return 0
