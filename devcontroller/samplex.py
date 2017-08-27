from e21_util.interruptor import InterruptableTimer, Interruptor, StopException
from controllers.baur.factory import *
from devcontroller.misc.logger import LoggerFactory


class SampleXController(object):

    def __init__(self, timer=None, interruptor=None, logger=None):
        if interruptor is None:
            interruptor = Interruptor()
        self._interrupt = interruptor

        if logger is None:
            logger = LoggerFactory().get_sample_x_logger()
        self._logger = logger

        if timer is None:
            timer = InterruptableTimer(self._interrupt)
        self._timer = timer

        self._motor = BaurFactory().create_x_stage()
        self._motor.initialize(4000, 20, 400, 300)

    def set_interrupt(self, interrupt):
        assert isinstance(interrupt, Interruptor)
        self._interrupt = interrupt

    def get_motor(self):
        return self._motor

    def get_interruptor(self):
        return self._interrupt

    def interrupt(self):
        self._interrupt.stop()

    def stop(self):
        self._motor.stop()

    def get_position(self):
        return self._motor.getPosition()

    def set_position(self, pos):
        self._motor.move_abs(pos)
        self._timer.sleep(0.5)
        cur_pos = self._motor.getPosition()
        try:
            while True:
                self._interrupt.stoppable()
                try:
                    cur_pos = self.get_position()
                except BaseException as e:
                    self._logger.warning("Could not read current position")
                    self._logger.exception(e)

                if pos == cur_pos:
                    break
                self._timer.sleep(1)
        except StopException as e:
            self._motor.stop()
            raise e

    def _move(self, steps):
        current_steps = self._motor.getPosition()
        final_steps = current_steps + steps
        try:
            while True:
                self._interrupt.stoppable()
                if current_steps == final_steps:
                    return True
                self._timer.sleep(1)
                current_steps = self._motor.getPosition()
        except StopException as e:
            self._motor.stop()
            raise e

    def move(self, diff):
        if diff > 0:
            self.move_right(diff)
        else:
            self.move_left(diff)

    def move_left(self, diff_in_mm):
        diff = abs(diff_in_mm)
        if abs(diff_in_mm) > 5:
            raise RuntimeError("Will not move more than 5 mm in total")
        steps = self._mm_to_steps(diff)
        self._logger.info("Moving %s mm to the left. This corresponds to %s steps" , diff, steps)
        self._move(steps)

    def move_right(self, diff_in_mm):
        diff = abs(diff_in_mm)
        if abs(diff_in_mm) > 5:
            raise RuntimeError("Will not move more than 5 mm in total")
        steps = self._mm_to_steps(-1 * diff)
        self._logger.info("Moving %s mm to the right. This corresponds to %s steps", diff, steps)
        self._move(steps)

    def move_left_steps(self, steps):
        abs_stps = abs(steps)
        if abs_stps > 30000:
            raise RuntimeError("Will not move more than 30.000 steps in total")
        self._logger.info("Moving %s steps to the left. This corresponds to %s mm", steps, self._steps_to_mm(steps))
        self._move(steps)

    def move_right_steps(self, steps):
        abs_stps = abs(steps)
        if abs_stps > 30000:
            raise RuntimeError("Will not move more than 30.000 steps in total")
        self._logger.info("Moving %s steps to the right. This corresponds to %s mm", steps, self._steps_to_mm(-1 * steps))
        self._move(-1 * steps)

    def _mm_to_steps(self, mm):
        return int(mm * 5977)

    def _steps_to_mm(self, steps):
        return steps * 0.000167308