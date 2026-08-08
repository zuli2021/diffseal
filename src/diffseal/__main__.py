"""Allow `python -m diffseal` to behave like `diffseal`."""

from diffseal.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
