# -*- coding:utf-8 -*-
__author__ = 'Brick'
#GUI主线程
del_all = False
def gui_mainloop(the_q, mas_q,obj_q,event):

    import tkinter as tk
    from PIL import Image, ImageTk
    import sys
    import support.utils_communication as uc
    class TkGui(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self, None)
            self.obj_show=[]
            self.parent = None
            self.title('object detection --BrickCV')
            self.resizable(0, 0)  # 禁止调整窗口大小
            self.geometry('800x800')
            self.ui_video_source((250, 520))
            self.ui_video_show((1,1))
            self.protocol("WM_DELETE_WINDOW", self.donothing)
            self.del_all=False

            self.ui_detection_select((30, 540, 30))

            self.ui_control((490,570),(680, 570))
        def donothing(self, *e):
            global del_all,p_cap
            self.del_all = True
            del_all=True
            mas_q.put('kill all')




        def ui_detection_select(self, anchor):
            self.var = tk.StringVar(value='Mouse')
            self.l = tk.Label(self, bg='yellow', width=20, text='empty')
            self.l.place(x=anchor[0], y=anchor[1] + anchor[2] * 0)
            self.print_selection()

            self.r1 = tk.Radiobutton(self, text='鼠标框选（人工选择）',
                                     variable=self.var, value='Mouse',
                                     command=self.print_selection)
            self.r1.place(x=anchor[0], y=anchor[1] + anchor[2] * 1)

            self.r2 = tk.Radiobutton(self, text='绿色检测（测试项）',
                                     variable=self.var, value='Color',
                                     command=self.print_selection)
            self.r2.place(x=anchor[0], y=anchor[1] + anchor[2] * 2)

            self.r3 = tk.Radiobutton(self, text='Harr检测（精度一般）',
                                     variable=self.var, value='Harr',
                                     command=self.print_selection)
            self.r3.place(x=anchor[0], y=anchor[1] + anchor[2] * 3)

            self.r4 = tk.Radiobutton(self, text='SSD检测（需要CUDA支持）',
                                     variable=self.var, value='SSD',
                                     command=self.print_selection)
            self.r4.place(x=anchor[0], y=anchor[1] + anchor[2] * 4)

            self.r5 = tk.Radiobutton(self, text='YOLO检测（需要CUDA支持）',
                                     variable=self.var, value='YOLO',
                                     command=self.print_selection)
            self.r5.place(x=anchor[0], y=anchor[1] + anchor[2] * 5)

        def ui_video_show(self, anchor):
            self.lmain = tk.Label(self, bg='green', height=500, width=650)
            self.lmain.place(x=anchor[0], y=anchor[1])

        def ui_video_source(self, anchor):
            self.sourceL = tk.Label(self,text='URL')
            self.sourceL.place(x=anchor[0],y=anchor[1])
            self.sourceURL = tk.Entry(self,width=50)
            self.sourceURL.place(x=anchor[0]+40, y=anchor[1])
            self.sourceURL.insert('insert', '0')

            self.sourceBt = tk.Button(self,text='更改源',width=8,height=1,command=self.text_handle)
            self.sourceBt.place(x=anchor[0]+440, y=anchor[1])

        def ui_object_list(self, anchor):

            if obj_q.empty() == False :
                self.obj_list = obj_q.get()
                i=0
                for obj in self.obj_list:
                    if len(self.obj_show) <= i:
                        self.obj_show.append(tk.Label(self,bg='green',height=5,width=15))
                        self.obj_show[i].place(x=anchor[0],y=anchor[1]+15*i)
                    if obj.existance == True:
                        str_show = str(obj.name)+'\n'+str(obj.ctr[0])+','+str(obj.ctr[1])+'\n'+str(obj.rad)
                        self.obj_show[i].config(text=str_show)
                    else:
                        #str_show = 'None'
                        self.obj_show[i].destroy()
                    i=i+1
            elif len(self.obj_show)>0:
                # str_show = 'None'
                # self.obj_show[0].config(text=str_show)
                self.obj_show[0].destroy()
                del self.obj_show[0]

        def ui_control(self, anchor, anchor2=(630, 600)):
            self.b1 = tk.Button(self,
                                text='清除目标',  # 显示在按钮上的文字
                                width=10, height=1,
                                command=self.clear_object)
            self.b2 = tk.Button(self,
                                text='暂停检测',  # 显示在按钮上的文字
                                width=10, height=1,
                                command=self.stop_detect)
            self.b3 = tk.Button(self,
                                text='确认捕捉',  # 显示在按钮上的文字
                                width=10, height=1,
                                command=uc.capture_command)
            self.b1.place(x=anchor2[0], y=anchor2[1])
            self.b2.place(x=anchor2[0], y=anchor2[1]+40)
            self.b3.place(x=anchor2[0], y=anchor2[1] + 80)

            self.b_up=tk.Button(self,
                                text='↑',  # 显示在按钮的文字
                                width=3, height=1,
                                command=uc.up_handle)
            self.b_down=tk.Button(self,
                                text='↓',  # 显示在按钮的文字
                                width=3, height=1,
                                command=uc.down_handle)
            self.b_left=tk.Button(self,
                                text='←',  # 显示在按钮的文字
                                width=3, height=1,
                                command=uc.left_handle)
            self.b_right=tk.Button(self,
                                text='→',  # 显示在按钮的文字
                                width=3, height=1,
                                command=uc.right_handle)

            self.b_elongate=tk.Button(self,
                                text='♦',  # 显示在按钮的文字
                                width=3, height=1,
                                command=uc.elongate_handle)
            self.b_shorten=tk.Button(self,
                                text='⊙',  # 显示在按钮的文字
                                width=3, height=1,
                                command=uc.shorten_handle)
            #快捷键设置
            self.b_up.bind_all('<KeyPress-Up>', uc.up_key_handle)
            self.b_down.bind_all('<KeyPress-Down>', uc.down_key_handle)
            self.b_left.bind_all('<KeyPress-Left>', uc.left_key_handle)
            self.b_right.bind_all('<KeyPress-Right>', uc.right_key_handle)
            self.b_elongate.bind_all('=', uc.elongate_key_handle)
            self.b_shorten.bind_all('-', uc.shorten_key_handle)
            self.b_up.place(x=anchor[0]+40, y=anchor[1])
            self.b_down.place(x=anchor[0] + 40, y=anchor[1]+50)
            self.b_left.place(x=anchor[0], y=anchor[1]+50)
            self.b_right.place(x=anchor[0]+80, y=anchor[1] + 50)
            self.b_elongate.place(x=anchor[0]+130, y=anchor[1])
            self.b_shorten.place(x=anchor[0] + 130, y=anchor[1]+50)




        def eventhandler(self, event):
            print(event)

        def update_frame(self, img):
            global del_all
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lmain.imgtk = imgtk
            self.lmain.configure(image=imgtk)
            if self.del_all==False:
                self.update()

        def stop_detect(self):
            a = 'Stop'
            mas_q.put(a)
            self.b2.configure(text='开始检测',command=self.start_detect)

        def start_detect(self):
            a = 'Start'
            mas_q.put(a)
            self.b2.configure(text='暂停检测', command=self.stop_detect)

        def clear_object(self):
            a = 'Clear'
            mas_q.put(a)
            #the_q.put(a)

        def print_selection(self):
            self.l.config(text='检测方法： ' + str(self.var.get()))
            mas_q.put(str(self.var.get()))

        def text_handle(self):
            s = self.sourceURL.get()
            url='URL'+ str(s)
            mas_q.put(str(url))

    gui = TkGui()

    while True:
        event.wait()
        img = the_q.get()
        if del_all == False:
            gui.update_frame(img)
            gui.ui_object_list((655,1))
        else:
            break
