

from tulip import UIScreen, UIElement, pal_to_lv, lv_depad, lv, frame_callback, ticks_ms, seq_add_callback, seq_remove_callback, seq_ppq, ticks_ms
import amy, tulip
import musica_confundida
import random

app = None

measure_count = 0
# define your custom tick / beat / measure callbacks (if any)
# call sig should be:
# xyz_action(my_tg, flags, time)
# finish_action(my_tg, time)

# flags is a list of beat maps that have triggered

def tick_action(tg, flags, t):

    amy.send(osc=50,wave=amy.PCM,freq=0,patch=app.patch_map[0],vel=4, time=t)


def beat_action(tg, flags, t):
    print("beat!")
    #print(flags)
    for i, f in enumerate(flags):
        amy.send(osc=51+i,wave=amy.PCM,freq=0,patch=app.patch_map[f+1],vel=4, time=t)

def measure_action(tg, flags, t):
    global measure_count 
    # a little accent every four measures
    if measure_count % 4 == 0:
        amy.send(osc=60,wave=amy.PCM,freq=0,patch=app.patch_map[4],vel=4, time=t)

    measure_count += 1

def finish_action(tg, t):
    print("mc dance got finish message.")
    amy.send(osc=61,wave=amy.PCM,freq=0,patch=app.patch_map[5],vel=4, time=t)

def quit(screen):
    screen.tg.reset()

def run(screen):

    import gc
    gc.collect()
    mem_free = gc.mem_free()
    print("starting memory:", mem_free)

    global app
    app = screen
    screen.quit_callback = quit

    amy.reset()

    screen.patch_map = [6,1,9,2,13,14]

    # the beat map is in 16th notes. so 4 means 4 x 16ths, aka a quarter note.
    # the ticks don't have to add up to 16 or anything in particular. 
    # each beatmap in each beat map map can have its own duration
    bmm_bass = musica_confundida.BeatMapMap()
    bass_maps = [[4,4,4,4],
                 [4,4,8]]
    bmm_bass.add_to_map_catalog(bass_maps)
    bmm_bass.set_map_use_map([0,0,0,1] * 2)

    # negative numbers mean a rest, so -3, 13 means rest for 3 ticks
    # then a 13 tick beat filling in the rest of the 16 tick measure    
    bmm_clap = musica_confundida.BeatMapMap()
    clap_maps = [[-3,13]]
    bmm_clap.add_to_map_catalog(clap_maps)
    bmm_clap.set_map_use_map([0] * 18)

    bmm_snare = musica_confundida.BeatMapMap()
    snare_maps = [[-3,3,3,2,3,2],[-3,3,6,1,1,1,1]]
    bmm_snare.add_to_map_catalog(snare_maps)
    bmm_snare.set_map_use_map([0,0,0,1] * 2)

    screen.tg = musica_confundida.TiempoGigante([bmm_bass, bmm_clap, bmm_snare])
    

    # set your tick / beat / measure actions (if any)
    screen.tg.set_tick_action(tick_action)
    screen.tg.set_beat_action(beat_action)
    screen.tg.set_measure_action(measure_action)
    screen.tg.set_finish_action(finish_action)


    screen.present()
    screen.tg.run()
    
    
    print("after run() memory:", gc.mem_free(), "used: ", str(mem_free - gc.mem_free()))
    
    

