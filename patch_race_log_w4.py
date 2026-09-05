#!/usr/bin/env python3
# Diagnostic patch v2 for OpenAdhoc GT5 race project.
# Logs the whole loading + race start sequence to /APP_DATA_RAW/4pmod_race.log
# (visible as USRDIR/4pmod_race.log over FTP).
import os, sys

# Wieviele Engine-Fenster maximal erlaubt sind (2 = alt, 3 = Test)
MOD_WINDOW_MAX = int(os.environ.get('MOD_WINDOW_MAX', '3'))

d = sys.argv[1] if len(sys.argv) > 1 else '.'
race = os.path.join(d, 'race.ad')
loadutil = os.path.join(d, 'LoadingUtil.ad')
root = os.path.join(d, 'RaceRoot.ad')


def insert(path, anchor, text, where='after'):
    """Insert `text` as its own line before/after the single line containing `anchor`."""
    lines = open(path, encoding='utf-8').read().split('\n')
    hits = [i for i, l in enumerate(lines) if anchor in l]
    assert len(hits) == 1, '%s: %d hits for %r' % (path, len(hits), anchor)
    i = hits[0]
    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    new = indent + text
    lines.insert(i + 1 if where == 'after' else i, new)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))


# ---------------------------------------------------------------- race.ad: the logger
s = open(race, encoding='utf-8').read()
if 'function log4p' not in s:
    anchor = '    static gSequenceCondition;\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, '''    static gSequenceCondition;

    // --- 4P split patch: diagnostic log
    static g4p_log = "";
    function log4p(text)
    {
        g4p_log = g4p_log + text + "\\n";
        pdistd::WriteFile("/APP_DATA_RAW/4pmod_race.log", g4p_log.getByteData());
    }
''')
    open(race, 'w', encoding='utf-8').write(s)
    print('patched', race)

# ---------------------------------------------------------------- LoadingUtil.ad: the wait points
insert(loadutil, 'var usec_start = pdistd::GetSystemTimeMicroSecond();',
       'log4p("LU: load_sequence start");')
# --- 4P split patch: raise the per-profile vehicle budget before check-in
insert(loadutil, 'log4p("LU: load_sequence start");',
       '{ var mp4p = [RaceOperator.getMemoryAssign_Standard(), RaceOperator.getMemoryAssign_WithGhost(), '
       'RaceOperator.getMemoryAssign_FewCars(), RaceOperator.getMemoryAssign_ExpandMemory(), '
       'RaceOperator.getMemoryAssign_WithoutReplay(), RaceOperator.getMemoryAssign_ForReplay()]; '
       'var mn4p = ["Standard", "WithGhost", "FewCars", "ExpandMemory", "WithoutReplay", "ForReplay"]; '
       'var ml4p = "LU: memprofiles"; '
       'for (var k4p = 0; k4p < mp4p.size; k4p++) { '
       'ml4p = ml4p + " " + mn4p[k4p] + "=" + mp4p[k4p].nb_vehicle.toString(); '
       'if (mp4p[k4p].nb_vehicle < 4) { mp4p[k4p].nb_vehicle = 4; ml4p = ml4p + "->4"; } } '
       'log4p(ml4p); }')
# --- 4P split patch: Fenstermaximum VOR der Ladeschleife setzen.
# RaceRoot.onInitialize laeuft erst nach dem Course-In, also viel zu spaet,
# um das Laden der Spielerautos zu beeinflussen.
insert(loadutil, 'log4p("LU: load_sequence start");',
       'log4p("LU: window_max vorher ORG=" + ORG.window_max.toString() '
       '+ " RaceOperator=" + RaceOperator.window_max.toString()); '
       'ORG.window_max = %d; '
       'log4p("LU: window_max jetzt ORG=" + ORG.window_max.toString());' % MOD_WINDOW_MAX)

insert(loadutil, 'var check_in_success = RaceOperator.checkIn(false);',
       'log4p("LU: checkIn -> " + (check_in_success ? "ok" : "FAIL"));')
insert(loadutil, 'while (true)',
       'log4p("LU: entryDone loop enter");', where='before')
insert(loadutil, 'RaceOperator.processAfterCheckIn();',
       'log4p("LU: entryDone loop passed");', where='before')
insert(loadutil, 'RaceOperator.processAfterCheckIn();',
       'log4p("LU: processAfterCheckIn done");')
insert(loadutil, 'while (!ORG.hasLoadingCarDone())',
       'log4p("LU: carload loop enter, need=" + loading_car_num.toString());', where='before')
insert(loadutil, 'log4p("LU: carload loop enter, need=',
       '{ var es4p = RaceOperator.game_parameter.event.entry_set.entries; '
       'var s4p = "LU: entries=" + es4p.size.toString(); '
       'for (var i4p = 0; i4p < es4p.size; i4p++) '
       's4p = s4p + " [" + i4p.toString() + "] player_no=" + es4p[i4p].player_no.toString() '
       '+ " vacant=" + (es4p[i4p].car_parameter.isVacant() ? "1" : "0") '
       '+ " code=" + es4p[i4p].car_parameter.getCarCode().toString(); log4p(s4p); }', where='before')
insert(loadutil, 'log4p("LU: carload loop enter, need=',
       'var lu_dbg = 0;', where='before')
insert(loadutil, 'var loaded_num = ORG.getLoadedCarCount();',
       'if (lu_dbg == 0 || lu_dbg == 10 || lu_dbg == 30 || lu_dbg == 60 || lu_dbg == 120) '
       'log4p("LU: carload t=" + lu_dbg.toString() + " loaded=" + loaded_num.toString() '
       '+ " racersMax=" + ORG.getCurrentRaceParameter().racers_max.toString() '
       '+ " winmax=" + ORG.window_max.toString()); lu_dbg++;')
insert(loadutil, 'pdistd::DelayThread(0x3E8 * 0x64);',
       'log4p("LU: carload loop passed, course requested");', where='before')
insert(loadutil, 'while (!ORG.canEnterCourse())',
       'log4p("LU: canEnterCourse loop enter");', where='before')
insert(loadutil, 'current_progress += time_course_ratio;',
       'log4p("LU: canEnterCourse loop passed");', where='before')
insert(loadutil, 'while (ORG.enterCourse() == false)',
       'log4p("LU: enterCourse loop enter");', where='before')
insert(loadutil, 'busy_wait(context, ORG.inCourse, 1000 * 100);',
       'log4p("LU: enterCourse done, waiting inCourse");', where='before')
insert(loadutil, 'busy_wait(context, ORG.inCourse, 1000 * 100);',
       'log4p("LU: inCourse ok; allEntries=" + (ORG.inCourseAllEntries() ? "1" : "0"));')
insert(loadutil, 'after_coursein_func(context);',
       'log4p("LU: calling after_coursein_func");', where='before')
insert(loadutil, 'busy_wait(context, ORG.inSession, 1000 * 100);',
       'log4p("LU: after_coursein_func returned, waiting inSession");', where='before')
insert(loadutil, 'busy_wait(context, ORG.inSession, 1000 * 100);',
       'log4p("LU: inSession ok");')
insert(loadutil, 'busy_wait(context, ORG.isRenderReady, 1000 * 100);',
       'log4p("LU: waiting isRenderReady");', where='before')
insert(loadutil, 'busy_wait(context, ORG.isFinishedFirstLoad, 1000 * 100);',
       'log4p("LU: renderReady ok, waiting isFinishedFirstLoad");', where='before')
insert(loadutil, 'busy_wait(context, ORG.isFinishedFirstLoad, 1000 * 100);',
       'log4p("LU: firstLoad ok");')
insert(loadutil, 'PROJECT::setEnemySuitableTire(context);',
       'log4p("LU: load_sequence finished");')
print('patched', loadutil)

# ---------------------------------------------------------------- RaceRoot.ad: start + condition poll
r = open(root, encoding='utf-8').read()
if 'log4p_poll' not in r:
    a1 = '        main::ORG.window_max = main::RaceOperator.window_max;\n'
    assert r.count(a1) == 1
    r = r.replace(a1, '''        // --- 4P split patch: window clamp, raised for the 3-window experiment.
        // RaceOperator.window_max keeps the real player count (needed for car loading),
        // the engine side is clamped to 2 here.
        main::ORG.window_max = (main::RaceOperator.window_max > ''' + str(MOD_WINDOW_MAX) + ''') ? ''' + str(MOD_WINDOW_MAX) + ''' : main::RaceOperator.window_max;
        log4p("RR.onInitialize: RaceOperator.window_max=" + main::RaceOperator.window_max.toString()
              + " ORG.window_max=" + main::ORG.window_max.toString()
              + " racers_num=" + ORG.racers_num.toString());
