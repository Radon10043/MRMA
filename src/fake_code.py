"""
Author       : Radon
Date         : 2025-07-12 05:46:51
LastEditors  : Radon
LastEditTime : 2025-07-12 14:40:03
Description  : Just for debugging
"""

FAKE_CPP = """
#include <iostream>
using namespace std;
int main() { cout << "Hello world!" << endl; return 0; }
"""

FAKE_JAVA = """
import org.junit.jupiter.api.Test;

public class DriverTest {
    public void test0() {
        System.out.println("Hello world!");
    }
}
"""

FAKE_PYTHON = """
import unittest
import os, subprocess, time

from parameterized import parameterized

class TestingClass(unittest.TestCase):
    def test0(self, tc: str):
        print("Hello world!")

if __name__ == "__main__":
    unittest.main()
"""
