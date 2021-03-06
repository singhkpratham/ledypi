import logging

from Equation import Expression

from patterns.default import Default
from utils import scale

pattern_logger = logging.getLogger("pattern_logger")


class Equation(Default):
    """
    Use user-defined function for the rgb values. The function may depend on :
        - the pixel position in the led strip 'idx'
        - the current timestep 't' which cycles in a predefined allowed range.
        - both
        - none
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.pattern_name = "Equation"

        self.fns = {}

        # r,g,b functions in string format
        self.r_eq = "cos(t)"
        self.g_eq = "sin(t)"
        self.b_eq = "idx"

        # time step
        self.t = 1

        # max range for function
        self.max_range = self.strip_length * 1000

        self.modifiers = dict(
            red_equation=self.r_eq,
            blue_equation=self.g_eq,
            green_equation=self.b_eq,
        )

    @property
    def r_eq(self):
        return self._r_eq

    @r_eq.setter
    def r_eq(self, value):
        assert isinstance(value, str), pattern_logger.warning("The equation value is not a string")
        self.fns['r_fn'] = Expression(value, ["t", "idx"])
        self._r_eq = value

    @property
    def g_eq(self):
        return self._g_eq

    @g_eq.setter
    def g_eq(self, value):
        assert isinstance(value, str), pattern_logger.warning("The equation value is not a string")
        self.fns['g_fn'] = Expression(value, ["t", "idx"])
        self._g_eq = value

    @property
    def b_eq(self):
        return self._b_eq

    @b_eq.setter
    def b_eq(self, value):
        assert isinstance(value, str), pattern_logger.warning("The equation value is not a string")
        self.fns['b_fn'] = Expression(value, ["t", "idx"])
        self._b_eq = value

    def fill(self):

        # cicle timestep
        if self.strip_length + self.t >= self.max_range:
            self.t = 1

        # get range for this execution
        rng = range(self.t, self.strip_length + self.t)

        try:
            # get vals for the current range
            rs = [self.fns['r_fn'](t=t, idx=idx) for idx, t in enumerate(rng, start=1)]
            gs = [self.fns['g_fn'](t=t, idx=idx) for idx, t in enumerate(rng, start=1)]
            bs = [self.fns['b_fn'](t=t, idx=idx) for idx, t in enumerate(rng, start=1)]

            # scale in 0,255 values
            rs, gs, bs = self.scale(rs, gs, bs)

            # set values
            for idx in range(self.strip_length):
                self.pixels[idx]['color'] = (rs[idx], gs[idx], bs[idx], self.color.a)

        except Exception as e:
            pattern_logger.warning(f"One of the equation failed to execute, please change it\nError: {e}")

        # update timestep
        self.t += 1

    @staticmethod
    def scale(rs, gs, bs):
        """
        Scale and convert to int lists of rgb values
        """

        # get maxs and mins
        r_min = min(rs)
        r_max = max(rs)

        g_min = min(gs)
        g_max = max(gs)

        b_min = min(bs)
        b_max = max(bs)

        # scale
        rs = [scale(r, 0, 255, r_min, r_max) for r in rs]
        gs = [scale(g, 0, 255, g_min, g_max) for g in gs]
        bs = [scale(b, 0, 255, b_min, b_max) for b in bs]

        # convert to int
        rs = [int(elem) for elem in rs]
        gs = [int(elem) for elem in gs]
        bs = [int(elem) for elem in bs]

        return rs, gs, bs
