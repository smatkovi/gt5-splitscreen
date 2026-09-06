#!/usr/bin/env python3
# Phase 1 patch for GT5 2.17 arcade.ad (OpenAdhoc source):
#  - createSplitBattle builds 2..4 entries (player 1 answers yes/no dialogs for players 3/4)
#  - window clamp lives in the race project (RaceRoot.onInitialize), not here
import sys, re, os

# Diagnose-Schalter: Entries ab Index 2 als KI markieren (player_no = -1),
# um zu pruefen, ob die 2er-Grenze speziell fuer Spielerfahrzeuge gilt.
P3_AS_AI = os.environ.get('MOD_P3_AS_AI') == '1'
AI_SRC = '''
        {
            var es_ai = gp.event.entry_set.entries;
            for (var k_ai = 2; k_ai < es_ai.size; k_ai++)
            {
                es_ai[k_ai].player_no = -1;
                modlog("entry " + k_ai.toString() + ": player_no = -1 (KI-Test)");
            }
        }
''' if P3_AS_AI else ''


path = sys.argv[1] if len(sys.argv) > 1 else 'arcade.ad'
src = open(path, encoding='utf-8').read()

# ---------------------------------------------------------------- 1. createSplitBattle
start = src.index('    function createSplitBattle(context, course_code, course_data_holder)')
end = src.index('    function goRaceSequence(context, game_mode, gp, course_data_holder)')

