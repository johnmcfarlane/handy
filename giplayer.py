#!/usr/bin/python

import os
from fcntl import fcntl,F_GETFL,F_SETFL
from select import select
from subprocess import Popen,PIPE,STDOUT 
from threading import Thread

import ConfigParser

try:
	import pygtk
	pygtk.require('2.0')
except:
	pass
try:
	import gtk
	import gobject
except:
	print('GTK not available')
	sys.exit(1)


##																				
## global function that calls a shell command, waits and returns stdout 		
##																				
def shell_pipe(arg_list):
	p = Popen(arg_list,stdout=PIPE,stderr=STDOUT)
	p.wait()
	return p.stdout


##																				
## Preferences class 															
##																				
class Preferences:
	def __init__ (self):
		self.changed = False
		self.quality = [
			'flashlow',
			'flashstd,flashlow',
			'flashhigh,flashstd',
			'flashvhigh,flashhigh,flashstd',
			'flashhd,flashvhigh,flashhigh,flashstd']
		self.config = ConfigParser.ConfigParser()
		self.fpath = os.path.expanduser("~/.get_iplayer/giPlayer.conf")
		if not self.config.read(self.fpath):
			self.initwrite()
		try: 
			self.config.get("TV","subtitles")
		except ConfigParser.NoOptionError:
			self.config.set("TV","subtitles","off")
			self.changed = True
			self.write()
			
	def initwrite(self):
		config_dir = os.path.expanduser("~/.get_iplayer")
		if not os.path.exists(config_dir): 
			os.mkdir(config_dir)
		config = self.config
		config.add_section("Radio")
		config.set("Radio","folder",os.path.expanduser("~/Videos"))
		config.set("Radio","format","mp3")
		config.add_section("TV")
		config.set("TV","folder",os.path.expanduser("~/Videos"))
		config.set("TV","format","mp4")
		config.set("TV","quality","3") # High
		config.set("TV","subtitles","off")
		config.add_section("Player")
		config.set("Player","default","vlc")
		config.set("Player","quality","5")
		self.changed = True
		self.write()
		
	def write(self):
		if self.changed:
			print "writing conf file"
			with open(self.fpath, 'wb') as configfile:
				self.config.write(configfile)
				self.changed = False
			
	def init_prefs_dialog(self):
		builder = iplayer.builder
		config = self.config
		# Radio Prefs
		builder.get_object("filechooserRadio").set_current_folder(
			config.get("Radio","folder"))
		if config.get("Radio","format")=="mp3":
			builder.get_object("rbRadioFormat").set_active(True)
		else:
			builder.get_object("rbRadioFormat2").set_active(True)
		# TV Prefs
		builder.get_object("filechooserTV").set_current_folder(
			config.get("TV","folder"))
		if config.get("TV","format")=="mp4":
			builder.get_object("rbTVFormat").set_active(True)
		else:
			builder.get_object("rbTVFormat2").set_active(True)
		if config.get("TV","subtitles")=="off":
			builder.get_object("subtitlesoff").set_active(True)
		else:
			builder.get_object("subtitles").set_active(True)
		# Player Prefs
		if config.get("Player","default")=="vlc":	
			builder.get_object("def_player").set_active(True)
		elif config.get("Player","default")=="mplayer":
			builder.get_object("def_player1").set_active(True)
		else:
			builder.get_object("def_player2").set_active(True)
			
		if config.get("Player","quality")=="4":
			builder.get_object("def_quality").set_active(True)
		elif config.get("Player","quality")=="3":
			builder.get_object("def_quality1").set_active(True)
		elif config.get("Player","quality")=="2":
			builder.get_object("def_quality2").set_active(True)
		else:
			builder.get_object("def_quality3").set_active(True)
			
			
			
	def apply_prefs_dialog(self):
		self.changed = True
		builder = iplayer.builder
		config = self.config
		# Radio Prefs
		config.set("Radio","folder",
			builder.get_object("filechooserRadio").get_current_folder())
		if builder.get_object("rbRadioFormat").get_active():
			config.set("Radio","format","mp3")
		else:
			config.set("Radio","format","aac")
		# TV Prefs
		config.set("TV","folder",
			builder.get_object("filechooserTV").get_current_folder())
		if builder.get_object("rbTVFormat").get_active():
			config.set("TV","format","mp4")
		else:
			config.set("TV","format","flv")
		if builder.get_object("subtitles").get_active():
			config.set("TV","subtitles","on")
		else:
			config.set("TV","subtitles","off")
		# Player Prefs
		if builder.get_object("def_player").get_active():	
			config.set("Player","default","vlc")
		elif builder.get_object("def_player1").get_active():
			config.set("Player","default","mplayer")
		else:
			config.set("Player","default","ffmpeg")
			
		if builder.get_object("def_quality").get_active():
			config.set("Player","quality","4")
		elif builder.get_object("def_quality1").get_active():
			config.set("Player","quality","3")
		elif builder.get_object("def_quality2").get_active():
			config.set("Player","quality","2")
		else:
			config.set("Player","quality","1")

	def init_menu(self,builder):
		i = self.config.getint("TV","quality")
		menuitem = builder.get_object("QualityItem").get_group()[i]
		menuitem.set_active(True)
	
	def set_quality(self,value):
		if self.config.getint("TV","quality")!=value:
			self.changed = True
			self.config.set("TV","quality",str(value))
			
	def get_quality(self):
		return self.quality[self.config.getint("TV","quality")]
		


