"""
ナンプレ（数独）ソルバー
=======================
Tkinter を使ったデスクトップ GUI アプリケーション。
バックトラッキング法で解を求め、
アニメーション付きで解く過程を可視化できます。
"""

import tkinter as tk
from tkinter import messagebox
import time


# ===== カラーパレット =====
BG_MAIN       = "#1e1e2e"   # メイン背景（ダーク）
BG_GRID       = "#2a2a3e"   # グリッド背景
BG_BLOCK_A    = "#2e2e45"   # 3x3 ブロック色 A
BG_BLOCK_B    = "#252538"   # 3x3 ブロック色 B
FG_FIXED      = "#cdd6f4"   # 初期値（ユーザー入力）の文字色
FG_SOLVED     = "#a6e3a1"   # ソルバーが埋めた文字色
FG_ANIM       = "#f9e2af"   # アニメーション中の試行色
FG_ERROR      = "#f38ba8"   # エラー色
BG_BTN_SOLVE  = "#89b4fa"   # 「解く」ボタン背景
BG_BTN_CLEAR  = "#f38ba8"   # 「クリア」ボタン背景
BG_BTN_ANIM   = "#a6e3a1"   # 「アニメーション」ボタン背景
FG_BTN        = "#1e1e2e"   # ボタン文字色
FONT_CELL     = ("Segoe UI", 18, "bold")   # セルフォント
FONT_BTN      = ("Segoe UI", 12, "bold")   # ボタンフォント
FONT_TITLE    = ("Segoe UI", 20, "bold")   # タイトルフォント


class SudokuSolver:
    """
    数独の盤面を管理し、バックトラッキング法で解くクラス。
    GUI には依存せず、純粋なロジックのみを保持する。
    """

    def __init__(self, board: list[list[int]]):
        # board は 9x9 の 2次元リスト。空マスは 0 で表す。
        self.board = [row[:] for row in board]  # ディープコピー

    # ---- 検証ロジック ------------------------------------------------

    def is_valid(self, row: int, col: int, num: int) -> bool:
        """指定セルに num を置いても規則違反がないか検証する。"""
        # 行チェック
        if num in self.board[row]:
            return False
        # 列チェック
        if num in [self.board[r][col] for r in range(9)]:
            return False
        # 3x3 ブロックチェック
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if self.board[r][c] == num:
                    return False
        return True

    # ---- 解法本体（バックトラッキング） -----------------------------

    def solve(self) -> bool:
        """
        バックトラッキング再帰で盤面を解く。
        解が見つかれば True、なければ False を返す。
        """
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:  # 空マスを発見
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            self.board[row][col] = num   # 仮置き
                            if self.solve():             # 再帰
                                return True
                            self.board[row][col] = 0    # バックトラック
                    return False  # どの数字も置けない → バックトラック
        return True  # 全マス埋まった