new_create = r'''    // --- 4P split patch: how many players take part in this split battle (2..4).
    // The menu layer only knows pads 1 and 2, so player 1 answers two yes/no dialogs
    // when starting the race; players 3 and 4 are bound to pads 3 and 4 in the race itself.
    static mod_log_buf = "";
    function modlog(text)
    {
        mod_log_buf = mod_log_buf + text + "\n";
        pdistd::WriteFile("/APP_DATA_RAW/4pmod.log", mod_log_buf.getByteData());
    }

    // --- 4P split patch: state shared between the split car select (CarSplitBaseRoot) and
    // createSplitBattle.  Round 1 of the car select is players 1/2, round 2 players 3/4.
    static mod_round = 1;
    static mod_ports = nil;        // controller ports of the entered players, set after round 1
    static mod_cars = [];          // MCarParameter per entered player (deep copies)
    static mod_drivers = [];       // MCarDriverParameter per entered player (deep copies)

    function rememberSplitPlayers(first_slot, count)
    {
        for (var i = 0; i < count; i++)
        {
            var c = gtengine::MCarParameter();
            c.deepCopy(GAME_STATUS.user_profile.context.getArcadeCar(first_slot + i));
            mod_cars.push(c);
            var d = gtengine::MCarDriverParameter();
            d.deepCopy(GAME_STATUS.user_profile.residence.getArcadePlayer(first_slot + i));
            mod_drivers.push(d);
        }
    }

    function restoreSplitPlayers()
    {
        for (var i = 0; i < 2 && i < mod_cars.size; i++)
        {
            GAME_STATUS.user_profile.context.setArcadeCar(mod_cars[i], i);
            GAME_STATUS.user_profile.residence.setArcadePlayer(i, mod_drivers[i]);
        }
    }

    function getSplitPlayerPorts(context)
    {
        var ports = [0, 1];
        modlog("getSplitPlayerPorts: start");
        var r3 = DialogUtil::openConfirmDialog(context, DialogUtil::YESNO, "Spieler 3 (Controller 3) faehrt mit?");
        modlog("dialog P3 -> " + (r3 ? "yes" : "no"));
        if (r3)
        {
            ports.push(2);
            var r4 = DialogUtil::openConfirmDialog(context, DialogUtil::YESNO, "Spieler 4 (Controller 4) faehrt mit?");
            modlog("dialog P4 -> " + (r4 ? "yes" : "no"));
            if (r4)
                ports.push(3);
        }
        modlog("ports: " + ports.size.toString());
        return ports;
    }

    // --- 4P split patch: a car model nobody else in this race uses
    static SPARE_CAR_LABELS = ["gtr_07", "impreza_wrx_sti_07", "rx7_spirit_r_typea_02",
                               "s2000_99", "civic_type_r_97", "supra_rz_97", "silvia_spec_r_02"];
    function pickSpareCarCode(used_cp_list)
    {
        foreach (var label in SPARE_CAR_LABELS)
        {
            var code = gtengine::MSpecDB::getCarCode(label);
            if (code == gtengine::MSpecDB::NO_CODE64)
                continue;

            var taken = false;
            foreach (var used in used_cp_list)
            {
                if (used.getCarCode() == code)
                    taken = true;
            }
            if (!taken)
            {
                modlog("spare car: " + label);
                return code;
            }
        }
        modlog("spare car: none found");
        return gtengine::MSpecDB::NO_CODE64;
    }

    function createSplitBattle(context, course_code, course_data_holder)
    {
        var ports = (mod_ports != nil) ? mod_ports : getSplitPlayerPorts(context);

        var cp_list = [];
        var dp_list = [];

        var i = 0;
        foreach (var port in ports)
        {
            var cp;
            var dp;
            if (mod_cars.size > i && mod_drivers.size > i)
            {
                // chosen in the split car select (round 1: players 1/2, round 2: players 3/4)
                cp = mod_cars[i];
                dp = mod_drivers[i];
                if (i >= 2)
                    dp.setPlayer(port);
            }
            else if (i < 2)
            {
                // players 1 and 2: car and driver chosen in the split car select, as before
                cp = GAME_STATUS.user_profile.context.getArcadeCar(i);
                dp = GAME_STATUS.user_profile.residence.getArcadePlayer(i);
            }
            else
            {
                // Players 3 and 4 need a car model of their own: the engine loads one
                // resource per distinct car code, so a copy of an already entered car
                // would never make the "all cars loaded" check pass.
                var code = pickSpareCarCode(cp_list);
                if (code != gtengine::MSpecDB::NO_CODE64)
                {
                    cp = gtengine::MCarParameter(code);
                    cp.rentacar = true;
                    cp.ownArcadePartsAll();
                }
                else
                {
                    var src_cp = GAME_STATUS.user_profile.context.getArcadeCar(i - 2);
                    cp = gtengine::MCarParameter();
                    cp.deepCopy(src_cp);
                }
                // Eigenes Fahrer-Objekt: createSplitBattle weist driver_parameter
                // per Referenz zu, ein geteiltes Objekt haengt sonst zwei Entries
                // an denselben Fahrer (und setPlayer wuerde Spieler 1 umbiegen).
                var src_dp = GAME_STATUS.user_profile.residence.getArcadePlayer(i - 2);
                dp = gtengine::MCarDriverParameter();
                dp.deepCopy(src_dp);
                dp.setPlayer(port);
            }
            dp.display_name = dp.display_name + "[%d]".format(i + 1);
            modlog("entry " + i.toString() + ": port=" + port.toString() + " name=" + dp.display_name
               + " ctrlport=" + dp.getControllerPort().toString()
               + " dpvacant=" + (dp.isVacant() ? "1" : "0")
               + " code=" + cp.getCarCode().toString());
            cp_list.push(cp);
            dp_list.push(dp);
            i++;
        }

        // --- 4P split patch: key configuration for controller ports 2 and 3.
        // GameOption::DeclareControllers() declares the pad channels for ports 0 and 1 only,
        // so pads 3/4 are polled by the engine but never mapped to accelerate/brake/steer.
        // Declare the SIXAXIS channels for the extra ports and give them player 1's config.
        if (ports.size > 2)
        {
            var kc = GAME_STATUS.user_profile.option.key_config;
            var cfg0 = kc.getConfig(0);
            var mode = main::gtengine::InputMode::PLAY_NORMAL;
            var buttons = ["UP", "DOWN", "LEFT", "RIGHT", "CIRCLE", "CROSS", "TRIANGLE", "SQUARE",
                           "L1", "R1", "L2", "R2", "L3", "R3", "START", "SELECT"];
            var analogs = ["PRESS_UP", "PRESS_DOWN", "PRESS_LEFT", "PRESS_RIGHT", "PRESS_CIRCLE", "PRESS_CROSS",
                           "PRESS_TRIANGLE", "PRESS_SQUARE", "PRESS_L1", "PRESS_R1", "PRESS_L2", "PRESS_R2",
                           "STICK_BY1F", "STICK_BY1L", "STICK_BX1", "STICK_BX1F", "STICK_BX1L",
                           "STICK_BY2F", "STICK_BY2L", "STICK_BX2", "STICK_BX2F", "STICK_BX2L"];
            for (var k = 2; k < ports.size; k++)
            {
                var kport = ports[k];
                foreach (var bname in buttons)
                    kc.declare(mode, "SIXAXIS", kport, "button", main::pdistd::SuperPortButtonBit[bname]);
                foreach (var aname in analogs)
                    kc.declare(mode, "SIXAXIS", kport, "analog", main::pdistd::SuperPortAnalogChannel[aname]);
                kc.setConfig(cfg0, kport);
                modlog("keyconfig: SIXAXIS declared and port 0 config copied to port " + kport.toString());
            }
        }

        var gp;
        if (course_data_holder.is_edit_course_)
        {
            var course_pathway = course_data_holder.course_pathway_;
            gp = GameParameterUtil::createSplitBattle(course_code, cp_list, dp_list);

            {
                var course_pathway_bin;
                if (course_pathway.isInstanceOf(gtengine::MCoursePathway))
                    course_pathway_bin = course_pathway.serialize();
                else
                    course_pathway_bin = course_pathway;
                gp.event.track.course_pathway = course_pathway_bin;
            }

            var data = CursorProject::LoadingRoot::EditCourseData(gp, course_pathway.title);
            CursorProject::LoadingRoot.setData(data);
        }
        else
        {
            gp = GameParameterUtil::createSplitBattle(course_code, cp_list, dp_list);
        }

''' + AI_SRC + '''        gp.event.race_parameter.low_mu_type = GAME_STATUS.user_profile.context.arcade_low_mu_type;
        gp.event.race_parameter.behavior_damage_type = GAME_STATUS.user_profile.context.arcade_behavior_damage_type;

        return gp;
    }


'''
src = src[:start] + new_create + src[end:]

