import pygame
import socket
import json
import sys
import time

# 服务器配置
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9527

# 棋盘配置
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 30
WINDOW_SIZE = MARGIN * 2 + CELL_SIZE * (BOARD_SIZE - 1)

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (210, 180, 140)
LINE_COLOR = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class GobanClient:
    def __init__(self):
        pygame.init()
        # 增大窗口高度，显示更多信息
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 120))
        pygame.display.set_caption("五子棋 - 联机版")
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)
        self.big_font = pygame.font.Font(None, 48)
        self.clock = pygame.time.Clock()
        
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.my_color = 0      # 1=黑, 2=白
        self.my_turn = False
        self.room_id = 0
        self.game_over = False
        self.winner = 0        # 0=未结束, 1=黑胜, 2=白胜
        self.win_reason = ""   # 赢家描述
        self.fd = None
        self.last_move = None
        self.status_msg = "连接中..."
        self.connected = False
        
        self.connect_to_server()
        
    def connect_to_server(self):
        try:
            self.fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.fd.connect((SERVER_IP, SERVER_PORT))
            print("连接服务器成功")
            self.status_msg = "已连接，匹配中..."
            
            msg = {"cmd": "match", "score": 1500}
            self.fd.send((json.dumps(msg) + "\n").encode())
            
            data = self.fd.recv(1024).decode()
            print("服务器响应:", data)
            resp = json.loads(data)
            
            if resp.get("cmd") == "match_success":
                self.room_id = resp.get("room_id", 0)
                color = resp.get("color", "black")
                self.my_color = 1 if color == "black" else 2
                self.my_turn = (self.my_color == 1)
                self.connected = True
                self.status_msg = f"房间 {self.room_id}，你是{'黑棋' if self.my_color == 1 else '白棋'}"
                print(f"配对成功！房间号: {self.room_id}，你是{'黑棋' if self.my_color == 1 else '白棋'}")
            else:
                self.status_msg = "匹配失败: " + resp.get("reason", "未知")
                
        except Exception as e:
            print(f"连接错误: {e}")
            self.status_msg = f"连接失败: {e}"
            self.fd = None
    
    def draw_board(self):
        self.screen.fill(BG_COLOR)
        
        # 画网格
        for i in range(BOARD_SIZE):
            start = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (MARGIN, start), (MARGIN + (BOARD_SIZE-1)*CELL_SIZE, start), 1)
            pygame.draw.line(self.screen, LINE_COLOR,
                           (start, MARGIN), (start, MARGIN + (BOARD_SIZE-1)*CELL_SIZE), 1)
        
        # 星位
        star_points = [(7,7), (3,3), (11,3), (3,11), (11,11)]
        for r, c in star_points:
            x = MARGIN + c * CELL_SIZE
            y = MARGIN + r * CELL_SIZE
            pygame.draw.circle(self.screen, BLACK, (x, y), 5)
        
        # 棋子
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 1:
                    x = MARGIN + c * CELL_SIZE
                    y = MARGIN + r * CELL_SIZE
                    pygame.draw.circle(self.screen, BLACK, (x, y), CELL_SIZE // 2 - 3)
                elif self.board[r][c] == 2:
                    x = MARGIN + c * CELL_SIZE
                    y = MARGIN + r * CELL_SIZE
                    pygame.draw.circle(self.screen, WHITE, (x, y), CELL_SIZE // 2 - 3)
                    pygame.draw.circle(self.screen, BLACK, (x, y), CELL_SIZE // 2 - 3, 1)
        
        # 最后落子标记
        if self.last_move:
            r, c = self.last_move
            x = MARGIN + c * CELL_SIZE
            y = MARGIN + r * CELL_SIZE
            pygame.draw.circle(self.screen, RED, (x, y), 6, 2)
        
        # ---- 底部信息栏 ----
        y_base = WINDOW_SIZE + 10
        
        # 房间号
        text = self.font.render(f"房间: {self.room_id}", True, BLACK)
        self.screen.blit(text, (10, y_base))
        
        # 状态信息
        if self.game_over:
            if self.winner == 1:
                winner_text = "黑棋胜利！"
                color = BLACK
            elif self.winner == 2:
                winner_text = "白棋胜利！"
                color = WHITE
            else:
                winner_text = "游戏结束"
                color = BLACK
            
            # 大号胜利信息
            big_text = self.big_font.render("🏆 " + winner_text, True, RED)
            self.screen.blit(big_text, (WINDOW_SIZE // 2 - 100, y_base - 10))
            
            # 提示重置
            reset_text = self.small_font.render("按 R 键重新开局（需重新匹配）", True, BLUE)
            self.screen.blit(reset_text, (10, y_base + 50))
            
        elif self.my_turn and self.connected:
            text = self.font.render("👉 轮到你了", True, GREEN)
            self.screen.blit(text, (200, y_base))
        elif self.connected:
            text = self.font.render("⏳ 等待对手走棋...", True, BLACK)
            self.screen.blit(text, (200, y_base))
        else:
            text = self.small_font.render(self.status_msg, True, RED)
            self.screen.blit(text, (200, y_base))
        
        # 显示你的颜色
        color_text = "● 你: " + ("黑棋" if self.my_color == 1 else "白棋")
        color_color = BLACK if self.my_color == 1 else WHITE
        text = self.small_font.render(color_text, True, color_color)
        self.screen.blit(text, (10, y_base + 35))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        if self.game_over or not self.my_turn or not self.connected or self.fd is None:
            return
        
        x, y = pos
        if x < MARGIN - CELL_SIZE//2 or x > MARGIN + (BOARD_SIZE-1)*CELL_SIZE + CELL_SIZE//2:
            return
        if y < MARGIN - CELL_SIZE//2 or y > MARGIN + (BOARD_SIZE-1)*CELL_SIZE + CELL_SIZE//2:
            return
        
        col = round((x - MARGIN) / CELL_SIZE)
        row = round((y - MARGIN) / CELL_SIZE)
        
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            return
        if self.board[row][col] != 0:
            return
        
        print(f"点击: row={row}, col={col}")
        msg = {"cmd": "move", "row": row, "col": col}
        try:
            self.fd.send((json.dumps(msg) + "\n").encode())
            self.my_turn = False
            self.status_msg = "等待服务器确认..."
        except Exception as e:
            print(f"发送落子错误: {e}")
            self.my_turn = True
    
    def handle_server_message(self, line):
        try:
            resp = json.loads(line)
            cmd = resp.get("cmd")
            
            if cmd == "move_ok":
                row = resp["row"]
                col = resp["col"]
                player = resp["player"]
                self.board[row][col] = player
                self.last_move = (row, col)
                self.my_turn = False
                self.status_msg = "等待对手走棋..."
                
            elif cmd == "opponent_move":
                row = resp["row"]
                col = resp["col"]
                player = resp["player"]
                self.board[row][col] = player
                self.last_move = (row, col)
                self.my_turn = True
                self.status_msg = "轮到你了"
                
            elif cmd == "game_over":
                winner = resp["winner"]
                row = resp.get("row", 0)
                col = resp.get("col", 0)
                self.game_over = True
                self.winner = 1 if winner == "black" else 2
                self.last_move = (row, col)
                self.status_msg = f"游戏结束，{'黑棋' if self.winner == 1 else '白棋'}胜!"
                print(f"🎉 游戏结束，胜者: {'黑棋' if self.winner == 1 else '白棋'}")
                
            elif cmd == "error":
                err_msg = resp.get("msg", "")
                if "还没轮到你" in err_msg:
                    self.my_turn = False
                elif "游戏已结束" in err_msg:
                    self.game_over = True
                elif "位置无效" in err_msg:
                    self.my_turn = True
                print(f"服务器错误: {err_msg}")
                
            elif cmd == "opponent_quit":
                self.game_over = True
                self.winner = self.my_color  # 对手退出，你获胜
                self.status_msg = "对手已断开，你获胜!"
                print("对手断开连接")
                
        except json.JSONDecodeError:
            pass
    
    def receive_messages(self):
        if self.fd is None:
            return
        
        try:
            self.fd.setblocking(False)
            data = self.fd.recv(4096).decode()
            if data:
                lines = data.strip().split('\n')
                for line in lines:
                    if line.strip():
                        self.handle_server_message(line.strip())
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"接收错误: {e}")
            self.fd = None
            self.connected = False
            self.status_msg = "连接断开"
        finally:
            self.fd.setblocking(True)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # 重置游戏状态（只清空棋盘，不重新连接）
                        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
                        self.game_over = False
                        self.winner = 0
                        self.last_move = None
                        self.my_turn = (self.my_color == 1)
                        self.status_msg = "已重置，等待走棋..."
                        print("游戏已重置")
            
            self.receive_messages()
            self.draw_board()
            self.clock.tick(60)
        
        if self.fd:
            self.fd.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    client = GobanClient()
    client.run()
