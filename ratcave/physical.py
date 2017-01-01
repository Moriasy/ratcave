import numpy as np
import _transformations as trans
from .utils import rotations as rotutils
from .utils import SceneNode, AutoRegisterObserver


class Physical(AutoRegisterObserver):

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), scale=1.,
                 **kwargs):
        """XYZ Position, Scale and XYZEuler Rotation Class.

        Args:
            position: (x, y, z) translation values.
            rotation: (x, y, z) rotation values
            scale (float): uniform scale factor. 1 = no scaling.
        """
        super(Physical, self).__init__(**kwargs)

        self._rot = rotutils.RotationEulerDegrees(*rotation)
        self._pos = rotutils.Translation(*position)
        self._scale = rotutils.Scale(scale)

        self.model_matrix = np.zeros((4, 4))
        self.normal_matrix = np.zeros((4, 4))
        self.view_matrix = np.zeros((4, 4))

        self.update()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, coords):
        if isinstance(coords, rotutils.Translation):
            self._pos = coords
        else:
            self._pos = rotutils.Translation(*coords)

    @property
    def rot(self):
        return self._rot

    @rot.setter
    def rot(self, coords):
        if isinstance(coords, rotutils.RotationBase):
            self._rot = coords
        elif hasattr(coords, '__iter__'):
            if len(coords) == 3:
                self._rot = rotutils.RotationEulerDegrees(*coords)
            elif len(coords) == 4:
                self._rot = rotutils.RotationQuaternion(*coords)
        else:
            raise ValueError("rot must be xyz values, xyzw values, or inherit from RotationBase")

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, coords):
        if isinstance(coords, rotutils.Scale):
            self._scale = coords
        elif hasattr(coords, '__iter__'):
            self._scale = rotutils.Scale(*coords)
        else:
            self._scale = rotutils.Scale(coords)

    def update(self):
        """Calculate model, normal, and view matrices from position, rotation, and scale data."""
        super(Physical, self).update()

        # Update Model, View, and Normal Matrices
        self.model_matrix[:] = np.dot(self.pos.to_matrix(), self.rot.to_matrix())
        self.view_matrix[:] = trans.inverse_matrix(self.model_matrix)
        self.model_matrix[:] = np.dot(self.model_matrix, self.scale.to_matrix())
        self.normal_matrix[:] = trans.inverse_matrix(self.model_matrix.T)


class PhysicalNode(Physical, SceneNode):

    def __init__(self, **kwargs):
        """Object with xyz position and rotation properties that are relative to its parent."""
        self.model_matrix_global = np.zeros((4, 4))
        self.normal_matrix_global = np.zeros((4, 4))
        self.view_matrix_global = np.zeros((4, 4))
        super(PhysicalNode, self).__init__(**kwargs)

    def update(self):
        super(PhysicalNode, self).update()

        """Calculate world matrix values from the dot product of the parent."""
        if self.parent:
            self.model_matrix_global[:] = np.dot(self.parent.model_matrix_global, self.model_matrix)
            self.normal_matrix_global[:] = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
            self.view_matrix_global[:] = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
        else:
            self.model_matrix_global[:] = self.model_matrix
            self.normal_matrix_global[:] = self.normal_matrix
            self.view_matrix_global[:] = self.view_matrix

    @property
    def position_global(self):
        return tuple(self.model_matrix_global[:3, -1].tolist())
