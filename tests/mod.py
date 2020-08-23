import sys; sys.path.insert(0, '../tinkerer')
import tinkerer.mod as tm


def test_mod_is_valid():
    mod = tm.Mod('A mod', 1, 1, False)
    assert mod is not None
