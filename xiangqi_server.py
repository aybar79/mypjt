#!/usr/bin/env python3
"""
中国象棋游戏服务器
提供Web界面和AI计算支持
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import random
import copy

app = Flask(__name__)
CORS(app)

class XiangqiAI:
    """象棋AI类"""
    
    def __init__(self):
        # 棋子价值表
        self.piece_values = {
            '帥': 1000, '将': 1000,
            '仕': 20, '士': 20,
            '相': 20, '象': 20,
            '馬': 40, '马': 40,
            '車': 90, '车': 90,
            '炮': 45, '砲': 45,
            '兵': 10, '卒': 10
        }
        
        # 位置价值表（简化版）
        self.position_values = {
            '兵': [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 2, 2, 3, 2, 2, 1, 1],
                [2, 2, 3, 3, 4, 3, 3, 2, 2],
                [3, 3, 4, 4, 5, 4, 4, 3, 3],
                [4, 4, 5, 5, 6, 5, 5, 4, 4],
                [5, 5, 6, 6, 7, 6, 6, 5, 5],
                [6, 6, 7, 7, 8, 7, 7, 6, 6]
            ]
        }

    def is_red_piece(self, piece):
        """判断是否为红方棋子"""
        red_pieces = ['車', '馬', '相', '仕', '帥', '炮', '兵']
        return piece in red_pieces

    def get_all_moves(self, board, is_red_turn):
        """获取当前玩家的所有合法移动"""
        moves = []
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece and ((is_red_turn and self.is_red_piece(piece)) or 
                             (not is_red_turn and not self.is_red_piece(piece))):
                    piece_moves = self.get_piece_moves(board, piece, row, col)
                    for move in piece_moves:
                        if self.is_valid_move(board, row, col, move[0], move[1]):
                            moves.append({
                                'from': [row, col],
                                'to': move,
                                'piece': piece
                            })
        
        return moves

    def get_piece_moves(self, board, piece, row, col):
        """获取指定棋子的可能移动"""
        moves = []
        
        if piece in ['帥', '将']:
            moves.extend(self.get_general_moves(board, row, col))
        elif piece in ['仕', '士']:
            moves.extend(self.get_advisor_moves(board, row, col))
        elif piece in ['相', '象']:
            moves.extend(self.get_elephant_moves(board, row, col))
        elif piece in ['馬', '马']:
            moves.extend(self.get_horse_moves(board, row, col))
        elif piece in ['車', '车']:
            moves.extend(self.get_chariot_moves(board, row, col))
        elif piece in ['炮', '砲']:
            moves.extend(self.get_cannon_moves(board, row, col))
        elif piece in ['兵', '卒']:
            moves.extend(self.get_soldier_moves(board, row, col))
        
        return moves

    def get_general_moves(self, board, row, col):
        """帅/将的移动"""
        moves = []
        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        is_red = self.is_red_piece(board[row][col])
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.in_palace(new_row, new_col, is_red):
                moves.append([new_row, new_col])
        
        return moves

    def get_advisor_moves(self, board, row, col):
        """仕/士的移动"""
        moves = []
        directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        is_red = self.is_red_piece(board[row][col])
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.in_palace(new_row, new_col, is_red):
                moves.append([new_row, new_col])
        
        return moves

    def get_elephant_moves(self, board, row, col):
        """相/象的移动"""
        moves = []
        directions = [[-2, -2], [-2, 2], [2, -2], [2, 2]]
        is_red = self.is_red_piece(board[row][col])
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # 检查边界和过河限制
            if new_row < 0 or new_row >= 10 or new_col < 0 or new_col >= 9:
                continue
            if (is_red and new_row < 5) or (not is_red and new_row > 4):
                continue
            
            # 检查象眼
            block_row, block_col = row + dr // 2, col + dc // 2
            if board[block_row][block_col] is None:
                moves.append([new_row, new_col])
        
        return moves

    def get_horse_moves(self, board, row, col):
        """马的移动"""
        moves = []
        horse_moves = [
            [-2, -1], [-2, 1], [-1, -2], [-1, 2],
            [1, -2], [1, 2], [2, -1], [2, 1]
        ]
        leg_blocks = [
            [-1, 0], [-1, 0], [0, -1], [0, 1],
            [0, -1], [0, 1], [1, 0], [1, 0]
        ]
        
        for i, (dr, dc) in enumerate(horse_moves):
            new_row, new_col = row + dr, col + dc
            
            if new_row < 0 or new_row >= 10 or new_col < 0 or new_col >= 9:
                continue
            
            # 检查马腿
            block_r, block_c = leg_blocks[i]
            if board[row + block_r][col + block_c] is None:
                moves.append([new_row, new_col])
        
        return moves

    def get_chariot_moves(self, board, row, col):
        """车的移动"""
        moves = []
        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        
        for dr, dc in directions:
            for i in range(1, 10):
                new_row, new_col = row + dr * i, col + dc * i
                
                if new_row < 0 or new_row >= 10 or new_col < 0 or new_col >= 9:
                    break
                
                if board[new_row][new_col] is None:
                    moves.append([new_row, new_col])
                else:
                    moves.append([new_row, new_col])  # 可以吃子
                    break
        
        return moves

    def get_cannon_moves(self, board, row, col):
        """炮的移动"""
        moves = []
        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        
        for dr, dc in directions:
            found_piece = False
            
            for i in range(1, 10):
                new_row, new_col = row + dr * i, col + dc * i
                
                if new_row < 0 or new_row >= 10 or new_col < 0 or new_col >= 9:
                    break
                
                if board[new_row][new_col] is None:
                    if not found_piece:
                        moves.append([new_row, new_col])
                else:
                    if not found_piece:
                        found_piece = True
                    else:
                        moves.append([new_row, new_col])  # 可以炮打
                        break
        
        return moves

    def get_soldier_moves(self, board, row, col):
        """兵/卒的移动"""
        moves = []
        is_red = self.is_red_piece(board[row][col])
        
        if is_red:
            # 红兵向上
            if row > 0:
                moves.append([row - 1, col])
            # 过河后可以左右
            if row < 5:
                if col > 0:
                    moves.append([row, col - 1])
                if col < 8:
                    moves.append([row, col + 1])
        else:
            # 黑卒向下
            if row < 9:
                moves.append([row + 1, col])
            # 过河后可以左右
            if row > 4:
                if col > 0:
                    moves.append([row, col - 1])
                if col < 8:
                    moves.append([row, col + 1])
        
        return moves

    def in_palace(self, row, col, is_red):
        """判断是否在九宫格内"""
        if col < 3 or col > 5:
            return False
        
        if is_red:
            return 7 <= row <= 9
        else:
            return 0 <= row <= 2

    def is_valid_move(self, board, from_row, from_col, to_row, to_col):
        """检查移动是否合法"""
        if to_row < 0 or to_row >= 10 or to_col < 0 or to_col >= 9:
            return False
        
        target_piece = board[to_row][to_col]
        current_piece = board[from_row][from_col]
        
        if target_piece:
            # 不能吃自己的棋子
            if (self.is_red_piece(current_piece) and self.is_red_piece(target_piece)) or \
               (not self.is_red_piece(current_piece) and not self.is_red_piece(target_piece)):
                return False
        
        return True

    def evaluate_board(self, board, is_red_perspective=False):
        """评估棋盘分数"""
        score = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece:
                    piece_value = self.piece_values.get(piece, 0)
                    
                    # 位置价值
                    if piece in ['兵', '卒']:
                        if piece == '兵':
                            piece_value += self.position_values['兵'][row][col]
                        else:
                            piece_value += self.position_values['兵'][9-row][col]
                    
                    if self.is_red_piece(piece):
                        score += piece_value
                    else:
                        score -= piece_value
        
        return score if is_red_perspective else -score

    def make_move(self, board, from_pos, to_pos):
        """执行移动并返回新棋盘"""
        new_board = copy.deepcopy(board)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = new_board[from_row][from_col]
        new_board[to_row][to_col] = piece
        new_board[from_row][from_col] = None
        
        return new_board

    def minimax(self, board, depth, is_maximizing, alpha=-float('inf'), beta=float('inf')):
        """极小极大算法与α-β剪枝"""
        if depth == 0:
            return self.evaluate_board(board, not is_maximizing)
        
        moves = self.get_all_moves(board, not is_maximizing)
        
        if not moves:
            return self.evaluate_board(board, not is_maximizing)
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in moves:
                new_board = self.make_move(board, move['from'], move['to'])
                eval_score = self.minimax(new_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = self.make_move(board, move['from'], move['to'])
                eval_score = self.minimax(new_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board, difficulty='medium'):
        """根据难度获取最佳移动"""
        moves = self.get_all_moves(board, False)  # AI是黑方
        
        if not moves:
            return None
        
        if difficulty == 'easy':
            # 简单：随机选择
            return random.choice(moves)
        
        elif difficulty == 'medium':
            # 中等：优先吃子，简单评估
            capture_moves = []
            good_moves = []
            
            for move in moves:
                target_piece = board[move['to'][0]][move['to'][1]]
                if target_piece:
                    capture_moves.append(move)
                else:
                    good_moves.append(move)
            
            if capture_moves:
                # 按照被吃棋子价值排序
                capture_moves.sort(key=lambda m: self.piece_values.get(
                    board[m['to'][0]][m['to'][1]], 0), reverse=True)
                return capture_moves[0]
            
            return random.choice(good_moves) if good_moves else random.choice(moves)
        
        elif difficulty == 'hard':
            # 困难：使用极小极大算法
            best_move = None
            best_score = float('inf')
            
            for move in moves:
                new_board = self.make_move(board, move['from'], move['to'])
                score = self.minimax(new_board, 3, True)  # 搜索深度3
                
                if score < best_score:
                    best_score = score
                    best_move = move
            
            return best_move if best_move else random.choice(moves)
        
        return random.choice(moves)

# 创建AI实例
xiangqi_ai = XiangqiAI()

@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'xiangqi.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('static', filename)

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """AI移动接口"""
    try:
        data = request.get_json()
        board = data.get('board', [])
        difficulty = data.get('difficulty', 'medium')
        
        # 获取AI最佳移动
        best_move = xiangqi_ai.get_best_move(board, difficulty)
        
        if best_move:
            return jsonify({
                'success': True,
                'move': {
                    'from': best_move['from'],
                    'to': best_move['to'],
                    'piece': best_move['piece']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No valid moves available'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hint', methods=['POST'])
def get_hint():
    """获取提示接口"""
    try:
        data = request.get_json()
        board = data.get('board', [])
        is_red_turn = data.get('is_red_turn', True)
        
        # 获取当前玩家的最佳移动
        moves = xiangqi_ai.get_all_moves(board, is_red_turn)
        
        if not moves:
            return jsonify({
                'success': False,
                'error': 'No valid moves available'
            })
        
        # 简单评估找出较好的移动
        best_move = None
        best_score = -float('inf') if is_red_turn else float('inf')
        
        for move in moves:
            new_board = xiangqi_ai.make_move(board, move['from'], move['to'])
            score = xiangqi_ai.evaluate_board(new_board, is_red_turn)
            
            if (is_red_turn and score > best_score) or (not is_red_turn and score < best_score):
                best_score = score
                best_move = move
        
        if best_move:
            return jsonify({
                'success': True,
                'hint': {
                    'from': best_move['from'],
                    'to': best_move['to'],
                    'piece': best_move['piece']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No good moves found'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate_position():
    """评估局面接口"""
    try:
        data = request.get_json()
        board = data.get('board', [])
        
        score = xiangqi_ai.evaluate_board(board, True)
        
        return jsonify({
            'success': True,
            'evaluation': {
                'score': score,
                'advantage': 'red' if score > 0 else 'black' if score < 0 else 'equal'
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Xiangqi Game Server',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🎮 中国象棋游戏服务器启动中...")
    print("✅ AI引擎初始化完成")
    print(f"🌐 服务器运行在 http://localhost:5000")
    print("💡 提示：使用 Ctrl+C 停止服务器")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
