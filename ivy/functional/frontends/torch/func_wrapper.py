# global
import functools
from typing import Callable

# local
import ivy
import ivy.functional.frontends.torch as torch_frontend


def _from_ivy_array_to_torch_frontend_tensor(x, nested=False, include_derived=None):
    if nested:
        return ivy.nested_map(
            x, _from_ivy_array_to_torch_frontend_tensor, include_derived, shallow=False
        )
    elif isinstance(x, ivy.Array) or ivy.is_native_array(x):
        a = torch_frontend.Tensor(x, _init_overload=True)
        return a
    return x


def _to_ivy_array(x):
    # if x is a native array return it as an ivy array
    if isinstance(x, ivy.NativeArray):
        return ivy.array(x)

    # else if x is a frontend torch Tensor (or any frontend "Tensor" actually) return the wrapped ivy array # noqa: E501
    elif hasattr(x, "ivy_array"):
        return x.ivy_array

    # else just return x
    return x


def inputs_to_ivy_arrays(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def new_fn(*args, **kwargs):
        """
        Converts all `Tensor` instances in both the positional and keyword
        arguments into `ivy.Array` instances, and then calls the function with the
        updated arguments.
        """
        # Remove out argument if present in kwargs
        if "out" in kwargs and not isinstance(
            kwargs["out"], (torch_frontend.Tensor, type(None))
        ):
            raise ivy.utils.exceptions.IvyException(
                "Out argument must be an ivy.frontends.torch.Tensor object"
            )
        # convert all input arrays to ivy.Array instances
        new_args = ivy.nested_map(
            args, _to_ivy_array, include_derived={tuple: True}, shallow=False
        )
        new_kwargs = ivy.nested_map(
            kwargs, _to_ivy_array, include_derived={tuple: True}, shallow=False
        )
        return fn(*new_args, **new_kwargs)

    return new_fn


def outputs_to_frontend_arrays(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def new_fn(*args, **kwargs):
        """
        Calls the function, and then converts all `ivy.Array` instances returned
        by the function into `Tensor` instances.
        """
        # call unmodified function
        # ToDo: Remove this default dtype setting
        #  once frontend specific backend setting is added
        ivy.set_default_int_dtype("int64")
        ivy.set_default_float_dtype(torch_frontend.get_default_dtype())
        try:
            ret = fn(*args, **kwargs)
        finally:
            ivy.unset_default_int_dtype()
            ivy.unset_default_float_dtype()
        # convert all arrays in the return to `torch_frontend.Tensor` instances
        return _from_ivy_array_to_torch_frontend_tensor(
            ret, nested=True, include_derived={tuple: True}
        )

    return new_fn


def to_ivy_arrays_and_back(fn: Callable) -> Callable:
    """
    Wraps `fn` so that input arrays are all converted to `ivy.Array` instances
    and return arrays are all converted to `Tensor` instances.
    """
    return outputs_to_frontend_arrays(inputs_to_ivy_arrays(fn))
