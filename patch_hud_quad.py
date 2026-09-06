#!/usr/bin/env python3
"""4P split patch for the race HUD (projects/gt5/race/OnboardMeterRoot.ad).

GT5's on-board HUD knows one window (1P layout) or two stacked windows (sLayoutSprit + DivWork copy).
With three or four windows it fell back to the 1P layout: one race map for window 0, the big
speedometer/tachometer panel drawn across the bottom of the screen.  This adds a quadrant layout for
sWinN >= 3: window 0 keeps ROOT's widgets (top-left quadrant), windows 1..3 get widget copies in
DivWork and further containers placed at their quadrant; every window gets its own course map.
The car meters (speedometer, rev counter, gear indicator) are hidden in this layout (requested).
Usage: patch_hud_quad.py <race project dir>
"""
import os, sys
d = sys.argv[1] if len(sys.argv) > 1 else '.'
p = os.path.join(d, 'OnboardMeterRoot.ad')
t = open(p, encoding='utf-8').read()
if 'sLayoutQuad' in t:
    print('already patched', p); sys.exit(0)

# 1. layout table + container list
anchor = '''    static sRacerCol = [
'''
assert t.count(anchor) == 1
t = t.replace(anchor, '''    // --- 4P split patch: HUD positions inside one 960x540 quadrant window
    static sLayoutQuad = [
        [Info::SectionTime,      250, 140],
        [Info::DiffTime,         250, 165],
        [Info::Current,          250, 100],
        [WongWay,                462, 150],
        [Adjuster,               366, 160],
        [InfoLeft::RacePosition, 30, 16],
        [InfoLeft::LapNumber,    258, 16],
        [MapClip,                10, 60],
        [InfoRight::TotalTime,   586, 16],
        [InfoRight::BestLap,     586, 108]
    ];
    static sQuadDivs = [];

''' + anchor)

# 2. the quadrant branch
anchor = '''        else
        {
            InfoRight::RacerPane.initialize(context, DriverName);
'''
assert t.count(anchor) == 1
branch = '''        else if (sWinN >= 3)
        {
            // --- 4P split patch: quadrant layout for 3 or 4 windows.
            MapClip.window_size = [220, 220];
            InfoRight::LastLap.visible = false;
            InfoRight::RacerPane.visible = false;
            Parette::Gmonitor.visible = false;
            Parette::Boost.visible = false;
            Parette::Input.visible = false;
            Parette::Gas.visible = false;
            Parette::Tire.visible = false;
            Panel.visible = false;

            foreach (var W in sLayoutQuad)
            {
                var B = W[0];
                B.x = W[1].toFloat();
                B.y = W[2].toFloat();
            }

            var wlist = [
                RaceDisplayFace,
                MapClip,
                Info,
                InfoLeft,
                InfoRight,
                Parette,
                Adjuster,
                WongWay
            ];

            // containers for windows 1..3: DivWork plus copies of it, created once and reused
            var containers = [DivWork];
            while (sQuadDivs.size < sWinN - 2)
            {
                var ND = DivWork.doCopy();
                ROOT.appendChild(context, ND);
                sQuadDivs.push(ND);
            }
            for (var k = 0; k < sWinN - 2; k++)
                containers.push(sQuadDivs[k]);

            for (var k = 1; k < sWinN; k++)
            {
                var D = containers[k - 1];
                D.clearWindow(context);
                foreach (var W in wlist)
                {
                    var A = W.doCopy();
                    D.appendChild(context, A);
                }
                // window order: 4 windows = TL, TR, BL, BR; 3 windows = TL, BL, BR
                var q = (sWinN == 3) ? k + 1 : k;
                D.x = (q == 1 || q == 3) ? 960.0 : 0.0;
                D.y = (q >= 2) ? 540.0 : 0.0;
                D.visible = true;
            }

            MapClip::CourseMapFace.begin(ORG, MapClip, MapClip::ComCar, OP.race_map_view_mode, map_scale, 0);
            RaceDisplayFace.begin(ORG, ROOT, 0, RaceRoot::Info);
            RaceDisplayFace.dispmode = OP.racedisplay_view_mode;
            RaceDisplayFace.carmeter_disp = false;
            Parette.visible = false;

            for (var k = 1; k < sWinN; k++)
            {
                var D = containers[k - 1];
                D.MapClip::CourseMapFace.begin(ORG, D.MapClip, D.MapClip::ComCar, OP.race_map_view_mode, map_scale, k);
                D.RaceDisplayFace.begin(ORG, D, k, RaceRoot::Info);
                D.RaceDisplayFace.dispmode = OP.racedisplay_view_mode;
                D.RaceDisplayFace.carmeter_disp = false;
                D.Parette.visible = false;
            }
        }
'''
t = t.replace(anchor, branch + anchor)

# 3. finalize: clear the extra containers too
anchor = '''        InfoRight::LastLap.clearWindow(context);
        DivWork.clearWindow(context);
'''
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + '''        foreach (var QD in sQuadDivs)
            QD.clearWindow(context);
''')
open(p, 'w', encoding='utf-8').write(t)
print('patched', p)
