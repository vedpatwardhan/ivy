# global
from hypothesis import strategies as st, assume

# local
import ivy
import ivy_tests.test_ivy.helpers as helpers
import ivy_tests.test_ivy.test_frontends.test_numpy.helpers as np_frontend_helpers
from ivy_tests.test_ivy.helpers import handle_frontend_test


# sum
@handle_frontend_test(
    fn_tree="numpy.sum",
    dtype_x_axis=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("float")
    ),
    dtype=helpers.get_dtypes("float", full=False, none=True),
    keep_dims=st.booleans(),
    initial=st.one_of(st.floats(), st.none()),
    where=np_frontend_helpers.where(),
)
def test_numpy_sum(
    dtype_x_axis,
    dtype,
    keep_dims,
    where,
    initial,
    frontend,
    test_flags,
    fn_tree,
    on_device,
):
    input_dtypes, x, axis = dtype_x_axis
    if initial is not None:
        (
            where,
            input_dtypes,
            test_flags,
        ) = np_frontend_helpers.handle_where_and_array_bools(
            where=where,
            input_dtype=input_dtypes,
            test_flags=test_flags,
        )
    else:
        where = None
    helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
        dtype=dtype[0],
        keepdims=keep_dims,
        initial=initial,
        where=where,
    )


# prod
@handle_frontend_test(
    fn_tree="numpy.prod",
    dtype_x_axis=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("float")
    ),
    dtype=helpers.get_dtypes("float", full=False, none=True),
    keep_dims=st.booleans(),
    initial=st.one_of(st.floats(), st.none()),
    where=np_frontend_helpers.where(),
)
def test_numpy_prod(
    dtype_x_axis,
    dtype,
    keep_dims,
    initial,
    where,
    frontend,
    test_flags,
    fn_tree,
    on_device,
):
    input_dtypes, x, axis = dtype_x_axis
    if initial is not None:
        (
            where,
            input_dtypes,
            test_flags,
        ) = np_frontend_helpers.handle_where_and_array_bools(
            where=where,
            input_dtype=input_dtypes,
            test_flags=test_flags,
        )
    else:
        where = None
    helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
        dtype=dtype[0],
        keepdims=keep_dims,
        initial=initial,
        where=where,
    )


@st.composite
def _get_castable_dtypes_values(draw, *, allow_nan=False):
    available_dtypes = helpers.get_dtypes("numeric")
    shape = draw(helpers.get_shape(min_num_dims=1, max_num_dims=4, max_dim_size=6))
    dtype, values = draw(
        helpers.dtype_and_values(
            available_dtypes=available_dtypes,
            num_arrays=1,
            large_abs_safety_factor=24,
            small_abs_safety_factor=24,
            safety_factor_scale="log",
            shape=shape,
            allow_nan=allow_nan,
        )
    )
    axis = draw(helpers.get_axis(shape=shape, force_int=True))
    dtype1, values, dtype2 = draw(
        helpers.get_castable_dtype(draw(available_dtypes), dtype[0], values[0])
    )
    return [dtype1], [values], axis, dtype2


# cumsum
@handle_frontend_test(
    fn_tree="numpy.cumsum",
    dtype_and_x_axis_dtype=_get_castable_dtypes_values(),
)
def test_numpy_cumsum(
    dtype_and_x_axis_dtype,
    frontend,
    test_flags,
    fn_tree,
    on_device,
):
    input_dtypes, x, axis, dtype = dtype_and_x_axis_dtype
    # ToDo: set as_variable_flags as the parameter generated by test_cumprod once
    # this issue is marked as completed https://github.com/pytorch/pytorch/issues/75733
    if ivy.current_backend_str() == "torch":
        assume(not test_flags.as_variable[0])
    np_frontend_helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
        dtype=dtype,
    )


# cumprod
@handle_frontend_test(
    fn_tree="numpy.cumprod",
    dtype_x_axis_dtypes=_get_castable_dtypes_values(),
)
def test_numpy_cumprod(
    dtype_x_axis_dtypes,
    frontend,
    test_flags,
    fn_tree,
    on_device,
):
    input_dtypes, x, axis, dtype = dtype_x_axis_dtypes
    # ToDo: set as_variable_flags as the parameter generated by test_cumprod once
    # this issue is marked as completed https://github.com/pytorch/pytorch/issues/75733
    if ivy.current_backend_str() == "torch":
        assume(not test_flags.as_variable[0])
    np_frontend_helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
        dtype=dtype,
    )


# nancumprod
@handle_frontend_test(
    fn_tree="numpy.nancumprod",
    dtype_and_x_axis_dtype=_get_castable_dtypes_values(allow_nan=True),
)
def test_numpy_nancumprod(
    dtype_and_x_axis_dtype,
    frontend,
    test_flags,
    fn_tree,
    on_device,
):
    input_dtypes, x, axis, dtype = dtype_and_x_axis_dtype
    np_frontend_helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
        dtype=dtype,
    )


# nancumsum
@handle_frontend_test(
    fn_tree="numpy.nancumsum",
    dtype_and_x_axis_dtype=_get_castable_dtypes_values(allow_nan=True),
)
def test_numpy_nancumsum(
    dtype_and_x_axis_dtype,
    frontend,
    test_flags,
    fn_tree,
    on_device,
):
    input_dtypes, x, axis, dtype = dtype_and_x_axis_dtype
    np_frontend_helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
        dtype=dtype,
    )


# nanprod
@handle_frontend_test(
    fn_tree="numpy.nanprod",
    dtype_and_x=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("numeric"),
        min_num_dims=1,
        valid_axis=True,
        force_int_axis=True,
        large_abs_safety_factor=2,
        safety_factor_scale="log",
    ),
    dtype=helpers.get_dtypes("float", full=False, none=True),
    keepdims=st.booleans(),
    where=np_frontend_helpers.where(),
)
def test_numpy_nanprod(
    dtype_and_x,
    dtype,
    frontend,
    test_flags,
    fn_tree,
    on_device,
    where,
    keepdims,
):
    input_dtypes, x, axis = dtype_and_x
    where, input_dtypes, test_flags = np_frontend_helpers.handle_where_and_array_bools(
        where=where,
        input_dtype=input_dtypes,
        test_flags=test_flags,
    )
    np_frontend_helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x[0],
        axis=axis,
        dtype=dtype[0],
        where=where,
        keepdims=keepdims,
    )


# nansum
@handle_frontend_test(
    fn_tree="numpy.nansum",
    dtype_and_x=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("numeric"),
        min_num_dims=1,
        valid_axis=True,
        force_int_axis=True,
        large_abs_safety_factor=2,
        safety_factor_scale="log",
    ),
    dtype=helpers.get_dtypes("float", full=False, none=True),
    keepdims=st.booleans(),
    where=np_frontend_helpers.where(),
)
def test_numpy_nansum(
    dtype_and_x,
    dtype,
    frontend,
    test_flags,
    fn_tree,
    on_device,
    where,
    keepdims,
):
    input_dtypes, x, axis = dtype_and_x
    where, input_dtypes, test_flags = np_frontend_helpers.handle_where_and_array_bools(
        where=where,
        input_dtype=input_dtypes,
        test_flags=test_flags,
    )
    np_frontend_helpers.test_frontend_function(
        input_dtypes=input_dtypes,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x[0],
        axis=axis,
        dtype=dtype[0],
        where=where,
        keepdims=keepdims,
    )
