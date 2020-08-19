module multid.tools.norm;
import mir.math.sum : sum;
import std.math : sqrt;
import mir.ndslice;

/++
    Computes the L2 norm
+/
auto nrmL2(V)(V v)
{
    return v.map!(x => x * x).sum.sqrt;
}

unittest
{
    assert([1, 2, 3, 4].sliced!double.nrmL2 == 30.0.sqrt);
    assert([1, 1].sliced!double.nrmL2 == 2.0.sqrt);
    assert([1, 1, 1, 1].sliced!double.nrmL2 == 2.0);
}
