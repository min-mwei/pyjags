import numpy as np
import typing as tp

from .modules import load_module
from .model import Model


def dic_samples(model: Model,
                n_iter: int,
                thin: int = 1,
                type: str="pD",
                *args,
                **kwargs) -> tp.Dict:
    if not isinstance(model, Model):
        raise ValueError("Invalid JAGS model")

    if model.chains == 1:
        raise ValueError("2 or more parallel chains required")

    if not isinstance(n_iter, int) or n_iter <= 0:
        raise ValueError("n_iter must be a positive integer")

    load_module(name='dic')

    if not type == "pD" or type == "popt":
        raise ValueError(f"type must either be pD or popt but is {type}")
    pdtype = type
    model.console.setMonitors(names=("deviance", pdtype),
                              thin=thin,
                              type="mean")

    model.update(iterations=n_iter)

    # this returns a dictionary
    # dev = model.console.getMonitoredValuesFlat(monitor_type="mean")
    dev = model.console.dumpMonitors(type="mean", flat=True)

    # for (i in seq(along=dev)) {
    #     class(dev[[i]]) < - "mcarray"
    # }

    model.console.clearMonitor(name="deviance", type="mean")
    model.console.clearMonitor(name=pdtype, type="mean")

    # how do I check the status?
    # if (status[1]) {
    #     .Call("clear_monitor", model$ptr(), "deviance", NULL, NULL, "mean", PACKAGE = "rjags")
    # }
    # if (status[2]) {
    #     .Call("clear_monitor", model$ptr(), pdtype, NULL, NULL, "mean", PACKAGE = "rjags")
    # }

    ans = {"deviance": dev['deviance'],
           "penalty": dev[type],
           "type": type}

    return ans


def print_dic(x: tp.Dict[str, tp.Any], digits: int = 2):
    deviance = np.sum(x['deviance'])
    print("Mean deviance: {:.{}f}".format(deviance, digits))
    psum = np.sum(x['penalty'])
    print("penalty: {:.{}f}".format(psum, digits))
    print("Penalized deviance: {:.{}f}".format(deviance + psum, digits))
