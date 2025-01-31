""" Unit test for the Nonlinear Gauss Seidel nonlinear solver. """

import unittest
from six import iteritems

import numpy as np

from openmdao.api import Group, Problem, IndepVarComp, LinearGaussSeidel, \
    Newton, ExecComp, ScipyGMRES
from openmdao.test.sellar import SellarDerivativesGrouped, \
                                 SellarNoDerivatives, SellarDerivatives, \
                                 SellarStateConnection
from openmdao.test.util import assert_rel_error


class TestNewton(unittest.TestCase):

    def test_sellar_grouped(self):

        prob = Problem()
        prob.root = SellarDerivativesGrouped()
        prob.root.mda.nl_solver = Newton()

        prob.setup(check=False)
        prob.run()

        assert_rel_error(self, prob['y1'], 25.58830273, .00001)
        assert_rel_error(self, prob['y2'], 12.05848819, .00001)

        # Make sure we aren't iterating like crazy
        self.assertLess(prob.root.nl_solver.iter_count, 8)

    def test_sellar(self):

        prob = Problem()
        prob.root = SellarNoDerivatives()
        prob.root.nl_solver = Newton()

        prob.setup(check=False)
        prob.run()

        assert_rel_error(self, prob['y1'], 25.58830273, .00001)
        assert_rel_error(self, prob['y2'], 12.05848819, .00001)

        # Make sure we aren't iterating like crazy
        self.assertLess(prob.root.nl_solver.iter_count, 8)

    def test_sellar_derivs(self):

        prob = Problem()
        prob.root = SellarDerivatives()
        prob.root.nl_solver = Newton()

        prob.setup(check=False)
        prob.run()

        assert_rel_error(self, prob['y1'], 25.58830273, .00001)
        assert_rel_error(self, prob['y2'], 12.05848819, .00001)

        # Make sure we aren't iterating like crazy
        self.assertLess(prob.root.nl_solver.iter_count, 8)

    def test_sellar_derivs_with_Lin_GS(self):

        prob = Problem()
        prob.root = SellarDerivatives()
        prob.root.nl_solver = Newton()
        prob.root.ln_solver = LinearGaussSeidel()
        prob.root.ln_solver.options['maxiter'] = 2

        prob.setup(check=False)
        prob.run()

        assert_rel_error(self, prob['y1'], 25.58830273, .00001)
        assert_rel_error(self, prob['y2'], 12.05848819, .00001)

        # Make sure we aren't iterating like crazy
        self.assertLess(prob.root.nl_solver.iter_count, 8)

    def test_sellar_state_connection(self):

        prob = Problem()
        prob.root = SellarStateConnection()
        prob.root.nl_solver = Newton()

        prob.setup(check=False)
        prob.run()

        assert_rel_error(self, prob['y1'], 25.58830273, .00001)
        assert_rel_error(self, prob['state_eq.y2_command'], 12.05848819, .00001)

        # Make sure we aren't iterating like crazy
        self.assertLess(prob.root.nl_solver.iter_count, 8)

    def test_sellar_specify_linear_solver(self):

        prob = Problem()
        prob.root = SellarStateConnection()
        prob.root.nl_solver = Newton()

        # Use bad settings for this one so that problem doesn't converge.
        # That way, we test that we are really using Newton's Lin Solver
        # instead.
        prob.root.ln_solver = ScipyGMRES()
        prob.root.ln_solver.options['maxiter'] = 1

        # The good solver
        prob.root.nl_solver.ln_solver = ScipyGMRES()

        prob.setup(check=False)
        prob.run()

        assert_rel_error(self, prob['y1'], 25.58830273, .00001)
        assert_rel_error(self, prob['state_eq.y2_command'], 12.05848819, .00001)

        # Make sure we aren't iterating like crazy
        self.assertLess(prob.root.nl_solver.iter_count, 8)
        self.assertEqual(prob.root.ln_solver.iter_count, 0)
        self.assertGreater(prob.root.nl_solver.ln_solver.iter_count, 0)

if __name__ == "__main__":
    unittest.main()
