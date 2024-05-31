import musica_confundida

BMM = musica_confundida.BeatMapMap()

maps = [[2,2,2],[-2,3,4],[4,5,6],[7,7,-7,7,7]]

BMM.add_to_map_catalog(maps)
BMM.set_map_use_map([0,0,1,1,3,2])


reply = BMM.tick()
print(reply)

while reply is not None:
    #print(reply)

    reply = BMM.tick()

    if reply is not None:
        if reply['is_measure'] is True:
            print("measure")
        if reply['is_beat'] == True:
            print("beat", reply['is_rest'])
