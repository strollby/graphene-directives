from nox import parametrize, session


@session(python=["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"])
@parametrize("graphene", ("3.0", "3.1", "3.2", "3.3", "3.4"))
def tests(session, graphene):  # noqa
    session.install(f"graphene=={graphene}")
    session.install("pytest", ".")
    session.run("pytest", "tests/")
