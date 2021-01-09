#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Copyright (C) 2011  P.L. Lucas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
import os
from gi.repository import GLib, GObject, Gio, Pango, GdkPixbuf, Gtk

class DialogEntry(Gtk.Dialog):
	def __init__(self, parent, label):
		Gtk.Dialog.__init__(self, "My Dialog", parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
		self.set_default_size(150, 100)
		label = Gtk.Label(label)
		self.entry=Gtk.Entry()
		box = self.get_content_area()
		box.add(label)
		box.add(self.entry)
		self.show_all()

class Builder:
	
	def xinput_list(self, treestore):
		fin=os.popen('xinput --list', 'r')
		lines=fin.read().split('\n')
		fin.close()
		spaces_level=-1
		treeiter=None
		for line in lines:
			if line=='' or line==None:
				break
			m = re.search('id=([0-9]+)', line)
			idn=m.group(1)
			m = re.search('[^A-Za-z0-9]*([A-Za-z0-9 ]+)', line)
			name=m.group(1)
			m = re.search('([^A-Za-z0-9]*)', line)
			n=len(m.group(1))
			if spaces_level==-1 or n<=spaces_level:
				treeiter=treestore.append(None, [name.strip(), int(idn)])
				spaces_level=n
			else:
				treestore.append(treeiter, [name.strip(), int(idn)])
	
	def apply_callback(self, widget):
		treeiter = self.treestore.get_iter_first()
		while treeiter!=None:
			if self.treestore.iter_has_child(treeiter):
				parent_id=self.treestore[treeiter][1]
				childiter = self.treestore.iter_children(treeiter)
				while childiter!=None:
					child_id=self.treestore[childiter][1]
					os.system('xinput --reattach {child_id} {parent_id}'.format( child_id=child_id, parent_id=parent_id ) )
					childiter= self.treestore.iter_next(childiter)
			treeiter = self.treestore.iter_next(treeiter)
		return False
	
	def reload_callback(self, widget):
		self.init_treeview()
	
	def remove_callback(self, widget):
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter != None and self.treestore[treeiter][1]!=None:
			os.system('xinput --remove-master "{name}"'.format( name=self.treestore[treeiter][1] ) )
			self.init_treeview()
	
	def add_callback(self, widget):
		dialog=DialogEntry(self.builder.get_object('window'), 'Name:')
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			name=dialog.entry.get_text()
			os.system('xinput --create-master "{name}"'.format( name=name ) )
			self.init_treeview()
		dialog.destroy()
	
	def delete_callback(self, window, data=None):
		Gtk.main_quit()
	
	def init_treeview(self):
		self.treestore = Gtk.TreeStore(str, int)
		self.treeview=self.builder.get_object('treeview')
		
		self.treeview.set_model(self.treestore)
		
		if self.column==None:
			renderer = Gtk.CellRendererText()
			self.column = Gtk.TreeViewColumn("Device", renderer, text=0)
			self.treeview.append_column(self.column)
		
		self.xinput_list(self.treestore)
		
		
		#select = self.treeview.get_selection()
		#select.connect("changed", self.select_callback)
		#self.treeview.connect("row-activated", self.row_activated_callback)
		
		
		#remove_toolbutton = self.builder.get_object("remove_toolbutton")
		#remove_toolbutton.set_state(Gtk.StateType.INSENSITIVE)
		
		#add_toolbutton = self.builder.get_object("add_toolbutton")
		#add_toolbutton.set_state(Gtk.StateType.INSENSITIVE)
		

	def __init__(self):
		# use GtkBuilder to build our interface from the XML file 
		self.builder = Gtk.Builder()
		if self.builder.add_from_file("xinput.xml")==0:
			print ("Failed to load UI XML file: mainwindow.xml")
			sys.exit(1)
		
		self.column=None
		
		# connect signals
		self.builder.connect_signals(self)

		
		self.window = self.builder.get_object("window")
		
		
		#self.comandos_treeview = self.builder.get_object("comandos_treeview")
		#self.conexiones_treeview = self.builder.get_object("conexiones_treeview")
		
		self.init_treeview()
		
		self.window.show()

if __name__ == "__main__":
	editor = Builder()
	Gtk.main()
