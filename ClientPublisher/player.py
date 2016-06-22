import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GObject

class PlayerWindow(Gtk.Window):
    def __init__(self, player_settings):
        self.build_window(player_settings["title"])
        self.build_player(player_settings)

    def build_window(self, title):
        Gtk.Window.__init__(self, title=title)
        self.main_box = Gtk.VBox()
        self.add(self.main_box)

        self.video_area = Gtk.DrawingArea()
        self.main_box.pack_start(self.video_area, True, True, 0)

        self.bottom_hbox = Gtk.HBox()
        self.main_box.pack_start(self.bottom_hbox, True, True, 0)

        self.url_entry = Gtk.Entry()
        self.bottom_hbox.pack_start(self.url_entry, True, True, 0)

        self.state_button = Gtk.Button("Start")
        self.bottom_hbox.pack_start(self.state_button, True, True, 0)
        self.state_button.connect("clicked", self.start_stop)

        self.connect("destroy", Gtk.main_quit)
        
    def build_player(self, player_settings):
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
        self.videosrc = Gst.ElementFactory.make(player_settings["videosrc"], "videosrc")
        #self.audiosrc = Gst.ElementFactory.make(player_settings["audiosrc"], "audiosrc")
        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", "rtmpsink")
        self.muxer = Gst.ElementFactory.make("flvmux", "muxer")
        self.muxer.set_property("streamable", True)
        self.video_filter = Gst.ElementFactory.make("capsfilter", "video_filter")
        self.video_enc = Gst.ElementFactory.make(player_settings["video_enc"], "video_enc")
        self.enc_filter = Gst.ElementFactory.make("capsfilter", "enc_filter")
        self.video_parse = Gst.ElementFactory.make(player_settings["video_parse"], "video_parse")

    def set_properties(self, player_settings):
        video_caps = Gst.Caps.from_string(player_settings["video_caps"])
        self.video_filter.set_property("caps", video_caps)
        enc_caps = Gst.Caps.from_string(player_settings["enc_caps"])
        self.enc_filter.set_property("caps", enc_caps)
        for param, value in player_settings["videosrc_properties"]:
            self.videosrc.set_property(param, value)
        for param, value in player_settings["video_enc_properties"]:
            self.video_enc.set_property(param, value)

    def add_elements(self, player_settings):
        self.player.add(self.videosrc)
        self.player.add(self.video_filter)
        self.player.add(self.video_enc)
        self.player.add(self.enc_filter)
        self.player.add(self.muxer)
        self.player.add(self.rtmpsink)

    def link_elements(self, player_settings):
        self.videosrc.link(self.video_filter)
        self.video_filter.link(self.video_enc)
        self.video_enc.link(self.enc_filter)
        self.enc_filter.link(self.muxer)
        self.muxer.link(self.rtmpsink)
        
    def start_stop(self, w):
        if self.state_button.get_label() == "Start":
            urlpath = self.url_entry.get_text().strip()
            self.state_button.set_label("Stop")
            self.player.get_by_name("rtmpsink").set_property("location", urlpath)
            self.player.set_state(Gst.State.PLAYING)

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
    "title" : "Untitled",
    "videosrc" : "v4l2src",
    "videosrc_properties" : (),
    "video_caps" : "video/x-raw,width=640,height=480",
    "video_enc" : "x264enc",
    "video_enc_properties" : (("tune", "zerolatency"),), 
    "enc_caps" : "video/x-h264,profile=baseline",
    "video_parse" : "h264parse",
} 

if __name__ == "__main__":
    Gst.init(None)
    win = PlayerWindow(default_settings)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