''')

    a2 = '''            var start_session_success = gSequenceCondition.startSessionForRace();
            if (!start_session_success)
            {
'''
    assert r.count(a2) == 1
    r = r.replace(a2, '''            var start_session_success = gSequenceCondition.startSessionForRace();
            log4p("RR: startSessionForRace -> " + (start_session_success ? "ok" : "FAILED"));
            {
                var t4p = Thread(self.log4p_poll, context);
                t4p.start();
            }
            if (!start_session_success)
            {
''')

    a3 = '    method onInitialize(context)\n'
    poll = '''    // --- 4P split patch: poll the race start conditions for 30 s
    method log4p_poll(context)
    {
        for (var n = 0; n < 30; n++)
        {
            Thread::Sleep(1.0);
            var line = "RR poll t=" + n.toString()
                + " inCourse=" + (ORG.inCourse() ? "1" : "0")
                + " inSession=" + (ORG.inSession() ? "1" : "0")
                + " renderReady=" + (ORG.isRenderReady() ? "1" : "0")
                + " firstLoad=" + (ORG.isFinishedFirstLoad() ? "1" : "0")
                + " carsDone=" + (ORG.hasLoadingCarDone() ? "1" : "0")
                + " allEntries=" + (ORG.inCourseAllEntries() ? "1" : "0")
                + " loadedCars=" + ORG.getLoadedCarCount().toString()
                + " slots:";
            for (var i = 0; i < 4; i++)
                line = line + " " + (ORG.checkInCourseSlot(i) ? "1" : "0");
            log4p(line);
            if (ORG.inSession() && ORG.inCourseAllEntries())
                break;
        }
    }

'''
    r = r.replace(a3, poll + a3, 1)
    open(root, 'w', encoding='utf-8').write(r)
    print('patched', root)
