#!/usr/bin/env python3
"""Build the web assets for the anonymous VAPS project page.

2026-09-17: the page now carries the sorted clip set of raps_video/CLIP_INVENTORY.md
-- both robots, simulation and hardware -- so this script builds three groups:
the original three G1 specialist renders and the two hardware failure clips (below),
the simulation gallery (the selector on each robot, the specialist arms), the
counterfactual replay, and the hardware predictor / closed-loop trials.

Sim clips: crop the stale burned-in banner strip (old colour scheme, and the
protective-fall clip's banner is mislabelled "NOMINAL POLICY (kto4dkrp)"),
then normalise to one 960x496 frame so the three tile evenly.

Real-robot failure clips: taken from the film's own processed copies
(raps_video/real robot video/blurred/fail_a.mp4, fail_b.mp4), built by
segment_blur.py -- robot sharp over a Gaussian-blurred frame, people removed
from the sharp region by YOLO person masks. The earlier in-script `privacy()`
pass is kept below for reference but is NOT used: it blurs a whole frame and
tracks the robot with a plain moving window, which reads far worse.
"""
import os, subprocess

# The research repository that holds the source footage (raps_video/ ...).
# Derived from this checkout's location so the path carries no user name;
# override with VAPS_ROOT if the two repositories do not sit side by side.
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ROOT = os.environ.get("VAPS_ROOT") or os.path.dirname(SITE)
OUT  = os.path.join(SITE, "static/videos")
IMG  = os.path.join(SITE, "static/images")
FPS  = 30

def run(cmd):
    subprocess.run(cmd, check=True)

# --- verbatim from raps_video/build_animatic.py --------------------------
def privacy(inlab, outlab, xc, box, half=310, feather=90, bfeather=58):
    x0, y0, x1, y1 = box
    m1 = ("color=black:s=960x540:r=%d:d=30,"
          "geq=lum='255*clip(min((X-((%s)-%d))\\,(((%s)+%d)-X))/%d\\,0\\,1)',format=gray"
          % (FPS, xc, half, xc, half, feather))
    m2 = ("color=black:s=960x540:r=%d:d=30,"
          "geq=lum='255*clip(min(min((X-(%d))\\,((%d)-X))\\,min((Y-(%d))\\,((%d)-Y)))/%d\\,0\\,1)',format=gray"
          % (FPS, x0, x1, y0, y1, bfeather))
    return ("%sscale=960:540,setsar=1,split=2[pv_a][pv_b];"
            "[pv_a]boxblur=10:2[pv_bg];"
            "%s[pv_m1];"
            "[pv_b]format=yuva420p[pv_bA];[pv_bA][pv_m1]alphamerge[pv_sharp];"
            "[pv_bg][pv_sharp]overlay[pv_c];"
            "[pv_c]split=2[pv_c1][pv_c2];"
            "[pv_c2]boxblur=22:6,format=yuva420p[pv_pb];"
            "%s[pv_m2];"
            "[pv_pb][pv_m2]alphamerge[pv_pbs];"
            "[pv_c1][pv_pbs]overlay%s"
            % (inlab, m1, m2, outlab))

PRIV = {
    "bad1": dict(xc="185+113*(T-0.5)", box=(345, 130, 675, 425)),
    "bad2": dict(xc="845-118*(T-0.5)", box=(420, -60, 790, 285)),
}
# ------------------------------------------------------------------------

ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
       "-an", "-movflags", "+faststart"]

def encode(src, dst, vf, ss=None, t=None):
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if ss is not None: cmd += ["-ss", str(ss)]
    cmd += ["-i", src]
    if t is not None: cmd += ["-t", str(t)]
    run(cmd + ["-vf", vf] + ENC + [os.path.join(OUT, dst)])
    print("  ", dst)

def encode_priv(src, dst, key, ss, t):
    graph = privacy("[0:v]", "[pv_out]", **PRIV[key]) + ";[pv_out]scale=960:496:force_original_aspect_ratio=increase,crop=960:496,setsar=1[v]"
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-i", src, "-t", str(t),
         "-filter_complex", graph, "-map", "[v]"] + ENC + [os.path.join(OUT, dst)])
    print("  ", dst)

SIM = os.path.join(ROOT, "raps_video/sim video")
REAL = os.path.join(ROOT, "raps_video/real robot video")

print("sim clips (banner strip cropped):")
# 960x540, no banner but crop to the common frame
encode(os.path.join(SIM, "nominal_sideflip466a.mp4"), "sim_nominal.mp4",
       "crop=960:496:0:44,scale=960:496,setsar=1")
# 1280x720, violet banner + 1px violet border
encode(os.path.join(SIM, "abort_counterfactual.mp4"), "sim_abort.mp4",
       "crop=1264:652:8:60,scale=960:496,setsar=1")
# 960x540, stale blue banner reading "NOMINAL POLICY (kto4dkrp)", plus a blue
# border on the other three sides
encode(os.path.join(SIM, "protective_fall_v9.mp4"), "sim_protective.mp4",
       "crop=944:486:8:46,scale=960:496,setsar=1")

print("real-robot clips:")
# 2026-09-09: the hardware abort / protective-fall trials of the paper's Fig. 1.
# Annotated lab exports (labels + x0.25 segment burnt in, no bystanders); only cropped.
encode(os.path.join(REAL, "abort/74_cut_annotated.mp4"), "real_abort.mp4",
       "crop=960:496:0:22,setsar=1")
