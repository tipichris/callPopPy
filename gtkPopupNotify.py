#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#gtkPopupNotify.py
#
# Copyright 2009 Daniel Woodhouse
# modified by NickCis 2010 http://github.com/NickCis/gtkPopupNotify
# Modifications:
# Added: * Corner support (notifications can be displayed in all corners
# * Use of gtk Stock items or pixbuf to render images in notifications
# * Posibility of use fixed height
# * Posibility of use image as background
# * Not displaying over Windows taskbar(taken from emesene gpl v3)
# * y separation.
# * font description options
# * Callbacks For left, middle and right click
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import gtk
import pango
import gobject

# This code is used only on Windows to get the location on the taskbar
# Taken from emesene Notifications (Gpl v3)
taskbarOffsety = 0
taskbarOffsetx = 0
if os.name == "nt":
    import ctypes
    from ctypes.wintypes import RECT, DWORD
    user = ctypes.windll.user32
    MONITORINFOF_PRIMARY = 1
    HMONITOR = 1

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ('cbSize', DWORD),
            ('rcMonitor', RECT),
            ('rcWork', RECT),
            ('dwFlags', DWORD)
            ]

    taskbarSide = "bottom"
    taskbarOffset = 30
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(info)
    info.dwFlags = MONITORINFOF_PRIMARY
    user.GetMonitorInfoW(HMONITOR, ctypes.byref(info))
    if info.rcMonitor.bottom != info.rcWork.bottom:
        taskbarOffsety = info.rcMonitor.bottom - info.rcWork.bottom
    if info.rcMonitor.top != info.rcWork.top:
        taskbarSide = "top"
        taskbarOffsety = info.rcWork.top - info.rcMonitor.top
    if info.rcMonitor.left != info.rcWork.left:
        taskbarSide = "left"
        taskbarOffsetx = info.rcWork.left - info.rcMonitor.left
    if info.rcMonitor.right != info.rcWork.right:
        taskbarSide = "right"
        taskbarOffsetx = info.rcMonitor.right - info.rcWork.right
        
class NotificationStack():
    def __init__(self, size_x=300, size_y=-1, timeout=5, corner=(False, False), sep_y=0):
        """
Create a new notification stack. The recommended way to create Popup instances.
Parameters:
`size_x` : The desired width of the notifications.
`size_y` : The desired minimum height of the notifications. If it isn't set,
or setted to None, the size will automatically adjust
`timeout` : Popup instance will disappear after this timeout if there
is no human intervention. This can be overridden temporarily by passing
a new timout to the new_popup method.
`coner` : 2 Value tuple: (true if left, True if top)
`sep_y` : y distance to separate notifications from each other
"""
        self.size_x = size_x
        self.size_y = -1 if (size_y == None) else size_y
        self.timeout = timeout
        self.corner = corner
        self.sep_y = sep_y
        """
Other parameters:
These will take effect for every popup created after the change.
`edge_offset_y` : distance from the bottom of the screen and
the bottom of the stack.
`edge_offset_x` : distance from the right edge of the screen and
the side of the stack.
`max_popups` : The maximum number of popups to be shown on the screen
at one time.
`bg_color` : if None default is used (usually grey). set with a gtk.gdk.Color.
`bg_pixmap` : Pixmap to use as background of notification. You can set a gtk.gdk.Pixmap
or a path to a image. If none, the color background will be displayed.
`bg_mask` : If a gtk.gdk.pixmap is specified under bg_pixmap, the mask of the pixmap has to be setted here.
`fg_color` : if None default is used (usually black). set with a gtk.gdk.Color.
`show_timeout` : if True, a countdown till destruction will be displayed.
`close_but` : if True, the close button will be displayed.
`fontdesc` : a 3 value Tuple containing the pango.FontDescriptions of the Header, message and counter
(in that order). If a string is suplyed, it will be used for the 3 the same FontDescription.
http://doc.stoq.com.br/devel/pygtk/class-pangofontdescription.html
"""
        self.edge_offset_x = 0
        self.edge_offset_y = 0
        self.max_popups = 5
        self.fg_color = None
        self.bg_color = None
        self.bg_pixmap = None
        self.bg_mask = None
        self.show_timeout = False
        self.close_but = True
        self.fontdesc = ("Sans Bold 14", "Sans 12", "Sans 10")
        
        self._notify_stack = []
        self._offset = 0

        
    def new_popup(self, title, message, image=None, leftCb=None, middleCb=None, rightCb=None):
        """Create a new Popup instance."""
        if len(self._notify_stack) == self.max_popups:
            self._notify_stack[0].hide_notification()
        self._notify_stack.append(Popup(self, title, message, image, leftCb, middleCb, rightCb))
        self._offset += self._notify_stack[-1].y
        
    def destroy_popup_cb(self, popup):
        self._notify_stack.remove(popup)
        #move popups down if required
        offset = 0
        for note in self._notify_stack:
            offset = note.reposition(offset, self)
        self._offset = offset
    
    

    
