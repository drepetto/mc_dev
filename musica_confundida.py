import tulip, sequencer

class TiempoGigante:
    def __init__(self, beat_map_maps):
        print("0")
        #already a list of lists    
        if isinstance(beat_map_maps[0], BeatMapMap):
            self.beat_map_maps = beat_map_maps
        else:
            self.beat_map_maps.append(beat_map_maps)

        self.clear_all_stats()
        self.seq = None
        self.running = False
        # empty but valid placeholder callbacks
        self.tick_action = lambda *args, **kwargs: None
        self.beat_action = lambda *args, **kwargs: None
        self.measure_action = lambda *args, **kwargs: None
        self.finish_action = lambda *args, **kwargs: None

        #self.set_ticks_per_second(ticks_per_second)

    def tick(self,t):
        if(not self.running):
            return
        tick_flags = []
        beat_flags = []
        measure_flags = []
        finish_flags = []
        for i, bmm in enumerate(self.beat_map_maps):
            reply = bmm.tick()
            #print(reply)

            if reply is None:
                self.running = False
                print("tg done ticking!")
                self.finish_action(self, t)
                return
            
            elif reply['is_beat']:
                if not reply['is_rest']:
                    beat_flags.append(i)
    
                if reply['is_measure']:
                    measure_flags.append(i)
        
        self.tick_action(self, tick_flags, t)
        if len(beat_flags) > 0:
            self.beat_action(self, beat_flags, t)        
        if len(measure_flags) > 0:
            self.measure_action(self, measure_flags, t)

    def set_tick_action(self, ta):
        self.tick_action = ta

    def set_beat_action(self, ba):
        self.beat_action = ba

    def set_measure_action(self, ma):
        self.measure_action = ma

    def set_finish_action(self, fa):
        self.finish_action = fa

    def clear_local_stats(self):
        self.num_beat_maps = len(self.beat_map_maps)
        #self.beats_per_measures = []
        self.tick_nums = [0] * self.num_beat_maps
        self.beat_nums = [0] * self.num_beat_maps
        self.measure_nums = [0] * self.num_beat_maps
        self.total_beats = [0] * self.num_beat_maps
        self.total_measures = [0] * self.num_beat_maps


    def clear_all_stats(self):
        self.clear_local_stats()

        self.total_ticks = 0

    def reset(self):
        #print("doing reset in tiempo gigante")
        self.clear_all_stats()
        self.running=False
        if(self.seq is not None):
            self.seq.clear()
        self.seq = None

    def run(self):
        # we us a divider of 12, giving us 16th notes (48/12 = 4 ticks per quarter note)
        # our BeatMapMap takes 16th note values
        self.seq = sequencer.Sequence(1,16)
        self.seq.add(0,self.tick)
        self.running=True


class BeatMapMap:
    def __init__(self):
        # what are all the beat maps we have access to?
        self.map_catalog = []

        # what is the sequence we use them in?
        self.map_use_map = []

        self.curr_map_num = -1
        self.curr_beat_num = -1
        self.curr_tick_num = -1

        self.curr_beat_length = 0
        self.curr_measure_length = 0

        self.total_beats = 0
        self.total_measures = 0
        self.total_ticks = 0
        
    
    def add_to_map_catalog(self, maps):

        if isinstance(maps[0], list):
            for m in maps:
                self.map_catalog.append(m)
        else:
            self.map_catalog.append(maps)

        print("map catalog:", self.map_catalog)


    def set_map_use_map(self, mum):
        if max(mum) >= len(self.map_catalog):
            print("bad MUM, no entry number", max(mum))
            return

        self.map_use_map = mum
        #first_map = self.map_catalog[self.map_use_map[0]]
        #self.curr_beat_length = self.map_catalog[self.map_use_map[self.curr_map_num]][0]

        print("mum:", self.map_use_map)
        #print("first length:", self.curr_beat_length)


    def tick(self):

        self.total_ticks += 1

        # first tick will always give us zero
        self.curr_tick_num += 1

        is_beat = False
        is_rest = False
        is_measure = False
        
        #problem with measures / curr_map_num...
        if self.curr_tick_num == self.curr_beat_length:
            #print("beat!")
            self.curr_tick_num = 0

            self.curr_beat_num += 1
            is_beat = True

            if self.curr_beat_num == self.curr_measure_length:
                #len(self.map_catalog[self.map_use_map[self.curr_map_num]]):
                self.curr_beat_num = 0
                self.curr_map_num += 1

                if self.curr_map_num == len(self.map_use_map):
                    print("finished!")
                    return None
                
                self.curr_measure_length = len(self.map_catalog[self.map_use_map[self.curr_map_num]])

                is_measure = True
                #print("cmn:", self.curr_map_num, "len mum:", len(self.map_use_map))

            self.curr_beat_length = self.map_catalog[self.map_use_map[self.curr_map_num]][self.curr_beat_num]

            if self.curr_beat_length < 0:
                is_rest = True
                self.curr_beat_length *= -1

            #print("cbl:" , self.curr_beat_length)

        return({"is_beat": is_beat, "is_rest": is_rest, "is_measure": is_measure})
    




    '''
    # mostly we should just call this?
    def get_next_beat_length(self):

        if self.curr_map_num < 0:
            self.curr_map_num = 0

        map = self.map_catalog[self.map_use_map[self.curr_map_num]]

        self.curr_beat_num += 1

        if self.curr_beat_num == len(map):
            map = self.get_next_map()
            self.curr_beat_num = 0

            if map is None:
                return None

        return BeatLength(map[self.curr_beat_num], self.curr_beat_num)


    def get_curr_map(self):
        return self.map_catalog[self.map_use_map[self.curr_map_num]]
    

    def get_next_map(self):
        self.curr_map_num += 1
        self.curr_beat_num = -1
        if (self.curr_map_num == len(self.map_use_map)):
            self.curr_map_num = -1
            return None
        else:
            return self.map_catalog[self.map_use_map[self.curr_map_num]]
    
    def print_lengths(self):

        for i, map_num in enumerate(self.map_use_map):
            curr_map = self.map_catalog[map_num]
            print(curr_map)

    '''

class BeatLength:
    def __init__(self, length, beat_num):

        self.length = length
        self.beat_num = beat_num


#class CantoGigante:
#    def __init__(self):