encode(os.path.join(REAL, "pFALL/sf71_cut_annotated.mp4"), "real_protfall.mp4",
       "crop=960:496:0:22,setsar=1")
# ss=2.2 lands just before the flip; the source's first 2 s are set-up
# 2026-09-16: the nominal flip of the paper's Fig. 1 (same corridor as the abort /
# protective-fall clips); replaces 32-nominal-1.qt (different room). Raw footage, no labels.
encode(os.path.join(REAL, "nominal/66.qt"), "real_nominal.mp4",
       "crop=960:496:0:22,setsar=1", ss=6.5, t=6.0)
# 2026-09-17: the film's own processed failure clips (segment_blur.py), which
# keep the robot sharp and hide every person. They replace the encode_priv()
# versions built from the raw .qt sources, which blurred most of the frame.
encode(os.path.join(REAL, "blurred/fail_a.mp4"), "real_fail_1.mp4", "setsar=1")
encode(os.path.join(REAL, "blurred/fail_b.mp4"), "real_fail_2.mp4", "setsar=1")

SIMD = os.path.join(ROOT, "raps_video/sim video")
CFD  = os.path.join(ROOT, "raps_video/counterfactual_rollout")

print("simulation gallery:")
# the selector with its viability read-out, one render per robot (1280x720 -> 960x540)
encode(os.path.join(SIMD, "g1_RAPS_sim.mp4"),   "g1_sim_vaps.mp4",  "scale=960:540,setsar=1")
encode(os.path.join(SIMD, "limx_RAPS_sim.mp4"), "oli_sim_vaps.mp4", "scale=960:540,setsar=1")
# four arms back to back, 3.5 s each; the 4th (the selector) is CUT -- its banner
# still reads RAPS, the paper's old name. 0-10.5 s = nominal / abort / protective fall.
encode(os.path.join(SIMD, "limx_specialist.mp4"), "oli_sim_specialists.mp4",
       "scale=640:480,setsar=1", t=10.5)

print("counterfactual replay:")
# frame-locked, switch on frame 150 (clip clock 5.05 s). The real panel's last clean
# frame is +3.4 s past the switch (source 6.4 s), where a bystander enters; every
# panel is cut there so the four stay locked to one clock.
for src, dst in [("real_robot", "cf_real"), ("nominal", "cf_nominal"),
                 ("abort_sim", "cf_abort"), ("safe_fall", "cf_protfall")]:
    encode(os.path.join(CFD, src + ".mp4"), dst + ".mp4", "setsar=1", t=6.4)

print("hardware predictor trials:")
# already face-passed by blur_bystanders.py and approved from blur_review_beat9.mp4
encode(os.path.join(REAL, "blurred/pred_a_faceblur.mp4"), "oli_pred_1.mp4", "setsar=1")
encode(os.path.join(REAL, "blurred/pred_b_faceblur.mp4"), "oli_pred_2.mp4", "setsar=1")

print("hardware closed loop:")
# 49: the film's own feathered patch, RAPS_PRIV["r1"] = (0, 30, 168, 300, "rtb")
_p = ("[0:v]split=2[c0][c1];[c1]crop=168:300:0:30,gblur=sigma=24:steps=3,format=rgba,"
      "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
      "a='min(min(255*clip((W-X)/44\,0\,1)\,255*clip(Y/44\,0\,1))\,255*clip((H-Y)/44\,0\,1))'[p];"
      "[c0][p]overlay=0:30,setsar=1[v]")
run(["ffmpeg", "-y", "-v", "error", "-ss", "4.0", "-i", os.path.join(REAL, "49_RAPS.mp4"),
     "-t", "11.0", "-filter_complex", _p, "-map", "[v]"] + ENC
    + [os.path.join(OUT, "oli_closedloop_abort.mp4")])
print("   oli_closedloop_abort.mp4")
# 62: the full cascade. No bystanders (MISSING_ASSETS R7), so no patch; it carries a
# burned-in x1 / x0.25 speed badge, so it must NOT be retimed.
encode(os.path.join(REAL, "62_3l_raps.mp4"), "oli_closedloop_cascade.mp4",
       "setsar=1", ss=5.5, t=11.5)

print("posters:")
for name, t in [("sim_nominal", 1.0), ("sim_abort", 2.0), ("sim_protective", 2.2),
                ("real_nominal", 1.5), ("real_fail_1", 3.2), ("real_fail_2", 3.2),
                ("real_abort", 8.6), ("real_protfall", 6.0),
                ("g1_sim_vaps", 2.6), ("oli_sim_vaps", 2.4), ("oli_sim_specialists", 1.2),
                ("cf_real", 5.6), ("cf_nominal", 5.6), ("cf_abort", 5.6), ("cf_protfall", 5.6),
                ("oli_pred_1", 3.0), ("oli_pred_2", 3.0),
                ("oli_closedloop_abort", 6.5), ("oli_closedloop_cascade", 7.0)]:
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(t),
         "-i", os.path.join(OUT, name + ".mp4"), "-frames:v", "1",
         "-q:v", "4", os.path.join(IMG, "poster_" + name + ".jpg")])
    print("   poster_%s.jpg" % name)