class Popup(gtk.Window):
    def __init__(self, stack, title, message, image, leftCb, middleCb, rightCb):
        gtk.Window.__init__(self, type=gtk.WINDOW_POPUP)
        
        self.leftclickCB = leftCb
        self.middleclickCB = middleCb
        self.rightclickCB = rightCb
        
        self.set_size_request(stack.size_x, stack.size_y)
        self.set_decorated(False)
        self.set_deletable(False)
        self.set_property("skip-pager-hint", True)
        self.set_property("skip-taskbar-hint", True)
        self.connect("enter-notify-event", self.on_hover, True)
        self.connect("leave-notify-event", self.on_hover, False)
        self.set_opacity(0.2)
        self.destroy_cb = stack.destroy_popup_cb
        
        if type(stack.fontdesc) == tuple or type(stack.fontdesc) == list:
            fontH, fontM, fontC = stack.fontdesc
        else:
            fontH = fontM = fontC = stack.fontdesc
        
        main_box = gtk.VBox()
        header_box = gtk.HBox()
        self.header = gtk.Label()
        self.header.set_markup("<b>%s</b>" % title)
        self.header.set_padding(3, 3)
        self.header.set_alignment(0, 0)
        try:
            self.header.modify_font(pango.FontDescription(fontH))
        except Exception, e:
            print e
        header_box.pack_start(self.header, True, True, 5)
        if stack.close_but:
            close_button = gtk.Image()
        
            close_button.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
            close_button.set_padding(3, 3)
            close_window = gtk.EventBox()
            close_window.set_visible_window(False)
            close_window.connect("button-press-event", self.hide_notification)
            close_window.add(close_button)
            header_box.pack_end(close_window, False, False)
        main_box.pack_start(header_box)
        
        body_box = gtk.HBox()
        if image is not None:
            self.image = gtk.Image()
            self.image.set_size_request(70, 70)
            self.image.set_alignment(0, 0)
            if image in gtk.stock_list_ids():
                self.image.set_from_stock(image, gtk.ICON_SIZE_DIALOG)
            elif type(image) == gtk.gdk.Pixbuf:
                self.image.set_from_pixbuf(image)
            else:
                self.image.set_from_file(image)
            body_box.pack_start(self.image, False, False, 5)
        self.message = gtk.Label()
        self.message.set_property("wrap", True)
        self.message.set_size_request(stack.size_x - 90, -1)
        self.message.set_alignment(0, 0)
        self.message.set_padding(5, 10)
        self.message.set_markup(message)
        try:
            self.message.modify_font(pango.FontDescription(fontM))
        except Exception, e:
            print e
        self.counter = gtk.Label()
        self.counter.set_alignment(1, 1)
        self.counter.set_padding(3, 3)
        try:
            self.counter.modify_font(pango.FontDescription(fontC))
        except Exception, e:
            print e
        self.timeout = stack.timeout
        
        body_box.pack_start(self.message, True, False, 5)
        body_box.pack_end(self.counter, False, False, 5)
        main_box.pack_start(body_box)
        eventbox = gtk.EventBox()
        eventbox.set_property('visible-window', False)
        eventbox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        eventbox.connect("button_press_event", self.onClick)
        eventbox.add(main_box)
        self.add(eventbox)
        if stack.bg_pixmap is not None:
            if not type(stack.bg_pixmap) == gtk.gdk.Pixmap:
                stack.bg_pixmap, stack.bg_mask = gtk.gdk.pixbuf_new_from_file(stack.bg_pixmap).render_pixmap_and_mask()
            self.set_app_paintable(True)
            self.connect_after("realize", self.callbackrealize, stack.bg_pixmap, stack.bg_mask)
        elif stack.bg_color is not None:
            self.modify_bg(gtk.STATE_NORMAL, stack.bg_color)
        if stack.fg_color is not None:
            self.message.modify_fg(gtk.STATE_NORMAL, stack.fg_color)
            self.header.modify_fg(gtk.STATE_NORMAL, stack.fg_color)
            self.counter.modify_fg(gtk.STATE_NORMAL, stack.fg_color)
        self.show_timeout = stack.show_timeout
        self.hover = False
        self.show_all()
        self.x, self.y = self.size_request()
        #Not displaying over windows bar
        if os.name == 'nt':
            if stack.corner[0] and taskbarSide == "left":
                stack.edge_offset_x += taskbarOffsetx
            elif not stack.corner[0] and taskbarSide == 'right':
                stack.edge_offset_x += taskbarOffsetx
            if stack.corner[1] and taskbarSide == "top":
                stack.edge_offset_x += taskbarOffsety
            elif not stack.corner[1] and taskbarSide == 'bottom':
                stack.edge_offset_x += taskbarOffsety
                
        if stack.corner[0]:
            posx = stack.edge_offset_x
        else:
            posx = gtk.gdk.screen_width() - self.x - stack.edge_offset_x
        sep_y = 0 if (stack._offset == 0) else stack.sep_y
        self.y += sep_y
        if stack.corner[1]:
            posy = stack._offset + stack.edge_offset_y + sep_y
        else:
            posy = gtk.gdk.screen_height()- self.y - stack._offset - stack.edge_offset_y
        self.move(posx, posy)
        self.fade_in_timer = gobject.timeout_add(100, self.fade_in)
        
        

    def reposition(self, offset, stack):
        """Move the notification window down, when an older notification is removed"""
        if stack.corner[0]:
            posx = stack.edge_offset_x
        else:
            posx = gtk.gdk.screen_width() - self.x - stack.edge_offset_x
        if stack.corner[1]:
            posy = offset + stack.edge_offset_y
            new_offset = self.y + offset
        else:
            new_offset = self.y + offset
            posy = gtk.gdk.screen_height() - new_offset - stack.edge_offset_y + stack.sep_y
        self.move(posx, posy)
        return new_offset

    
    def fade_in(self):
        opacity = self.get_opacity()
        opacity += 0.15
        if opacity >= 1:
            self.wait_timer = gobject.timeout_add(1000, self.wait)
            return False
        self.set_opacity(opacity)
        return True
            
    def wait(self):
        if not self.hover:
            self.timeout -= 1
        if self.show_timeout:
            self.counter.set_markup(str("<b>%s</b>" % self.timeout))
        if self.timeout == 0:
            self.fade_out_timer = gobject.timeout_add(100, self.fade_out)
            return False
        return True
      
    
    def fade_out(self):
        opacity = self.get_opacity()
        opacity -= 0.10
        if opacity <= 0:
            self.in_progress = False
            self.hide_notification()
            return False
        self.set_opacity(opacity)
        return True
    
    def on_hover(self, window, event, hover):
        """Starts/Stops the notification timer on a mouse in/out event"""
        self.hover = hover

        
    def hide_notification(self, *args):
        """Destroys the notification and tells the stack to move the
remaining notification windows"""
        for timer in ("fade_in_timer", "fade_out_timer", "wait_timer"):
            if hasattr(self, timer):
                gobject.source_remove(getattr(self, timer))
        self.destroy()
        self.destroy_cb(self)

    def callbackrealize(self, widget, pixmap, mask=False):
        #width, height = pixmap.get_size()
        #self.resize(width, height)
        if mask is not False:
            self.shape_combine_mask(mask, 0, 0)
        self.window.set_back_pixmap(pixmap, False)
        return True

    def onClick(self, widget, event):
        if event.button == 1 and self.leftclickCB != None:
            self.leftclickCB()
            self.hide_notification()
        if event.button == 2 and self.middleclickCB != None:
            self.middleclickCB()
            self.hide_notification()
        if event.button == 3 and self.rightclickCB != None:
            self.rightclickCB()
            self.hide_notification()

if __name__ == "__main__":
    #example usage
    
    import random
    color_combos = (("red", "white"), ("white", "blue"), ("green", "black"))
    messages = (("Hello", "This is a popup"),
            ("Some Latin", "Quidquid latine dictum sit, altum sonatur."),
            ("A long message", "The quick brown fox jumped over the lazy dog. " * 6))
    images = ("logo1_64.png", None)

    def notify_factory():
        color = random.choice(color_combos)
        message = random.choice(messages)
        image = random.choice(images)
        notifier.bg_color = gtk.gdk.Color(color[0])
        notifier.fg_color = gtk.gdk.Color(color[1])
        notifier.show_timeout = random.choice((True, False))
        notifier.edge_offset_x = 20
        notifier.new_popup(title=message[0], message=message[1], image=image)
        return True

    def gtk_main_quit():
        print "quitting"
        gtk.main_quit()
    
    notifier = NotificationStack(timeout=6)
    gobject.timeout_add(4000, notify_factory)
    gobject.timeout_add(20000, gtk_main_quit)
    gtk.main()