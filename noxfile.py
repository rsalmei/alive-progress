import nox

@nox.session(python=["2.7", "3.5", "3.6", "3.7", "3.8"])
def tests(session):
    session.install('-r', 'requirements/test.txt')
    session.run('pytest')
