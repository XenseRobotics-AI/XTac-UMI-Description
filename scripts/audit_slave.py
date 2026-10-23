"""Audit every URDF field, mesh byte, source file and physical-property conversion.

Compares a fixed downstream baseline, the untouched vendor snapshot and the
adapted package. Optional live-source verification never writes to upstream.
"""

import argparse
import hashlib
import json
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "ros/taccap_description"
VENDOR = ROOT / "vendor/taccap_slave"
SOURCE = VENDOR / "source"
BASELINE = "f2d701e"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def flatten(root):
    """Include all attributes, meaningful text and child identity/order per node."""
    result = {}

    def visit(element, path):
        result[path + "/@attributes"] = dict(sorted(element.attrib.items()))
        if element.text and element.text.strip():
            result[path + "/text()"] = element.text.strip()
        counts = {}
        identities = []
        for child in element:
            counts[child.tag] = counts.get(child.tag, 0) + 1
            key = f"{child.tag}[@name='{child.get('name')}']" if child.get("name") else f"{child.tag}[{counts[child.tag]}]"
            identities.append(key)
            visit(child, path + "/" + key)
        result[path + "/children_order"] = identities
    visit(root, root.tag)
    return result


def differences(before, after):
    return [{"field": key, "before": before.get(key), "after": after.get(key)}
            for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]


def frame(origin):
    pose = np.eye(4)
    if origin is not None:
        pose[:3, 3] = np.fromstring(origin.get("xyz", "0 0 0"), sep=" ")
        pose[:3, :3] = Rotation.from_euler("xyz", np.fromstring(origin.get("rpy", "0 0 0"), sep=" ")).as_matrix()
    return pose


def poses(root, angle):
    joints = root.findall("joint")
    children = {j.find("child").get("link") for j in joints}
    roots = {l.get("name") for l in root.findall("link")} - children
    assert len(roots) == 1
    result = {roots.pop(): np.eye(4)}
    pending = list(joints)
    while pending:
        before = len(pending)
        for joint in pending[:]:
            parent = joint.find("parent").get("link")
            if parent not in result:
                continue
            motion = np.eye(4)
            if joint.get("type") == "revolute":
                mimic = joint.find("mimic")
                q = angle if mimic is None else angle * float(mimic.get("multiplier", "1")) + float(mimic.get("offset", "0"))
                axis = np.fromstring(joint.find("axis").get("xyz"), sep=" ")
                motion[:3, :3] = Rotation.from_rotvec(axis * q).as_matrix()
            result[joint.find("child").get("link")] = result[parent] @ frame(joint.find("origin")) @ motion
            pending.remove(joint)
        assert len(pending) < before
    return result


def inertial_data(link):
    inertial = link.find("inertial")
    if inertial is None:
        return None
    v = {k: float(x) for k, x in inertial.find("inertia").attrib.items()}
    tensor = np.array([[v["ixx"], v["ixy"], v["ixz"]],
                       [v["ixy"], v["iyy"], v["iyz"]],
                       [v["ixz"], v["iyz"], v["izz"]]])
    return {"mass_kg": float(inertial.find("mass").get("value")),
            "com_m": frame(inertial.find("origin"))[:3, 3].tolist(),
            "origin_rpy_rad": inertial.find("origin").get("rpy", "0 0 0"),
            "tensor_kg_m2": tensor.tolist(),
            "principal_moments_kg_m2": np.linalg.eigvalsh(tensor).tolist()}


def aggregate(root):
    fk = poses(root, 0)
    base_inverse = np.linalg.inv(fk["taccap_base_link"])
    items = []
    for link in root.findall("link"):
        inertial = inertial_data(link)
        if inertial:
            t = base_inverse @ fk[link.get("name")] @ frame(link.find("inertial/origin"))
            items.append((inertial["mass_kg"], t[:3, 3], t[:3, :3] @ inertial["tensor_kg_m2"] @ t[:3, :3].T))
    mass = sum(m for m, _, _ in items)
    com = sum(m * c for m, c, _ in items) / mass
    tensor = np.zeros((3, 3))
    for m, c, i in items:
        r = c - com
        tensor += i + m * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    return {"mass_kg": mass, "com_in_base_m": com.tolist(), "centroidal_tensor_in_base_kg_m2": tensor.tolist()}


