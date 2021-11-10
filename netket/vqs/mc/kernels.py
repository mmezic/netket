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

"""
This module implements some common kernels used by MCState and MCMixedState.
"""

from typing import Any
from functools import partial

import jax
import jax.numpy as jnp

import netket.jax as nkjax


def local_value_kernel(logpsi, pars, σ, σp, mel):
    """
    local_value kernel for MCState and generic operators
    """
    return jnp.sum(mel * jnp.exp(logpsi(pars, σp) - logpsi(pars, σ)))


def local_value_squared_kernel(logpsi, pars, σ, σp, mel):
    """
    local_value kernel for MCState and Squared (generic) operators
    """
    return jnp.abs(local_value_kernel(logpsi, pars, σ, σp, mel)) ** 2


def local_value_op_op_cost(logpsi, pars, σ, σp, mel):
    """
    local_value kernel for MCMixedState and generic operators
    """
    σ_σp = jax.vmap(lambda σp, σ: jnp.hstack((σp, σ)), in_axes=(0, None))(σp, σ)
    σ_σ = jnp.hstack((σ, σ))
    return jnp.sum(mel * jnp.exp(logpsi(pars, σ_σp) - logpsi(pars, σ_σ)))


## Chunked versions of those kernels are defined below.


def local_valuekernel_chunked(logpsi, pars, σ, σp, mel, *, chunk_size=None):
    """
    local_value kernel for MCState and generic operators
    """
    logpsi_batched = nkjax.vmap_batched(
        partial(logpsi, pars), in_axes=0, batch_size=chunk_size
    )
    N = σ.shape[-1]

    logpsi_σ = logpsi_batched(σ.reshape((-1, N))).reshape(σ.shape[:-1] + (1,))
    logpsi_σp = logpsi_batched(σp.reshape((-1, N))).reshape(σp.shape[:-1])

    return jnp.sum(mel * jnp.exp(logpsi_σp - logpsi_σ), axis=-1)


def local_value_squaredkernel_chunked(logpsi, pars, σ, σp, mel, *, chunk_size=None):
    """
    local_value kernel for MCState and Squared (generic) operators
    """
    return (
        jnp.abs(
            local_valuekernel_chunked(logpsi, pars, σ, σp, mel, batch_size=chunk_size)
        )
        ** 2
    )


def local_value_op_op_cost_chunked(logpsi, pars, σ, σp, mel, *, chunk_size=None):
    """
    local_value kernel for MCMixedState and generic operators
    """
    σ_σp = jax.vmap(
        lambda σpi, σi: jax.vmap(lambda σp, σ: jnp.hstack((σp, σ)), in_axes=(0, None))(
            σpi, σi
        ),
        in_axes=(0, 0),
        out_axes=0,
    )
    σ_σ = jax.vmap(lambda σi: jnp.hstack((σi, σi)), in_axes=0)(σ)

    return local_valuekernel_chunked(
        logpsi, pars, σ_σ, σ_σp, mel, batch_size=chunk_size
    )
