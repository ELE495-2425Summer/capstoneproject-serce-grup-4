import numpy as np
from speech_io import send_to_ui

class Kalman1D:
    def __init__(self, deltaT=0):
        self.x_prev = np.array([[0],
                                [0],
                                [0]])
        self.x_est = self.x_prev

        self.I = np.identity(3)

        self.set_deltaT(deltaT)

        self.P_prev = np.eye(3) * 0.1
        self.P_est = self.P_prev

        self.R = np.array([[0.001, 0],
                           [0,    0.1]])

        self.Z = np.array([[0], [0]])

    def set_deltaT(self, deltaT):
        self.F = np.array([
            [1, deltaT, 0.5 * deltaT],
            [0, 1,      deltaT],
            [0, 0,      1]
        ])

        self.Q = np.array([
            [deltaT**4/4, deltaT**3/2, deltaT**2/2],
            [deltaT**3/2, deltaT**2,   deltaT],
            [deltaT**2/2, deltaT,      1]
        ]) * 0.05

        self.H = np.array([
            [0, 1, 1],
            [0, 0, 1]
        ])

    def measure(self, measurements):
        self.Z = measurements

    def update(self):
        S = self.H @ self.P_est @ self.H.T + self.R
        K = self.P_est @ self.H.T @ np.linalg.inv(S)
        self.x_prev = self.x_est + K @ (self.Z - self.H @ self.x_est)
        self.P_prev = (self.I - K @ self.H) @ self.P_est

    def predict(self):
        self.x_est = self.F @ self.x_prev
        self.P_est = self.F @ self.P_prev @ self.F.T + self.Q
        send_to_ui(f"Yaw: {self.x_est[0]}")
        return self.x_est

    def execute(self, deltaT, measurements):
        self.set_deltaT(deltaT)
        self.measure(measurements)
        self.update()
        return self.predict()
    
    def get_x_loc(self):
        return self.x_est[0]

    def reset(self):
        self.__init__()
