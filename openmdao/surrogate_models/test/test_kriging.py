
# pylint: disable-msg=C0111,C0103

import unittest
import random
import itertools

from numpy import array, linspace, sin, cos, pi, meshgrid

from openmdao.surrogate_models import KrigingSurrogate
from openmdao.test.util import assert_rel_error
from six.moves import zip


def branin(x):
    y = (x[1] - (5.1 / (4. * pi ** 2.)) * x[0] ** 2. + 5. * x[0] / pi - 6.) ** 2. + 10. * (1. - 1. / (8. * pi)) * cos(
        x[0]) + 10.
    return y


def branin_1d(x):
    return branin(array([x[0], 2.275]))


class TestKrigingSurrogate(unittest.TestCase):

    def setUp(self):
        random.seed(10)

    def test_1d_training(self):

        x = array([[0.0], [2.0], [3.0], [4.0], [6.0]])
        y = array([[branin_1d(case)] for case in x])
        krig1 = KrigingSurrogate()
        krig1.train(x, y)

        for x0, y0 in zip(x, y):
            mu, sigma = krig1.predict(x0)
            assert_rel_error(self, mu, y0, 1e-9)
            assert_rel_error(self, sigma, 0, 1e-6)

    def test_1d_predictor(self):
        x = array([[0.0], [2.0], [3.0], [4.0], [6.0]])
        y = array([[branin_1d(case)] for case in x])

        krig1 = KrigingSurrogate()
        krig1.train(x, y)

        new_x = array([pi])
        mu, sigma = krig1.predict(new_x)

        assert_rel_error(self, mu, 0.397887, 1e-1)
        assert_rel_error(self, sigma, 0.0294172, 1e-2)

    def test_1d_ill_conditioned(self):
        # Test for least squares solver utilization when ill-conditioned
        x = array([[case] for case in linspace(0., 1., 40)])
        y = sin(x)
        krig1 = KrigingSurrogate()
        krig1.train(x, y)
        new_x = array([0.5])
        mu, sigma = krig1.predict(new_x)

        self.assertTrue( sigma < 1e-8 )
        assert_rel_error(self, mu, sin(0.5), 1e-6)

    def test_2d(self):

        x = array([[-2., 0.], [-0.5, 1.5], [1., 3.], [8.5, 4.5], [-3.5, 6.], [4., 7.5], [-5., 9.], [5.5, 10.5],
                   [10., 12.], [7., 13.5], [2.5, 15.]])
        y = array([[branin(case)] for case in x])

        krig1 = KrigingSurrogate()
        krig1.train(x, y)

        for x0, y0 in zip(x, y):
            mu, sigma = krig1.predict(x0)
            assert_rel_error(self, mu, y0, 1e-9)
            assert_rel_error(self, sigma, 0, 1e-6)

        mu, sigma = krig1.predict([5., 5.])

        assert_rel_error(self, mu, branin([5., 5.]), 1e-1)
        assert_rel_error(self, sigma, 5.79, 1e-2)

    def test_no_training_data(self):
        krig1 = KrigingSurrogate()

        try:
            krig1.predict([0., 1.])
        except RuntimeError as err:
            self.assertEqual(str(err),
                "KrigingSurrogate has not been trained, so no prediction can be made.")
        else:
            self.fail("RuntimeError Expected")

    def test_one_pt(self):
        krig1 = KrigingSurrogate()
        x = [[0.]]
        y = [[1.]]

        with self.assertRaises(ValueError) as cm:
            krig1.train(x,y)

        self.assertEqual(str(cm.exception), 'KrigingSurrogates require at least 2 training points.')

    def test_vector_input(self):
        krig1 = KrigingSurrogate()

        x = array([[0., 0., 0.], [1., 1., 1.]])
        y = array([[0.], [3.]])

        krig1.train(x, y)

        for x0, y0 in zip(x, y):
            mu, sigma = krig1.predict(x0)
            assert_rel_error(self, mu, y0, 1e-9)
            assert_rel_error(self, sigma, 0, 1e-6)

    def test_vector_output(self):
        krig1 = KrigingSurrogate()

        y = array([[0., 0.], [1., 1.], [2., 0.]])
        x = array([[0.], [2.], [4.]])

        krig1.train(x, y)

        for x0, y0 in zip(x, y):
            mu, sigma = krig1.predict(x0)
            assert_rel_error(self, mu, y0, 1e-9)
            assert_rel_error(self, sigma, 0, 1e-6)

    def test_scalar_derivs(self):
        krig1 = KrigingSurrogate()

        x = array([[0.], [1.], [2.], [3.]])
        y = x.copy()

        krig1.train(x,y)
        jac = krig1.jacobian(array([[0.]]))

        assert_rel_error(self, jac[0][0], 1., 1e-3)

    def test_vector_derivs(self):
        krig1 = KrigingSurrogate()

        X = array([[x, y] for x,y in itertools.product(linspace(0, 1, 10), repeat=2)])
        Y = array([[a+b, a-b] for a, b in X])

        krig1.train(X, Y)
        jac = krig1.jacobian(array([[0.5, 0.5]]))
        assert_rel_error(self, jac, array([[1, 1], [1, -1]]), 1e-5)

if __name__ == "__main__":
    unittest.main()
