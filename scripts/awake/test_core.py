import unittest

from core import Leases, Power

ONE = '00000000-0000-4000-8000-000000000001'
TWO = '00000000-0000-4000-8000-000000000002'


class LeaseTests(unittest.TestCase):
    def test_overlap_expiration_and_mode_downgrade(self):
        leases = Leases()
        leases.renew(ONE, 'build', 'system', 30, 0)
        leases.renew(TWO, 'agent', 'active', 10, 0)
        self.assertEqual(leases.mode(5), 'active')
        self.assertEqual(leases.mode(10), 'system')
        self.assertIsNone(leases.mode(30))

    def test_renew_release_and_restart_recovery(self):
        leases = Leases()
        leases.renew(ONE, 'build', 'display', 30, 0)
        leases.renew(ONE, 'build', 'display', 30, 20)
        self.assertEqual(len(leases.snapshot(35)), 1)
        leases.release(TWO)
        leases.release(ONE)
        leases.release(ONE)
        self.assertIsNone(leases.mode(36))
        restarted = Leases()
        restarted.renew(ONE, 'build', 'display', 30, 40)
        self.assertEqual(restarted.mode(41), 'display')

    def test_rejects_invalid_contract(self):
        valid = [ONE, 'build', 'system', 30, 0]
        for position, bad in [(0, '../evil'), (1, 'x' * 81), (1, '\n'),
                              (2, 'never-lock'), (3, 0), (3, 301), (3, True), (3, float('nan'))]:
            with self.subTest(position=position, bad=bad):
                args = list(valid)
                args[position] = bad
                with self.assertRaises(ValueError):
                    Leases().renew(*args)


class PowerTests(unittest.TestCase):
    def test_assertions_are_bounded_and_released(self):
        calls = []
        class Child:
            ended = False
            def poll(self): return 0 if self.ended else None
            def terminate(self): self.ended = True
            def wait(self, timeout=None): return 0
        def spawn(command, **kwargs):
            calls.append(command)
            return Child()
        power = Power(spawn)
        power.update('system', 0)
        first = power.child
        power.update('active', 1)
        self.assertTrue(first.ended)
        self.assertIn('-diu', calls[-1])
        self.assertIn('-t', calls[-1])
        power.update('active', 22)
        self.assertEqual(len(calls), 3)
        power.update(None, 23)
        self.assertIsNone(power.child)


if __name__ == '__main__':
    unittest.main()
