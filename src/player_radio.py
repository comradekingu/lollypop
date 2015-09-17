# Copyright (c) 2014-2015 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import TotemPlParser

from lollypop.playlists import RadiosManager
from lollypop.player_base import BasePlayer
from lollypop.define import Type
from lollypop.objects import Track


class RadioPlayer(BasePlayer):
    """
        Radio player
        This class neeed the parent object to be a BinPlayer
    """

    def __init__(self):
        """
            Init radio player
        """
        BasePlayer.__init__(self)
        self._current = None

    def load(self, track):
        """
            Load radio at uri
            @param track as Track
        """
        try:
            self._current = track
            parser = TotemPlParser.Parser.new()
            parser.connect("entry-parsed", self._on_entry_parsed, track)
            parser.parse_async(track.uri, True, None,
                               self._on_parsing_finished, track)
        except Exception as e:
            print("RadioPlayer::load(): ", e)
            return False
        self.set_party(False)
        self._albums = None
        return True

    def next(self):
        """
            Return next radio name, uri
            @return Track
        """
        track = Track()
        if self.current_track.id != Type.RADIOS:
            return track

        radios_manager = RadiosManager()
        radios = radios_manager.get()
        i = 0
        for (radio_id, name) in radios:
            i += 1
            if self.current_track.album_artist == name:
                break

        # Get next radio
        if i >= len(radios):
            i = 0

        name = radios[i][1]
        uris = radios_manager.get_tracks(name)
        if len(uris) > 0:
            track.set_radio(name, uris[0])
        return track

    def prev(self):
        """
            Return prev radio name, uri
            @return Track
        """
        track = Track()
        if self.current_track.id != Type.RADIOS:
            return track

        radios_manager = RadiosManager()
        radios = radios_manager.get()
        i = len(radios) - 1
        for (radio_id, name) in reversed(radios):
            i -= 1
            if self.current_track.album_artist == name:
                break

        # Get prev radio
        if i < 0:
            i = len(radios) - 1

        name = radios[i][1]
        uris = radios_manager.get_tracks(name)
        if len(uris) > 0:
            track.set_radio(name, uris[0])
        return track

#######################
# PRIVATE             #
#######################
    def _on_entry_parsed(self, parser, uri, metadata, track):
        """
            Play stream
            @param parser as TotemPlParser.Parser
            @param track uri as str
            @param metadata as GLib.HastTable
            @param track as Track
        """
        # Only start playing if context always True
        if self._current == track:
            self._stop()
            self._playbin.set_property('uri', uri)
            self.current_track = track
            self._current = None
            self.play()

    def _on_parsing_finished(self, source, result, track):
        """
            Play track if was not a playlist
            @param source as GObject.Object
            @param result as Gio.AsyncResult
            @param track as Track
        """
        if self.current_track != track:
            self._stop()
            self._playbin.set_property('uri', track.uri)
            self.current_track = track
            self._current = None
            self.play()