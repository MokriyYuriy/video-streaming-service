import gi, gstvideomode
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GObject

class PlayerWindow(Gtk.Window):
    def __init__(self, player_settings):
        self.build_window(player_settings["title"])
        self.player = None
        self.player_settings = player_settings

    def build_window(self, title):
        Gtk.Window.__init__(self, title=title)
        self.main_box = Gtk.VBox()
        self.add(self.main_box)
        
        self.top_hbox = Gtk.HBox()
        self.main_box.pack_start(self.top_hbox, True, True, 0)

        self.bottom_hbox = Gtk.HBox()
        self.main_box.pack_start(self.bottom_hbox, True, True, 0)

        self.radio_button_one_src = \
            Gtk.RadioButton.new_with_label_from_widget(None, "One Source Mode")
        self.radio_button_one_src.connect("toggled", self.on_button_toggled, "1")
        self.top_hbox.pack_start(self.radio_button_one_src, True, True, 0)

        self.radio_button_two_src = \
            Gtk.RadioButton.new_with_label_from_widget(self.radio_button_one_src, "Two Source Mode")
        self.radio_button_two_src.connect("toggled", self.on_button_toggled, "2")
        self.top_hbox.pack_start(self.radio_button_two_src, True, True, 0)
        
        self.url_entry = Gtk.Entry()
        self.bottom_hbox.pack_start(self.url_entry, True, True, 0)

        self.state_button = Gtk.Button("Start")
        self.bottom_hbox.pack_start(self.state_button, True, True, 0)
        self.state_button.connect("clicked", self.start_stop)

        self.connect("destroy", Gtk.main_quit)

    def on_button_toggled(self, button, name):
        if button.get_active():
            if name == "1":
                mode = gstvideomode.single_mode
            elif name == "2":
                mode = gstvideomode.first_in_second_mode
            self.player_settings["video_mode"] = mode
            self.build_player(self.player_settings)
            self.player.set_state(Gst.State.PLAYING)
                                                  
    def build_player(self, player_settings):
        if player_settings["rtmp_dst"] == None:
            return
        if self.player != None:
            self.player.set_state(Gst.State.NULL)

        #Creating elements
        self.create_elements(player_settings)

        #Setting properties
        self.set_properties(player_settings)

        #Adding elements to player
        self.add_elements(player_settings)

        #Linking elements
        self.link_elements(player_settings)


        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def create_elements(self, player_settings):
        self.player = Gst.Pipeline.new("player")
        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", "rtmpsink")
        self.muxer = Gst.ElementFactory.make("flvmux", "muxer")
        self.muxer.set_property("streamable", True)
        self.video_enc = Gst.ElementFactory.make(player_settings["video_enc"], "video_enc")
        self.enc_filter = Gst.ElementFactory.make("capsfilter", "enc_filter")
        self.video_parse = Gst.ElementFactory.make(player_settings["video_parse"], "video_parse")
        self.audiosrc = Gst.ElementFactory.make(player_settings["audiosrc"], "audiosrc")
        self.audio_enc = Gst.ElementFactory.make(player_settings["audio_enc"], "audio_enc")
        self.audio_parse = Gst.ElementFactory.make(player_settings["audio_parse"], "audio_parse")
        self.audio_queue = Gst.ElementFactory.make("queue", "audio_queue")
        self.audio_convert = Gst.ElementFactory.make("audioconvert", "audio_convert")
        
    def set_properties(self, player_settings):
        enc_caps = Gst.Caps.from_string(player_settings["enc_caps"])
        self.enc_filter.set_property("caps", enc_caps)
        for param, value in player_settings["video_enc_properties"]:
            self.video_enc.set_property(param, value)
        if player_settings["rtmp_dst"] != None:
            self.rtmpsink.set_property("location", player_settings["rtmp_dst"])

    def add_elements(self, player_settings):
        self.video_mixer = player_settings["video_mode"](self.player, player_settings)
        self.player.add(self.video_enc)
        self.player.add(self.enc_filter)
        self.player.add(self.muxer)
        self.player.add(self.rtmpsink)
        self.player.add(self.audiosrc)
        self.player.add(self.audio_enc)
        self.player.add(self.audio_parse)
        self.player.add(self.audio_convert)
        self.player.add(self.audio_queue)

    def link_elements(self, player_settings):
        self.video_mixer.link(self.video_enc)
        self.video_enc.link(self.enc_filter)
        self.enc_filter.link(self.muxer)
        self.audiosrc.link(self.audio_queue)
        self.audio_queue.link(self.audio_convert)
        self.audio_convert.link(self.audio_enc)
        self.audio_enc.link(self.audio_parse)
        self.audio_parse.link(self.muxer)
        self.muxer.link(self.rtmpsink)
        
    def start_stop(self, w):
        if self.state_button.get_label() == "Start":
            self.player_settings["rtmp_dst"] = self.url_entry.get_text().strip()
            self.build_player(self.player_settings)
            self.state_button.set_label("Stop")
            self.player.set_state(Gst.State.PLAYING)
        else:
            self.player.set_state(Gst.State.NULL)
            self.state_button.set_label("Start")

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.state_button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.state_button.set_label("Start")
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
        
default_settings = {
    "title" : "Player",
    "video_mode" : gstvideomode.single_mode,
    "videosrc" : ("v4l2src", "ximagesrc"),
    "videosrc_properties" : ((), (("use-damage", 0),)),
    "video_caps" : ("video/x-raw,width=320,height=240", None),
    "video_enc" : "x264enc",
    "video_enc_properties" : (("tune", "zerolatency"),), 
    "enc_caps" : "video/x-h264,profile=baseline",
    "video_parse" : "h264parse",
    "audiosrc" : "alsasrc",
    "audio_enc" : "voaacenc",
    "audio_parse" : "aacparse",
    "rtmp_dst" : None,
} 

if __name__ == "__main__":
    Gst.init(None)
    win = PlayerWindow(default_settings)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
