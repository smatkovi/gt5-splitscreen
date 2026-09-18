#!/usr/bin/env python3
"""Start countdown for the 3P/4P split screen (projects/gt5/race/RaceRoot.ad).

GT5 draws the start countdown and the GO message from a single widget pair
(Info::CountDown, Info::Go) that the native race display face positions for one or two
windows.  With three or four windows neither shows up any more.

This patch gives every window its own copy: at the first countdown tick, copies of
Info::CountDown and Info::Go are appended to ROOT and placed at the centre of each
quadrant; onCountDownDefault / onStartVehicle / resetDisplay then drive the copies in
addition to the originals.  Two or fewer windows are left untouched.

Logging (log4p, from patch_race_log_w6.py) records every countdown callback so a run can
be checked against the log even if nothing becomes visible.
Usage: patch_countdown_split.py <race project dir>
"""
import os, sys

d = sys.argv[1] if len(sys.argv) > 1 else '.'
p = os.path.join(d, 'RaceRoot.ad')
t = open(p, encoding='utf-8').read()
if 'sModCountDown' in t:
    print('already patched', p); sys.exit(0)

# ---------------------------------------------------------------- helper methods
helper = '''    // --- 4P split patch: per-window copies of the start countdown and the GO message.
    static sModCountDown = nil;    // one copy of Info::CountDown per window
    static sModGo = nil;           // one copy of Info::Go per window
    static sModCDWinN = 0;         // window count the copies were built for

    // Quadrant centres: 4 windows TL, TR, BL, BR; 3 windows TL, BL, BR (same order as the HUD).
    method modSplitCountDownSetup(context)
    {
        var n = main::ORG.window_max;
        if (n < 3 || sModCDWinN == n)
            return;

        modSplitCountDownHide();
        modSplitGoShow(false);

        sModCountDown = [];
        sModGo = [];

        for (var k = 0; k < n; k++)
        {
            var q = (n == 3) ? ((k == 0) ? 0 : k + 1) : k;
            var cx = ((q == 1 || q == 3) ? 1440 : 480).toFloat();
            var cy = ((q >= 2) ? 810 : 270).toFloat();

            var C = Info::CountDown.doCopy();
            ROOT.appendChild(context, C);
            C.x = cx - C.w / 2;
            C.y = cy - C.h / 2;
            C.visible = false;
            sModCountDown.push(C);

            var G = Info::Go.doCopy();
            ROOT.appendChild(context, G);
            G.x = cx - G.w / 2;
            G.y = cy - G.h / 2;
            G.visible = false;
            sModGo.push(G);
        }

        sModCDWinN = n;
        log4p("CD: built " + n.toString() + " countdown copies");
    }

    method modSplitCountDownShow(context, count)
    {
        modSplitCountDownSetup(context);
        if (sModCountDown == nil)
            return;

        foreach (var C in sModCountDown)
        {
            C.CD_1.visible = (count == 1) ? true : false;
            C.CD_2.visible = (count == 2) ? true : false;
            C.CD_3.visible = (count == 3) ? true : false;
            C.ScalarInterpolator.restart();
            C.visible = true;
        }

        // the stock widget sits in the middle of the whole screen, across the window borders
        Info::CountDown.visible = false;
    }

    function modSplitCountDownHide()
    {
        if (sModCountDown == nil)
            return;
        foreach (var C in sModCountDown)
            C.visible = false;
    }

    // Called from Go_Message, which is a plain function without a context - the copies must
    // already exist by then (built at the first countdown tick, or in resetDisplay).
    function modSplitGoShow(show)
    {
        if (sModGo == nil)
            return;

        foreach (var G in sModGo)
        {
            if (show)
            {
                G.ScalarInterpolator.restart();
                G.VectorInterpolator.restart();
                G.ImageFace0::ScalarInterpolator.restart();
            }
            G.visible = show;
        }
    }

'''
anchor = '    method onInitialize(context)\n'
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

# ---------------------------------------------------------------- onCountDown: log every tick
anchor = '''    method onCountDown(context, count)
    {
        if (gSequenceCondition.isDemo())
            return;
'''
assert t.count(anchor) == 1
t = t.replace(anchor, '''    method onCountDown(context, count)
    {
        log4p("CD: onCountDown count=" + count.toString()
              + " winmax=" + main::ORG.window_max.toString()
              + " demo=" + (gSequenceCondition.isDemo() ? "1" : "0"));

        if (gSequenceCondition.isDemo())
            return;
''')

# ---------------------------------------------------------------- drive the copies
anchor = '''            Info::CountDown::ScalarInterpolator.restart();
            Info::CountDown.visible = true;
'''
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + '''            modSplitCountDownShow(context, count);
''')

# ---------------------------------------------------------------- hide them again
anchor = '''    method onStartVehicle(context, slot_id, disp_start, start_sound)
    {
        Info::CountDown.visible = false;
'''
assert t.count(anchor) == 1
t = t.replace(anchor, '''    method onStartVehicle(context, slot_id, disp_start, start_sound)
    {
        log4p("CD: onStartVehicle slot=" + slot_id.toString());
        Info::CountDown.visible = false;
        modSplitCountDownHide();
''')

anchor = '''    method onOvertakeRestart(context, slot_id)
    {
'''
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + '''        modSplitCountDownHide();
''')

anchor = '''    method resetDisplay(context)
    {
        ROOT.visible = true;
        Info::CountDown.visible = false;
'''
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + '''        modSplitCountDownSetup(context);
        modSplitCountDownHide();
        modSplitGoShow(false);
''')

# ---------------------------------------------------------------- GO message for every window
anchor = '''            W.visible = true;
        }
    }

    function GoalMessage(finish, win, lose, succ, disq)'''
assert t.count(anchor) == 1, 'Go_Message tail changed: %d hits' % t.count(anchor)
t = t.replace(anchor, '''            W.visible = true;
        }

        if (sModGo != nil)
        {
            modSplitGoShow(toinit == true);
            W.visible = false;   // the stock widget straddles the window borders
        }
    }

    function GoalMessage(finish, win, lose, succ, disq)''')

open(p, 'w', encoding='utf-8').write(t)
print('patched', p)
