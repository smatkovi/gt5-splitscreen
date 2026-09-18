#!/usr/bin/env python3
"""Open up the arcade car and course lists (projects/gt5/arcade).

Three restrictions keep content out of the arcade (and therefore out of the split screen):

1. The "Arcade" tab of the car select queries the spec DB with `arcade = 1`
   (`CarData::ArcadeModeGT5::getCarList`), which is a few hundred of the ~970 cars on the disc.
   Here the same query is issued without that condition, so every car in the spec DB can be picked.

2. The course list drops every course whose `COURSE_AVAILABLE` save flag is not set - that is the
   gate for Nurburgring Nordschleife (`nurburgring`), the 24h and VLN layouts, the day/night
   variants, Spa, Motegi, Kart Space, Route X and the Top Gear test track.  The GP layouts
   (`nurburgring_GP`, `nurburgring_dtm`) have no flag and are therefore always listed - which is
   exactly what a locked save looks like: GP yes, Nordschleife no.  The check is removed.

3. In a split battle every course with changeable weather is greyed out - the Nordschleife is one
   of them.  Instead of dropping those courses, the weather is pinned to sunny
   (`weather_changeable_ = false`, `decisive_weather_ = SUNNY`), which is the state the game itself
   uses for courses that have a fixed weather; `createSplitBattle` then writes it into the race
   parameter.  No dynamic weather is enabled for split screen.

Set MOD_ARCADE_UNLOCK=0 to build the stock behaviour.
Usage: patch_arcade_unlock.py <arcade project dir>
"""
import os, sys

if os.environ.get('MOD_ARCADE_UNLOCK', '1') == '0':
    print('arcade unlock disabled (MOD_ARCADE_UNLOCK=0)')
    sys.exit(0)

d = sys.argv[1] if len(sys.argv) > 1 else '.'


def patch(name, marker, old, new, count=1):
    p = os.path.join(d, name)
    t = open(p, encoding='utf-8').read()
    if marker in t:
        print('already patched', name, '-', marker)
        return
    assert t.count(old) == count, '%s: %d hits' % (name, t.count(old))
    open(p, 'w', encoding='utf-8').write(t.replace(old, new))
    print('patched', name, '-', marker)


# ---------------------------------------------------------------- 1. every car in the arcade tab
car_old = '''                        else
                        {    
                            cars = CarData::ArcadeModeGT5::getCarList();
                        }'''
car_new = '''                        else
                        {    
                            // --- 4P split patch: the stock call adds "arcade = 1" to the query,
                            // which hides most of the cars on the disc.  Same query without it.
                            cars = CarData::getCPPListImpl(nil, nil, nil, nil, "pp", "ASC", nil, true);
                        }'''
for f in ('CarRoot.ad', 'CarSplitRoot.ad'):
    patch(f, 'getCPPListImpl', car_old, car_new)

# ---------------------------------------------------------------- 2. no COURSE_AVAILABLE gate
patch('CourseRoot.ad', 'COURSE_AVAILABLE save flag gates', '''                            var course_label = main::gtengine::MSpecDB::getCourseLabel(crs_param.course_code_);
                            if (GAME_STATUS.user_profile.game_flags.getFlag("COURSE_AVAILABLE", course_label) == false)
                                continue;

''', '''                            // --- 4P split patch: the COURSE_AVAILABLE save flag gates the
                            // Nordschleife, the 24h/VLN/day-night layouts, Spa, Motegi, Kart Space,
                            // Route X and Top Gear.  All of them ship on the disc, so list them.

''')

# ---------------------------------------------------------------- 3. weather courses in a split battle
patch('CourseRoot.ad', 'Pin the weather to sunny', '''                else if (ArcadeProject::ArcadeModeEnum::SPLIT_BATTLE == gArcadeSequence.getArcadeMode())
                {

                    if (crs_param.weather_changeable_ ||
                        crs_param.rain_situation_ ||
                        crs_param.snow_situation_)
                    {
                        is_enable = false;
                    }
                }''', '''                else if (ArcadeProject::ArcadeModeEnum::SPLIT_BATTLE == gArcadeSequence.getArcadeMode())
                {
                    // --- 4P split patch: the stock code greys out every course with changeable
                    // weather (the Nordschleife among them).  Pin the weather to sunny instead -
                    // createSplitBattle copies decisive_weather_ into the race parameter when
                    // weather_changeable_ is false, so the race runs without dynamic weather.
                    if (crs_param.weather_changeable_ ||
                        crs_param.rain_situation_ ||
                        crs_param.snow_situation_)
                    {
                        crs_param.rain_situation_ = false;
                        crs_param.snow_situation_ = false;
                        crs_param.weather_changeable_ = false;
                        crs_param.decisive_weather_ = main::gtengine::DecisiveWeather::SUNNY;
                    }
                }''')
