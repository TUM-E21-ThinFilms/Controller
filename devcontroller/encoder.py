import heidenhain
import devcontroller.encoder_calibration
from e21_util.lock import HEIDENHAIN_LOCK


class EncoderFactory(object):
    def __init__(self):
        self._encoder = HeidenhainEncoder()
        self._z = ZEncoder(self._encoder)
        self._theta = ThetaEncoder(self._encoder)

    def initialize(self):
        self._encoder.connect()

    def get_encoder(self):
        return self._encoder

    def get_z(self):
        return self._z

    def get_theta(self):
        return self._theta


class HeidenhainEncoder(object):
    def __init__(self):
        self._connected = False
        self._encoder = None
        self._lock = HEIDENHAIN_LOCK()

    def connect(self):
        if self._connected:
            return True

        self._encoder = heidenhain.get_encoder()

        try:
            success = self._lock.acquire(blocking=False)

            if not success:
                raise RuntimeError("Heidenhain-Encoder is already in use! Could not acquire lock.")

            suc = self._encoder.connect()

            if not suc:
                raise RuntimeError("Could not connect to Heidenhain-Encoder")

            self._connected = True
            return True
        except BaseException as e:
            self._lock.release()
            self._encoder = None
            self._connected = False
            raise e

    def disconnect(self):
        if not self._connected:
            return True

        try:
            suc = self._encoder.disconnect()

            if not suc:
                raise RuntimeError("Could not disconnect from Heidenhain-Encoder. Releasing lock ...")

            self._connected = False

        finally:
            self._lock.release()

        return True

    def is_connected(self):
        return self._connected

    def assert_connected(self):
        if not self.is_connected():
            raise RuntimeError("Heidenhain-Encoder is not connected.")

    def get_encoder(self):
        return self._encoder

    def clear(self):
        self.assert_connected()
        self._encoder.clearStatus()
        self._encoder.clear()

    def clear_connection(self):
        return self._encoder.clearConnection()

    def read(self):
        self.assert_connected()
        return self._encoder.read()

    def clear_buffer(self):
        self.assert_connected()
        return self._encoder.clearBuffer()

    def has_error(self):
        self.assert_connected()
        return self._encoder.hasError()

    def get_error(self):
        self.assert_connected()
        return self._encoder.getError()


class ThetaEncoder(object):
    def __init__(self, encoder):

        if not isinstance(encoder, HeidenhainEncoder):
            raise RuntimeError("encoder must be an instance of HeidenhainEncoder")

        self._encoder = encoder
        self._calibration = devcontroller.encoder_calibration.THETA_CALIBRATION

    def info(self):
        self._encoder.assert_connected()

        data = self._encoder.get_encoder().getThetaData().getData()

        return [data.position, data.status, data.triggerCounter, data.timestamp, data.ref1, data.ref2, data.distCodedRef]

    def get_angle(self):
        if not self.has_reference():
            raise RuntimeError("Cannot read angle, no valid reference given")

        return self._encoder.get_encoder().getThetaData().getAbsoluteDegree() - self._calibration

    def get_reference(self):
        if not self.has_reference():
            raise RuntimeError("Cannot read angle, no valid reference given")
        theta_data = self._encoder.get_encoder().getThetaData()
        data = theta_data.getData()
        ref1 = data.ref1
        ref2 = data.ref2

        return [theta_data.computeDegree(ref1) - self._calibration, theta_data.computeDegree(ref2) - self._calibration]

    def get_trigger(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().getThetaData().getThetaData().getData().trigger

    def start_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().startReferenceTheta()

    def stop_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().stopReferenceTheta()

    def has_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().getThetaData().hasReference()

    def clear_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().clearReferenceTheta()

    def read_calibration(self):
        try:
            reload(devcontroller.encoder_calibration)
            self._calibration = devcontroller.encoder_calibration.THETA_CALIBRATION
        except:
            raise RuntimeError("Could not read calibration values")

    def compute_calibration(self, angle):
        old_calib = self._calibration
        self._calibration = 0
        new_calib = self.get_angle() - angle
        self._calibration = old_calib
        return new_calib


class ZEncoder(object):
    def __init__(self, encoder):
        if not isinstance(encoder, HeidenhainEncoder):
            raise RuntimeError("encoder must be an instance of HeidenhainEncoder")

        self._encoder = encoder
        self._calibration = devcontroller.encoder_calibration.Z_CALIBRATION

    def info(self):
        self._encoder.assert_connected()

        data = self._encoder.get_encoder().getZData().getData()

        return [data.position, data.status, data.triggerCounter, data.timestamp, data.ref1, data.ref2, data.distCodedRef]

    def get_reference(self):
        if not self.has_reference():
            raise RuntimeError("Cannot read position, no valid reference given")

        z_data = self._encoder.get_encoder().getZData()
        data = z_data.data.getData()
        ref1 = data.ref1
        ref2 = data.ref2

        return [z_data.computePosition(ref1) - self._calibration, z_data.computePosition(ref2) - self._calibration]

    def get_position(self):
        if not self.has_reference():
            raise RuntimeError("Cannot read position, no valid reference given")

        return self._encoder.get_encoder().getZData().getAbsoluteDegree() - self._calibration

    def get_trigger(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().getZData().getThetaData().getData().trigger

    def start_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().startReferenceZ()

    def stop_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().stopReferenceZ()

    def has_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().getZData().hasReference()

    def clear_reference(self):
        self._encoder.assert_connected()
        return self._encoder.get_encoder().clearReferenceZ()

    def read_calibration(self):
        try:
            reload(devcontroller.encoder_calibration)
            self._calibration = devcontroller.encoder_calibration.Z_CALIBRATION
        except:
            raise RuntimeError("Could not read calibration values")

    def compute_calibration(self, position):
        old_calib = self._calibration
        self._calibration = 0
        new_calib = self.get_position() - position
        self._calibration = old_calib
        return new_calib


class ReferenceMarkHelper(object):
    def __init__(self, encoder):
        if not isinstance(encoder, HeidenhainEncoder):
            raise RuntimeError("encoder must be an instance of HeidenhainEncoder")

        self._encoder = encoder

    def _search(self, axis):
        is_connected = False
        try:
            is_connected = self._encoder.is_connected()
            if not is_connected:
                self._encoder.connect()

            self._encoder.clear_buffer()
            axis.clear_reference()
            axis.start_reference()
            while not axis.has_reference():
                self._encoder.read()
                print(axis.info())
        except BaseException as e:
            print(e)
        finally:
            axis.stop_reference()
            if not is_connected:
                self._encoder.disconnect()

    def search_theta(self):
        self._search(ThetaEncoder(self._encoder))

    def search_z(self):
        self._search(ZEncoder(self._encoder))