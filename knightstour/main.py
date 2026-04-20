import sys
import unittest


def main():
    if "--test" in sys.argv:
        from tests import KnightsTourTests
        suite  = unittest.TestLoader().loadTestsFromTestCase(KnightsTourTests)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    from app import KnightsTourApp
    app = KnightsTourApp()
    app.mainloop()


if __name__ == "__main__":
    main()