##																				
## Base class that calls a command in a new thread and reads stdout				
## The inherited class parses each line											
##																				
class CommandThread(Thread):
	def __init__ (self,errout):
		Thread.__init__(self)
		self.command = []
		self.errout = errout
		self.status = -1

	def run(self):
		if self.errout:
			self.process = Popen(self.command, stdout=PIPE, stderr=STDOUT)
		else:
			self.process = Popen(self.command, stdout=PIPE)
			
		out = self.process.stdout
		outfd = out.fileno()
		file_flags = fcntl(outfd, F_GETFL)
		fcntl(outfd, F_SETFL, file_flags | os.O_NDELAY)

		# use 'select' for reading
		while not self.process.poll():
			ready = select([outfd],[],[]) # wait for input
			if outfd in ready[0]:
				outchunk = out.read()
				if outchunk == '' : break
				select([],[],[],.1) # give a little time to fill buffers
		
				lines = outchunk.split('\n')
				for line in lines:
					ok = self.parse_line(line)
					if not ok: break
			if not ok: break
					
	def parse_line(self,line):
		return True
	
	def abort(self):
		self.process.kill()
					

##																				
## Class that searches for TV and Radio Programmes								
##																				
class SearchThread(CommandThread):
	def __init__ (self):
		CommandThread.__init__(self,False)
		builder = iplayer.builder
		programme = builder.get_object("NameEntry").get_chars(0,-1)		
		iplayer.listview.reset()
		self.pb = iplayer.progress_bar
		
		print "searching for " + iplayer.mediatype + " programme: " + programme
		self.command = ["get_iplayer","--type",iplayer.mediatype,programme,
			"--listformat","<index>|<name>|<episode>|<channel>|<pid>"]
		

	def parse_line(self,line):
		if self.pb.cancelled: 
			return False
		
		elif "INFO: Getting" in line:
			print line
			gtk.gdk.threads_enter()
			self.pb.show(line[6:-1],200)
			gtk.gdk.threads_leave()

		elif '|' in line:
			if self.pb.timer: self.pb.hide()
			if "Added:" in line: return True
			field = line.split('|')
			id = field[0].strip()
			name = field[1].strip()
			episode = field[2].strip()
			channel = field[3].strip()
			pid = field[4].strip()
			
			iplayer.listview.append([name,episode,channel,id,pid])
			
		return True