# ---------------------------------------------------------------- 2. clamp after executeArcade
old_exec = '''        var result = GameParameterUtil::executeArcade(context, gp, GAME_STATUS, driving_option);

        GameParameterUtil::end();
'''
new_exec = '''        var result = GameParameterUtil::executeArcade(context, gp, GAME_STATUS, driving_option);

        // --- 4P split patch (phase 1): the engine's window manager has two hard-wired
        // windows; keep window_max at 2 even when 3 or 4 human players are entered.
        if (game_mode == gtengine::GameMode::SPLIT_BATTLE)
        {
            modlog("after executeArcade: result=" + (result ? "true" : "false") + " RaceOperator.window_max=" + main::RaceOperator.window_max.toString() + " ORG.window_max=" + main::ORG.window_max.toString());
            // NOTE: no clamp here on purpose - RaceOperator.window_max must stay at the
            // real player count so the engine loads every player car. The engine-side
            // window manager is clamped later, in RaceRoot.onInitialize (race project).
        }

        GameParameterUtil::end();
'''
assert src.count(old_exec) == 1, 'executeArcade site not found exactly once'
src = src.replace(old_exec, new_exec)

# ---------------------------------------------------------------- 3. pad masks in round 2
# Tried: event_mask 4/8 for the two panes in round 2 so that pads 3/4 would drive them - the panes
# went deaf to every pad (the mask bits are not pad ports).  The panes therefore keep their normal
# masks (5/10): in round 2 controller 1 picks for player 3 (left pane), controller 2 for player 4.

