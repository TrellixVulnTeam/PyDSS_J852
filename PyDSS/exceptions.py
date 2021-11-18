"""Exceptions used in PyDSS"""


class PyDssException(Exception):
    """Base class for all PyDSS exceptions"""


class InvalidConfiguration(PyDssException):
    """Raised when a bad configuration is detected."""


class InvalidParameter(PyDssException):
    """Raised when bad user input is detected."""


class OpenDssConvergenceError(PyDssException):
    """Raised when OpenDSS fails to converge on a solution."""


class OpenDssConvergenceErrorCountExceeded(PyDssException):
    """Raised when OpenDSS exceeds the threshold of convergence error counts."""


class OpenDssModelError(PyDssException):
    """Raised when OpenDSS fails to compile a model."""


class PyDssConvergenceError(PyDssException):
    """Raised when PyDSS fails to converge on a solution."""


class PyDssConvergenceMaxError(PyDssException):
    """Raised when PyDSS exceeds a max convergence error threshold."""


class PyDssConvergenceErrorCountExceeded(PyDssException):
    """Raised when PyDSS exceeds the threshold of convergence error counts."""
