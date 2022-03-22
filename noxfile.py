import nox

LOCATIONS = "src", "tests"
PYTHON_VERSIONS = ["3.8", "3.7", "3.6"]


@nox.session(python=PYTHON_VERSIONS)
def lint(session):
    args = session.posargs or LOCATIONS
    session.install("poetry")
    session.run("poetry", "install")
    session.run("poetry", "run", "flake8", *args)


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    args = session.posargs or LOCATIONS
    session.install("poetry")
    session.run("poetry", "install")
    session.run("poetry", "run", "pytest", *args)
    session.run("poetry", "run", "cucu", "run", "features")
