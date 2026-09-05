#!/usr/bin/env python3
# Phase 1 patch for GT5 2.17 arcade.ad (OpenAdhoc source):
#  - createSplitBattle builds 2..4 entries (player 1 answers yes/no dialogs for players 3/4)
#  - window clamp lives in the race project (RaceRoot.onInitialize), not here
import sys, re

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
        var ports = getSplitPlayerPorts(context);

        var cp_list = [];
        var dp_list = [];

        var i = 0;
        foreach (var port in ports)
        {
            var cp;
            var dp;
            if (i < 2)
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
                dp = GAME_STATUS.user_profile.residence.getArcadePlayer(i - 2);
                dp.setPlayer(port);
            }
            dp.display_name = dp.display_name + "[%d]".format(i + 1);
            modlog("entry " + i.toString() + ": port=" + port.toString() + " name=" + dp.display_name + " code=" + cp.getCarCode().toString());
            cp_list.push(cp);
            dp_list.push(dp);
            i++;
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

        gp.event.race_parameter.low_mu_type = GAME_STATUS.user_profile.context.arcade_low_mu_type;
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
