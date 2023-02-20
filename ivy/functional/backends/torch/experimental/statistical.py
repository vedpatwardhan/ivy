# global
from typing import Optional, Union, Tuple, Sequence
import torch

# local
from ivy.func_wrapper import with_unsupported_dtypes
from . import backend_version


@with_unsupported_dtypes({"1.11.0 and below": ("float16",)}, backend_version)
def median(
    input: torch.tensor,
    /,
    *,
    axis: Optional[Union[Tuple[int], int]] = None,
    keepdims: Optional[bool] = False,
    out: Optional[torch.tensor] = None,
) -> torch.tensor:
    temp = input
    if hasattr(axis, "__iter__"):
        for dim in axis:
            temp = torch.quantile(
                temp,
                0.5,
                dim=dim,
                keepdim=keepdims,
                interpolation="midpoint",
            )[0]
        return temp
    else:
        return torch.quantile(
            input,
            0.5,
            dim=axis,
            keepdim=keepdims,
            interpolation="midpoint",
        )[0]


median.support_native_out = False


def nanmean(
    a: torch.Tensor,
    /,
    *,
    axis: Optional[Union[int, Tuple[int]]] = None,
    keepdims: Optional[bool] = False,
    dtype: Optional[torch.dtype] = None,
    out: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    if isinstance(dtype, str):
        TORCH_DTYPES = {
            'float32': torch.float32,
            'float64': torch.float64,
        }
        temp = Torch_DTYPES[dtype]
    else:
        temp = dtype
    return torch.nanmean(a, dim=axis, keepdim=keepdims, dtype=temp, out=out)


nanmean.support_native_out = True


@with_unsupported_dtypes(
    {"1.11.0 and below": ("bfloat16", "bfloat32", "float16")}, backend_version
)
def quantile(
    a: torch.tensor,
    q: Union[torch.tensor, float],
    /,
    *,
    axis: Optional[Union[Sequence[int], int]] = None,
    keepdims: Optional[bool] = False,
    interpolation: Optional[str] = "linear",
    out: Optional[torch.tensor] = None,
) -> torch.tensor:

    if axis is None:
        return torch.quantile(a, q, keepdim=keepdims, interpolation=interpolation)

    if isinstance(axis, list) or isinstance(axis, tuple):
        """
        In Tensorflow, Jax, and Numpy backends when multiple axes are provided, first
        the tensor/array gets flatten along those axes such that it preserves the size
        of the remaining axes. Afterwards, it compute the quantile(s) along axis = 0.

        In Torch backend, it is not possible to provide multiple axes. Therefore it is
        needed to mimic same procedure to reach desired shape of tensor/array and
        compute quantile(s) along axis=0.
        """

        desired_shape = []
        current_shape = a.size()

        for i in range(len(current_shape)):
            if i not in axis:
                desired_shape += [current_shape[i]]

        temp = a.reshape((-1,) + tuple(desired_shape))

        return torch.quantile(
            temp, q, dim=0, keepdim=keepdims, interpolation=interpolation
        )

    return torch.quantile(a, q, dim=axis, keepdim=keepdims, interpolation=interpolation)


quantile.support_native_out = False


def corrcoef(
    x: torch.Tensor,
    /,
    *,
    y: Optional[torch.Tensor] = None,
    rowvar: Optional[bool] = True,
    out: Optional[torch.tensor] = None,
) -> torch.Tensor:
    if y is None:
        xarr = x
    else:
        axis = 0 if rowvar else 1
        xarr = torch.concat([x, y], dim=axis)
        xarr = xarr.T if not rowvar else xarr

    return torch.corrcoef(xarr)


def nanmedian(
    input: torch.tensor,
    /,
    *,
    axis: Optional[Union[Tuple[int], int]] = None,
    keepdims: Optional[bool] = False,
    overwrite_input: Optional[bool] = False,
    out: Optional[torch.tensor] = None,
) -> torch.tensor:
    return torch.nanmedian(
        input, axis=axis, keepdims=keepdims, overwrite_input=overwrite_input, out=out
    )


nanmedian.support_native_out = True


def unravel_index(
    indices: torch.Tensor,
    shape: Tuple[int],
    /,
    *,
    out: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    temp = indices.to("int64")
    output = []
    for dim in reversed(shape):
        output.append(temp % dim)
        temp = temp // dim
    return tuple(reversed(output))


unravel_index.support_native_out = False
