# users/management/commands/runtestsall.py
# command - python manage.py runtestsall

import unittest

from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner
from users.tests.test_metadata import TEST_CASES

class ResultCollector(unittest.TextTestResult):
    """
    Collect pass/fail results so we can print a custom table in terminal.
    """
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_results.append((test, "Pass", ""))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results.append((test, "Fail", self._exc_info_to_string(err, test)))

    def addError(self, test, err):
        super().addError(test, err)
        self.test_results.append((test, "Fail", self._exc_info_to_string(err, test)))


class CustomTestRunner(DiscoverRunner):
    """
    Custom Django test runner that uses ResultCollector.
    """
    test_runner = unittest.TextTestRunner
    resultclass = ResultCollector

    def run_suite(self, suite, **kwargs):
        runner = self.test_runner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=self.resultclass
        )
        return runner.run(suite)


class Command(BaseCommand):
    help = "Run whole hospital system tests and print custom formatted report"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\nRunning Hospital Management System Tests...\n"))

        runner = CustomTestRunner(verbosity=1)
        suite = runner.build_suite(test_labels=[
            "users.tests.system_tests",
        ])

        result = runner.run_suite(suite)

        self.stdout.write("\n" + "=" * 110)
        self.stdout.write(f"{'ID':<10}{'Description':<35}{'Expected Result':<40}{'Status':<10}")
        self.stdout.write("=" * 110)

        for test, status, error in result.test_results:
            method_name = test._testMethodName
            meta = TEST_CASES.get(method_name, {
                "id": "N/A",
                "description": method_name,
                "expected": "-"
            })

            tc_id = meta["id"]
            description = meta["description"]
            expected = meta["expected"]

            self.stdout.write(f"{tc_id:<10}{description:<35}{expected:<40}{status:<10}")

        self.stdout.write("=" * 110)

        total = len(result.test_results)
        passed = len([r for r in result.test_results if r[1] == "Pass"])
        failed = len([r for r in result.test_results if r[1] == "Fail"])

        self.stdout.write(f"\nTotal Test Cases : {total}")
        self.stdout.write(self.style.SUCCESS(f"Passed           : {passed}"))
        if failed:
            self.stdout.write(self.style.ERROR(f"Failed           : {failed}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Failed           : {failed}"))

        # Print failure details if any
        if failed:
            self.stdout.write(self.style.ERROR("\nFailure Details:\n"))
            for test, status, error in result.test_results:
                if status == "Fail":
                    method_name = test._testMethodName
                    meta = TEST_CASES.get(method_name, {"id": "N/A", "description": method_name})
                    self.stdout.write(self.style.ERROR(f"{meta['id']} - {meta['description']}"))
                    self.stdout.write(error)
                    self.stdout.write("-" * 100)

        # Exit code for CI / terminal correctness
        if failed:
            raise SystemExit(1)
        