##																				
## Class that downloads TV and Radio Programmes									
##																				
class DownloadThread(CommandThread):
	def __init__ (self,details):
		CommandThread.__init__(self,True) # include stderr
		self.id = details[3]
		self.pb = iplayer.progress_bar
		self.pb.show("Starting download...",-1) # -1 = update manually
		
		command = ["get_iplayer","--force",
			"--file-prefix",'<name>-<episode>',
			"",self.id]
		if iplayer.mediatype == "tv":
			self.filepath = prefs.config.get("TV","folder")
			command.append("--modes")
			command.append(prefs.get_quality())
			if prefs.config.get("TV","format")=="flv":
				command.append("--raw")
			if prefs.config.get("TV","subtitles")=="on":
				command.append("--subtitles")
		else: # radio
			self.filepath = prefs.config.get("Radio","folder")
			if prefs.config.get("Radio","format")=="aac":
				command.append("--radiomode")
				command.append("flashaac")
			
		command.append("--output")
		command.append(self.filepath)
		
		self.command = command
		self.filename = ""
		self.completed = False
		self.REALfrmt = False
		self.status = -1
		
	def run(self):
		CommandThread.run(self)		
		if self.pb.cancelled:
			print "abort download"
			self.abort()
		
	def parse_line(self,line):
		if self.pb.cancelled: 
			return False
		
		elif "INFO: " in line:
			if "Recorded" in line:
				self.filename = self.filepath + "/" + line.split('/')[-1]
				print "downloaded: "+self.filename
				self.pb.hide()
			
			elif ("tagging" in line) and self.completed:
				id_tagging = True
				print "id_tagging"
				self.pb.set_label("Tagging file")
		
		elif line[0:11]=="FLVStreamer":
			print "using flvstreamer"
			self.pb.set_label("Downloading using Flvstreamer...")
			
		elif line[0:25]=="REAL file format detected":
			print "Downloading REAL audio..."
			#self.pb.set_label("Downloading REAL audio...")
			self.REALfrmt = True
			self.pb.show("Downloading REAL audio...",200)
			
		elif line[0:17]=="Download complete":
			self.completed = True
			print "download complete"
			self.pb.set_label("Post processing...")
			
		else:
			if not self.completed and not self.REALfrmt:
				# update progress
				if line.find('%')>0:
					gtk.gdk.threads_enter()
					self.pb.parse(line)				
					gtk.gdk.threads_leave()
				elif line.find("kB / ")>0:
					gtk.gdk.threads_enter()
					self.pb.update_text(line.strip())				
					gtk.gdk.threads_leave()					
		return True

##																				
## Class that Plays TV and Radio Programmes									
##																				
class PlayThread(CommandThread):
	def __init__ (self,details):
		CommandThread.__init__(self,True) # include stderr
		self.id = details[3]
		self.modes = "flashstd, flashnormal"
		if prefs.config.get("Player","quality") == "2":
			self.modes = "flashhigh, " + self.modes
		elif prefs.config.get("Player","quality") == "3":
			self.modes = "flashvhigh, flashhigh, " + self.modes
		elif prefs.config.get("Player","quality") == "4":
			self.modes = "flashhd, flashvhigh, flashhigh, " + self.modes
		
		self.player='"vlc -"'
		if prefs.config.get("Player","default") == "mplayer":
			self.player = '"mplayer -cache 3072 -"'
		elif prefs.config.get("Player","default") == "ffmpeg":
			self.player = '"ffplay -"'

		command = "get_iplayer --stream " + self.id + ' --modes ' + self.modes + ' --player='+self.player
		self.command = command
		print self.command
				
	def run(self):
		os.system (self.command)
		return True

##																				
## Class that represents the Progress Bar Dialog								
##																				
class ProgressDialog:
	def reset(self):
		builder = iplayer.builder
		self.dlg = builder.get_object("ProgressDialog")
		self.label = builder.get_object("ProgressLabel")
		self.bar = builder.get_object("ProgressBar")
		self.timer = 0
		self.percent = 0
		self.cancelled = False

	def pulse(self):
		self.bar.pulse()
		return True
		
	def update(self,percent):
		p = float(percent)
		if (p<0.0) or (p>100.0): return
		if self.percent == p: return
		self.percent = p
		self.bar.set_text(percent+'%')
		self.bar.set_fraction(p/100.0)
		
	def update_text(self,text):
		self.bar.set_text(text)
	
	def set_label(self,text):
		self.label.set_text(text)
		
	def show(self,label,pulse_ms):
		self.label.set_text(label)
		if(pulse_ms>0):
			text=""
		else:
			text="0.0%"
		self.bar.set_text(text)
		self.bar.set_fraction(0.0)
		self.cancelled = False
		self.dlg.show()
		if(pulse_ms>0):
			self.timer = gobject.timeout_add(pulse_ms, self.pulse)
			
	def hide(self):	
		if self.timer:
			gobject.source_remove(self.timer)
			self.timer = 0
		self.dlg.hide()
	
	def cancel(self):
		self.cancelled = True
		self.hide()
		
	def parse(self,line):
		# calculate percentage from text in line
		end = line.find("%")
		if end > 0 :
			st = end - 1
			while line[st].isdigit() or line[st]=='.': st = st - 1 
			self.update(line[st+1:end])
			

