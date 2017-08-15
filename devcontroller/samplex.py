from controllers.baur.factory import *

class SampleThetaController(object):

    def __init__(self):
        self._motor = BaurFactory().create_x_stage()

    def get_motor(self):
        return self._motor

    def stop(self):
        self._motor.stop()

    def move_left(self, diff_in_mm):
        diff = abs(diff_in_mm)
        if abs(diff_in_mm) > 5:
            raise RuntimeError("Will not move more than 5 mm in total")
        steps = self._mm_to_steps(diff)
        print("Moving %s mm to the left. This corresponds to %s steps" % (diff, steps))
        self._motor.move_rel(steps)

    def move_right(self, diff_in_mm):
        diff = abs(diff_in_mm)
        if abs(diff_in_mm) > 5:
            raise RuntimeError("Will not move more than 5 mm in total")
        steps = self._mm_to_steps(-1 * diff)
        print("Moving %s mm to the right. This corresponds to %s steps" % (diff, steps))
        self._motor.move_rel(steps)

    def move_left_steps(self, steps):
        abs_stps = abs(steps)
        if abs_stps > 30000:
            raise RuntimeError("Will not move more than 30.000 steps in total")
        print("Moving %s steps to the left. This corresponds to %s mm" % (steps, self._steps_to_mm(steps)))
        self._motor.move_rel(steps)

    def move_right_steps(self, steps):
        abs_stps = abs(steps)
        if abs_stps > 30000:
            raise RuntimeError("Will not move more than 30.000 steps in total")
        print("Moving %s steps to the right. This corresponds to %s mm" % (steps, self._steps_to_mm(-1 * steps)))
        self._motor.move_rel(-1 * steps)

    def _mm_to_steps(self, mm):
        return int(mm * 5977)

    def _steps_to_mm(self, steps):
        return steps * 0.000167308