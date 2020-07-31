import std.stdio;
import std.range : generate;
import std.random : uniform;
import std.array;
import std.algorithm;
import mir.ndslice;

import multid.gaussseidel.redblack;

void main()
{
    auto U = slice!double(10);
    auto fun = generate!(() => uniform(0.0, 1.0));
    U.field.fill(fun);
    auto F = slice!double([10], 0.0);
    const double h = 1 / 10;
    // auto F = generate!(() => uniform(0, 0.99)).take(10).array.sliced;
    // F = F.reshape([5,2]);
    writeln(GS_RB!(double, 1, 666)(F, U, h));
}
