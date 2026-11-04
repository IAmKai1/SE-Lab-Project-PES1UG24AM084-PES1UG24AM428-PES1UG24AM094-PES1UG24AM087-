"""
Automated runner to execute the full LRG test suite with coverage and performance benchmarking.
"""

import subprocess
import sys
import time


def main():
    print("=" * 70)
    print("Digital Campus Library Reservation Gateway - Automated Test Runner")
    print("=" * 70)

    start_time = time.time()
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing",
        "--cov-report=html:docs/coverage_html",
        "--cov-report=xml:docs/coverage.xml",
        "-v"
    ]

    result = subprocess.run(cmd)
    elapsed = time.time() - start_time

    print("-" * 70)
    print(f"Test run completed in {elapsed:.2f} seconds.")
    if result.returncode == 0:
        print("ALL TESTS PASSED! Quality gates satisfied.")
    else:
        print("TEST FAILURES DETECTED!")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
