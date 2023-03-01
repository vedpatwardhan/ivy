from typing import Optional, Union

# global
import torch
import torch.nn

# local
from ivy.func_wrapper import with_unsupported_dtypes
from . import backend_version


@with_unsupported_dtypes({"1.11.0 and below": ("float16",)}, backend_version)
def logit(x: torch.Tensor, /, *, eps: Optional[float] = None, out=None):
    return torch.logit(x, eps=eps, out=out)


@with_unsupported_dtypes({"1.11.0 and below": ("complex", "float16")}, backend_version)
def thresholded_relu(
    x: torch.Tensor,
    /,
    *,
    threshold: Optional[Union[int, float]] = None,
    out: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    return torch.threshold(x, threshold=threshold, value=0)


@with_unsupported_dtypes({"1.11.0 and below": ("bfloat16", "float16")}, backend_version)
def relu6(x: torch.Tensor, /, *, out: Optional[torch.Tensor] = None) -> torch.Tensor:
    return torch.nn.functional.relu6(x)


relu6.unsupported_dtypes = (
    "float16",
    "bfloat16",
)


@with_unsupported_dtypes({"1.11.0 and below": ("bfloat16", "float16")}, backend_version)
def batch_norm(
    x: torch.Tensor,
    mean: torch.Tensor,
    variance: torch.Tensor,
    /,
    *,
    scale: Optional[torch.Tensor] = None,
    offset: Optional[torch.Tensor] = None,
    training: bool = False,
    eps: float = 1e-5,
):
    mean.requires_grad = False
    variance.requires_grad = False
    scale.requires_grad = False
    offset.requires_grad = False
    return torch.nn.functional.batch_norm(
        x, mean, variance, weight=scale, bias=offset, training=training, eps=eps
    )