def mesh_info(data):
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + 50 * count
    vertices = np.ndarray((count, 9), dtype="<f4", buffer=data, offset=96, strides=(50, 4)).reshape(-1, 3)
    return {"sha256": digest(data), "bytes": len(data), "triangles": count,
            "native_bounds_m": [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--live-source", type=Path, help="Path to the upstream asset directory (read only)")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/slave-v2026.10.23-audit")
    args = parser.parse_args()
    baseline = git("rev-parse", args.baseline).decode().strip()
    lock = json.loads((VENDOR / "upstream.json").read_text())
    hashes = inventory(SOURCE)
    assert hashes == lock["files_sha256"], "Vendor snapshot changed"
    if args.live_source:
        assert inventory(args.live_source) == hashes, "Live upstream changed since capture"
    package_before = {}
    for path in git("ls-tree", "-r", "--name-only", baseline, "--", "ros/taccap_description").decode().splitlines():
        package_before[str(Path(path).relative_to("ros/taccap_description"))] = digest(git("show", f"{baseline}:{path}"))
    package_after = inventory(ASSETS)
    report = {"baseline_commit": baseline, "upstream": {"repository": lock["repository"], "path": lock["path"], "revision": lock["revision"]},
              "live_source_matches_snapshot": True if args.live_source else None,
              "upstream_files_sha256": hashes,
              "package_file_inventory": {"baseline": package_before, "current": package_after},
              "package_file_changes": differences(package_before, package_after),
              "models": {}, "meshes": {}, "physical_conversion": {}}
    models = {}
    for mounted in (False, True):
        suffix = "_with_mount" if mounted else ""
        relative = f"urdf/taccap_g1_slave{suffix}.urdf"
        old = ET.fromstring(git("show", f"{baseline}:ros/taccap_description/{relative}"))
        raw = ET.parse(SOURCE / relative).getroot()
        local = ET.parse(ASSETS / relative).getroot()
        models[mounted] = (old, raw, local)
        mapped = ET.fromstring(ET.tostring(raw))
        if mounted:
            mapped.find("link[@name='flange_link']").set("name", "taccap_mount_link")
            mapped.find("joint[@name='flange_to_base_joint']").set("name", "taccap_mount_joint")
            mapped.find("joint[@name='taccap_mount_joint']/parent").set("link", "taccap_mount_link")
        else:
            mapped.remove(mapped.find("link[@name='flange_link']"))
            mapped.remove(mapped.find("joint[@name='flange_to_base_joint']"))
        mapped_diff = differences(flatten(mapped), flatten(local))
        # All remaining field differences MUST be the two approved effort values.
        assert len(mapped_diff) == 2, mapped_diff
        for difference in mapped_diff:
            assert difference["field"].endswith("/limit[1]/@attributes")
            before, after = difference["before"].copy(), difference["after"].copy()
            assert before.pop("effort") == "4" and after.pop("effort") == "1.1"
            assert before == after
        geometry_errors = []
        for q in (0, .25 * .5047492196767601, .5047492196767601):
            raw_fk, local_fk = poses(raw, q), poses(local, q)
            shift = np.eye(4)
            shift[2, 3] = 0 if mounted else -.012
            for name, pose in local_fk.items():
                raw_name = "flange_link" if name == "taccap_mount_link" else name
                geometry_errors.append(float(np.max(np.abs(pose - shift @ raw_fk[raw_name]))))
        report["models"][suffix or "bare"] = {
            "baseline_to_upstream_every_field": differences(flatten(old), flatten(raw)),
            "baseline_to_current_every_field": differences(flatten(old), flatten(local)),
            "upstream_to_current_every_field": differences(flatten(raw), flatten(local)),
            "after_explicit_root_mapping": mapped_diff,
            "baseline_links": {l.get("name"): inertial_data(l) for l in old.findall("link")},
            "upstream_links": {l.get("name"): inertial_data(l) for l in raw.findall("link")},
            "current_links": {l.get("name"): inertial_data(l) for l in local.findall("link")},
            "aggregate": {"baseline": aggregate(old), "upstream": aggregate(raw), "current": aggregate(local)},
            "max_fk_error_after_root_mapping": max(geometry_errors)}
        assert max(geometry_errors) < 1e-14
    for relative in package_before:
        if relative.lower().endswith(".stl"):
            report["meshes"]["baseline/" + relative] = mesh_info(git("show", f"{baseline}:ros/taccap_description/{relative}"))
    for relative in hashes:
        if relative.lower().endswith(".stl"):
            data = (SOURCE / relative).read_bytes()
            assert (ASSETS / relative).read_bytes() == data
            report["meshes"]["upstream_and_current/" + relative] = mesh_info(data)
    # Recompute all physical conversions from recorded SW inputs independently
    # of both import/URDF generators, including the measurement finger pose.
    config = json.loads((SOURCE / "config/model.json").read_text())
    measurement = json.loads((SOURCE / "provenance/finger_reference.json").read_text())["measurement_driver_angle_rad"]
    raw = models[True][1]
    fk = poses(raw, measurement)
    sw_rotation = np.array(config["sw_reference"]["sw_to_mount_rotation"], dtype=float)
    for part, values in config["parts"].items():
        link = raw.find(f"link[@name='{values['link']}']")
        actual = inertial_data(link)
        pose = fk[values["link"]]
        com = (np.linalg.inv(pose) @ np.r_[sw_rotation @ (np.array(values["com_cm"]) * .01), 1])[:3]
        u, _, vt = np.linalg.svd(np.array(values["axes"]).T)
        axes = u @ vt
        sw_tensor = axes @ np.diag(np.array(values["moments"]) * 1e-7) @ axes.T
        rotate = pose[:3, :3].T @ sw_rotation
        tensor = rotate @ sw_tensor @ rotate.T
        errors = {"mass_error_kg": abs(actual["mass_kg"] - values["mass_g"] / 1000),
                  "max_com_error_m": float(np.max(np.abs(com - actual["com_m"]))),
                  "max_tensor_error_kg_m2": float(np.max(np.abs(tensor - actual["tensor_kg_m2"])))}
        assert errors["mass_error_kg"] < 1e-15 and errors["max_com_error_m"] < 1e-14 and errors["max_tensor_error_kg_m2"] < 1e-14, (part, errors)
        report["physical_conversion"][part] = {"measurement_driver_angle_rad": measurement, "recomputed_com_m": com.tolist(),
                                                    "recomputed_tensor_kg_m2": tensor.tolist(), **errors}
    manifest = json.loads((SOURCE / "asset.json").read_text())
    report["upstream_manifest_hash_discrepancies"] = [
        {"path": path, "declared": entry["sha256"], "actual": hashes.get(path)}
        for path, entry in manifest["files"].items() if entry["sha256"] != hashes.get(path)]
    # A second read detects concurrent upstream changes during the audit.
    if args.live_source:
        assert inventory(args.live_source) == hashes, "Live upstream changed during audit"
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "details.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    lines = ["# 从夹爪逐项差异审计", "", f"本仓库原版：`{baseline}`。上游：`{lock['path']}`，commit：`{lock['revision'] or '尚未固定'}`。",
             "", "本次运行逐文件复核了实时上游与快照（如传入 `--live-source`）；完整字段、文件哈希、网格边界、惯量张量及全部差异见 [details.json](details.json)。",
             "", "## 质量与物理 link", "", "| Link | 原版 kg | 上游 kg | 适配后 kg |", "| --- | ---: | ---: | ---: |"]
    old_links, raw_links, local_links = [report["models"]["_with_mount"][key] for key in ("baseline_links", "upstream_links", "current_links")]
    for name in local_links:
        upstream_name = "flange_link" if name == "taccap_mount_link" else name
        def mass(mapping, key):
            if key not in mapping:
                return "无该 link"
            return str(mapping[key]["mass_kg"]) if mapping[key] else "无惯性"
        lines.append(f"| `{name}` | {mass(old_links, name)} | {mass(raw_links, upstream_name)} | {mass(local_links, name)} |")
    lines += ["", "## 每个物理 link 的质心（link 坐标，m）", "", "| Link | 原版 xyz | 新版 xyz |", "| --- | --- | --- |"]
    for name, values in local_links.items():
        if values:
            old = old_links.get(name)
            before = old["com_m"] if old else "无惯性/无该 link"
            lines.append(f"| `{name}` | `{before}` | `{values['com_m']}` |")
    lines += ["", "## 完整惯量张量六个独立元素（kg·m²，质心处、link 轴）", "", "| Link / 版本 | Ixx | Iyy | Izz | Ixy | Ixz | Iyz |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name, values in local_links.items():
        if values:
            for label, item in (("原版", old_links.get(name)), ("新版", values)):
                if item:
                    tensor = np.array(item["tensor_kg_m2"])
                    six = [tensor[0,0],tensor[1,1],tensor[2,2],tensor[0,1],tensor[0,2],tensor[1,2]]
                    lines.append(f"| `{name}` / {label} | " + " | ".join(f"{v:.16g}" for v in six) + " |")
    lines += ["", "## 各入口总质量", "", "| 入口 | 原版 kg | 上游 kg | 适配后 kg |", "| --- | ---: | ---: | ---: |"]
    for variant, details in report["models"].items():
        totals = [f"{details['aggregate'][k]['mass_kg']:.8g}" for k in ("baseline", "upstream", "current")]
        lines.append(f"| {variant} | {' | '.join(totals)} |")
    lines += ["", "## 网格逐文件核对", "", "全部 11 个上游 visual/collision 网格与当前包逐字节相同。下表坐标边界与完整 SHA 在 JSON 中。",
              "", "| 文件 | 三角形数 | 字节数 |", "| --- | ---: | ---: |"]
    for name, details in report["meshes"].items():
        lines.append(f"| `{name}` | {details['triangles']} | {details['bytes']} |")
    lines += ["", "## 独立物理属性换算", "", "使用上游记录的 SW→法兰旋转、cm→m、g·cm²→kg·m²、主轴正交化及测量姿态独立重算六个部件。",
              "", "| 部件 | 质量误差 kg | 最大质心误差 m | 最大张量元素误差 kg·m² |", "| --- | ---: | ---: | ---: |"]
    for name, errors in report["physical_conversion"].items():
        lines.append(f"| {name} | {errors['mass_error_kg']:.3g} | {errors['max_com_error_m']:.3g} | {errors['max_tensor_error_kg_m2']:.3g} |")
    lines += ["", f"上游 asset.json 声明哈希不一致项：{len(report['upstream_manifest_hash_discrepancies'])}（完整明细在 JSON 中）。",
              "", "详见[差异解释与处理结论](../../docs/SLAVE_V2026_10_23_DIFF.md)。",
              "", "## 适配差异封闭检查", "", "对两个入口逐属性及子元素顺序比较，在明确根坐标映射后，差异仅为两个夹指的 effort 从 4 改为 1.1。三个开合姿态下，所有 link 的 FK 与映射后上游一致。",
              "", "XML 声明、缩进、生成注释随本仓库生成器变化；上述字段核对包含所有 XML 属性、有意义文本和子元素顺序，不把这些序列化差异当作物理参数。"]
    (args.output / "README.md").write_text("\n".join(lines) + "\n")
    print(f"Audit complete: {len(hashes)} source files, {len(report['meshes'])} mesh versions, 6 independent physical conversions")
    print(f"Manifest hash discrepancies: {len(report['upstream_manifest_hash_discrepancies'])}")
    print(args.output)


if __name__ == "__main__":
    main()
