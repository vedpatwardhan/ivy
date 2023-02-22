# global
import torch
from typing import Optional, Union


# msort
def msort(
    a: Union[torch.Tensor, list, tuple], /, *, out: Optional[torch.Tensor] = None
) -> torch.Tensor:
    return torch.msort(a, out=out)


msort.support_native_out = True


# lexsort
def lexsort(
    keys: torch.Tensor, /, *, axis: int = -1, out: Optional[torch.Tensor] = None
) -> torch.Tensor:
    shape = keys.size()
    if len(shape) == 1:
        _, result = torch.sort(keys, dim=axis, stable=True)
        return result
    if shape[0] == 0:
        raise TypeError("need sequence of keys with len > 0 in lexsort")
    if len(shape) == 2 and shape[1] == 1:
        return torch.tensor([0])
    _, result = torch.sort(keys[0], dim=axis, stable=True)
    # result = torch.argsort(keys[0], dim=axis, stable=True)
    # only valid for torch > 1.12.0
    if shape[0] == 1:
        return result
    for i in range(1, shape[0]):
        key = keys[i]
        ind = key[result]
        _, temp = torch.sort(ind, dim=axis, stable=True)
        # temp = torch.argsort(ind, dim=axis, stable=True)
        # only valid for torch > 1.12.0
        result = result[temp]
    return result


lexsort.support_native_out = False
