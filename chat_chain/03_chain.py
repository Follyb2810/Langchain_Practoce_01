def demo_args(*args):
    print("args =", args)


names = [1, 2, 3, 4]
name = (1, 2, 3, 4)

demo_args(names)
demo_args(name)


def demo_kwargs(**kwargs):
    print("kwargs =", kwargs)


data = {"a": 1, "b": 2}

demo_kwargs(data)
demo_kwargs(**data)


def demo_all(*args, **kwargs):
    print("args =", args)
    print("kwargs =", kwargs)


nums = [10, 20, 30]
info = {"x": 100, "y": 200}

demo_all(*nums, **info)
demo_all(10, 20, 30, x=100, y=200)