# ---------------------------------------------------------------- 4. CarSplitBaseRoot: second car-select round
import os
csb_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'CarSplitBaseRoot.ad')
csb = open(csb_path, encoding='utf-8').read()
if 'mod_round' not in csb:
    old = "    method onInitialize(context)\n    {\n        OverLapRoot::ButtonHelpGT5.onSplitCarSelect();\n"
    assert csb.count(old) == 1
    csb = csb.replace(old, old + """
        // --- 4P split patch: a fresh car select starts with round 1
        ArcadeProject::mod_round = 1;
        ArcadeProject::mod_ports = nil;
        ArcadeProject::mod_cars = [];
        ArcadeProject::mod_drivers = [];
""")
    old = "    method close(context)\n    {\n        ArcadeProject::ignorePadEvent(true, true);\n"
    assert csb.count(old) == 1
    csb = csb.replace(old, "    method close(context)\n    {\n        ArcadeProject::mod_round = 1;\n        ArcadeProject::ignorePadEvent(true, true);\n")
    old = """                if (root1.defined("ready") && root1.ready &&
                    root2.defined("ready") && root2.ready)
                {
                    var res = gArcadeSequence.moveNextPage(context);
"""
    assert csb.count(old) == 1
    csb = csb.replace(old, """                var ready1 = root1.defined("ready") && root1.ready;
                var ready2 = root2.defined("ready") && root2.ready;
                // --- 4P split patch: in round 2 with three players only pane 1 (player 3) counts
                if (ArcadeProject::mod_round == 2 && ArcadeProject::mod_ports.size == 3)
                    ready2 = true;
                if (ready1 && ready2)
                {
                    if (ArcadeProject::mod_round == 1)
                    {
                        // players 1/2 have chosen: remember them, then ask who else plays
                        ArcadeProject::rememberSplitPlayers(0, 2);
                        ArcadeProject::mod_ports = ArcadeProject::getSplitPlayerPorts(context);
                        if (ArcadeProject::mod_ports.size > 2)
                        {
                            ArcadeProject::mod_round = 2;
                            ArcadeProject::modlog("car select round 2 for " + (ArcadeProject::mod_ports.size - 2).toString() + " player(s)");
                            ArcadeProject::ignorePadEvent(true, true);
                            foreach (var root in Context1P.getPageList().reverse())
                                root.close(Context1P);
                            foreach (var root in Context2P.getPageList().reverse())
                                root.close(Context2P);
                            context.sync(2.0);
                            Context1P.clearPage();
                            Context2P.clearPage();
                            var msg = (ArcadeProject::mod_ports.size == 3)
                                ? "Auto fuer Spieler 3 waehlen (linke Seite, Controller 1 bedient)."
                                : "Autos fuer Spieler 3 (links, Controller 1 bedient) und Spieler 4 (rechts, Controller 2 bedient) waehlen.";
                            DialogUtil::openConfirmDialog(context, DialogUtil::OK, msg);
                            thread_ = Thread(self.event_pad_mask, context);
                            thread_.start();
                            effect_end_func(context);
                            break;   // event_pad_mask starts a new check_page_status thread
                        }
                    }
                    else
                    {
                        // round 2 done: slots 0/1 now hold players 3/4; restore players 1/2
                        ArcadeProject::rememberSplitPlayers(0, ArcadeProject::mod_ports.size - 2);
                        ArcadeProject::restoreSplitPlayers();
                        ArcadeProject::mod_round = 1;
                    }
                    var res = gArcadeSequence.moveNextPage(context);
""")
    open(csb_path, 'w', encoding='utf-8').write(csb)
    print('patched', csb_path)


# ---------------------------------------------------------------- 3. 2.17 delta in CarRoot.ad
import os
carroot = os.path.join(os.path.dirname(os.path.abspath(path)), 'CarRoot.ad')
cr = open(carroot, encoding='utf-8').read()
old_cp = """                    if (tab_id == TAB_TYPE::FAVORITE)
                    {
                        var cp = car.getCP();

                        if (course_is_dirt)"""
new_cp = """                    if (tab_id == TAB_TYPE::FAVORITE)
                    {
                        var cp = car.getCP();

                        cp.checkValid(); // added in GT5 2.17

                        if (course_is_dirt)"""
if 'cp.checkValid();' not in cr:
    assert cr.count(old_cp) == 1, 'CarRoot.ad FAVORITE block not found exactly once'
    cr = cr.replace(old_cp, new_cp)
    open(carroot, 'w', encoding='utf-8').write(cr)
    print('patched', carroot)

open(path, 'w', encoding='utf-8').write(src)
print('patched', path)
