# -*- coding: utf-8 -*-
"""VIOLATION: Interface Segregation - fat interface forces unused implementations."""

from abc import ABC, abstractmethod


class Worker(ABC):
    """Fat interface forcing all workers to implement every method."""

    @abstractmethod
    def code(self):
        ...

    @abstractmethod
    def test(self):
        ...

    @abstractmethod
    def design(self):
        ...

    @abstractmethod
    def manage(self):
        ...

    @abstractmethod
    def deploy(self):
        ...


class JuniorDeveloper(Worker):
    """Junior dev forced to implement manage/deploy which are not their role."""

    def code(self):
        return "Writing Python code"

    def test(self):
        return "Running unit tests"

    def design(self):
        raise NotImplementedError("Juniors do not design architecture")

    def manage(self):
        raise NotImplementedError("Juniors do not manage teams")

    def deploy(self):
        raise NotImplementedError("Juniors do not deploy to production")


class ProjectManager(Worker):
    """PM forced to implement code/test/deploy which are not their role."""

    def code(self):
        raise NotImplementedError("PMs do not write code")

    def test(self):
        raise NotImplementedError("PMs do not run tests")

    def design(self):
        return "Designing system architecture"

    def manage(self):
        return "Managing project timeline"

    def deploy(self):
        raise NotImplementedError("PMs do not deploy")
