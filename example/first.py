import texscript

ts = texscript.session()

fn = ts.compute(r'f(x,y,z) = \sqrt{x^2 + y^2 + z^2}')

print(fn(1,2,3))
