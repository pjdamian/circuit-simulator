# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 08:32:38 2026

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built-in
import unittest
import time

# -----------------------------------------------------------------------------
# Run all tests
# -----------------------------------------------------------------------------
# # V1 - simple output
# loader = unittest.TestLoader()
# suite = loader.discover("tests")
# runner = unittest.TextTestRunner(verbosity=2)
# runner.run(suite)
# V2 - Formatting output
class FormatTestResults(unittest.TextTestResult):

    def startTest(self, test):
        super().startTest(test)
        print(f"RUN  {test._testMethodName:<40} ", end="", flush=True)

    def addSuccess(self, test):
        super().addSuccess(test)
        print("PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print("FAIL")

    def addError(self, test, err):
        super().addError(test, err)
        print("ERROR")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        print("XFAIL")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        print("XPASS")


class FormatTestRunner(unittest.TextTestRunner):
    resultclass = FormatTestResults
    
    def run(self, test):
        
        result = self.resultclass(stream=None, descriptions=True, verbosity=0)
        start = time.time()
        test(result)
        end = time.time()
        result.elapsed = end - start
        
        return result


def run_tests():

    print("\n" + "=" * 55)
    print("RUNNING TESTS")
    print("=" * 55)
    
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    start = time.time()


    runner = FormatTestRunner(verbosity=0)
    result = runner.run(suite)

    end = time.time()

    print("\n" + "=" * 55)
    print("TEST SUMMARY")
    print("=" * 55)

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    xfail = len(result.expectedFailures)
    xpass = len(result.unexpectedSuccesses)

    passed = total - failures - errors - skipped - xfail

    print(f"Total tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failures}")
    print(f"Errors      : {errors}")
    print(f"ExpectedFail: {xfail}")
    print(f"Skipped     : {skipped}")
    print(f"UnexpectedOK: {xpass}")
    print(f"Time        : {end-start:.3f}s")

    print("=" * 55)

    if not result.wasSuccessful():
        exit(1)


if __name__ == "__main__":
    run_tests()
