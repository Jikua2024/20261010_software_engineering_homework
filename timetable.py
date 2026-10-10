# -*- coding: utf-8 -*-
"""
课程作业管理 GUI 程序

核心数据结构与逻辑（Course、parse_weeks、sample_courses）不依赖 GUI，
可被独立导入进行单元测试。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Set, List
from collections import defaultdict
import colorsys
import sys


# ---------------------------------------------------------------------------
# Windows 高 DPI 支持：让 tkinter 窗口在高分屏上不模糊
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        from ctypes import windll
        # 1 = PROCESS_PER_MONITOR_DPI_AWARE
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ===========================================================================
# 核心数据结构（不依赖 GUI，便于单元测试）
# ===========================================================================
@dataclass
class Course:
    """一门课程的信息。

    属性:
        name:     课程名称
        day:      星期几，0=周一 ... 4=周五
        start:    起始节次（1-13）
        end:      结束节次（1-13，含）
        weeks:    原始周次字符串，如 "1-12周"、"第1周"
        campus:   校区
        location: 上课地点
    """
    name: str
    day: int
    start: int
    end: int
    weeks: str
    campus: str
    location: str


def parse_weeks(weeks_str: str) -> Set[int]:
    """把周次字符串解析为周次集合。

    支持的格式示例:
        "1-12周"      -> {1, 2, ..., 12}
        "第1周"       -> {1}
        "1-8,10-12周" -> {1..8, 10..12}
        "1,3,5周"     -> {1, 3, 5}
        ""            -> set()
    """
    if not weeks_str:
        return set()
    s = weeks_str.strip()
    # 去掉末尾的"周"字
    if s.endswith("周"):
        s = s[:-1]
    # 去掉"第"字（"第1周" -> "1"）
    s = s.replace("第", "")

    weeks: Set[int] = set()
    try:
        for part in s.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                lo, hi = part.split("-", 1)
                lo = int(lo.strip())
                hi = int(hi.strip())
                for w in range(lo, hi + 1):
                    # 范围约束：只保留 1~20 周内的有效周次
                    if 1 <= w <= 20:
                        weeks.add(w)
            else:
                w = int(part)
                if 1 <= w <= 20:
                    weeks.add(w)
    except ValueError:
        # 非法输入（如 "abc周"、"1-2-3周"、"1-4周半"）返回空集合，
        # 不向上抛异常，避免 CourseDialog 提交时崩溃。
        return set()
    return weeks


def sample_courses() -> List[Course]:
    """返回预加载的课表数据（共 20 门课）。"""
    return [
        # ---------- 星期一 (day=0) ----------
        Course("生产计划与控制", 0, 3, 4, "1-12周", "闵行", "下院312"),
        Course("计算复杂性", 0, 3, 4, "1-12周", "闵行", "东下院311"),
        Course("生产系统建模与仿真", 0, 6, 8, "第1周", "闵行", "东下院102"),
        Course("生产系统建模与仿真", 0, 6, 8, "2-16周", "闵行", "东中院3-206"),
        Course("新兴风险的感知与沟通", 0, 9, 10, "1-16周", "闵行", "上院501"),
        Course("大数据算法与分析", 0, 11, 13, "1-16周", "闵行", "下院113"),

        # ---------- 星期二 (day=1) ----------
        Course("优化算法设计", 1, 3, 4, "1-8周", "闵行", "东下院202"),
        Course("管理学基础", 1, 7, 8, "1-12周", "闵行", "东下院202"),
        Course("日语（1）", 1, 9, 10, "1-16周", "闵行", "上院404"),
        Course("软件工程", 1, 11, 13, "1-16周", "闵行", "上院203"),

        # ---------- 星期三 (day=2) ----------
        Course("人因工程", 2, 3, 4, "1-12周", "闵行", "下院312"),
        Course("中国医疗保险制度的转型发展与创新", 2, 11, 13, "5-15周", "闵行", "上院203"),

        # ---------- 星期四 (day=3) ----------
        Course("计算复杂性", 3, 1, 2, "1-12周", "闵行", "东下院311"),
        Course("生产计划与控制", 3, 3, 4, "1-12周", "闵行", "下院312"),
        Course("毛泽东思想和中国特色社会主义理论体系概论", 3, 6, 8, "1-16周", "闵行", "上院115"),
        Course("日语（1）", 3, 9, 10, "1-16周", "闵行", "上院404"),
        Course("优化算法设计", 3, 12, 13, "1-8周", "闵行", "东下院202"),

        # ---------- 星期五 (day=4) ----------
        Course("人因工程", 4, 1, 2, "1-12周", "闵行", "下院312"),
        Course("管理学基础", 4, 3, 4, "1-12周", "闵行", "东下院202"),
        Course("工程与社会", 4, 7, 9, "1-11周", "闵行", "东下院309"),
    ]


def course_color(index: int) -> str:
    """根据课程索引生成蓝色系配色，通过明度区分不同课程。

    固定 hue 在蓝色区间（0.58~0.66），明度在 0.55~0.82 之间循环，
    保证所有课程色块都属于蓝色家族（蓝/靛蓝/浅蓝）。
    """
    hue = 0.58 + (index % 5) * 0.018          # 蓝色区间
    lightness = 0.55 + (index % 8) * 0.038    # 明度变化
    saturation = 0.55
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


# ===========================================================================
# 添加 / 编辑课程对话框
# ===========================================================================
DAY_NAMES = ["周一", "周二", "周三", "周四", "周五"]


class CourseDialog(tk.Toplevel):
    """课程添加/编辑对话框。

    若传入 course 则为编辑模式，对话框会预填原有信息；否则为添加模式。
    确认后通过 self.result 返回一个 Course 对象；取消则为 None。
    """

    def __init__(self, parent, course: Course = None, title: str = "添加课程"):
        super().__init__(parent)
        self.title(title)
        self.course = course
        self.result: Course = None

        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # ---- 表单变量 ----
        self.var_name = tk.StringVar(value=course.name if course else "")
        self.var_day = tk.StringVar(value=DAY_NAMES[course.day] if course else DAY_NAMES[0])
        self.var_start = tk.IntVar(value=course.start if course else 1)
        self.var_end = tk.IntVar(value=course.end if course else 2)
        self.var_weeks = tk.StringVar(value=course.weeks if course else "1-16周")
        self.var_campus = tk.StringVar(value=course.campus if course else "闵行")
        self.var_location = tk.StringVar(value=course.location if course else "")

        self._build_form()

        # 居中显示
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry("+{}+{}".format(max(x, 0), max(y, 0)))

        # 等待用户操作
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _build_form(self):
        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # 课程名
        ttk.Label(frm, text="课程名:").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_name, width=28).grid(row=0, column=1, sticky="w", **pad)

        # 星期
        ttk.Label(frm, text="星期:").grid(row=1, column=0, sticky="e", **pad)
        ttk.Combobox(frm, textvariable=self.var_day, values=DAY_NAMES,
                     state="readonly", width=10).grid(row=1, column=1, sticky="w", **pad)

        # 起止节次
        ttk.Label(frm, text="起止节次:").grid(row=2, column=0, sticky="e", **pad)
        row2 = ttk.Frame(frm)
        row2.grid(row=2, column=1, sticky="w", **pad)
        ttk.Spinbox(row2, from_=1, to=13, textvariable=self.var_start, width=5).pack(side=tk.LEFT)
        ttk.Label(row2, text="  —  ").pack(side=tk.LEFT)
        ttk.Spinbox(row2, from_=1, to=13, textvariable=self.var_end, width=5).pack(side=tk.LEFT)

        # 周次
        ttk.Label(frm, text="周次:").grid(row=3, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_weeks, width=28).grid(row=3, column=1, sticky="w", **pad)
        ttk.Label(frm, text="（如 1-12周、第1周、1,3,5周）",
                  foreground="gray").grid(row=3, column=2, sticky="w", **pad)

        # 校区
        ttk.Label(frm, text="校区:").grid(row=4, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_campus, width=28).grid(row=4, column=1, sticky="w", **pad)

        # 地点
        ttk.Label(frm, text="上课地点:").grid(row=5, column=0, sticky="e", **pad)
        ttk.Entry(frm, textvariable=self.var_location, width=28).grid(row=5, column=1, sticky="w", **pad)

        # 按钮
        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(btns, text="确定", command=self._on_ok).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btns, text="取消", command=self._on_cancel).pack(side=tk.RIGHT, padx=4)

    def _on_ok(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("提示", "课程名不能为空", parent=self)
            return
        try:
            start = int(self.var_start.get())
            end = int(self.var_end.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("提示", "节次必须是整数", parent=self)
            return
        if not (1 <= start <= end <= 13):
            messagebox.showwarning("提示", "节次范围应在 1-13 之间，且起始 ≤ 结束", parent=self)
            return
        weeks = self.var_weeks.get().strip()
        if not parse_weeks(weeks):
            messagebox.showwarning("提示", "周次格式不正确，例如 1-12周、第1周", parent=self)
            return

        self.result = Course(
            name=name,
            day=DAY_NAMES.index(self.var_day.get()),
            start=start,
            end=end,
            weeks=weeks,
            campus=self.var_campus.get().strip(),
            location=self.var_location.get().strip(),
        )
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


# ===========================================================================
# 主窗口
# ===========================================================================
class App(tk.Tk):
    """课程作业管理主窗口。

    布局：
        顶部工具栏：添加课程按钮、当前周次选择器
        左侧：课表 Canvas（周一至周五 x 13 节）
        右侧：课程列表 Treeview（支持双击编辑、删除选中）
    """

    N_PERIODS = 13
    N_DAYS = 5

    def __init__(self):
        super().__init__()
        self.title("课程作业管理")
        self.geometry("1280x820")
        self.minsize(960, 640)

        # 数据
        self.courses: List[Course] = sample_courses()
        self.current_week = tk.IntVar(value=1)

        self._build_ui()
        self._bind_events()

        # 初始绘制
        self.after(50, self._refresh_timetable)
        self._refresh_list()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # ---- 顶部工具栏 ----
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        ttk.Button(toolbar, text="添加课程", command=self.add_course).pack(side=tk.LEFT)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        ttk.Label(toolbar, text="当前周次:").pack(side=tk.LEFT)
        self.week_spin = ttk.Spinbox(
            toolbar, from_=1, to=20, textvariable=self.current_week,
            width=5, command=self._on_week_change,
        )
        self.week_spin.pack(side=tk.LEFT, padx=4)
        ttk.Label(toolbar, text="周（非本周课程灰显）").pack(side=tk.LEFT)

        # "仅显示本周"开关：开启时只绘制当前周有效的课程，并据此决定横向均分的份数；
        # 关闭时保持原有行为（全部课程均分，非本周课程灰显）。
        self.show_only_current_week = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar, text="仅显示本周",
            variable=self.show_only_current_week,
            command=self._refresh_timetable,
        ).pack(side=tk.LEFT, padx=10)

        # ---- 主体：左右分栏 ----
        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        # 左侧课表
        left = ttk.Frame(main)
        main.add(left, weight=3)
        self.canvas = tk.Canvas(left, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 右侧列表
        right = ttk.Frame(main)
        main.add(right, weight=1)

        list_header = ttk.Frame(right)
        list_header.pack(fill=tk.X, padx=6, pady=(8, 4))
        ttk.Label(list_header, text="课程列表", font=("Microsoft YaHei", 11, "bold")).pack(side=tk.LEFT)
        ttk.Button(list_header, text="删除选中", command=self.delete_selected).pack(side=tk.RIGHT)

        columns = ("name", "time", "weeks", "location")
        self.tree = ttk.Treeview(
            right, columns=columns, show="headings", selectmode="browse",
        )
        self.tree.heading("name", text="课程名")
        self.tree.heading("time", text="时间")
        self.tree.heading("weeks", text="周次")
        self.tree.heading("location", text="地点")
        # 课程名列可伸缩，其余列固定宽度，长名称被裁剪而非覆盖相邻列
        self.tree.column("name", width=160, anchor="w", stretch=True)
        self.tree.column("time", width=90, anchor="center", stretch=False)
        self.tree.column("weeks", width=80, anchor="center", stretch=False)
        self.tree.column("location", width=90, anchor="center", stretch=False)

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0), pady=4)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

    def _bind_events(self):
        # 窗口尺寸变化时重绘课表，实现字号/行高/列宽跟随缩放
        self.canvas.bind("<Configure>", lambda e: self._refresh_timetable())

        # 课表卡片双击编辑、右键删除
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)

        # 列表双击编辑、Delete 键删除
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.tree.bind("<Delete>", lambda e: self.delete_selected())

    # -------------------------------------------------------------- 课表绘制
    def _refresh_timetable(self):
        """根据当前窗口尺寸重新绘制整张课表。"""
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 20 or h < 20:
            return

        # 边距与网格尺寸
        left_margin = 46
        top_margin = 34
        right_margin = 6
        bottom_margin = 6
        grid_w = w - left_margin - right_margin
        grid_h = h - top_margin - bottom_margin
        if grid_w <= 0 or grid_h <= 0:
            return

        cell_w = grid_w / self.N_DAYS
        cell_h = grid_h / self.N_PERIODS

        # 字体大小根据格子尺寸动态计算，窗口缩放时字号跟随变化
        font_size = max(8, int(min(cell_h * 0.30, cell_w * 0.13)))
        header_font = ("Microsoft YaHei", font_size, "bold")
        course_font = ("Microsoft YaHei", max(7, font_size - 1))
        loc_font = ("Microsoft YaHei", max(6, font_size - 3))

        current_week = self.current_week.get()
        only_current = self.show_only_current_week.get()

        # ---- 绘制表头背景 ----
        c.create_rectangle(0, 0, w, top_margin, fill="#eef2f7", outline="#cfd8e3")
        c.create_rectangle(0, 0, left_margin, h, fill="#eef2f7", outline="#cfd8e3")

        # ---- 节次号与网格横线 ----
        for i in range(self.N_PERIODS):
            y = top_margin + i * cell_h
            c.create_text(left_margin / 2, y + cell_h / 2,
                          text=str(i + 1), font=header_font, fill="#445566")
            c.create_line(0, y, w, y, fill="#e3e8ef")
        c.create_line(0, top_margin + self.N_PERIODS * cell_h,
                      w, top_margin + self.N_PERIODS * cell_h, fill="#e3e8ef")

        # ---- 星期表头与网格竖线 ----
        for j, name in enumerate(DAY_NAMES):
            x = left_margin + j * cell_w
            c.create_text(x + cell_w / 2, top_margin / 2,
                          text=name, font=header_font, fill="#223344")
            c.create_line(x, 0, x, h, fill="#e3e8ef")
        c.create_line(left_margin + self.N_DAYS * cell_w, 0,
                      left_margin + self.N_DAYS * cell_w, h, fill="#e3e8ef")

        # ---- 绘制课程卡片 ----
        # 按 (day, start, end) 分组，处理同一时间段多门课的冲突（横向均分）
        slots = defaultdict(list)
        for course in self.courses:
            slots[(course.day, course.start, course.end)].append(course)

        for (day, start, end), group in slots.items():
            # 当开启"仅显示本周"时，先过滤出当前周有效的课程，再据此决定均分份数；
            # 这样同时间段但周次不重叠的课程不会互相挤占格子。
            # 关闭时保持原有行为：全部课程均分，非本周课程灰显。
            if only_current:
                visible = [c for c in group
                           if current_week in parse_weeks(c.weeks)]
            else:
                visible = group

            if not visible:
                continue

            n = len(visible)
            for i, course in enumerate(visible):
                # 横向均分给冲突课程
                x0 = left_margin + day * cell_w + i * (cell_w / n)
                x1 = x0 + cell_w / n
                y0 = top_margin + (start - 1) * cell_h
                y1 = top_margin + end * cell_h

                # 是否本周课程
                is_current = current_week in parse_weeks(course.weeks)

                idx = self.courses.index(course)
                if is_current:
                    fill = course_color(idx)
                    outline = "#3a5a8a"
                    text_color = "#14233a"
                else:
                    # 非本周灰显
                    fill = "#d4d8de"
                    outline = "#b4b9c2"
                    text_color = "#7a7f88"

                tag = "course_{}".format(idx)
                pad = 2
                c.create_rectangle(x0 + pad, y0 + pad, x1 - pad, y1 - pad,
                                   fill=fill, outline=outline, width=1,
                                   tags=(tag,))

                # 卡片内文字：课程名 + 地点，留出内边距避免塞满格子
                text_w = (x1 - x0) - pad * 4
                cx = (x0 + x1) / 2
                # 课程名（自动换行）
                name_id = c.create_text(
                    cx, (y0 + y1) / 2 - (cell_h * 0.12 if end - start >= 2 else 0),
                    text=course.name, font=course_font, fill=text_color,
                    width=max(20, text_w), tags=(tag,),
                )
                # 地点（多行课程才显示，避免拥挤）
                if end - start >= 2:
                    c.create_text(
                        cx, (y0 + y1) / 2 + cell_h * 0.22,
                        text=course.location, font=loc_font, fill=text_color,
                        width=max(20, text_w), tags=(tag,),
                    )

    # ---------------------------------------------------------- 事件处理
    def _course_index_at(self, event) -> int:
        """返回画布上点击位置对应的课程索引，未命中返回 -1。"""
        c = self.canvas
        items = c.find_withtag("current")
        if not items:
            # current 可能未命中，用最近点再试一次
            items = c.find_closest(event.x, event.y)
        for item in items:
            for tag in c.gettags(item):
                if tag.startswith("course_"):
                    return int(tag.split("_", 1)[1])
        return -1

    def _on_canvas_double_click(self, event):
        idx = self._course_index_at(event)
        if idx >= 0:
            self.edit_course(idx)

    def _on_canvas_right_click(self, event):
        idx = self._course_index_at(event)
        if idx >= 0:
            if messagebox.askyesno("删除课程",
                                   "确定删除课程「{}」吗？".format(self.courses[idx].name),
                                   parent=self):
                self.delete_course(idx)

    def _on_week_change(self):
        self._refresh_timetable()

    # ---------------------------------------------------------- 增删改
    def add_course(self):
        dlg = CourseDialog(self, title="添加课程")
        if dlg.result is not None:
            self.courses.append(dlg.result)
            self._refresh_timetable()
            self._refresh_list()

    def edit_course(self, idx: int):
        dlg = CourseDialog(self, course=self.courses[idx], title="编辑课程")
        if dlg.result is not None:
            self.courses[idx] = dlg.result
            self._refresh_timetable()
            self._refresh_list()

    def delete_course(self, idx: int):
        del self.courses[idx]
        self._refresh_timetable()
        self._refresh_list()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "tags")[0])
        self.edit_course(idx)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在列表中选中一门课程", parent=self)
            return
        idx = int(self.tree.item(sel[0], "tags")[0])
        if messagebox.askyesno("删除课程",
                               "确定删除课程「{}」吗？".format(self.courses[idx].name),
                               parent=self):
            self.delete_course(idx)

    # -------------------------------------------------------------- 列表刷新
    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, course in enumerate(self.courses):
            time_str = "{} {}-{}节".format(DAY_NAMES[course.day], course.start, course.end)
            self.tree.insert(
                "", tk.END,
                values=(course.name, time_str, course.weeks, course.location),
                tags=(str(idx),),
            )


# ===========================================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()
