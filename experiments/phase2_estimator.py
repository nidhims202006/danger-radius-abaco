"""Small constant-velocity Kalman filter used by the phase-2 simulator."""
from __future__ import annotations
import numpy as np


class CVKalman:
    def __init__(self, row: float, col: float, sigma: float):
        self.x = np.array([[row], [col], [0.0], [0.0]], dtype=float)
        self.P = np.eye(4) * 0.5
        self.sigma = float(sigma)

    def predict(self, dt: float = 1.0):
        F = np.array([[1, 0, dt, 0], [0, 1, 0, dt],
                      [0, 0, 1, 0], [0, 0, 0, 1]], float)
        q = 0.05
        Q = np.diag([q, q, q * 0.5, q * 0.5])
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
        return self.x.copy()

    def update(self, row: float, col: float):
        if self.sigma <= 0:
            self.x[0, 0], self.x[1, 0] = row, col
            return self.x.copy()
        H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], float)
        R = np.eye(2) * (self.sigma ** 2)
        z = np.array([[row], [col]], float)
        y = z - H @ self.x
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P
        return self.x.copy()

    @property
    def position(self):
        return float(self.x[0, 0]), float(self.x[1, 0])

    @property
    def velocity(self):
        return float(self.x[2, 0]), float(self.x[3, 0])
