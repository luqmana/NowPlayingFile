# coding: utf-8
#
# Copyright (C) 2011 - Luqman Aden
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

import os
import rb
from gi.repository import GObject, Peas
from gi.repository import RB

NORMAL_SONG_ARTIST = 'artist'
NORMAL_SONG_TITLE  = 'title'
NORMAL_SONG_ALBUM  = 'album'
STREAM_SONG_ARTIST = 'rb:stream-song-artist'
STREAM_SONG_TITLE  = 'rb:stream-song-title'
STREAM_SONG_ALBUM  = 'rb:stream-song-album'

class NowPlayingFilePlugin (GObject.Object, Peas.Activatable):

	__gtype_name__ = 'NowPlayingFilePlugin'
	object = GObject.property(type = GObject.Object)

	def __init__(self):
	
		GObject.Object.__init__(self)
		
	def do_activate(self):
	
		self.shell = self.object
		self.db = self.shell.get_property("db")
		self.current_entry = None
		self.out_file = "/tmp/nowplaying.out"
				
		sp = self.shell.props.shell_player
		
		self.pc_id = sp.connect('playing-changed',
								self.playing_changed)
		self.psc_id = sp.connect('playing-song-changed',
								 self.playing_song_changed)
		self.pspc_id = sp.connect('playing-song-property-changed',
								  self.playing_song_property_changed)
								  
		if sp.get_playing():
			self.set_entry(sp.get_playing_entry())
			
	def do_deactivate(self):
	
		sp = self.shell.props.shell_player
		sp.disconnect(self.pc_id)
		sp.disconnect(self.psc_id)
		sp.disconnect(self.pspc_id)
		
		self.nothing_playing()
		os.remove(self.out_file)
		
		del self.db
		del self.shell
		del self.current_entry
		del self.output_file
		
	def playing_changed(self, sp, playing):
	
		if playing:
			self.set_entry(sp.get_playing_entry())
		else:
			self.current_entry = None
			self.nothing_playing()
			
	def playing_song_changed(self, sp, entry):
	
		if sp.get_playing():
			self.set_entry(entry)
		else:
			self.nothing_playing()
			
	def playing_song_property_changed(self, sp, uri, property, old, new):
	
		if sp.get_playing():
			self.get_songinfo_from_entry()
		else:
			self.nothing_playing()
			
	def set_entry(self, entry):
	
		if entry == self.current_entry: return
		if entry is None: return
		
		self.current_entry = entry
		
		self.get_songinfo_from_entry()
		
	def get_songinfo_from_entry(self):
	
		properties = {}
	
		properties = {
	
			"title" : RB.RhythmDBPropType.TITLE,
			"artist" : RB.RhythmDBPropType.ARTIST,
			"album" : RB.RhythmDBPropType.ALBUM
	
		}
		
	
		properties = dict(
			(k, self.current_entry.get_string(v))
			for k, v in properties.items()
		)

		if self.current_entry.get_entry_type().props.category == RB.RhythmDBEntryCategory.STREAM:
			
			properties["title"] = self.db.entry_request_extra_metadata(self.current_entry, STREAM_SONG_TITLE)
			properties["album"] = self.current_entry.get_string(RB.RhythmDBPropType.TITLE)
			
		self.write_file_from_songinfo(properties)
			
	def nothing_playing(self):
	
		output_file = open(self.out_file, "w")
		print >> output_file, "Nothing",
		output_file.close()
				
	def write_file_from_songinfo(self, properties):
	
		output_file = open(self.out_file, "w")
		if "artists" not in properties:
			print >> output_file, properties["title"] + " - " + properties["artist"] + " (" + properties["album"] + ") ♫",
		else:
			print >> output_file, properties["title"] + "(" + properties["album"] + ") ♫",
		output_file.close()