class SudokuApp:
    """
    Tkinter を使った数独ソルバー GUI。
    ・9×9 の入力グリッド
    ・「解く」「アニメーション」「クリア」の 3 ボタン
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ナンプレ ソルバー")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)
        self.root.minsize(420, 500)  # 最小サイズを設定（小さくしすぎ防止）

        # セルごとの StringVar（入力管理）
        self.cells: list[list[tk.StringVar]] = []
        # セルごとの Entry ウィジェット参照
        self.entries: list[list[tk.Entry]] = []
        # アニメーション速度（秒）
        self.anim_delay = 0.03

        self._build_ui()

    # ===== UI 構築 ====================================================

    def _build_ui(self):
        """全ウィジェットを生成・配置する。"""

        # ウィンドウ全体のリサイズ設定
        # row 1（グリッドフレーム行）だけを伸縮させる
        self.root.rowconfigure(0, weight=0)  # タイトル行：固定
        self.root.rowconfigure(1, weight=1)  # グリッド行：伸縮
        self.root.rowconfigure(2, weight=0)  # ボタン行：固定
        self.root.rowconfigure(3, weight=0)  # ヒント行：固定
        self.root.columnconfigure(0, weight=1)  # 列方向は全体を伸縮

        # --- タイトルラベル
        title = tk.Label(
            self.root,
            text="🔢 ナンプレ ソルバー",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=FG_FIXED,
            pady=14,
        )
        title.grid(row=0, column=0, sticky="ew")

        # --- グリッドフレーム（リサイズで拡縮する）
        grid_frame = tk.Frame(self.root, bg=BG_MAIN, padx=12, pady=4)
        grid_frame.grid(row=1, column=0, sticky="nsew")

        # グリッドフレーム内の各行・列をリサイズ時に均等に伸縮させる
        for i in range(9):
            grid_frame.rowconfigure(i, weight=1)
            grid_frame.columnconfigure(i, weight=1)

        for row in range(9):
            row_vars = []
            row_entries = []
            for col in range(9):
                var = tk.StringVar()
                # 3x3 ブロックの色分け（市松模様）
                block_row, block_col = row // 3, col // 3
                is_dark = (block_row + block_col) % 2 == 0
                bg_color = BG_BLOCK_A if is_dark else BG_BLOCK_B

                # セル外枠の余白でブロック境界を強調
                pad_top    = 4 if row % 3 == 0 else 1
                pad_left   = 4 if col % 3 == 0 else 1
                pad_bottom = 4 if row % 3 == 2 else 1
                pad_right  = 4 if col % 3 == 2 else 1

                entry = tk.Entry(
                    grid_frame,
                    textvariable=var,
                    # width は指定しない → セルがウィンドウに合わせて伸縮する
                    font=FONT_CELL,
                    justify="center",
                    bg=bg_color,
                    fg=FG_FIXED,
                    insertbackground=FG_FIXED,
                    relief="flat",
                    bd=0,
                    highlightthickness=1,
                    highlightcolor="#89b4fa",
                    highlightbackground="#3e3e5e",
                )
                entry.grid(
                    row=row,
                    column=col,
                    padx=(pad_left, pad_right),
                    pady=(pad_top, pad_bottom),
                    sticky="nsew",  # セルをフレームいっぱいに広げる
                    ipady=6,
                )
                # 入力バリデーション（1〜9 の一文字のみ許可）
                entry.bind("<KeyRelease>", lambda e, r=row, c=col: self._validate_input(r, c))
                # Tab キーでセル移動
                entry.bind("<Tab>", lambda e, r=row, c=col: self._move_focus(r, c, 1))
                entry.bind("<Shift-Tab>", lambda e, r=row, c=col: self._move_focus(r, c, -1))

                row_vars.append(var)
                row_entries.append(entry)

            self.cells.append(row_vars)
            self.entries.append(row_entries)

        # --- ボタンエリア
        btn_frame = tk.Frame(self.root, bg=BG_MAIN, pady=16)
        btn_frame.grid(row=2, column=0)

        self._make_button(btn_frame, "⚡ 即時に解く",   BG_BTN_SOLVE, self.solve_instant, 0)
        self._make_button(btn_frame, "🎬 アニメーション", BG_BTN_ANIM, self.solve_animated, 1)
        self._make_button(btn_frame, "🗑 クリア",        BG_BTN_CLEAR, self.clear_board,   2)

        # --- フッター（操作ヒント）
        hint = tk.Label(
            self.root,
            text="数字（1〜9）を入力して「解く」ボタンを押してください。空欄 = 0 または空白",
            font=("Segoe UI", 9),
            bg=BG_MAIN,
            fg="#6c7086",
            pady=8,
        )
        hint.grid(row=3, column=0)

    def _make_button(self, parent, text: str, bg: str, command, col: int):
        """統一スタイルのボタンを生成する。"""
        btn = tk.Button(
            parent,
            text=text,
            font=FONT_BTN,
            bg=bg,
            fg=FG_BTN,
            activebackground=bg,
            activeforeground=FG_BTN,
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=command,
        )
        btn.grid(row=0, column=col, padx=10)
        # ホバーエフェクト
        btn.bind("<Enter>", lambda e, b=btn, c=bg: b.config(bg=self._lighten(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))

    # ===== 入力ユーティリティ =========================================

    def _validate_input(self, row: int, col: int):
        """1〜9 以外の文字が入力されたらクリアする。"""
        val = self.cells[row][col].get()
        if val not in ("", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            self.cells[row][col].set("")
        # 入力後もフォントをユーザー色に保つ
        self.entries[row][col].config(fg=FG_FIXED)

    def _move_focus(self, row: int, col: int, direction: int):
        """Tab/Shift-Tab でセルを移動する。"""
        idx = row * 9 + col + direction
        idx = max(0, min(80, idx))
        r, c = divmod(idx, 9)
        self.entries[r][c].focus_set()

    def _get_board(self) -> list[list[int]] | None:
        """
        GUI から 9x9 の盤面を読み取り整数リストで返す。
        無効な値がある場合は None を返す。
        """
        board = []
        for row in range(9):
            row_data = []
            for col in range(9):
                val = self.cells[row][col].get().strip()
                if val == "" or val == "0":
                    row_data.append(0)
                elif val.isdigit() and 1 <= int(val) <= 9:
                    row_data.append(int(val))
                else:
                    messagebox.showerror(
                        "入力エラー",
                        f"行{row+1}・列{col+1} の値が不正です：「{val}」\n1〜9 の数字のみ入力できます。"
                    )
                    return None
            board.append(row_data)
        return board

    def _set_board(self, board: list[list[int]], original: list[list[int]]):
        """解いた盤面を GUI に書き込む（ソルバーが埋めたセルを色分け）。"""
        for row in range(9):
            for col in range(9):
                val = board[row][col]
                is_solver_filled = (original[row][col] == 0)
                self.cells[row][col].set(str(val) if val != 0 else "")
                color = FG_SOLVED if is_solver_filled else FG_FIXED
                self.entries[row][col].config(fg=color)

    # ===== ボタンアクション ==========================================

    def solve_instant(self):
        """即時に解いて結果を表示する。"""
        board = self._get_board()
        if board is None:
            return  # 入力エラー時は中断

        original = [row[:] for row in board]  # 初期盤面を保存
        solver = SudokuSolver(board)

        if solver.solve():
            self._set_board(solver.board, original)
            messagebox.showinfo("完了", "✅ 解が見つかりました！")
        else:
            messagebox.showerror("解なし", "❌ この問題には解がありません。\n入力を確認してください。")

    def solve_animated(self):
        """バックトラッキングの過程をアニメーションで見せながら解く。"""
        board = self._get_board()
        if board is None:
            return

        original = [row[:] for row in board]  # 初期盤面を保存

        # アニメーション用の再帰関数（GUI を直接操作する）
        def animate(b: list[list[int]]) -> bool:
            for row in range(9):
                for col in range(9):
                    if b[row][col] == 0:  # 空マスを発見
                        for num in range(1, 10):
                            if SudokuSolver(b).is_valid(row, col, num):
                                b[row][col] = num
                                # --- GUI をリアルタイム更新
                                self.cells[row][col].set(str(num))
                                self.entries[row][col].config(fg=FG_ANIM)
                                self.root.update()
                                time.sleep(self.anim_delay)

                                if animate(b):
                                    return True

                                # バックトラック → セルをクリア
                                b[row][col] = 0
                                self.cells[row][col].set("")
                                self.entries[row][col].config(fg=FG_ERROR)
                                self.root.update()
                                time.sleep(self.anim_delay * 0.5)
                                self.entries[row][col].config(fg=FG_FIXED)
                        return False
            return True

        if animate(board):
            # アニメーション完了 → 色を正式に設定
            self._set_board(board, original)
            messagebox.showinfo("完了", "✅ 解が見つかりました！")
        else:
            messagebox.showerror("解なし", "❌ この問題には解がありません。\n入力を確認してください。")

    def clear_board(self):
        """全セルをクリアし、初期状態に戻す。"""
        for row in range(9):
            for col in range(9):
                self.cells[row][col].set("")
                self.entries[row][col].config(fg=FG_FIXED)

    # ===== ユーティリティ ============================================

    @staticmethod
    def _lighten(hex_color: str) -> str:
        """
        16 進数カラー文字列を少し明るくする。
        ボタンホバーエフェクト用。
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"


# ===== エントリーポイント =============================================

def main():
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
