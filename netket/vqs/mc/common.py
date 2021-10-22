# Copyright 2021 The NetKet Authors - All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

import jax
from jax import numpy as jnp

from netket.hilbert import AbstractHilbert
from netket.utils.dispatch import dispatch
from netket.operator import AbstractOperator

from netket.vqs import VariationalState


def check_hilbert(A: AbstractHilbert, B: AbstractHilbert):
    if not A == B:
        raise NotImplementedError(  # pragma: no cover
            f"Non matching hilbert spaces {A} and {B}"
        )


@dispatch.abstract
def get_configs(vstate: Any, Ô: Any):
    """
    Returns the samples of vstate used to compute the expectation value
    of the operator O, and the connected elements and matrix elements.

    Args:
        vstate: the variational state
        Ô: the operator

    Returns:
        A Tuple with 3 elements (sigma, sigmap, mels)
    """


@dispatch.abstract
def get_fun(vstate: Any, Ô: Any):
    """
    Returns the function computing the local estimator for the given variational
    state and operator.

    Args:
        vstate: the variational state
        Ô: the operator

    Returns:
        A callable accepting the output of `get_configs(vstate, O)`.
    """