##																				
## Class that represents the ListView of programmes								
##																				
class ListView:
	def __init__(self,widget):
		self.listview = widget		
		# create tree view columns
		self._add_column("Title",0,240)
		self._add_column("Episode",1,240)
		self._add_column("Channel",2,-1)
		#Create the listStore Model
		self.liststore = gtk.ListStore(str,str,str,str,str)
		#Attach the model to the treeView
		self.listview.set_model(self.liststore)	

	def _add_column(self,name,pos,width):
		column = gtk.TreeViewColumn(name, gtk.CellRendererText(),text=pos)
		if width>0:
			column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)		
			column.set_fixed_width(width)
		else:
			column.set_resizable(False)		
		self.listview.append_column(column)			

	def append(self,text):
		self.liststore.append(text)
		
	def reset(self):
		self.liststore.clear()
		
	def get_row(self):
		tuple = self.listview.get_selection().get_selected()
		return int(tuple[0].get_string_from_iter(tuple[1]))
		
	def row_data(self,row):
		return self.liststore[row]		
		
		
##																				
## Main Application Window class												
##																				
class MainWindow:
	def __init__(self):
		self.builder = gtk.Builder()
		#self.builder.add_from_file("giPlayer.ui")
		self.builder.add_from_file("/usr/share/giPlayer/giPlayer.ui")
		dic = {
			"on_radio_clicked": self.search_radio,
			"on_tv_clicked": self.search_tv,
			"on_download_clicked": self.download,
			"on_play_clicked": self.play,
			"on_row_selected": self.row_selected,
			"on_row_activated": self.row_activated,
			"on_about": self.about,
			"on_pb_cancel": self.progress_bar_cancel,
			"on_preferences": self.preferences,
			"on_quality": self.quality,
			"gtk_main_quit": self.quit,
		}
		self.builder.connect_signals(dic)
		self.window = self.builder.get_object("MainWindow")
		self.window.show()
		self.listview = ListView(self.builder.get_object("ProgrammeView"))
		self.progress_bar = ProgressDialog()
		prefs.init_menu(self.builder)

	def search_radio(self,widget):
		self._search("radio")
		
	def search_tv(self,widget):
		self._search("tv")
		
	def _search(self,mediatype):
		self.progress_bar.reset()
		self.builder.get_object("Download").set_sensitive(False)
		self.builder.get_object("Play").set_sensitive(False)
		self.mediatype = mediatype
		SearchThread().start()
		
	def row_selected(self,widget):
		self.builder.get_object("Download").set_sensitive(True)		
		self.builder.get_object("Play").set_sensitive(True)		

	def row_activated(self,widget,rowdata,column):
		self._download_programme(rowdata[0])
		
	def download(self,widget):
		self._download_programme(self.listview.get_row())
		
	def _download_programme(self,row):
		self.progress_bar.reset()
		download = DownloadThread(self.listview.row_data(row)).start()
		
	def play(self,widget):
		self._play_programme(self.listview.get_row())	
		
	def _play_programme(self,row):
		play = PlayThread(self.listview.row_data(row)).start()
			
	def about(self,widget):
		version = shell_pipe(["get_iplayer","-V"]).readline()
		self.builder.get_object("get_iplayerLabel").set_text(version)
		self._modal_dialog("AboutDialog")		
		
	def _modal_dialog(self,name):
		dlg = self.builder.get_object(name)
		result = dlg.run()
		dlg.hide()
		return result
		
	def progress_bar_cancel(self,widget):
		self.progress_bar.cancel()
		
	def preferences(self,widget):
		prefs.init_prefs_dialog()
		id = self._modal_dialog("PreferencesDialog")
		if id==1:
			prefs.apply_prefs_dialog()
			
	def quality(self,widget):
		if not widget.get_active(): return
		items = widget.get_group()
		i = items.index(widget)
		print "Quality setting = "+str(i)
		prefs.set_quality(i)
		
	def quit(self,widget):
		prefs.write()
		gtk.main_quit()

## main																			
if __name__ == "__main__":	

	gtk.gdk.threads_init()	
	prefs = Preferences()
	iplayer = MainWindow()
	gtk.main()
	
