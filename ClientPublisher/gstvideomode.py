import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


def create_element(name, element):
    return Gst.ElementFactory.make(element, name)


def set_properties(videosrc, properties):
    for prop in properties:
        videosrc.set_property(prop[0], prop[1])

def add_elements(player, elements):
    for elem in elements:
        if elem != None:
            player.add(elem)
        
def create_filter(name, video_caps):
    print(video_caps)
    if video_caps == None:
        return None
    caps = Gst.Caps.from_string(video_caps)
    video_filter = create_element(name, "capsfilter")
    video_filter.set_property("caps", caps)
    return video_filter

def link_elements(src, sink):
    if src != None and sink != None:
        assert src.link(sink)

def single_mode(player, player_settings):
    videosrc = create_element("videosrc0", player_settings["videosrc"][0])
    set_properties(videosrc, player_settings["videosrc_properties"][0])
    video_filter = create_filter("video_caps0", player_settings["video_caps"][0])
    video_mixer = create_element("video_mixer", "videomixer")

    add_elements(player, (videosrc, video_filter, video_mixer))
    
    videosrc.link(video_filter)
    video_filter.link(video_mixer)
    return video_mixer
    

def first_in_second_mode(player, player_settings):
    videosrcs = tuple(create_element("videosrc%s" % i, player_settings["videosrc"][i])
                     for i in range(2))
    video_filters = tuple(create_filter("video_filter%s" % i, player_settings["video_caps"][i])
                          for i in range(2))    
    video_mixer = create_element("video_mixer", "videomixer")
    video_box = create_element("video_box", "videobox")

    set_properties(video_box, (("border-alpha", 0), ("alpha", 0.5)))
    for i in range(2):
        set_properties(videosrcs[i], player_settings["videosrc_properties"][i])
    
    add_elements(player, videosrcs + video_filters + (video_box, video_mixer))
    for i in range(2):
        link_elements(videosrcs[i], video_filters[i])
    link_elements(video_filters[0] if video_filters[0] != None else videosrcs[0], video_box)
    link_elements(video_filters[1] if video_filters[1] != None else videosrcs[1], video_mixer)
    link_elements(video_box, video_mixer)
    return video_mixer
    
    
    
