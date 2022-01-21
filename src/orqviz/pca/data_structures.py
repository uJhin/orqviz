from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from sklearn.decomposition import PCA

from ..aliases import ArrayOfParameterVectors


@dataclass(init=True)
class PCAobject:
    """PCA datatype to combine PCA object with the corresponding higher-dimensional
    points and the components of interest"""

    def __init__(
        self,
        all_points: ArrayOfParameterVectors,
        components_ids: Tuple[int, int] = (0, 1),
    ):
        self.all_points = all_points
        self._params_shape = np.shape(self.all_points)[1:]
        self.components_ids = components_ids
        self.fit_pca(max(self.components_ids) + 1)

    def set_component_ids(self, new_component_ids: Tuple[int, int]) -> None:
        new_n_components = max(new_component_ids) + 1
        self.fit_pca(new_n_components)
        self.components_ids = new_component_ids

    def fit_pca(self, n_components: int) -> None:
        self.pca = PCA(n_components=n_components)
        params = self.all_points.reshape(-1, np.prod(self._params_shape))
        self.pca.fit(params)

    def get_transformed_points(
        self, points: Optional[ArrayOfParameterVectors] = None
    ) -> np.ndarray:
        high_dim_points = self.all_points if points is None else points
        return self.pca.transform(
            high_dim_points.reshape(-1, np.prod(self._params_shape))
        )

    def get_inverse_transformed_point(
        self, pca_params: np.ndarray
    ) -> ArrayOfParameterVectors:
        return self.pca.inverse_transform(pca_params).reshape(*self._params_shape)

    @property
    def components(self) -> np.ndarray:
        """Returns a numpy array of component vectors in the shape of the parameters"""
        return self.pca.components_.reshape(-1, *self._params_shape)

    @property
    def mean(self) -> np.ndarray:
        """Returns the fitted mean of the high-dimensional parameter vectors"""
        return self.pca.mean_.reshape(*self._params_shape)

    def _get_endpoints_from_pca(
        self,
        offset: Tuple[float, float] = (-1.0, 1.0),
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Helper function to get the scan coordinate ranges of PCA-transformed
            coordinates in the specified components with a provided offset.

        Args:
            components_ids: Which components of the PCA object are used as
                scan directions. Defaults to (0, 1).
            offset: Offset in x-y directions added to the scan range on top
                of the range that is necessary to display all_points.
                Defaults to (-1.0, 1.0).

        """
        pca_transformed_points = self.get_transformed_points()

        end_points_x = (
            float(min(pca_transformed_points[:, self.components_ids[0]]) + offset[0]),
            float(max(pca_transformed_points[:, self.components_ids[0]]) + offset[1]),
        )
        end_points_y = (
            float(min(pca_transformed_points[:, self.components_ids[1]]) + offset[0]),
            float(max(pca_transformed_points[:, self.components_ids[1]]) + offset[1]),
        )
        return end_points_x, end_points_y


def get_pca(
    all_points: ArrayOfParameterVectors,
    components_ids: Tuple[int, int] = (0, 1),
) -> PCAobject:
    """Fits and returns a sklearn PCA instance to the provided parameters.

    Args:
        all_points: List/array of parameter vectors to perform PCA on
        components_ids: Which components are of interest. PCA fits to
            max(components_ids)+1 components. Defaults to (0, 1).
    """
    return PCAobject(all_points, components_ids)
