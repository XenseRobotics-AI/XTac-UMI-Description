# Camera COM correction, 2026-10-23

The user supplied camera_com_corrected.png and requested the formal correction
with a manually fixed mass of 18 g. SW COM (cm) is
[0.009135, -2.305604, -7.877412]. The screenshot reports 17.9 g and
8.917957 cm^3; measured/assigned mass and SW inertia are separate inputs.

Existing SW-to-URDF axes are [Y, X, -Z]. The locked source STEP total-assembly
frame corresponds to flange_link in this asset. Camera entity and base share
the same frame, located 12 mm along flange +Z. Therefore the camera COM is
[-0.02305604, 0.00009135, 0.06677412] m in the physical camera link, and
[-0.02305604, 0.00009135, 0.07877412] m in flange_link.

The same source STEP camera occurrence [1,5,1] was independently integrated:
volume 8.917953125838249 cm^3, source COM in mm
[0.09135286930715453, -23.05603583594988, -78.77411991039652].
At 17.9 g, principal moments (g*cm^2) are
[18.1217114453201, 20.9367958116842, 21.6116741960832], consistent with
SW [18.121707, 20.936797, 21.611675] within exchange/report precision.
The reference-frame mapping was derived from the existing geometry transforms,
not fitted to the COM or moved to the optical center.

The original screenshot and temporary COM=0 input are retained in
superseded_camera_com.json and the original 2026-10-15 source files.
The active temporary override has been removed. Mass stays 18 g, and the
original SW principal axes/moments are retained without scaling. Meshes,
joint frames, optical/EEF frames, and all other part parameters are unchanged.
This is a source/geometry consistency correction, not hardware mass-distribution,
contact, dynamics or optical calibration. Screenshot redistribution rights
remain unconfirmed, as with the original sources.
