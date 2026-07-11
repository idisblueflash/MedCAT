from typing import List, Dict, Any, Set, Optional

import os
import re
import importlib.metadata
import pkg_resources
import platform
import logging


logger = logging.getLogger(__name__)


ENV_SNAPSHOT_FILE_NAME = "environment_snapshot.json"

PACKAGE_NAME = "medcat"


def _requirement_name(requirement: str) -> str:
    """Extract the bare distribution name from a PEP 508 requirement string."""
    # drop any environment marker, then the extras / version specifier
    requirement = requirement.split(";", 1)[0]
    return re.split(r"[@<=>~!\[ (]", requirement, 1)[0].strip()


def _load_pyproject_toml(path: str) -> Optional[Dict[str, Any]]:
    """Load a TOML file, or return None if no TOML parser is available."""
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # type: ignore
        except ModuleNotFoundError:
            return None
    with open(path, "rb") as f:
        return tomllib.load(f)


def _dependencies_from_pyproject() -> List[str]:
    """Read [project.dependencies] directly from pyproject.toml.

    Fallback for when MedCAT is run from a source checkout without being
    installed, so package metadata is unavailable.
    """
    pyproject_path = os.path.join(os.path.dirname(__file__),
                                  "..", "..", "..", "pyproject.toml")
    if not os.path.exists(pyproject_path):
        return []
    data = _load_pyproject_toml(pyproject_path)
    if data is not None:
        return data.get("project", {}).get("dependencies", [])
    # last resort without a TOML library (source checkout on Python 3.9/3.10)
    with open(pyproject_path) as f:
        text = f.read()
    match = re.search(r"(?ms)^\[project\].*?^dependencies\s*=\s*\[(.*?)\]", text)
    if not match:
        return []
    return re.findall(r"""["']([^"']+)["']""", match.group(1))


def get_direct_dependencies() -> Set[str]:
    """Get the set of direct dependency names.

    Reads the installed package metadata (i.e. ``[project.dependencies]`` in
    pyproject.toml) and returns the dependency names with versions, extras and
    environment markers stripped. Falls back to reading pyproject.toml directly
    when MedCAT is run from a source checkout without being installed.

    Returns:
        Set[str]: The set of direct dependency names.
    """
    try:
        requirements = importlib.metadata.requires(PACKAGE_NAME)
    except importlib.metadata.PackageNotFoundError:
        requirements = None
    if not requirements:
        requirements = _dependencies_from_pyproject()
    names = set()
    for requirement in requirements:
        # skip optional-dependency/extra requirements (MedCAT declares none,
        # but guard against it regardless)
        if "extra ==" in requirement:
            continue
        name = _requirement_name(requirement)
        if name:
            names.add(name)
    return names


def _update_installed_dependencies_recursive(
        gathered: Dict[str, str],
        package: pkg_resources.Distribution) -> Dict[str, str]:
    if package.project_name in gathered:
        logger.debug("Trying to update already found transitive dependency '%'",
                     package.egg_name)
        return gathered
    for req in package.requires():
        if req.project_name in gathered:
            logger.debug("Trying to look up already found transitive dependency '%'",
                         req.project_name)
            continue # don't look for it again
        try:
            dep = pkg_resources.get_distribution(req.project_name)
        except pkg_resources.DistributionNotFound as e:
            logger.warning("Unable to locate requirement '%s':", req.project_name,
                           exc_info=e)
            continue
        gathered[dep.project_name] = dep.version
        _update_installed_dependencies_recursive(gathered, dep)
    return gathered


def get_transitive_deps(direct_deps: List[str]) -> List[List[str]]:
    """Get the transitive dependencies of the direct dependencies.

    Args:
        direct_deps (List[str]): List of direct dependencies.

    Returns:
        List[List[str]]: The list of dependency names along with their versions.
    """
    # map from name to version so as to avoid multiples of the same package
    all_transitive_deps: Dict[str, str] = {}
    for dep in direct_deps:
        package = pkg_resources.get_distribution(dep)
        _update_installed_dependencies_recursive(all_transitive_deps, package)
    trans_deps = [list(td) for td in all_transitive_deps.items()]
    return sorted(trans_deps, key=lambda t: t[0])


def get_installed_packages() -> List[List[str]]:
    """Get the installed packages and their versions.

    Returns:
        List[List[str]]: List of lists. Each item contains of a dependency name and version.
    """
    direct_deps = get_direct_dependencies()
    installed_packages = []
    for package in pkg_resources.working_set:
        if package.project_name not in direct_deps:
            continue
        installed_packages.append([package.project_name, package.version])
    return installed_packages


def get_environment_info(include_transitive_deps: bool = True) -> Dict[str, Any]:
    """Get the current environment information.

    Args:
        include_transitive_deps (bool): Whether to include transitive dependencies. Defaults to True.

    This includes dependency versions, the OS, the CPU architecture and the python version.

    Returns:
        Dict[str, Any]: _description_
    """
    env_info = {
        "dependencies": get_installed_packages(),
        "os": platform.platform(),
        "cpu_architecture": platform.machine(),
        "python_version": platform.python_version()
    }
    if include_transitive_deps:
        direct_deps = [dep_name for dep_name, _ in env_info["dependencies"]]
        env_info["transitive_deps"] = get_transitive_deps(direct_deps)
    return env_info
