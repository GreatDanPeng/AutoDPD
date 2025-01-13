#!/usr/bin/env python3
from autodepend.autodpd import autodpd

def main():
    """Entry point for the command line interface"""
    detector = autodpd()
    detector.main()

if __name__ == "__main__":
    main() 