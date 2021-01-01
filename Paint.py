import wx
import sys
import math
import os


class Canvas(wx.ScrolledWindow):
    def __init__(self, parent):
        self.size = (1267,712)
        self.user_scale = 1
        super(Canvas, self).__init__(parent, size=self.size, style=wx.BORDER_RAISED)
        self.SetBackgroundColour((0,0,0))
        self.FitInside()
        self.SetScrollRate(1,1)
        self.coord = []
        self.color = (0,0,0)
        self.last_color = (0,0,0)
        self.pen_width = 1
        self.init_drawing()
        self.prepare_buffer()
        self.Bind(wx.EVT_LEFT_DOWN, self.on_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_up)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.t = wx.Timer(self)
        self.t_shape = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.button_timer, self.t)
        self.Bind(wx.EVT_TIMER, self.shape_timer, self.t_shape)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.mouse_leave_window)
        self.overlay = wx.Overlay()
        self.rect = ()

    def prepare_buffer(self):
        self.buffer = wx.Bitmap(self.size)
        self.front_buffer = wx.Bitmap(self.size)
        dc = wx.BufferedDC(None, self.buffer)
        dc2 = wx.BufferedDC(None, self.front_buffer)
        dc.Clear()
        dc2.Clear()
        
    def scale_bitmap(self, size):
        buffer_image = self.buffer.ConvertToImage()
        buffer_image.Rescale(size[0], size[1], wx.IMAGE_QUALITY_NORMAL)
        self.front_buffer = buffer_image.ConvertToBitmap(-1)
        self.Refresh()

    def color_change(self, color):
        self.color = color
        
    def simple_pen(self, width):
        self.pen_width = int(width)
        
    def init_drawing(self):
        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
    def on_down(self, event):
        if paint.pipette_on:
            self.Refresh()
            event.Skip()
        elif paint.fill_on:
            self.fill_process()
            event.Skip()
        elif paint.shape_on:
            ms = wx.GetMouseState()
            client_coord = self.ScreenToClient(ms.GetX(),ms.GetY())
            client_coord_scaled = (int(client_coord[0]), int(client_coord[1]))
            self.starting_point = client_coord_scaled
            self.t_shape.Start(1)
            event.Skip()
        else:
            self.t.Start(1)
            event.Skip()
        
    def button_timer(self, event):
        ms = wx.GetMouseState()
        client_coord = self.CalcUnscrolledPosition(self.ScreenToClient(ms.GetX(),ms.GetY()))
        client_coord_scaled = (int(client_coord[0]/self.user_scale), int(client_coord[1]/self.user_scale))
        if client_coord_scaled not in self.coord:
            self.coord.append(client_coord_scaled)
            
        dc = wx.BufferedDC(None, self.buffer)
        self.pen = wx.Pen()
        self.pen.SetWidth(self.pen_width)
        self.pen.SetColour(self.color)
        dc.SetPen(self.pen)
        for index, x in enumerate(self.coord):
            if x == self.coord[0]:
                dc.DrawLine(x[0],x[1],x[0]+1,x[1])
            else:
                dc.DrawLine(self.coord[index-1][0],self.coord[index-1][1],x[0],x[1])
        else:
            pass
            
        buffer_image = self.buffer.ConvertToImage()
        buffer_image.Rescale(self.size[0]*self.user_scale, self.size[1]*self.user_scale,
            wx.IMAGE_QUALITY_NORMAL)
        self.front_buffer = buffer_image.ConvertToBitmap(-1)
        self.Refresh()
        event.Skip()
        
    def fill_process(self):
        ms = wx.GetMouseState()
        client_coord = self.CalcUnscrolledPosition(self.ScreenToClient(ms.GetX(),ms.GetY()))
        client_coord_scaled = (int(client_coord[0]/self.user_scale), int(client_coord[1]/self.user_scale))
        
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBrush(wx.Brush(self.color, wx.BRUSHSTYLE_SOLID))
        pixel_color = dc.GetPixel(client_coord_scaled[0], client_coord_scaled[1])
        dc.FloodFill(client_coord_scaled[0],client_coord_scaled[1],pixel_color,wx.FLOOD_SURFACE)
                
        buffer_image = self.buffer.ConvertToImage()
        buffer_image.Rescale(self.size[0]*self.user_scale, self.size[1]*self.user_scale,
            wx.IMAGE_QUALITY_NORMAL)
        self.front_buffer = buffer_image.ConvertToBitmap(-1)
        self.Refresh()
        
    def shape_timer(self, event):
        ms = wx.GetMouseState()
        client_coord = self.ScreenToClient(ms.GetX(),ms.GetY())
        client_coord_scaled = (int(client_coord[0]), int(client_coord[1]))
        rect = wx.Rect(self.starting_point[0], self.starting_point[1],
            client_coord_scaled[0]-self.starting_point[0],
            client_coord_scaled[1]-self.starting_point[1])
        self.rect = rect.GetSize()
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        if 'wxMac' in wx.PlatformInfo:
            dc.SetBrush(wx.Brush(wx.Colour(0xC0, 0xC0, 0xC0, 0x80)))
        else:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
 
        self.pen = wx.Pen()
        self.pen.SetWidth(self.pen_width*self.user_scale)
        self.pen.SetColour(self.color)
        dc.SetPen(self.pen)
        if paint.button_id == 100:
            dc.DrawCircle(self.starting_point[0]+int(rect.GetSize()[0]/2),
                self.starting_point[1]+int(rect.GetSize()[1]/2), int(min(abs(rect.GetSize()[0]),
                abs(rect.GetSize()[1]))/2)-10)
        elif paint.button_id == 110:
            dc.DrawRectangle(rect)
        elif paint.button_id == 120:
            dc.DrawEllipse(rect)
        elif paint.button_id == 130:
            dc.DrawLine(self.starting_point[0],self.starting_point[1],
                self.starting_point[0]+rect.GetSize()[0],
                self.starting_point[1]+rect.GetSize()[1])
        del odc
        event.Skip()
              
    def on_up(self, event):
        if paint.pipette_on:
            event.Skip()
        elif paint.fill_on:
            event.Skip()
        elif paint.shape_on:
            self.t_shape.Stop()
            dc = wx.ClientDC(self)
            odc = wx.DCOverlay(self.overlay, dc)
            odc.Clear()
            del odc
            self.overlay.Reset()
            self.shape_on_up()           
            event.Skip()
        else:
            self.t.Stop()
            event.Skip()
            self.coord = []
            
    def shape_on_up(self):
        ms = wx.GetMouseState()
        client_coord = self.ScreenToClient(ms.GetX(),ms.GetY())
        client_coord_scaled = (client_coord[0], client_coord[1])
        rect = wx.Rect(self.starting_point[0], self.starting_point[1],
            client_coord_scaled[0]-self.starting_point[0],
            client_coord_scaled[1]-self.starting_point[1])
        self.rect = rect.GetSize()
        rect_corners_x = [rect.GetBottomLeft()[0],rect.GetBottomRight()[0],
            rect.GetTopLeft()[0],rect.GetTopRight()[0]]
        rect_corners_y = [rect.GetBottomLeft()[1],rect.GetBottomRight()[1],
            rect.GetTopLeft()[1],rect.GetTopRight()[1]]
        self.frame_on = True
        self.frame = wx.Frame(self)
        self.frame.SetWindowStyle(wx.RESIZE_BORDER)
        self.frame.SetPosition(self.ClientToScreen(min(rect_corners_x),min(rect_corners_y)))
        self.frame.SetSize(abs(self.rect[0]),abs(self.rect[1]))
        self.frame.SetTransparent(15)
        self.frame.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.frame.Show()        
        
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        if 'wxMac' in wx.PlatformInfo:
            dc.SetBrush(wx.Brush(wx.Colour(0xC0, 0xC0, 0xC0, 0x80)))
        else:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
        self.pen = wx.Pen()
        self.pen.SetWidth(self.pen_width*self.user_scale)
        self.pen.SetColour(self.color)
        dc.SetPen(self.pen)
        if paint.button_id == 100:
            dc.DrawCircle(self.starting_point[0]+int(rect.GetSize()[0]/2),
                self.starting_point[1]+int(rect.GetSize()[1]/2), int(min(abs(rect.GetSize()[0]),
                abs(rect.GetSize()[1]))/2)-10)
        elif paint.button_id == 110:
            dc.DrawRectangle(rect)
        elif paint.button_id == 120:
            dc.DrawEllipse(rect)
        elif paint.button_id == 130:
            self.line_1x = self.ScreenToClient(self.frame.GetPosition())[0]-self.starting_point[0]
            self.line_1y = self.ScreenToClient(self.frame.GetPosition())[1]-self.starting_point[1]
            self.shape_exit(wx.EVT_KILL_FOCUS)
        del odc
        self.frame.Bind(wx.EVT_SIZE, self.shape_resize)
        self.frame.Bind(wx.EVT_MOUSE_EVENTS, self.click_on_shape)
        self.frame.Bind(wx.EVT_LEFT_DOWN, self.click_coord)
        self.frame.Bind(wx.EVT_KILL_FOCUS, self.shape_exit)
        self.frame.Bind(wx.EVT_MOVE, self.shape_moving)
        self.frame.Bind(wx.EVT_KEY_DOWN, self.key_pressed)
        
    def key_pressed(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.shape_exit(wx.EVT_KILL_FOCUS)
        elif event.GetKeyCode() == wx.WXK_ESCAPE or event.GetKeyCode() == wx.WXK_DELETE:
            self.shape_delete()
        event.Skip()
        
    def click_coord(self, event):
        self.x_dif = wx.GetMousePosition()[0] - self.frame.GetPosition()[0]
        self.y_dif = wx.GetMousePosition()[1] - self.frame.GetPosition()[1]
        event.Skip()
        
    def shape_delete(self):
        self.frame_on = False
        self.overlay.Reset()
        self.Refresh()
        self.frame.Destroy()
    
    def click_on_shape(self, event):
        if event.LeftIsDown() and event.Dragging() and wx.GetActiveWindow() == self.frame:
            self.frame.Move(wx.GetMousePosition()[0]-self.x_dif,wx.GetMousePosition()[1]-self.y_dif)
        event.Skip()
        
    def shape_moving(self, event):
        ms = self.ScreenToClient(self.frame.GetPosition())
        rect = wx.Rect(ms[0],ms[1],self.frame.GetSize()[0],self.frame.GetSize()[1])
        self.rect = rect.GetSize()
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        if 'wxMac' in wx.PlatformInfo:
            dc.SetBrush(wx.Brush(wx.Colour(0xC0, 0xC0, 0xC0, 0x80)))
        else:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
        self.pen = wx.Pen()
        self.pen.SetWidth(self.pen_width*self.user_scale)
        self.pen.SetColour(self.color)
        dc.SetPen(self.pen)
        if paint.button_id == 100:
            dc.DrawCircle(ms[0]+int(rect.GetSize()[0]/2), ms[1]+int(rect.GetSize()[1]/2),
                int(min(abs(rect.GetSize()[0]), abs(rect.GetSize()[1]))/2)-10)
        elif paint.button_id == 110:
            dc.DrawRectangle(rect)
        elif paint.button_id == 120:
            dc.DrawEllipse(rect)
        del odc
        event.Skip()        
        
    def shape_resize(self, event):
        ms = self.ScreenToClient(self.frame.GetPosition())
        rect = wx.Rect(ms[0],ms[1],self.frame.GetSize()[0],self.frame.GetSize()[1])
        self.rect = rect.GetSize()
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        if 'wxMac' in wx.PlatformInfo:
            dc.SetBrush(wx.Brush(wx.Colour(0xC0, 0xC0, 0xC0, 0x80)))
        else:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
        self.pen = wx.Pen()
        self.pen.SetWidth(self.pen_width*self.user_scale)
        self.pen.SetColour(self.color)
        dc.SetPen(self.pen)
        if paint.button_id == 100:
            dc.DrawCircle(int(ms[0]+(rect.GetSize()[0]/2)), int(ms[1]+(rect.GetSize()[1]/2)),
                int(min(abs(rect.GetSize()[0]), abs(rect.GetSize()[1]))/2)-10)
        elif paint.button_id == 110:
            dc.DrawRectangle(rect)
        elif paint.button_id == 120:
            dc.DrawEllipse(rect)
        del odc
        event.Skip()
        
    def shape_exit(self, event):
        if self.frame_on:
            ms = self.CalcUnscrolledPosition(self.ScreenToClient(self.frame.GetPosition()))
            rect = wx.Rect(ms[0],ms[1],self.frame.GetSize()[0],self.frame.GetSize()[1])
            dc = wx.BufferedDC(None, self.buffer)
            self.pen = wx.Pen()
            self.pen.SetWidth(self.pen_width)
            self.pen.SetColour(self.color)
            dc.SetPen(self.pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            
            if paint.button_id == 100:
                dc.DrawCircle(int((ms[0]+((rect.GetSize()[0]/2)))/self.user_scale),
                    int((ms[1]+((rect.GetSize()[1]/2)))/self.user_scale), int(((min(abs(rect.GetSize()[0]),
                    abs(rect.GetSize()[1]))/2)-10)/self.user_scale))
                    
            elif paint.button_id == 110:
                dc.DrawRectangle(int(ms[0]/self.user_scale),int(ms[1]/self.user_scale),
                    int(self.frame.GetSize()[0]/self.user_scale),
                    int(self.frame.GetSize()[1]/self.user_scale))
                    
            elif paint.button_id == 120:
                dc.DrawEllipse(int(ms[0]/self.user_scale),int(ms[1]/self.user_scale),
                    int(self.frame.GetSize()[0]/self.user_scale),int(self.frame.GetSize()[1]/self.user_scale))
                    
            elif paint.button_id == 130:
                dc.DrawLine(int((ms[0]+abs(self.line_1x))/self.user_scale),
                    int((ms[1]+abs(self.line_1y))/self.user_scale),
                    int((ms[0]+rect.GetSize()[0]-abs(self.line_1x))/self.user_scale),
                    int((ms[1]+rect.GetSize()[1]-abs(self.line_1y))/self.user_scale))
                    
            buffer_image = self.buffer.ConvertToImage()
            buffer_image.Rescale(self.size[0]*self.user_scale, self.size[1]*self.user_scale,
                wx.IMAGE_QUALITY_NORMAL)
            self.front_buffer = buffer_image.ConvertToBitmap(-1)
            self.frame.Destroy()
            dc = wx.ClientDC(self)
            odc = wx.DCOverlay(self.overlay, dc)
            odc.Clear()
            del odc
            self.overlay.Reset()
            self.Refresh()       
            
    def mouse_leave_window(self, event):
        ms = wx.GetMouseState()
        if ms.LeftIsDown():
            self.t.Stop()
            event.Skip()
            self.coord = []
        else:
            event.Skip()
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.front_buffer, wx.BUFFER_VIRTUAL_AREA)

        if paint.pipette_on:
            ms = wx.GetMouseState()
            self.color_coord = self.CalcUnscrolledPosition(self.ScreenToClient(ms.GetX(),ms.GetY()))            
            dc_color = dc.GetPixel(self.color_coord[0], self.color_coord[1])
            self.color = dc_color
            paint.color1_bm = wx.Bitmap.FromRGBA(30,20,dc_color[0],dc_color[1],dc_color[2],255)
            paint.color_button1.SetBitmap(paint.color1_bm)
            self.last_color = dc_color
        event.Skip()

class MyFrame(wx.Frame):
    def __init__(self):
        super(MyFrame, self).__init__(parent=None, size=(1450,900))
        self.Center()
        self.panel = wx.Panel(self)
        self.panel.SetOwnBackgroundColour((225,243,255))
        self.canvas = Canvas(self.panel)
        self.color = (0,0,0)
        self.save_path = ''
        self.set_title("Untitled")
        pen_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Pen.bmp", wx.BITMAP_TYPE_ANY)
        eraser_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Eraser.bmp", wx.BITMAP_TYPE_ANY)
        pipette_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Pipette.bmp", wx.BITMAP_TYPE_ANY)
        fill_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Fill.bmp", wx.BITMAP_TYPE_ANY)
        shape_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Shape.bmp", wx.BITMAP_TYPE_ANY)
        circle_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Circle.bmp", wx.BITMAP_TYPE_ANY)
        rect_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Rect.bmp", wx.BITMAP_TYPE_ANY)
        ellipse_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Ellipse.bmp", wx.BITMAP_TYPE_ANY)
        line_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Line.bmp", wx.BITMAP_TYPE_ANY)
        self.pipette_on = False
        self.eraser_on = False
        self.fill_on = False
        self.shape_on = False
        self.color1_bm = wx.Bitmap.FromRGBA(30,20,self.color[0], self.color[1], self.color[2], 255)
        width_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
        self.zoom_choices = ['100%', '200%', '400%']
        self.zoom_multiplier = [1, 2, 4]
        self.pen_cursor = wx.Cursor(wx.CURSOR_PENCIL)
        self.pipette_cursor = wx.Cursor(os.getcwd()+r"\Ressources\Pipette.ico",
            wx.BITMAP_TYPE_ICO, hotSpotX=4, hotSpotY=30)
        self.fill_cursor = wx.Cursor(os.getcwd()+r"\Ressources\Fill_Tool.ico",
            wx.BITMAP_TYPE_ICO, hotSpotX=1, hotSpotY=30)
        self.shape_cursor = wx.Cursor(wx.CURSOR_CROSS)
        self.canvas.SetCursor(self.pen_cursor)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        tool_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        button1 = wx.BitmapButton(self.panel, bitmap=pen_bm)
        button1.Bind(wx.EVT_BUTTON, self.pen_button_pressed)
        tool_sizer.Add(button1, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)

        button2 = wx.BitmapButton(self.panel, bitmap=eraser_bm)
        button2.Bind(wx.EVT_BUTTON, self.eraser_button_pressed)
        tool_sizer.Add(button2, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
        
        button3 = wx.BitmapButton(self.panel, bitmap=pipette_bm)
        button3.Bind(wx.EVT_BUTTON, self.pipette_button_pressed)
        tool_sizer.Add(button3, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
        
        button4 = wx.BitmapButton(self.panel, bitmap=fill_bm, size=(48,48))
        button4.Bind(wx.EVT_BUTTON, self.fill_button_pressed)
        tool_sizer.Add(button4, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
        
        grid_sizer2 = wx.GridSizer(2,2,1,1)
        button5 = wx.BitmapButton(self.panel, id=100, bitmap=circle_bm)
        button5.Bind(wx.EVT_BUTTON, self.shape_button_pressed)
        grid_sizer2.Add(button5)
        button6 = wx.BitmapButton(self.panel, id=110, bitmap=rect_bm)
        button6.Bind(wx.EVT_BUTTON, self.shape_button_pressed)
        grid_sizer2.Add(button6)
        button7 = wx.BitmapButton(self.panel, id=120, bitmap=ellipse_bm)
        button7.Bind(wx.EVT_BUTTON, self.shape_button_pressed)
        grid_sizer2.Add(button7)
        button8 = wx.BitmapButton(self.panel, id=130, bitmap=line_bm)
        button8.Bind(wx.EVT_BUTTON, self.shape_button_pressed)
        grid_sizer2.Add(button8)        
        tool_sizer.Add(grid_sizer2, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=6)
        
        width_sizer = wx.BoxSizer(wx.VERTICAL)
        text_width = wx.StaticText(self.panel, label="Width")
        width_sizer.Add(text_width, flag=wx.LEFT | wx.TOP, border=3)
        self.combobox_width = wx.ComboBox(self.panel, size=(40,40),
            choices=width_choices, style=wx.CB_DROPDOWN)
        self.combobox_width.SetSelection(0)
        self.combobox_width.Bind(wx.EVT_TEXT, self.width_button_pressed)
        width_sizer.Add(self.combobox_width, flag=wx.TOP, border=2)
        tool_sizer.Add(width_sizer, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
        
        color_sizer = wx.BoxSizer(wx.VERTICAL)
        text_color1 = wx.StaticText(self.panel, label="Color")
        color_sizer.Add(text_color1, flag=wx.LEFT | wx.TOP, border=3)
        self.color_button1 = wx.BitmapButton(self.panel, bitmap=self.color1_bm)
        self.color_button1.Bind(wx.EVT_BUTTON, self.color_button1_pressed)
        color_sizer.Add(self.color_button1, flag=wx.LEFT | wx.TOP, border=2)
        tool_sizer.Add(color_sizer, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
        
        grid_sizer = wx.GridSizer(2,10,1,1)
        cb1_bm = wx.Bitmap.FromRGBA(12,12,0,0,0,255)
        cb1 = wx.BitmapButton(self.panel, id=1, bitmap=cb1_bm, size=(20,20))
        cb1.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb1)
        
        cb2_bm = wx.Bitmap.FromRGBA(12,12,127,127,127,255)
        cb2 = wx.BitmapButton(self.panel, id=2, bitmap=cb2_bm, size=(20,20))
        cb2.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb2)
        
        cb3_bm = wx.Bitmap.FromRGBA(12,12,126,0,21,255)
        cb3 = wx.BitmapButton(self.panel, id=3, bitmap=cb3_bm, size=(20,20))
        cb3.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb3)
        
        cb4_bm = wx.Bitmap.FromRGBA(12,12,237,28,36,255)
        cb4 = wx.BitmapButton(self.panel, id=4, bitmap=cb4_bm, size=(20,20))
        cb4.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb4)
        
        cb5_bm = wx.Bitmap.FromRGBA(12,12,255,127,39,255)
        cb5 = wx.BitmapButton(self.panel, id=5, bitmap=cb5_bm, size=(20,20))
        cb5.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb5)
        
        cb6_bm = wx.Bitmap.FromRGBA(12,12,255,242,0,255)
        cb6 = wx.BitmapButton(self.panel, id=6, bitmap=cb6_bm, size=(20,20))
        cb6.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb6)
        
        cb7_bm = wx.Bitmap.FromRGBA(12,12,34,177,76,255)
        cb7 = wx.BitmapButton(self.panel, id=7, bitmap=cb7_bm, size=(20,20))
        cb7.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb7)
        
        cb8_bm = wx.Bitmap.FromRGBA(12,12,0,162,232,255)
        cb8 = wx.BitmapButton(self.panel, id=8, bitmap=cb8_bm, size=(20,20))
        cb8.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb8)
        
        cb9_bm = wx.Bitmap.FromRGBA(12,12,63,72,204,255)
        cb9 = wx.BitmapButton(self.panel, id=9, bitmap=cb9_bm, size=(20,20))
        cb9.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb9)
        
        cb11_bm = wx.Bitmap.FromRGBA(12,12,163,73,164,255)
        cb11 = wx.BitmapButton(self.panel, id=11, bitmap=cb11_bm, size=(20,20))
        cb11.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb11)
        
        cb12_bm = wx.Bitmap.FromRGBA(12,12,255,255,255,255)
        cb12 = wx.BitmapButton(self.panel, id=12, bitmap=cb12_bm, size=(20,20))
        cb12.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb12)
        
        cb13_bm = wx.Bitmap.FromRGBA(12,12,195,195,195,255)
        cb13 = wx.BitmapButton(self.panel, id=13, bitmap=cb13_bm, size=(20,20))
        cb13.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb13)
        
        cb14_bm = wx.Bitmap.FromRGBA(12,12,185,122,87,255)
        cb14 = wx.BitmapButton(self.panel, id=14, bitmap=cb14_bm, size=(20,20))
        cb14.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb14)
        
        cb15_bm = wx.Bitmap.FromRGBA(12,12,255,174,201,255)
        cb15 = wx.BitmapButton(self.panel, id=15, bitmap=cb15_bm, size=(20,20))
        cb15.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb15)
        
        cb16_bm = wx.Bitmap.FromRGBA(12,12,255,201,14,255)
        cb16 = wx.BitmapButton(self.panel, id=16, bitmap=cb16_bm, size=(20,20))
        cb16.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb16)
        
        cb17_bm = wx.Bitmap.FromRGBA(12,12,239,228,176,255)
        cb17 = wx.BitmapButton(self.panel, id=17, bitmap=cb17_bm, size=(20,20))
        cb17.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb17)
        
        cb18_bm = wx.Bitmap.FromRGBA(12,12,181,230,29,255)
        cb18 = wx.BitmapButton(self.panel, id=18, bitmap=cb18_bm, size=(20,20))
        cb18.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb18)
        
        cb19_bm = wx.Bitmap.FromRGBA(12,12,153,217,234,255)
        cb19 = wx.BitmapButton(self.panel, id=19, bitmap=cb19_bm, size=(20,20))
        cb19.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb19)
        
        cb20_bm = wx.Bitmap.FromRGBA(12,12,112,146,190,255)
        cb20 = wx.BitmapButton(self.panel, id=20, bitmap=cb20_bm, size=(20,20))
        cb20.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb20)
        
        cb21_bm = wx.Bitmap.FromRGBA(12,12,200,191,231,255)
        cb21 = wx.BitmapButton(self.panel, id=21, bitmap=cb21_bm, size=(20,20))
        cb21.Bind(wx.EVT_BUTTON, self.mini_button_pressed)
        grid_sizer.Add(cb21)        
        tool_sizer.Add(grid_sizer, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=10)
        
        self.main_sizer.Add(tool_sizer)
        self.main_sizer.Add(self.canvas, flag=wx.LEFT, border=5)
        
        self.panel.SetSizer(self.main_sizer)
        
        self.menu_bar = wx.MenuBar()
        self.menu = wx.Menu()
        new_event = self.menu.Append(id=wx.ID_ANY, item='New')
        self.Bind(wx.EVT_MENU, self.new_event, new_event)
        open_event = self.menu.Append(id=wx.ID_ANY, item='Open')
        self.Bind(wx.EVT_MENU, self.open_event, open_event)
        save_event = self.menu.Append(id=wx.ID_ANY, item='Save')
        self.Bind(wx.EVT_MENU, self.save_event, save_event)
        save_as_event = self.menu.Append(id=wx.ID_ANY, item='Save as')
        self.Bind(wx.EVT_MENU, self.save_as_event, save_as_event)
        exit_event = self.menu.Append(id=wx.ID_EXIT, item='Exit')
        self.Bind(wx.EVT_MENU, self.exit_event, exit_event)
        self.menu_bar.Append(self.menu, 'Data')
        self.SetMenuBar(self.menu_bar)
        
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-1,45])
        self.zoom_button = wx.Choice(self.status_bar, choices=self.zoom_choices)
        self.zoom_button.SetSelection(0)
        self.zoom_button.Bind(wx.EVT_CHOICE, self.zoom_button_pressed)
        self.status_bar.Bind(wx.EVT_SIZE, self.on_size)
        self.zoom_button.SetRect(self.status_bar.GetFieldRect(1))        
        self.Show()
        
    def set_title(self, title):
        self.SetLabel("%s - Paint" % title)        
        
    def new_event(self, event):
        size = (1267,712)
        image = wx.Bitmap(size)
        self.canvas.SetSize(size)
        self.canvas.size = size
        self.main_sizer.SetItemMinSize(self.canvas, size[0], size[1])
        self.canvas.FitInside()
        self.canvas.buffer = image
        self.canvas.front_buffer = image
        dc = wx.BufferedDC(None, self.canvas.buffer)
        dc2 = wx.BufferedDC(None, self.canvas.front_buffer)
        dc.Clear()
        dc2.Clear()
        self.canvas.Refresh()
        self.main_sizer.Layout()
        self.save_path = ''
        self.set_title("Untitled")
        self.zoom_button.SetSelection(0)
        self.zoom_button_pressed(wx.EVT_CHOICE)
        event.Skip()
        
    def open_event(self, event):
        title = "Open File"
        dialog = wx.FileDialog(self, title,
            wildcard='JPEG files (*.jpg)|*.jpg|PNG files (*.png)|*.png',
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            
        if dialog.ShowModal() == wx.ID_OK:
            open_path = dialog.GetPath()
            self.save_path = open_path
            self.set_title(dialog.GetFilename())
            image = wx.Bitmap(open_path)
            image_size = image.GetSize()
            self.canvas.SetSize(image_size)
            self.canvas.size = image_size
            self.main_sizer.SetItemMinSize(self.canvas, image_size[0], image_size[1])
            self.canvas.FitInside()
            self.canvas.buffer = image
            self.canvas.front_buffer = image
            self.canvas.Refresh()
            self.main_sizer.Layout()
        dialog.Destroy()
        event.Skip()
        
    def save_event(self, event):
        if self.save_path == '':
            self.save_as_event(wx.EVT_MENU)
            event.Skip()
        else:
            image = self.canvas.buffer.ConvertToImage()
            image.SaveFile(self.save_path)
            event.Skip()            
        
    def save_as_event(self, event):
        title = "Save as"
        dialog = wx.FileDialog(self, title, defaultFile='Untitled',
            wildcard='JPEG files (*.jpg)|*.jpg|PNG files (*.png)|*.png',
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            
        if dialog.ShowModal() == wx.ID_OK:
            save_path = dialog.GetPath()
            self.save_path = save_path
            image = self.canvas.buffer.ConvertToImage()
            image.SaveFile(save_path)
            self.set_title(dialog.GetFilename())
        dialog.Destroy()
        event.Skip()
        
    def exit_event(self, event):
        sys.exit(0)
        
    def eraser_cursor(self, width_input):
        width = int(width_input)*self.canvas.user_scale
        eraser_buffer = wx.Bitmap(width+2,width+2)
        dc = wx.BufferedDC(None, eraser_buffer)
        dc.Clear()
        dc.DrawCircle(math.ceil(width/2),math.ceil(width/2),math.ceil(width/2))
        bm = eraser_buffer.ConvertToImage()
        bm.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, math.ceil(width/2))
        bm.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, math.ceil(width/2))
        bm.InitAlpha()
        for x in range(width+2):
            for y in range(width+2):
                if (bm.GetRed(x,y), bm.GetGreen(x,y), bm.GetBlue(x,y)) == (255,255,255):
                    bm.SetAlpha(x,y,0)
                else:
                    pass
                
        cursor = wx.Cursor(bm)
        self.canvas.SetCursor(cursor)
    
    def width_button_pressed(self, event):
        self.canvas.simple_pen(event.GetString())        
        if self.eraser_on == True:
            self.eraser_cursor(event.GetString())
        event.Skip()
        
    def pen_button_pressed(self, event):
        self.pipette_on = False
        self.eraser_on = False
        self.fill_on = False
        self.shape_on = False
        self.canvas.color_change(self.canvas.last_color)
        self.canvas.SetCursor(self.pen_cursor)
        self.color1_bm = wx.Bitmap.FromRGBA(30,20,self.canvas.last_color[0],
            self.canvas.last_color[1],self.canvas.last_color[2],255)
        self.color_button1.SetBitmap(self.color1_bm)
        event.Skip()
        
    def eraser_button_pressed(self, event):
        self.pipette_on = False
        self.eraser_on = True
        self.fill_on = False
        self.shape_on = False
        self.eraser_cursor(15)
        self.canvas.color_change((255,255,255))
        self.combobox_width.SetValue('15')
        self.color1_bm = wx.Bitmap.FromRGBA(30,20,255,255,255,255)
        self.color_button1.SetBitmap(self.color1_bm)
        event.Skip()
        
    def pipette_button_pressed(self, event):
        self.pipette_on = True
        self.eraser_on = False
        self.fill_on = False
        self.shape_on = False
        self.canvas.SetCursor(self.pipette_cursor)
        event.Skip()
        
    def fill_button_pressed(self, event):
        self.pipette_on = False
        self.eraser_on = False
        self.fill_on = True
        self.shape_on = False
        self.canvas.color_change(self.canvas.last_color)
        self.canvas.SetCursor(self.fill_cursor)
        self.color1_bm = wx.Bitmap.FromRGBA(30,20,self.canvas.last_color[0],
            self.canvas.last_color[1],self.canvas.last_color[2],255)
        self.color_button1.SetBitmap(self.color1_bm)
        event.Skip()
        
    def shape_button_pressed(self, event):
        self.pipette_on = False
        self.eraser_on = False
        self.fill_on = False
        self.shape_on = True
        self.button_id = event.GetEventObject().GetId()
        self.canvas.color_change(self.canvas.last_color)
        self.canvas.SetCursor(self.shape_cursor)
        self.color1_bm = wx.Bitmap.FromRGBA(30,20,self.canvas.last_color[0],
            self.canvas.last_color[1],self.canvas.last_color[2],255)
        self.color_button1.SetBitmap(self.color1_bm)
        event.Skip()        
        
    def color_button1_pressed(self, event):
        self.chosen_color = self.canvas.last_color
        data = wx.ColourData()
        data.SetColour(self.canvas.last_color)
        dialog = wx.ColourDialog(self, data)
        dialog.Bind(wx.EVT_COLOUR_CHANGED, self.new_color)
        if dialog.ShowModal() == wx.ID_OK:
            self.color = (self.chosen_color[0],self.chosen_color[1],self.chosen_color[2])
            self.color1_bm = wx.Bitmap.FromRGBA(30,20,self.color[0],
                self.color[1], self.color[2], 255)        
            button_id = event.GetId()
            event.GetEventObject().SetBitmap(self.color1_bm)
            self.canvas.color_change(self.color)
            self.canvas.last_color = self.color
        dialog.Destroy()
        event.Skip()
        
    def new_color(self, event):
        self.chosen_color = event.GetColour()
        event.Skip()
        
    def mini_button_pressed(self, event):
        bm = event.GetEventObject().GetBitmap()
        image = bm.ConvertToImage()
        color = (image.GetRed(6,6), image.GetGreen(6,6), image.GetBlue(6,6))
        self.canvas.color_change(color)
        self.canvas.last_color = color
        self.color1_bm = wx.Bitmap.FromRGBA(30,20,color[0],color[1],color[2],255)
        self.color_button1.SetBitmap(self.color1_bm)
        event.Skip()
        
    def zoom_button_pressed(self, event):
        scroll_bar_coord = self.canvas.GetViewStart()
        rect_size = self.canvas.GetClientSize()
        center_before = ((rect_size[0]/2)+scroll_bar_coord[0],
            (rect_size[1]/2)+scroll_bar_coord[1])
        old_user_scale = self.canvas.user_scale
        button_selection = self.zoom_button.GetSelection()
        self.canvas.user_scale = self.zoom_multiplier[button_selection]
        new_size = (self.canvas.size[0]*self.canvas.user_scale,
            self.canvas.size[1]*self.canvas.user_scale)
        self.canvas.SetSize((new_size))
        self.main_sizer.SetItemMinSize(self.canvas, new_size[0], new_size[1])
        self.canvas.FitInside()
        self.canvas.scale_bitmap(new_size)
        self.main_sizer.Layout()
        self.canvas.Scroll(int(((center_before[0]/old_user_scale)*self.canvas.user_scale)-(rect_size[0]/2)),
            int(((center_before[1]/old_user_scale)*self.canvas.user_scale)-(rect_size[1]/2)))        
        if self.eraser_on == True:
            self.eraser_cursor(self.canvas.pen_width)
        
    def on_size(self, event):
        self.zoom_button.SetRect(self.status_bar.GetFieldRect(1))
        
        
if __name__ == '__main__':
    app = wx.App()
    paint = MyFrame()
    app.MainLoop()
