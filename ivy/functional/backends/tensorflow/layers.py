"""Collection of TensorFlow network layers, wrapped to fit Ivy syntax and signature."""

# global
from typing import Optional, Tuple, Union, List, Sequence

import tensorflow as tf
from tensorflow.python.types.core import Tensor

# local
import ivy
from ivy.func_wrapper import with_unsupported_dtypes
from . import backend_version
from ivy.functional.ivy.layers import _deconv_length, _get_x_data_format


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv1d(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: int,
    padding: str,
    /,
    *,
    data_format: str = "NWC",
    dilations: int = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Union[tf.Tensor, tf.Variable]:
    if data_format == "NCW":
        x = tf.transpose(x, (0, 2, 1))
    res = tf.nn.conv1d(x, filters, strides, padding, "NWC", dilations)
    if data_format == "NCW":
        res = tf.transpose(res, (0, 2, 1))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv1d_transpose(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: int,
    padding: str,
    /,
    *,
    output_shape: Optional[Union[ivy.NativeShape, Sequence[int]]] = None,
    data_format: str = "NWC",
    dilations: int = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
):
    if not ivy.gpu_is_available() and dilations > 1:
        raise ivy.exceptions.IvyException(
            "Tensorflow does not support dilations greater than 1 when device is cpu"
        )
    filters = tf.transpose(filters, (0, 2, 1))
    if data_format == "NCW":
        x = tf.transpose(x, (0, 2, 1))
    if output_shape is None:
        output_shape = _deconv_length(
            x.shape[1], strides, filters.shape[0], padding, dilations
        )
        output_shape = [x.shape[0], output_shape, filters.shape[1]]
    elif len(output_shape) == 1:
        output_shape = [x.shape[0], output_shape[0], filters.shape[1]]
    res = tf.nn.conv1d_transpose(
        x,
        filters,
        output_shape,
        strides,
        padding,
        "NWC",
        dilations,
    )
    if data_format == "NCW":
        res = tf.transpose(res, (0, 2, 1))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv2d(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: Union[int, Tuple[int, int]],
    padding: str,
    /,
    *,
    data_format: str = "NHWC",
    dilations: Union[int, Tuple[int, int]] = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Union[tf.Tensor, tf.Variable]:
    if data_format == "NCHW":
        x = tf.transpose(x, (0, 2, 3, 1))
    res = tf.nn.conv2d(x, filters, strides, padding, "NHWC", dilations)
    if data_format == "NCHW":
        return tf.transpose(res, (0, 3, 1, 2))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv2d_transpose(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: Union[int, Tuple[int, int]],
    padding: str,
    /,
    *,
    output_shape: Optional[Union[ivy.NativeShape, Sequence[int]]] = None,
    data_format: str = "NHWC",
    dilations: Optional[Union[int, Tuple[int, int]]] = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
):
    if not ivy.gpu_is_available() and (
        (dilations > 1) if isinstance(dilations, int) else any(d > 1 for d in dilations)
    ):
        raise ivy.exceptions.IvyException(
            "Tensorflow does not support dilations greater than 1 when device is cpu"
        )
    if isinstance(strides, int):
        strides = [strides] * 2
    dilations = [dilations] * 2 if isinstance(dilations, int) else dilations
    filters = tf.transpose(filters, (0, 1, 3, 2))
    if data_format == "NCHW":
        x = tf.transpose(x, (0, 2, 3, 1))
    if output_shape is None:
        new_h = _deconv_length(
            x.shape[1], strides[0], filters.shape[0], padding, dilations[0]
        )
        new_w = _deconv_length(
            x.shape[2], strides[1], filters.shape[1], padding, dilations[1]
        )
        output_shape = [x.shape[0], new_h, new_w, filters.shape[-2]]
    elif len(output_shape) == 2:
        output_shape = [x.shape[0], output_shape[0], output_shape[1], filters.shape[-2]]
    res = tf.nn.conv2d_transpose(
        x, filters, output_shape, strides, padding, "NHWC", dilations
    )
    if data_format == "NCHW":
        return tf.transpose(res, (0, 3, 1, 2))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def depthwise_conv2d(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: Union[int, Tuple[int, int]],
    padding: Union[str, List[int]],
    /,
    *,
    data_format: str = "NHWC",
    dilations: Union[int, Tuple[int, int]] = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Union[tf.Tensor, tf.Variable]:
    strides = [strides] * 2 if isinstance(strides, int) else strides
    dilations = [dilations] * 2 if isinstance(dilations, int) else dilations
    if tf.rank(filters) == 3:
        filters = tf.expand_dims(filters, -1)
    if len(strides) == 2:
        strides = [1, strides[0], strides[1], 1]
    if data_format == "NCHW":
        x = tf.transpose(x, (0, 2, 3, 1))
    res = tf.nn.depthwise_conv2d(x, filters, strides, padding, "NHWC", dilations)
    if data_format == "NCHW":
        return tf.transpose(res, (0, 3, 1, 2))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv3d(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: Union[int, Tuple[int, int, int]],
    padding: str,
    /,
    *,
    data_format: str = "NDHWC",
    dilations: Union[int, Tuple[int, int, int]] = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
):
    strides = [1] + ([strides] * 3 if isinstance(strides, int) else strides) + [1]
    dilations = (
        [1] + ([dilations] * 3 if isinstance(dilations, int) else dilations) + [1]
    )
    if data_format == "NCDHW":
        x = tf.transpose(x, (0, 2, 3, 4, 1))
    res = tf.nn.conv3d(x, filters, strides, padding, "NDHWC", dilations)
    if data_format == "NCDHW":
        return tf.transpose(res, (0, 4, 1, 2, 3))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv3d_transpose(
    x: Tensor,
    filters: Tensor,
    strides: Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int]],
    padding: str,
    /,
    *,
    output_shape=None,
    data_format: str = "NDHWC",
    dilations: Union[int, Tuple[int, int, int]] = 1,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Tensor:
    strides = [1] + ([strides] * 3 if isinstance(strides, int) else strides) + [1]
    dilations = (
        [1] + ([dilations] * 3 if isinstance(dilations, int) else dilations) + [1]
    )
    filters = tf.transpose(filters, (0, 1, 2, 4, 3))
    if data_format == "NCDHW":
        x = tf.transpose(x, (0, 2, 3, 4, 1))
    if output_shape is None:
        new_d = _deconv_length(
            x.shape[1], strides[1], filters.shape[0], padding, dilations[0]
        )
        new_h = _deconv_length(
            x.shape[2], strides[2], filters.shape[1], padding, dilations[1]
        )
        new_w = _deconv_length(
            x.shape[3], strides[3], filters.shape[2], padding, dilations[2]
        )
        output_shape = [x.shape[0], new_d, new_h, new_w, filters.shape[-2]]
    elif len(output_shape) == 3:
        output_shape = [
            x.shape[0],
            output_shape[0],
            output_shape[1],
            output_shape[2],
            filters.shape[-2],
        ]
    res = tf.nn.conv3d_transpose(
        x, filters, output_shape, strides, padding, "NDHWC", dilations
    )
    if data_format == "NCDHW":
        return tf.transpose(res, (0, 4, 1, 2, 3))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv_general_dilated(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: Union[int, Tuple[int, int]],
    padding: str,
    /,
    *,
    dims: int = 2,
    data_format: str = "channel_last",
    feature_group_count: int = 1,
    x_dilations: Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int]] = 1,
    dilations: Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int]] = 1,
    bias: Optional[Union[tf.Tensor, tf.Variable]] = None,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Union[tf.Tensor, tf.Variable]:
    strides = [strides] * dims if isinstance(strides, int) else strides
    dilations = [dilations] * dims if isinstance(dilations, int) else dilations
    x_dilations = [x_dilations] * dims if isinstance(x_dilations, int) else x_dilations

    if dims == 3:
        strides = [1] + strides + [1]
        dilations = [1] + dilations + [1]

    if data_format == "channel_first":
        x = tf.transpose(x, (0, *range(2, dims + 2), 1))
    x_shape = list(x.shape[1 : dims + 2])

    # adding dilation in input
    for i in range(dims):
        if x_dilations[i] > 1:
            h = x_shape[i]
            new_height = h + (h - 1) * (x_dilations[i] - 1)
            h = tf.eye(new_height, dtype=x.dtype)[:: x_dilations[i]]
            x = tf.experimental.numpy.swapaxes(x, 1 + i, -1)
            x = tf.matmul(x, h)
            x = tf.experimental.numpy.swapaxes(x, -1, 1 + i)

    df = _get_x_data_format(dims, "channel_last")
    if dims == 1:
        res = tf.concat(
            [
                tf.nn.conv1d(
                    x[:, :, i : i + filters.shape[-2]],
                    filters[:, :, j : j + filters.shape[-1] // feature_group_count],
                    strides,
                    padding,
                    df,
                    dilations,
                )
                for i, j in zip(
                    range(0, x.shape[-1], filters.shape[-2]),
                    range(
                        0, filters.shape[-1], filters.shape[-1] // feature_group_count
                    ),
                )
            ],
            axis=-1,
        )
    elif dims == 2:
        res = tf.concat(
            [
                tf.nn.conv2d(
                    x[:, :, :, i : i + filters.shape[-2]],
                    filters[:, :, :, j : j + filters.shape[-1] // feature_group_count],
                    strides,
                    padding,
                    df,
                    dilations,
                )
                for i, j in zip(
                    range(0, x.shape[-1], filters.shape[-2]),
                    range(
                        0, filters.shape[-1], filters.shape[-1] // feature_group_count
                    ),
                )
            ],
            axis=-1,
        )
    else:
        res = tf.concat(
            [
                tf.nn.conv3d(
                    x[:, :, :, :, i : i + filters.shape[-2]],
                    filters[
                        :, :, :, :, j : j + filters.shape[-1] // feature_group_count
                    ],
                    strides,
                    padding,
                    df,
                    dilations,
                )
                for i, j in zip(
                    range(0, x.shape[-1], filters.shape[-2]),
                    range(
                        0, filters.shape[-1], filters.shape[-1] // feature_group_count
                    ),
                )
            ],
            axis=-1,
        )
    res = tf.math.add(res, bias) if bias is not None else res
    if data_format == "channel_first":
        res = tf.transpose(res, (0, dims + 1, *range(1, dims + 1)))
    return res


@with_unsupported_dtypes({"2.9.1 and below": ("bfloat16", "complex")}, backend_version)
def conv_general_transpose(
    x: Union[tf.Tensor, tf.Variable],
    filters: Union[tf.Tensor, tf.Variable],
    strides: Union[int, Tuple[int, int]],
    padding: str,
    /,
    *,
    dims: int = 2,
    data_format: str = "channel_last",
    output_shape=None,
    dilations: Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int]] = 1,
    feature_group_count: int = 1,
    bias: Optional[Union[tf.Tensor, tf.Variable]] = None,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Union[tf.Tensor, tf.Variable]:
    if data_format == "channel_first":
        x = tf.transpose(x, (0, *range(2, dims + 2), 1))
    if dims == 1:
        res = tf.concat(
            [
                conv1d_transpose(
                    x[..., j : j + filters.shape[-2] // feature_group_count],
                    filters[..., j : j + filters.shape[-2] // feature_group_count, :],
                    strides,
                    padding,
                    output_shape=output_shape,
                    data_format="NWC",
                    dilations=dilations,
                )
                for j in range(
                    0, filters.shape[-2], filters.shape[-2] // feature_group_count
                )
            ],
            axis=-1,
        )
    elif dims == 2:
        res = tf.concat(
            [
                conv2d_transpose(
                    x[..., j : j + filters.shape[-2] // feature_group_count],
                    filters[..., j : j + filters.shape[-2] // feature_group_count, :],
                    strides,
                    padding,
                    output_shape=output_shape,
                    data_format="NHWC",
                    dilations=dilations,
                )
                for j in range(
                    0, filters.shape[-2], filters.shape[-2] // feature_group_count
                )
            ],
            axis=-1,
        )
    else:
        res = tf.concat(
            [
                conv3d_transpose(
                    x[..., j : j + filters.shape[-2] // feature_group_count],
                    filters[..., j : j + filters.shape[-2] // feature_group_count, :],
                    strides,
                    padding,
                    output_shape=output_shape,
                    data_format="NDHWC",
                    dilations=dilations,
                )
                for j in range(
                    0, filters.shape[-2], filters.shape[-2] // feature_group_count
                )
            ],
            axis=-1,
        )
    res = tf.math.add(res, bias) if bias is not None else res
    if data_format == "channel_first":
        res = tf.transpose(res, (0, dims + 1, *range(1, dims + 1)))
    return res
