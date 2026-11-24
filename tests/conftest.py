"""Shared pytest fixtures."""

import pytest
from pxr import Sdr, Usd, UsdUtils


def _shader_registry_available():
    """Whether UsdPreviewSurface can be resolved in this USD build.

    usd-core ships without ``shaderDefs.usda``, so materials cannot be
    introspected; the compliance checker then either flags every shader as an
    unknown node or raises while dereferencing the registry.
    """
    try:
        return Sdr.Registry().GetShaderNodeByIdentifier("UsdPreviewSurface") is not None
    except Exception:  # noqa: BLE001 - a registry that cannot answer is a no
        return False


@pytest.fixture(scope="session")
def usd_compliance():
    """Validate a USD layer the way the component should ship.

    With a complete shader registry this is the stock ``UsdUtils`` compliance
    check. Without one (plain usd-core) the shader checks are impossible, so the
    layer is validated structurally instead: it must open, carry no external file
    dependencies and have no unresolved references. That keeps the asset honest
    in CI without encoding an environment limitation as a pass.
    """
    resolvable = _shader_registry_available()

    def check(path):
        if resolvable:
            checker = UsdUtils.ComplianceChecker()
            checker.CheckCompliance(str(path))
            assert not checker.GetErrors(), checker.GetErrors()
            assert not checker.GetFailedChecks(), checker.GetFailedChecks()
            assert not checker.GetWarnings(), checker.GetWarnings()
            return
        stage = Usd.Stage.Open(str(path))
        assert stage, f"{path} does not open"
        assert stage.GetDefaultPrim(), f"{path} has no default prim"
        _, assets, unresolved = UsdUtils.ComputeAllDependencies(str(path))
        assert not assets, assets
        assert not unresolved, unresolved

    return check
