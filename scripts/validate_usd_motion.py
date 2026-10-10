"""Exercise single-drive USD mimic in CPU PhysX (ovphysx 0.6.3).

Angles in this low-level USD interface are degrees. Isaac articulation APIs
may use radians; follow the consuming API. Source assets are never modified.
"""
import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
import ovstage
import ovphysx
from ovphysx import PhysX, PhysXConfig
from ovphysx.types import ObjectScope, SimObjectType
from pxr import Usd, UsdPhysics, Sdf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--driver", default="taccap_right_finger_joint")
    parser.add_argument("--no-collision", action="store_true")
    parser.add_argument("--target", type=float, default=28.92)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    usd = Usd.Stage.Open(str(args.source))
    scene = UsdPhysics.Scene.Define(usd, "/PhysicsScene")
    scene.CreateGravityMagnitudeAttr(0)
    scene.GetPrim().AddAppliedSchema("PhysxSceneAPI")
    scene.GetPrim().CreateAttribute(
        "physxScene:enableGPUDynamics", Sdf.ValueTypeNames.Bool
    ).Set(False)
    scene.GetPrim().CreateAttribute(
        "physxScene:broadphaseType", Sdf.ValueTypeNames.Token
    ).Set("MBP")
    if args.no_collision:
        for prim in usd.Traverse():
            if prim.HasAPI(UsdPhysics.CollisionAPI):
                UsdPhysics.CollisionAPI(prim).CreateCollisionEnabledAttr(False)

    with tempfile.TemporaryDirectory(prefix="physx-probe-") as tmp:
        source = Path(tmp) / "scene.usdc"
        usd.Flatten().Export(str(source))
        ovstage.population.register_usd_schemas([str(ovphysx.codeless_schema_root())])
        PhysX.set_cpu_mode(True)
        physx = PhysX(config=PhysXConfig(num_threads=2))
        stage = ovstage.Stage("probe")
        ovstage.population.open_usd(
            stage, str(source), ordinal=1, domains=ovstage.PopulationDomain.PHYSICS
        )
        stage.advance_write_floor(ordinal=1).wait()
        physx.attach_ovstage(stage, read_ordinal=1)
        physx.step_sync(1 / 240)
        paths = ovstage.PathDictionary(stage)

        def read():
            values = {}
            with physx.read(
                SimObjectType.ARTICULATION_JOINT,
                ["jointPosition"],
                scope=ObjectScope.ALL,
            ) as result:
                for group in result.groups:
                    names = paths.get_path_strings(group.prim_list)
                    for name, tensor in zip(names, group.tensors):
                        if "_finger_joint" in name:
                            values[name] = tensor.numpy().tolist()
            return values

        report = {
            "source": str(args.source),
            "runtime": ovphysx.__version__,
            "collision": not args.no_collision,
            "initial": read(),
            "phases": [],
        }
        for target in (args.target, 0.0, args.target, 0.0):
            matched = 0
            with physx.write(
                SimObjectType.ARTICULATION_JOINT, "jointPositionTarget"
            ) as session:
                for group in session.groups:
                    names = paths.get_path_strings(group.prim_list)
                    for name, tensor in zip(names, group.tensors):
                        if name.endswith(args.driver):
                            tensor.fill_(target)
                            matched += 1
                    session.commit(group)
            assert matched, "No active gripper joints matched"
            for _ in range(720):
                physx.step_sync(1 / 240)
            positions = read()
            assert positions, "No gripper state returned by PhysX"
            for name, value in positions.items():
                if name.endswith(args.driver):
                    assert abs(value[0] - target) < 0.1, (name, value, target)
            coupling_errors = []
            for prim in usd.Traverse():
                rel = prim.GetRelationship("physxMimicJoint:rotZ:referenceJoint")
                if rel and rel.GetTargets():
                    follower, reference = str(prim.GetPath()), str(rel.GetTargets()[0])
                    if follower in positions:
                        gearing = prim.GetAttribute(
                            "physxMimicJoint:rotZ:gearing"
                        ).Get()
                        offset = prim.GetAttribute("physxMimicJoint:rotZ:offset").Get()
                        error = abs(
                            positions[follower][0]
                            + gearing * positions[reference][0]
                            + offset
                        )
                        coupling_errors.append(error)
                        assert error < 0.01, (follower, error)
            assert coupling_errors, "No executed mimic relation found"
            phase = {
                "target_deg": target,
                "positions_deg": positions,
                "max_mimic_error_deg": max(coupling_errors),
            }
            report["phases"].append(phase)
            print(json.dumps(phase), flush=True)
        report["passed"] = True
        if args.output:
            args.output.write_text(json.dumps(report, indent=2) + "\n")
        paths.__exit__(None, None, None)
        physx.detach_ovstage()
        physx.destroy()
        stage.destroy()


if __name__ == "__main__":
    main()
