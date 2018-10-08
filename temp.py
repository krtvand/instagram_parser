def sum(n):
    s = 0
    def f(b):
        nonlocal s
        s += b
        return s
    return f(n)


print(sum(1)(2)(3))