# -*- coding: utf-8 -*-
"""
DH聚焦追踪器
功能：
  1. 可视化交互窗口，可添加/删除角色
  2. 点击头像可更换自定义图片，点击名称输入框可编辑角色名称
  3. 默认聚焦次数为 3，每个角色后面的计数点数量可由工具栏「聚焦次数」全局调节（2-10），
     新添加的角色会自动同步当前聚焦次数
  4. 计数点从左到右依次标记，点击点切换 标记/未标记 状态
  5. 所有角色的点全部标记时，弹窗提示「回合结束，新回合开始。」并在聚焦记录中打隔断，
     记录中显示「第 n 回合结束，第 n+1 回合开始」；记录序号从 1 开始，新回合后重头计
  6. 聚焦记录带滑动条，默认显示最新一条；可手动清空记录并重新从第 1 回合开始
  7. 可保存/使用设置方案（角色头像、名称与聚焦次数），关闭程序时自动清除记录缓存
运行：python DH聚焦追踪器.py
"""

import base64
import ctypes
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog

try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _enable_high_dpi():
    """Windows 下启用高 DPI 感知，提升界面与头像清晰度"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# 骰子原图 base64（512x512 PNG，原样嵌入，不依赖 Pillow/外部文件）
_DICE_ICON_B64 = "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"

POINT_MIN = 2
POINT_MAX = 10
AVATAR_COLORS = ["#5b8def", "#f0785a", "#45c48b", "#f2b84b",
                 "#9b7bf2", "#4bc7cf", "#e86fa8", "#8bca3e"]


class RoundCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DH聚焦追踪器")
        self.root.geometry("1080x700")
        self.root.minsize(760, 480)
        self.root.configure(bg="#eef1f7")

        self.roles = []
        self._color_idx = 0
        self.mark_log = []          # 聚焦记录 [(role, canvas), ("round", n), ...]
        self._log_photos = []       # 记录区头像缓存引用
        self.global_count = 3       # 默认聚焦次数
        self.round_no = 1           # 当前回合号（从第 1 回合开始记录）
        self._next_role_index = 1   # 角色默认编号递增序号（应用方案后重置为 1）
        self._undo_stack = []       # 撤销栈
        self._redo_stack = []       # 重做栈
        self.profiles_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "dh_focus_profiles.json")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Control-z>", self._on_undo_key)
        self.root.bind("<Control-y>", self._on_redo_key)
        self._build_toolbar()
        self._build_main_area()
        self.add_role()

    # ---------- 界面构建 ----------
    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg="#eef1f7")
        bar.pack(fill="x", padx=14, pady=(14, 6))

        add_btn = tk.Button(bar, text="＋ 添加角色", font=("Microsoft YaHei", 11),
                            bg="#4f8cff", fg="white", relief="flat",
                            padx=14, pady=6, cursor="hand2", command=self.add_role)
        add_btn.pack(side="left")

        reset_btn = tk.Button(bar, text="重置追踪器", font=("Microsoft YaHei", 11),
                              bg="#f0785a", fg="white", relief="flat",
                              padx=14, pady=6, cursor="hand2", command=self.reset_all)
        reset_btn.pack(side="left", padx=(10, 0))

        clear_btn = tk.Button(bar, text="清空记录", font=("Microsoft YaHei", 11),
                              bg="#8a94a8", fg="white", relief="flat",
                              padx=10, pady=6, cursor="hand2", command=self.clear_log)
        clear_btn.pack(side="left", padx=(8, 0))

        save_btn = tk.Button(bar, text="保存方案", font=("Microsoft YaHei", 11),
                             bg="#45c48b", fg="white", relief="flat",
                             padx=10, pady=6, cursor="hand2", command=self.save_profile)
        save_btn.pack(side="left", padx=(8, 0))

        load_btn = tk.Button(bar, text="使用方案", font=("Microsoft YaHei", 11),
                             bg="#9b7bf2", fg="white", relief="flat",
                             padx=10, pady=6, cursor="hand2", command=self.choose_profile)
        load_btn.pack(side="left", padx=(8, 0))

        # 全局聚焦次数调节（同步所有角色的聚焦次数）
        global_frame = tk.Frame(bar, bg="#eef1f7")
        global_frame.pack(side="left", padx=(24, 0))
        tk.Label(global_frame, text="聚焦次数：", font=("Microsoft YaHei", 10),
                 bg="#eef1f7", fg="#555c6e").pack(side="left")
        tk.Button(global_frame, text="－", font=("Microsoft YaHei", 11, "bold"), width=2,
                  bg="#e6e9f2", relief="flat", cursor="hand2",
                  command=lambda: self.set_global_count(-1)).pack(side="left", padx=(4, 2))
        self.global_count_var = tk.StringVar(value="3")
        tk.Label(global_frame, textvariable=self.global_count_var,
                 font=("Microsoft YaHei", 11, "bold"), bg="#eef1f7",
                 fg="#333b4d", width=3).pack(side="left")
        tk.Button(global_frame, text="＋", font=("Microsoft YaHei", 11, "bold"), width=2,
                  bg="#e6e9f2", relief="flat", cursor="hand2",
                  command=lambda: self.set_global_count(1)).pack(side="left", padx=(2, 6))

        tip = tk.Label(bar, text="点从左到右依次标记；Ctrl+Z 撤销 / Ctrl+Y 重做；全部标记自动进入新回合",
                       font=("Microsoft YaHei", 9), bg="#eef1f7", fg="#8a94a8")
        tip.pack(side="right")

    def _build_main_area(self):
        main = tk.Frame(self.root, bg="#eef1f7")
        main.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # 左侧：角色列表（可滚动）
        left = tk.Frame(main, bg="#eef1f7")
        left.pack(side="left", fill="both", expand=True)

        self.scroll_canvas = tk.Canvas(left, bg="#eef1f7", highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(self.scroll_canvas, bg="#eef1f7")
        self._win = self.scroll_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
                             lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scroll_canvas.bind("<Configure>",
                                lambda e: self.scroll_canvas.itemconfigure(self._win, width=e.width))

        # 右侧：聚焦记录面板
        right = tk.Frame(main, bg="#ffffff", width=260,
                         highlightbackground="#dfe3ee", highlightthickness=1)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)
        self.log_panel = right       # 记录面板引用，用于滚轮命中判断

        tk.Label(right, text="聚焦记录", font=("Microsoft YaHei", 12, "bold"),
                 bg="#ffffff", fg="#333b4d").pack(pady=(12, 6))

        self.log_canvas = tk.Canvas(right, bg="#ffffff", highlightthickness=0)
        log_sb = ttk.Scrollbar(right, orient="vertical", command=self.log_canvas.yview)
        self.log_canvas.configure(yscrollcommand=log_sb.set)
        self.log_canvas.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=(0, 6))
        log_sb.pack(side="right", fill="y", pady=(0, 6))

        self.log_inner = tk.Frame(self.log_canvas, bg="#ffffff")
        self._log_win = self.log_canvas.create_window((0, 0), window=self.log_inner, anchor="nw")
        self.log_inner.bind("<Configure>",
                            lambda e: self.log_canvas.configure(scrollregion=self.log_canvas.bbox("all")))
        self.log_canvas.bind("<Configure>",
                             lambda e: self.log_canvas.itemconfigure(self._log_win, width=e.width))
        # 鼠标滚轮滚动记录（全局绑定，按鼠标实际位置判断是否位于记录面板内）
        self.root.bind_all("<MouseWheel>", self._on_log_wheel)

    # ---------- 角色管理 ----------
    def add_role(self):
        role = self._create_role_data(self._next_role_index)
        self._next_role_index += 1
        role["frame"].pack(fill="x", padx=2, pady=8)
        self.roles.append(role)
        self._clear_history()

    def _create_role_data(self, index, preset=None):
        """新建角色数据；preset 为已保存方案中的角色信息（名称/头像/颜色）"""
        frame = tk.Frame(self.list_frame, bg="#ffffff",
                         highlightbackground="#dfe3ee", highlightthickness=1)
        frame.columnconfigure(3, weight=1)

        # 头像（点击更换图片，64px 高清显示）
        if preset and preset.get("avatar_color"):
            color = preset["avatar_color"]
        else:
            color = AVATAR_COLORS[self._color_idx % len(AVATAR_COLORS)]
            self._color_idx += 1
        avatar_path = preset.get("avatar_path") if preset else None
        avatar = tk.Canvas(frame, width=64, height=64, bg="#ffffff",
                           highlightthickness=0, cursor="hand2")
        avatar.grid(row=0, column=0, rowspan=2, padx=(12, 12), pady=12)
        avatar.bind("<Button-1>", lambda e: self.change_avatar(role))

        # 名称（可编辑）
        default_name = preset.get("name") if preset else "角色%d" % index
        name_var = tk.StringVar(value=default_name)
        name_entry = tk.Entry(frame, textvariable=name_var, font=("Microsoft YaHei", 11),
                              relief="solid", bd=1, width=16)
        name_entry.grid(row=0, column=1, sticky="w", pady=(16, 6))
        name_entry.bind("<FocusOut>", lambda e: self._on_name_changed(role))

        # 删除角色
        del_btn = tk.Button(frame, text="✕", font=("Microsoft YaHei", 10), width=2,
                            bg="#f5f6fa", fg="#a0a6b5", relief="flat", cursor="hand2",
                            command=lambda: self.remove_role(role))
        del_btn.grid(row=0, column=2, padx=(6, 12), pady=(14, 0))

        # 点阵区
        points_frame = tk.Frame(frame, bg="#ffffff")
        points_frame.grid(row=0, column=3, rowspan=2, sticky="e", padx=(8, 14), pady=16)

        role = {
            "frame": frame,
            "avatar": avatar,
            "avatar_path": avatar_path,
            "avatar_color": color,
            "name_var": name_var,
            "point_count": self.global_count,   # 新角色默认同步当前聚焦次数
            "points_frame": points_frame,
            "point_widgets": [],
            "marked": {},
        }
        self._draw_avatar(role)
        self._rebuild_points(role)
        return role

    # ---------- 头像 ----------
    def _draw_avatar(self, role):
        c = role["avatar"]
        c.delete("all")
        if role["avatar_path"]:
            img = Image.open(role["avatar_path"]).convert("RGBA")
            img = img.resize((64, 64), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            c.create_image(32, 32, image=photo)
            role["_photo"] = photo  # 保持引用防止被回收
        else:
            color = role["avatar_color"]
            c.create_oval(2, 2, 62, 62, fill=color, outline="")
            text = (role["name_var"].get() or "?").strip()
            c.create_text(32, 34, text=text[0] if text else "?",
                          fill="white", font=("Microsoft YaHei", 22, "bold"))

    def _refresh_avatar_text(self, role):
        if not role["avatar_path"]:
            self._draw_avatar(role)

    def _on_name_changed(self, role):
        self._refresh_avatar_text(role)
        self._update_log()

    def change_avatar(self, role):
        if not HAS_PIL:
            self.show_notice("提示", "需要安装 Pillow 才能使用自定义图片头像。\n\n安装命令：pip install pillow\n安装后重新运行本程序即可。")
            return
        path = filedialog.askopenfilename(
            title="选择头像图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                       ("所有文件", "*.*")])
        if not path:
            return
        try:
            role["avatar_path"] = path
            self._draw_avatar(role)
            self._update_log()
        except Exception as e:
            self.show_notice("加载失败", "无法加载图片：%s" % e)

    # ---------- 计数器点 ----------
    def _rebuild_points(self, role, keep_marked=None):
        for w in role["point_widgets"]:
            w.destroy()
        role["point_widgets"] = []
        role["marked"] = {}
        old = keep_marked or []
        n = role["point_count"]
        for i in range(n):
            canvas = tk.Canvas(role["points_frame"], width=32, height=32,
                               bg="#ffffff", highlightthickness=0, cursor="hand2")
            canvas.pack(side="left", padx=3)
            marked = old[i] if i < len(old) else False
            role["marked"][canvas] = marked
            self._draw_point(canvas, marked)
            canvas.bind("<Button-1>", lambda e, c=canvas: self.toggle_point(role, c))
            role["point_widgets"].append(canvas)

    def _draw_point(self, canvas, marked):
        canvas.delete("all")
        if marked:
            canvas.create_oval(2, 2, 30, 30, fill="#4f8cff", outline="#3572d8")
            canvas.create_line(9, 17, 14, 22, 23, 10, fill="white", width=3,
                               capstyle="round", joinstyle="round")
        else:
            canvas.create_oval(2, 2, 30, 30, fill="#ffffff", outline="#b9c0d4", width=2)

    def toggle_point(self, role, canvas):
        old_marked = bool(role["marked"].get(canvas, False))
        if old_marked:
            # 取消标记：只允许从最右侧的已标记点往回退，点击更靠左的已标记点则忽略
            rightmost = None
            for c in role["point_widgets"]:
                if role["marked"].get(c, False):
                    rightmost = c
            if rightmost is not canvas:
                return
            pos = self._find_mark_entry_index(role, canvas)
        else:
            # 标记：只能从左到右依次标记，点击的不是最靠左的未标记点则忽略
            for c in role["point_widgets"]:
                if not role["marked"].get(c, False):
                    if c is not canvas:
                        return
                    break
            pos = None
        marked = not old_marked
        role["marked"][canvas] = marked
        self._draw_point(canvas, marked)
        if marked:
            self.mark_log.append((role, canvas))
        else:
            self._remove_mark_entry(role, canvas)
        self._push_undo(("toggle", role, canvas, old_marked, marked, pos))
        self._update_log()
        self._check_round_complete()

    def _find_mark_entry_index(self, role, canvas):
        for i, item in enumerate(self.mark_log):
            if (isinstance(item, tuple) and len(item) == 2
                    and item[0] is role and item[1] is canvas):
                return i
        return None

    def _remove_mark_entry(self, role, canvas):
        for i, item in enumerate(self.mark_log):
            if (isinstance(item, tuple) and len(item) == 2
                    and item[0] is role and item[1] is canvas):
                self.mark_log.pop(i)
                return

    def set_global_count(self, delta):
        new_count = self.global_count + delta
        if new_count < POINT_MIN or new_count > POINT_MAX:
            return
        self.global_count = new_count
        self.global_count_var.set(str(new_count))
        for role in self.roles:
            self._recount_role_points(role, new_count)
        self._clear_history()        # 调整聚焦次数后清空撤销/重做历史

    def _recount_role_points(self, role, new_count):
        """聚焦次数变化时重建点阵：保留最左侧已标记点；若新次数小于已标记数量，
        截断最右侧多余标记并清理 mark_log 对应记录；新增加的点保持未标记"""
        old_marked = [c for c in role["point_widgets"] if role["marked"].get(c, False)]
        keep = min(len(old_marked), new_count)
        role["point_count"] = new_count
        keep_marked = [True] * keep + [False] * (new_count - keep)
        self._rebuild_points(role, keep_marked=keep_marked)
        # 以新 canvas 对象按原相对顺序重建该角色的 mark_log 条目，截断的条目丢弃
        new_widgets = role["point_widgets"]
        kept = iter(new_widgets[:keep])
        new_log = []
        for item in self.mark_log:
            if isinstance(item, tuple) and len(item) == 2 and item[0] is role:
                nw = next(kept, None)
                if nw is not None:
                    new_log.append((role, nw))
            else:
                new_log.append(item)
        self.mark_log = new_log
        self._update_log()

    # ---------- 回合 / 重置 ----------
    def _check_round_complete(self):
        if not self.roles:
            return
        for role in self.roles:
            for c in role["point_widgets"]:
                if not role["marked"].get(c, False):
                    return
        self.show_notice("回合结束", "回合结束，新回合开始。")
        self.reset_all()

    def _start_new_round(self):
        """进入新回合：在记录中打隔断，标注「第 n 回合结束，第 n+1 回合开始」"""
        self.mark_log.append(("round", self.round_no))
        self.round_no += 1
        self._update_log()

    def reset_all(self):
        # 记录撤销所需的回合快照（各角色标记状态 + 当前回合号）
        snapshot = []
        for role in self.roles:
            states = [bool(role["marked"].get(c, False)) for c in role["point_widgets"]]
            snapshot.append((role, states, list(role["point_widgets"])))
        round_before = self.round_no
        for role in self.roles:
            for c in role["point_widgets"]:
                role["marked"][c] = False
                self._draw_point(c, False)
        self._start_new_round()      # 新回合打隔断，不清空记录
        round_after = self.round_no
        self._push_undo(("reset", round_before, round_after, snapshot, ("round", round_before)))

    def clear_log(self):
        self.mark_log = []
        self.round_no = 1            # 手动清空记录后从第 1 回合重新开始
        self._clear_history()
        self._update_log()

    # ---------- 撤销 / 重做 ----------
    def _clear_history(self):
        self._undo_stack = []
        self._redo_stack = []

    def _push_undo(self, op):
        self._undo_stack.append(op)
        if len(self._undo_stack) > 200:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _on_undo_key(self, event):
        # 焦点位于角色名称输入框（Entry）时不触发撤销，避免与输入框文本撤销冲突
        w = self.root.focus_get()
        if isinstance(w, tk.Entry):
            return None
        self.undo()
        return "break"

    def _on_redo_key(self, event):
        self.redo()
        return "break"

    def undo(self):
        if not self._undo_stack:
            return
        op = self._undo_stack.pop()
        self._redo_stack.append(op)
        if op[0] == "toggle":
            self._undo_toggle(op)
        elif op[0] == "reset":
            self._undo_reset(op)

    def redo(self):
        if not self._redo_stack:
            return
        op = self._redo_stack.pop()
        self._undo_stack.append(op)
        if op[0] == "toggle":
            self._redo_toggle(op)
        elif op[0] == "reset":
            self._redo_reset(op)

    def _undo_toggle(self, op):
        _, role, canvas, old_marked, _new_marked, pos = op
        role["marked"][canvas] = old_marked
        self._draw_point(canvas, old_marked)
        self._remove_mark_entry(role, canvas)
        if old_marked:
            entry = (role, canvas)
            if pos is not None and 0 <= pos <= len(self.mark_log):
                self.mark_log.insert(pos, entry)
            else:
                self.mark_log.append(entry)
        self._update_log()

    def _redo_toggle(self, op):
        _, role, canvas, _old_marked, new_marked, _pos = op
        role["marked"][canvas] = new_marked
        self._draw_point(canvas, new_marked)
        self._remove_mark_entry(role, canvas)
        if new_marked:
            self.mark_log.append((role, canvas))
        self._update_log()

    def _undo_reset(self, op):
        _, round_before, _round_after, snapshot, round_entry = op
        self._remove_round_entry(round_entry)
        for role, states, widgets in snapshot:
            for c, st in zip(widgets, states):
                role["marked"][c] = st
                self._draw_point(c, st)
        self.round_no = round_before
        self._update_log()

    def _redo_reset(self, op):
        _, _round_before, round_after, snapshot, round_entry = op
        for role, _states, widgets in snapshot:
            for c in widgets:
                role["marked"][c] = False
                self._draw_point(c, False)
        self.mark_log.append(round_entry)
        self.round_no = round_after
        self._update_log()

    def _remove_round_entry(self, entry):
        for i in range(len(self.mark_log) - 1, -1, -1):
            item = self.mark_log[i]
            if (isinstance(item, tuple) and len(item) == 2
                    and item[0] == "round" and item[1] == entry[1]):
                self.mark_log.pop(i)
                return

    def remove_role(self, role):
        role["frame"].destroy()
        self.roles.remove(role)
        self.mark_log = [item for item in self.mark_log
                         if not (isinstance(item, tuple) and len(item) == 2 and item[0] is role)]
        self._clear_history()
        self._update_log()

    def _make_log_avatar(self, role, size=24):
        """生成记录区小头像缩略图；头像变更时 _update_log 会重新生成，自动同步"""
        if not HAS_PIL:
            return None
        try:
            if role["avatar_path"]:
                img = Image.open(role["avatar_path"]).convert("RGBA")
                img = img.resize((size, size), Image.LANCZOS)
            else:
                img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.ellipse((0, 0, size - 1, size - 1), fill=role["avatar_color"])
            photo = ImageTk.PhotoImage(img)
            self._log_photos.append(photo)
            return photo
        except Exception:
            return None

    def _update_log(self):
        """刷新右侧聚焦记录：记录带从 1 开始的序号，新回合重头计；
        隔断明显标注「第 n 回合结束，第 n+1 回合开始」；默认显示最新记录"""
        for w in self.log_inner.winfo_children():
            w.destroy()
        if not self.mark_log:
            tk.Label(self.log_inner, text="暂无记录", font=("Microsoft YaHei", 10),
                     bg="#ffffff", fg="#a0a6b5").pack(pady=18)
            return
        seq = 0
        for item in self.mark_log:
            # 回合隔断：明显分隔线 + 回合起止文案
            if isinstance(item, tuple) and len(item) == 2 and item[0] == "round":
                n = item[1]
                seq = 0              # 新回合开始，序号从 1 重新计
                tk.Frame(self.log_inner, height=2, bg="#f0785a").pack(
                    fill="x", padx=4, pady=(10, 2))
                tk.Label(self.log_inner,
                         text="第%d回合结束，第%d回合开始" % (n, n + 1),
                         font=("Microsoft YaHei", 9, "bold"),
                         bg="#fff3ef", fg="#c05b3a").pack(fill="x", padx=4, pady=(0, 6))
                continue
            role, canvas = item
            seq += 1
            row = tk.Frame(self.log_inner, bg="#f5f6fa")
            row.pack(fill="x", padx=8, pady=3)
            avatar = self._make_log_avatar(role)
            if avatar:
                tk.Label(row, image=avatar, bg="#f5f6fa").pack(side="left", padx=(4, 6))
            name = (role["name_var"].get() or "未命名").strip()
            tk.Label(row, text="%d. %s" % (seq, name), font=("Microsoft YaHei", 10),
                     bg="#f5f6fa", fg="#333b4d").pack(side="left", pady=2)
        # 默认滚动到最底部，保证最新一条记录可见
        self.root.after(30, lambda: self.log_canvas.yview_moveto(1.0))

    def _on_log_wheel(self, event):
        """鼠标滚轮滚动聚焦记录：仅当指针位于记录面板（含其子组件）时生效，
        其他区域（如左侧角色列表）不受影响。Windows 事件 delta 为 ±120 的倍数，
        正为向上滚，使用 int(-delta/120) 使内容随滚轮方向移动"""
        delta = getattr(event, "delta", 0)
        if delta == 0:
            return None
        node = getattr(event, "widget", None)
        while node is not None:
            if node is self.log_panel:
                self.log_canvas.yview_scroll(int(-delta / 120), "units")
                return "break"
            node = node.master
        return None

    # ---------- 设置方案（保存/使用） ----------
    def save_profile(self):
        """弹出输入框，将当前角色（头像/名称）与聚焦次数保存为一个设置方案"""
        top = tk.Toplevel(self.root)
        top.title("保存设置方案")
        top.configure(bg="#ffffff")
        top.resizable(False, False)
        top.attributes("-topmost", True)
        x = self.root.winfo_rootx() + 180
        y = self.root.winfo_rooty() + 180
        top.geometry("360x150+%d+%d" % (max(x, 0), max(y, 0)))

        tk.Label(top, text="方案名称：", font=("Microsoft YaHei", 11),
                 bg="#ffffff", fg="#333b4d").pack(pady=(20, 4))
        entry = tk.Entry(top, font=("Microsoft YaHei", 11), width=24)
        entry.pack(pady=(0, 12))
        entry.focus_set()

        def _ok():
            name = entry.get().strip()
            if not name:
                return
            self._save_profile(name)
            top.destroy()

        def _cancel():
            top.destroy()

        btn_row = tk.Frame(top, bg="#ffffff")
        btn_row.pack(pady=(0, 12))
        tk.Button(btn_row, text="取消", font=("Microsoft YaHei", 11),
                  bg="#e6e9f2", fg="#555c6e", relief="flat", width=10, pady=4,
                  cursor="hand2", command=_cancel).pack(side="left", padx=6)
        tk.Button(btn_row, text="保存", font=("Microsoft YaHei", 11),
                  bg="#45c48b", fg="white", relief="flat", width=10, pady=4,
                  cursor="hand2", command=_ok).pack(side="left", padx=6)
        entry.bind("<Return>", lambda e: _ok())
        top.transient(self.root)
        top.grab_set()

    def _read_profiles(self):
        try:
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_profile(self, name):
        """将当前状态写入方案文件（角色头像/名称 + 聚焦次数）"""
        profiles = self._read_profiles()
        profile = {
            "name": name,
            "global_count": self.global_count,
            "roles": [
                {
                    "name": (r["name_var"].get() or "角色").strip(),
                    "avatar_path": r["avatar_path"],
                    "avatar_color": r["avatar_color"],
                }
                for r in self.roles
            ],
        }
        for i, p in enumerate(profiles):
            if p.get("name") == name:
                profiles[i] = profile
                break
        else:
            profiles.append(profile)
        try:
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            self.show_notice("已保存", "设置方案「%s」已保存。" % name)
        except Exception as e:
            self.show_notice("保存失败", "无法保存方案：%s" % e)

    def choose_profile(self):
        """弹出方案列表，用户自由选择要使用的设置方案"""
        profiles = self._read_profiles()
        if not profiles:
            self.show_notice("提示", "暂无已保存的设置方案。\n请先点击「保存方案」保存当前设置。")
            return
        top = tk.Toplevel(self.root)
        top.title("选择设置方案")
        top.configure(bg="#ffffff")
        top.resizable(False, False)
        top.attributes("-topmost", True)
        x = self.root.winfo_rootx() + 150
        y = self.root.winfo_rooty() + 120
        top.geometry("420x300+%d+%d" % (max(x, 0), max(y, 0)))

        tk.Label(top, text="请选择要使用的方案：", font=("Microsoft YaHei", 11),
                 bg="#ffffff", fg="#333b4d").pack(pady=(14, 6))
        lb = tk.Listbox(top, font=("Microsoft YaHei", 10), height=8,
                        selectmode="single", relief="solid", bd=1)
        for p in profiles:
            lb.insert("end", "%s（聚焦次数：%d，角色：%d）" % (
                p.get("name", "未命名"),
                int(p.get("global_count", 3)),
                len(p.get("roles", []))))
        lb.pack(fill="both", expand=True, padx=18, pady=(0, 10))
        if profiles:
            lb.selection_set(0)

        def _apply():
            sel = lb.curselection()
            if not sel:
                return
            self._apply_profile(profiles[sel[0]])
            top.destroy()

        def _cancel():
            top.destroy()

        btn_row = tk.Frame(top, bg="#ffffff")
        btn_row.pack(pady=(0, 12))
        tk.Button(btn_row, text="取消", font=("Microsoft YaHei", 11),
                  bg="#e6e9f2", fg="#555c6e", relief="flat", width=10, pady=4,
                  cursor="hand2", command=_cancel).pack(side="left", padx=6)
        tk.Button(btn_row, text="使用此方案", font=("Microsoft YaHei", 11),
                  bg="#9b7bf2", fg="white", relief="flat", width=12, pady=4,
                  cursor="hand2", command=_apply).pack(side="left", padx=6)
        lb.bind("<Double-Button-1>", lambda e: _apply())
        top.transient(self.root)
        top.grab_set()

    def _apply_profile(self, profile):
        """按选定方案重建界面：角色（头像/名称）与全局聚焦次数"""
        for role in list(self.roles):
            role["frame"].destroy()
        self.roles = []
        self._color_idx = 0
        self.global_count = int(profile.get("global_count", 3))
        self.global_count_var.set(str(self.global_count))
        for i, rdata in enumerate(profile.get("roles", []), start=1):
            role = self._create_role_data(i, preset=rdata)
            role["frame"].pack(fill="x", padx=2, pady=8)
            self.roles.append(role)
        # 应用方案后清空记录，从第 1 回合重新开始；角色编号从 1 重新递增
        self.mark_log = []
        self.round_no = 1
        self._next_role_index = 1
        self._clear_history()
        self._update_log()

    def _on_close(self):
        """关闭程序时清除记录缓存（内存中的记录与头像句柄）"""
        self.mark_log = []
        self._log_photos = []
        for role in self.roles:
            role["_photo"] = None
        self.root.destroy()

    def show_notice(self, title, text):
        """自定义无声音弹窗（替代 messagebox，避免系统铃声）"""
        top = tk.Toplevel(self.root)
        top.title(title)
        top.configure(bg="#ffffff")
        top.resizable(False, False)
        top.attributes("-topmost", True)

        width, height = 440, 170
        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - height) // 2
        top.geometry("%dx%d+%d+%d" % (width, height, max(x, 0), max(y, 0)))

        tk.Label(top, text=text, font=("Microsoft YaHei", 11), bg="#ffffff",
                 fg="#333b4d", justify="center", wraplength=400).pack(pady=(28, 16))

        def _close():
            top.destroy()

        tk.Button(top, text="确定", font=("Microsoft YaHei", 11),
                  bg="#4f8cff", fg="white", relief="flat", width=10, pady=4,
                  cursor="hand2", command=_close).pack(pady=(0, 20))
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)


def main():
    _enable_high_dpi()
    root = tk.Tk()
    # 用骰子原图（base64 嵌入）设置标题栏与任务栏图标，不依赖外部文件/Pillow
    try:
        _icon_photo = tk.PhotoImage(data=_DICE_ICON_B64)
        root.iconphoto(True, _icon_photo)
        root._icon_photo_ref = _icon_photo  # 保持引用防止被回收
    except Exception:
        pass
    RoundCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
