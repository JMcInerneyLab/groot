"""
Groot's core logic.

* This subpackage should be considered internal: Groot's API is exposed through `groot.__init__.py`.
* Groot's workflow is linear, so the stages are named after the order in which they appear.
* Note that despite this submodule's name, several algorithms are outsourced to user provided
  functions or external tools, which can be supplemented by providing a Groot extension:- see the `groot_ex` package.
* These algorithms are able to report their progress through Intermake (`MCMD`).
* The `gimmicks` subpackage contains features not required for groot's core logic, but which may be useful to the user.
"""


from . import gimmicks
from . import workflow