"""
GUI示例代码
    from: https://morvanzhou.github.io/tutorials/python-basic/tkinter/
    按钮
    self.b = tk.Button(self,
                                   text='关闭',  # 显示在按钮上的文字
                                   width=15, height=2,
                                   command=self.print_info #触发回调函数
                                   )
                self.b.place(x=10, y=600)
                
    标签
    self.lmain = tk.Label(self,bg = 'green',height = 500,width = 650)
    self.b.place(x=10, y=600)
    
    文本框
    t = tk.Text(self,height=2)
    self.b.place(x=10, y=600)
    
    var = e.get() #获取文本框内容
    t.insert('insert',var) #给文本框插入文本

    列表
    var2 = tk.StringVar()
    var2.set((11,22,33,44)) #为变量设置值

    #创建Listbox

    lb = tk.Listbox(window, listvariable=var2)  #将var2的值赋给Listbox

    #创建一个list并将值循环添加到Listbox控件中
    list_items = [1,2,3,4]
    for item in list_items:
        lb.insert('end', item)  #从最后一个位置开始加入值
    lb.insert(1, 'first')       #在第一个位置加入'first'字符
    lb.insert(2, 'second')      #在第二个位置加入'second'字符
    lb.delete(2)                #删除第二个位置的字符
    lb.pack()

    选择按钮
    var = tk.StringVar()
    l = tk.Label(window, bg='yellow', width=20, text='empty')
    l.pack()
    
    r1 = tk.Radiobutton(window, text='Option A',
                        variable=var, value='A',
                        command=print_selection)
    r1.pack()
    
    def print_selection():
        l.config(text='you have selected ' + var.get())
        
    滚动条
    s = tk.Scale(window, label='try me', from_=5, to=11, orient=tk.HORIZONTAL,
             length=200, showvalue=0, tickinterval=2, resolution=0.01, command=print_selection)
    s.pack()
    这里的参数label是指scale部件的名称，即在这里scale部件名称为try me
    
    参数from_=5，to=11的意思就是从5到11，即这个滚动条最小值为5，最大值为11（这里使用from_是因为在python中有from这个关键词）
    参数orient=tk.HORIZONTAL在这里就是设置滚动条的方向，如我们所看到的效果图，这里HORIZONTAL就是横向。
    参数length这里是指滚动条部件的长度，但注意的是和其他部件width表示不同，width表示的是以字符为单位，
    比如width=4，就是4个字符的长度，而此处的length=200，是指我们常用的像素为单位，即长度为200个像素
    参数resolution=0.01这里我们可以借助数学题来理解，我们做的很多数学题都会让我们来保留几位小数，
    此处的0.01就是保留2位小数，即效果图中的5.00 9.00等等后面的两位小数，如果保留一位就是resolution=0.1 
    这里的showvalue就是设置在滚动条上方的显示。showvalue=0显示的就是效果图，上方无结果显示，如果改为showvalue=1，
    则会显示为保留两位小数
    
    l = tk.Label(window, bg='yellow', width=20, text='empty')
    l.pack()
    
    def print_selection(v):
        l.config(text='you have selected ' + v)
        
    多选选项
    var1 = tk.IntVar()
    c1 = tk.Checkbutton(window, text='Python', variable=var1, onvalue=1, offvalue=0,
                    command=print_selection)
    c1.pack()
    
    def print_selection():
    if (var1.get() == 1) & (var2.get() == 0):   #如果选中第一个选项，未选中第二个选项
        l.config(text='I love only Python ')
    elif (var1.get() == 0) & (var2.get() == 1): #如果选中第二个选项，未选中第一个选项
        l.config(text='I love only C++')
    elif (var1.get() == 0) & (var2.get() == 0):  #如果两个选项都未选中
        l.config(text='I do not love either')
    else:
        l.config(text='I love both')             #如果两个选项都选中
        
    菜单
    ##创建一个菜单栏，这里我们可以把他理解成一个容器，在窗口的上方
    menubar = tk.Menu(window)
    
    ##定义一个空菜单单元
    filemenu = tk.Menu(menubar, tearoff=0)
    
    ##将上面定义的空菜单命名为`File`，放在菜单栏中，就是装入那个容器中
    menubar.add_cascade(label='File', menu=filemenu)
    
    ##在`File`中加入`New`的小菜单，即我们平时看到的下拉菜单，每一个小菜单对应命令操作。
    ##如果点击这些单元, 就会触发`do_job`的功能
    filemenu.add_command(label='New', command=do_job)
    filemenu.add_command(label='Open', command=do_job)##同样的在`File`中加入`Open`小菜单
    filemenu.add_command(label='Save', command=do_job)##同样的在`File`中加入`Save`小菜单
    
    filemenu.add_separator()##这里就是一条分割线
    
    ##同样的在`File`中加入`Exit`小菜单,此处对应命令为`window.quit`
    filemenu.add_command(label='Exit', command=window.quit)
    
    submenu = tk.Menu(filemenu)##和上面定义菜单一样，不过此处实在`File`上创建一个空的菜单
    filemenu.add_cascade(label='Import', menu=submenu, underline=0)##给放入的菜单`submenu`命名为`Import`
    submenu.add_command(label="Submenu1", command=do_job)##这里和上面也一样，在`Import`中加入一个小菜单命令`Submenu1`
    counter = 0
    #触发功能
    def do_job():
        global counter
        l.config(text='do '+ str(counter))
        counter+=1
        
    弹窗
    def hit_me():
    tk.messagebox.showinfo(title='Hi', message='hahahaha')
    
    tk.messagebox.showinfo(title='',message='')#提示信息对话窗
    tk.messagebox.showwarning()#提出警告对话窗
    tk.messagebox.showerror()#提出错误对话窗
    tk.messagebox.askquestion()#询问选择对话窗
    
    def hit_me():
    print(tk.messagebox.askquestion(title='Hi', message='hahahaha'))
    
    
"""