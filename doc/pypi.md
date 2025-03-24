How to push a new version to PyPI

* Test locally
  ```
  deactivate; rm ~/virtualenvs/junk -rf; virtualenv ~/virtualenvs/junk; . ~/virtualenvs/junk/bin/activate
  pip install .
  resman echo 123
  ```

* Bump version number in ` pyproject.toml`

* Build
  ```
  python -m build
  ```

* Push to PyPI test server
  ```
  python -m twine upload --repository testpypi --verbose --skip-existing dist/*
  ```

* When ready, push to PyPI
  ```
  python -m twine upload --repository pypi --verbose --skip-existing dist/*
  ```

