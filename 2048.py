import random
import numpy as np
import curses
from itertools import chain


# 定义游戏类
class Game(object):
    # 初始化棋盘格式和分数
    def __init__(self, width=4, height=4):
        self.width = width
        self.height = height
        self.field = [[0 for j in range(width)] for i in range(height)]
        self.score = 0
        with open('max_score.txt', 'r') as f:
            max_score = f.read()
            if max_score:
                self.max_score = int(max_score)
            else:
                self.max_score = 0

    # 创建棋盘界面
    def create_field(self, stdstr):
        stdstr.clear()
        stdstr.addstr('历史最高分：%s\n' % (self.max_score))
        stdstr.addstr('当前得分：%s\n' % (self.score))
        for j in range(self.height):
            # +----+----+----+----+

            stdstr.addstr('+-----' * self.width + '+\n')
            [stdstr.addstr('|{0:5}'.format(' ')) if cell == 0 else stdstr.addstr('|{0:5}'.format(str(cell))) for cell in
             self.field[j]]
            stdstr.addstr('|\n')

        stdstr.addstr('+-----' * self.height + '+\n')
        stdstr.addstr('q:退出\n')
        stdstr.addstr('r:重置\n')

    # 初始化棋盘点数
    def init(self):
        rands = [2, 2, 2, 2, 4]
        row_index = random.randint(0, 3)
        col_index = random.randint(0, 3)
        if self.field[row_index][col_index] == 0:
            self.field[row_index][col_index] = random.choices(rands)[0]
        else:
            self.init()

    # 初始化棋盘
    def init_field(self, stdstr):
        self.init()
        self.init()
        self.create_field(stdstr)

    # 判断棋盘能否移动方向

    @staticmethod
    def is_row_move(row):
        for i in range(len(row) - 1):
            if (row[i] != 0 and row[i] == row[i + 1]) or (row[i] == 0 and row[i + 1] != 0):
                return True
        else:
            return False

    @staticmethod
    def is_move_left(field):
        for row in field:
            if Game.is_row_move(row):
                return True
        else:
            return False

    @staticmethod
    def is_move_right(field):
        field = [row[::-1] for row in field]
        return Game.is_move_left(field)

    @staticmethod
    def is_move_up(field):
        field = np.array(field).T
        return Game.is_move_left(list(field))

    @staticmethod
    def is_move_down(field):
        field = np.array(field).T
        return Game.is_move_right(list(field))

    # 实现棋盘移动方向
    def row_left(self, row):
        while Game.is_row_move(row):
            row = sorted(row, key=lambda x: 1 if x == 0 else 0)
            for i in range(len(row) - 1):
                if row[i] == row[i + 1]:
                    row[i] = row[i] * 2
                    row[i + 1] = 0
                    self.score += row[i]
        return row

    def move_left(self):

        field = []
        for row in self.field:
            field.append(self.row_left(row))
        self.field = field

    def move_right(self):

        self.field = [row[::-1] for row in self.field]
        self.move_left()
        self.field = [row[::-1] for row in self.field]

    def move_up(self):

        self.field = list(np.array(self.field).T)
        self.move_left()
        self.field = list(np.array(self.field).T)

    def move_down(self):

        self.field = list(np.array(self.field).T)
        self.move_right()
        self.field = list(np.array(self.field).T)

    # 判断游戏是否结束
    def is_over(self, stdstr):

        if not any([self.is_move_up(self.field),
                    self.is_move_down(self.field),
                    self.is_move_right(self.field),
                    self.is_move_left(self.field)]):

            if sorted(chain(*self.field), reverse=True)[0] >= 2048:
                stdstr.addstr('is win...\n')
            else:
                stdstr.addstr('is over...\n')
            if self.score > self.max_score:
                self.max_score = self.score
            return 1

        return 0

    def restart(self):
        self.field = [[0 for j in range(self.height)] for i in range(self.width)]
        self.score = 0
        return True


# 定义主函数
def main(stdstr):
    # 实例化2048游戏类对象
    game = Game()
    # 设置重置键
    reset_flag = False
    # 设置游戏结束标志位
    over_flag = False
    # 初始化棋盘界面
    game.init_field(stdstr)

    while True:
        # 游戏结束判断
        over_flag = game.is_over(stdstr)
        # 游戏结束，用户相关操作
        if over_flag == 1:
            stdstr.addstr('q:退出/r:重置\n')
            while True:
                choice = stdstr.getch()
                if choice == ord('q'):
                    with open('max_score.txt', 'w') as f:
                        f.write(str(game.max_score))
                    exit(0)
                elif choice == ord('r'):
                    reset_flag = game.restart()
                    break
                else:
                    continue

        # 游戏中，用户相关操作
        else:
            choice = stdstr.getch()
            if choice == curses.KEY_UP:
                if game.is_move_up(game.field):
                    game.move_up()
                else:
                    continue
            elif choice == curses.KEY_LEFT:
                if game.is_move_left(game.field):
                    game.move_left()
                else:
                    continue
            elif choice == curses.KEY_DOWN:
                if game.is_move_down(game.field):
                    game.move_down()
                else:
                    continue
            elif choice == curses.KEY_RIGHT:
                if game.is_move_right(game.field):
                    game.move_right()
                else:
                    continue
            elif choice == ord('q'):
                with open('max_score.txt', 'w') as f:
                    f.write(str(game.max_score))
                exit(0)
            elif choice == ord('r'):
                reset_flag = game.restart()
            else:
                continue

        # 重置游戏棋盘
        if reset_flag:
            reset_flag = False
            game.init_field(stdstr)

        # 游戏中
        if over_flag == 0:
            game.init()
            game.create_field(stdstr)


if __name__ == '__main__':
    # 装饰主函数，实现键盘输入转换ASKII码值
    curses.wrapper(main)
   