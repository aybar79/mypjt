/**
 * 中国象棋游戏 JavaScript 实现
 * 功能：双人对局 + 人机对局（三个难度等级）
 */

class XiangqiGame {
    constructor() {
        this.board = this.initializeBoard();
        this.currentPlayer = 'red'; // 'red' or 'black'
        this.selectedPiece = null;
        this.gameMode = 'pvp'; // 'pvp' or 'ai'
        this.aiDifficulty = 'easy'; // 'easy', 'medium', 'hard'
        this.moveHistory = [];
        this.gameStatus = 'playing'; // 'playing', 'checkmate', 'stalemate'
        this.moveCount = 0;
        
        this.initializeUI();
        this.setupEventListeners();
        this.renderBoard();
    }

    // 初始化棋盘状态
    initializeBoard() {
        const board = Array(10).fill(null).map(() => Array(9).fill(null));
        
        // 红方棋子 (底部)
        board[9] = ['車', '馬', '相', '仕', '帥', '仕', '相', '馬', '車'];
        board[7] = [null, '炮', null, null, null, null, null, '炮', null];
        board[6] = ['兵', null, '兵', null, '兵', null, '兵', null, '兵'];
        
        // 黑方棋子 (顶部)
        board[0] = ['车', '马', '象', '士', '将', '士', '象', '马', '车'];
        board[2] = [null, '砲', null, null, null, null, null, '砲', null];
        board[3] = ['卒', null, '卒', null, '卒', null, '卒', null, '卒'];
        
        return board;
    }

    // 初始化UI
    initializeUI() {
        this.boardElement = document.getElementById('xiangqiBoard');
        this.currentPlayerElement = document.getElementById('currentPlayer');
        this.gameStatusElement = document.getElementById('gameStatus');
        this.moveCountElement = document.getElementById('moveCount');
        this.moveHistoryElement = document.getElementById('moveHistory');
        
        this.updateUI();
    }

    // 设置事件监听器
    setupEventListeners() {
        // 游戏模式切换
        document.querySelectorAll('input[name="gameMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.gameMode = e.target.value;
                const difficultySection = document.getElementById('difficultySection');
                difficultySection.style.display = e.target.value === 'ai' ? 'block' : 'none';
                this.newGame();
            });
        });

        // AI难度选择
        document.getElementById('aiDifficulty').addEventListener('change', (e) => {
            this.aiDifficulty = e.target.value;
        });

        // 游戏控制按钮
        document.getElementById('newGameBtn').addEventListener('click', () => this.newGame());
        document.getElementById('undoBtn').addEventListener('click', () => this.undoMove());
        document.getElementById('hintBtn').addEventListener('click', () => this.showHint());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetGame());
        document.getElementById('playAgainBtn').addEventListener('click', () => {
            this.newGame();
            bootstrap.Modal.getInstance(document.getElementById('gameOverModal')).hide();
        });
    }

    // 渲染棋盘
    renderBoard() {
        // 清除现有棋子
        const existingPieces = this.boardElement.querySelectorAll('.piece');
        existingPieces.forEach(piece => piece.remove());

        // 清除可能的移动标记
        const possibleMoves = this.boardElement.querySelectorAll('.possible-move');
        possibleMoves.forEach(move => move.remove());

        // 渲染所有棋子
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece) {
                    this.createPieceElement(piece, row, col);
                }
            }
        }
    }

    // 创建棋子元素
    createPieceElement(piece, row, col) {
        const pieceElement = document.createElement('div');
        pieceElement.className = 'piece';
        pieceElement.textContent = piece;
        
        // 确定棋子颜色
        const isRed = this.isRedPiece(piece);
        pieceElement.classList.add(isRed ? 'red' : 'black');
        
        // 设置位置
        const x = 30 + col * 60 - 25; // 居中对齐到交叉点
        const y = 30 + row * 60 - 25;
        pieceElement.style.left = x + 'px';
        pieceElement.style.top = y + 'px';
        
        // 添加数据属性
        pieceElement.dataset.row = row;
        pieceElement.dataset.col = col;
        pieceElement.dataset.piece = piece;
        
        // 添加点击事件
        pieceElement.addEventListener('click', (e) => this.handlePieceClick(e));
        
        this.boardElement.appendChild(pieceElement);
    }

    // 判断是否为红方棋子
    isRedPiece(piece) {
        const redPieces = ['車', '馬', '相', '仕', '帥', '炮', '兵'];
        return redPieces.includes(piece);
    }

    // 判断棋子是否属于当前玩家
    isPieceOwnedByCurrentPlayer(piece) {
        const isRed = this.isRedPiece(piece);
        return (this.currentPlayer === 'red' && isRed) || (this.currentPlayer === 'black' && !isRed);
    }

    // 处理棋子点击
    handlePieceClick(event) {
        if (this.gameStatus !== 'playing') return;
        
        const clickedElement = event.target;
        const row = parseInt(clickedElement.dataset.row);
        const col = parseInt(clickedElement.dataset.col);
        const piece = clickedElement.dataset.piece;

        // 如果点击的是当前玩家的棋子
        if (this.isPieceOwnedByCurrentPlayer(piece)) {
            this.selectPiece(clickedElement, row, col);
        } else if (this.selectedPiece) {
            // 如果已选择棋子，尝试攻击
            this.attemptMove(this.selectedPiece.row, this.selectedPiece.col, row, col);
        }
    }

    // 选择棋子
    selectPiece(element, row, col) {
        // 清除之前的选择
        const previousSelected = this.boardElement.querySelector('.piece.selected');
        if (previousSelected) {
            previousSelected.classList.remove('selected');
        }

        // 清除可能的移动标记
        const possibleMoves = this.boardElement.querySelectorAll('.possible-move');
        possibleMoves.forEach(move => move.remove());

        // 选择新棋子
        element.classList.add('selected');
        this.selectedPiece = { element, row, col, piece: element.dataset.piece };

        // 显示可能的移动
        this.showPossibleMoves(row, col);

        // 添加棋盘点击事件来处理移动到空位
        this.addBoardClickListener();
    }

    // 添加棋盘点击监听器
    addBoardClickListener() {
        // 移除现有监听器
        this.removeBoardClickListener();

        this.boardClickHandler = (event) => {
            if (event.target.classList.contains('piece') || 
                event.target.classList.contains('possible-move')) {
                return;
            }

            // 计算点击位置对应的棋盘坐标
            const rect = this.boardElement.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            const col = Math.round((x - 30) / 60);
            const row = Math.round((y - 30) / 60);

            if (row >= 0 && row < 10 && col >= 0 && col < 9 && this.selectedPiece) {
                this.attemptMove(this.selectedPiece.row, this.selectedPiece.col, row, col);
            }
        };

        this.boardElement.addEventListener('click', this.boardClickHandler);
    }

    // 移除棋盘点击监听器
    removeBoardClickListener() {
        if (this.boardClickHandler) {
            this.boardElement.removeEventListener('click', this.boardClickHandler);
            this.boardClickHandler = null;
        }
    }

    // 显示可能的移动
    showPossibleMoves(row, col) {
        const piece = this.board[row][col];
        const possibleMoves = this.getPossibleMoves(piece, row, col);

        possibleMoves.forEach(move => {
            const [moveRow, moveCol] = move;
            const moveElement = document.createElement('div');
            moveElement.className = 'possible-move';
            
            const x = 30 + moveCol * 60 - 10;
            const y = 30 + moveRow * 60 - 10;
            moveElement.style.left = x + 'px';
            moveElement.style.top = y + 'px';
            
            moveElement.addEventListener('click', () => {
                this.attemptMove(row, col, moveRow, moveCol);
            });
            
            this.boardElement.appendChild(moveElement);
        });
    }

    // 获取棋子可能的移动
    getPossibleMoves(piece, row, col) {
        const moves = [];
        
        switch (piece) {
            case '帥':
            case '将':
                moves.push(...this.getGeneralMoves(row, col));
                break;
            case '仕':
            case '士':
                moves.push(...this.getAdvisorMoves(row, col));
                break;
            case '相':
            case '象':
                moves.push(...this.getElephantMoves(row, col));
                break;
            case '馬':
            case '马':
                moves.push(...this.getHorseMoves(row, col));
                break;
            case '車':
            case '车':
                moves.push(...this.getChariotMoves(row, col));
                break;
            case '炮':
            case '砲':
                moves.push(...this.getCannonMoves(row, col));
                break;
            case '兵':
            case '卒':
                moves.push(...this.getSoldierMoves(row, col));
                break;
        }
        
        // 过滤掉无效移动
        return moves.filter(move => {
            const [moveRow, moveCol] = move;
            return this.isValidMove(row, col, moveRow, moveCol);
        });
    }

    // 帅/将的移动
    getGeneralMoves(row, col) {
        const moves = [];
        const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        
        for (const [dr, dc] of directions) {
            const newRow = row + dr;
            const newCol = col + dc;
            
            // 必须在九宫格内
            if (this.inPalace(newRow, newCol, this.isRedPiece(this.board[row][col]))) {
                moves.push([newRow, newCol]);
            }
        }
        
        return moves;
    }

    // 仕/士的移动
    getAdvisorMoves(row, col) {
        const moves = [];
        const directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]];
        
        for (const [dr, dc] of directions) {
            const newRow = row + dr;
            const newCol = col + dc;
            
            if (this.inPalace(newRow, newCol, this.isRedPiece(this.board[row][col]))) {
                moves.push([newRow, newCol]);
            }
        }
        
        return moves;
    }

    // 相/象的移动
    getElephantMoves(row, col) {
        const moves = [];
        const directions = [[-2, -2], [-2, 2], [2, -2], [2, 2]];
        const isRed = this.isRedPiece(this.board[row][col]);
        
        for (const [dr, dc] of directions) {
            const newRow = row + dr;
            const newCol = col + dc;
            
            // 不能过河
            if ((isRed && newRow < 5) || (!isRed && newRow > 4)) continue;
            
            // 检查边界
            if (newRow < 0 || newRow >= 10 || newCol < 0 || newCol >= 9) continue;
            
            // 检查是否被憋象眼
            const blockRow = row + dr / 2;
            const blockCol = col + dc / 2;
            if (this.board[blockRow][blockCol] === null) {
                moves.push([newRow, newCol]);
            }
        }
        
        return moves;
    }

    // 馬/马的移动
    getHorseMoves(row, col) {
        const moves = [];
        const horseMoves = [
            [-2, -1], [-2, 1], [-1, -2], [-1, 2],
            [1, -2], [1, 2], [2, -1], [2, 1]
        ];
        
        const legBlocks = [
            [-1, 0], [-1, 0], [0, -1], [0, 1],
            [0, -1], [0, 1], [1, 0], [1, 0]
        ];
        
        for (let i = 0; i < horseMoves.length; i++) {
            const [dr, dc] = horseMoves[i];
            const [blockR, blockC] = legBlocks[i];
            const newRow = row + dr;
            const newCol = col + dc;
            
            // 检查边界
            if (newRow < 0 || newRow >= 10 || newCol < 0 || newCol >= 9) continue;
            
            // 检查是否被憋马腿
            if (this.board[row + blockR][col + blockC] === null) {
                moves.push([newRow, newCol]);
            }
        }
        
        return moves;
    }

    // 車/车的移动
    getChariotMoves(row, col) {
        const moves = [];
        const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        
        for (const [dr, dc] of directions) {
            for (let i = 1; i < 10; i++) {
                const newRow = row + dr * i;
                const newCol = col + dc * i;
                
                if (newRow < 0 || newRow >= 10 || newCol < 0 || newCol >= 9) break;
                
                if (this.board[newRow][newCol] === null) {
                    moves.push([newRow, newCol]);
                } else {
                    // 如果遇到对方棋子，可以吃掉
                    if (!this.isPieceOwnedByCurrentPlayer(this.board[newRow][newCol])) {
                        moves.push([newRow, newCol]);
                    }
                    break;
                }
            }
        }
        
        return moves;
    }

    // 炮/砲的移动
    getCannonMoves(row, col) {
        const moves = [];
        const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        
        for (const [dr, dc] of directions) {
            let foundPiece = false;
            
            for (let i = 1; i < 10; i++) {
                const newRow = row + dr * i;
                const newCol = col + dc * i;
                
                if (newRow < 0 || newRow >= 10 || newCol < 0 || newCol >= 9) break;
                
                if (this.board[newRow][newCol] === null) {
                    if (!foundPiece) {
                        // 没有遇到炮架，可以直接移动
                        moves.push([newRow, newCol]);
                    }
                } else {
                    if (!foundPiece) {
                        // 第一次遇到棋子，作为炮架
                        foundPiece = true;
                    } else {
                        // 第二次遇到棋子，如果是对方棋子可以吃掉
                        if (!this.isPieceOwnedByCurrentPlayer(this.board[newRow][newCol])) {
                            moves.push([newRow, newCol]);
                        }
                        break;
                    }
                }
            }
        }
        
        return moves;
    }

    // 兵/卒的移动
    getSoldierMoves(row, col) {
        const moves = [];
        const isRed = this.isRedPiece(this.board[row][col]);
        
        if (isRed) {
            // 红兵向上走
            if (row > 0) {
                moves.push([row - 1, col]);
            }
            // 过河后可以左右走
            if (row < 5) {
                if (col > 0) moves.push([row, col - 1]);
                if (col < 8) moves.push([row, col + 1]);
            }
        } else {
            // 黑卒向下走
            if (row < 9) {
                moves.push([row + 1, col]);
            }
            // 过河后可以左右走
            if (row > 4) {
                if (col > 0) moves.push([row, col - 1]);
                if (col < 8) moves.push([row, col + 1]);
            }
        }
        
        return moves;
    }

    // 判断是否在九宫格内
    inPalace(row, col, isRed) {
        if (col < 3 || col > 5) return false;
        
        if (isRed) {
            return row >= 7 && row <= 9;
        } else {
            return row >= 0 && row <= 2;
        }
    }

    // 验证移动是否合法
    isValidMove(fromRow, fromCol, toRow, toCol) {
        // 检查边界
        if (toRow < 0 || toRow >= 10 || toCol < 0 || toCol >= 9) return false;
        
        // 检查目标位置是否有自己的棋子
        const targetPiece = this.board[toRow][toCol];
        if (targetPiece && this.isPieceOwnedByCurrentPlayer(targetPiece)) return false;
        
        return true;
    }

    // 尝试移动棋子
    attemptMove(fromRow, fromCol, toRow, toCol) {
        const piece = this.board[fromRow][fromCol];
        
        if (!this.isValidMove(fromRow, fromCol, toRow, toCol)) return;
        
        const possibleMoves = this.getPossibleMoves(piece, fromRow, fromCol);
        const moveExists = possibleMoves.some(move => move[0] === toRow && move[1] === toCol);
        
        if (!moveExists) return;
        
        // 执行移动
        this.makeMove(fromRow, fromCol, toRow, toCol);
    }

    // 执行移动
    makeMove(fromRow, fromCol, toRow, toCol) {
        const piece = this.board[fromRow][fromCol];
        const capturedPiece = this.board[toRow][toCol];
        
        // 记录移动历史
        const move = {
            from: [fromRow, fromCol],
            to: [toRow, toCol],
            piece: piece,
            capturedPiece: capturedPiece,
            player: this.currentPlayer
        };
        this.moveHistory.push(move);
        
        // 更新棋盘
        this.board[toRow][toCol] = piece;
        this.board[fromRow][fromCol] = null;
        
        // 清除选择状态
        this.selectedPiece = null;
        this.removeBoardClickListener();
        
        // 更新移动计数
        this.moveCount++;
        
        // 检查游戏结束条件
        this.checkGameEnd();
        
        // 切换玩家
        if (this.gameStatus === 'playing') {
            this.switchPlayer();
        }
        
        // 重新渲染棋盘
        this.renderBoard();
        this.updateUI();
        
        // 如果是AI模式且轮到AI
        if (this.gameMode === 'ai' && this.currentPlayer === 'black' && this.gameStatus === 'playing') {
            setTimeout(() => this.makeAIMove(), 1000);
        }
    }

    // 切换玩家
    switchPlayer() {
        this.currentPlayer = this.currentPlayer === 'red' ? 'black' : 'red';
    }

    // 检查游戏结束
    checkGameEnd() {
        // 检查是否将军或将死
        const opponentColor = this.currentPlayer === 'red' ? 'black' : 'red';
        
        // 简单的胜负判定：如果对方的帅/将被吃掉
        let foundGeneral = false;
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece === '帥' || piece === '将') {
                    const pieceColor = this.isRedPiece(piece) ? 'red' : 'black';
                    if (pieceColor === opponentColor) {
                        foundGeneral = true;
                        break;
                    }
                }
            }
            if (foundGeneral) break;
        }
        
        if (!foundGeneral) {
            this.gameStatus = 'checkmate';
            this.showGameOver(`${this.currentPlayer === 'red' ? '红方' : '黑方'}胜利！`);
        }
    }

    // 显示游戏结束
    showGameOver(message) {
        document.getElementById('gameResult').innerHTML = 
            `<h4>${message}</h4><p>游戏结束，感谢游玩！</p>`;
        
        const modal = new bootstrap.Modal(document.getElementById('gameOverModal'));
        modal.show();
    }

    // AI移动
    makeAIMove() {
        let move;
        
        switch (this.aiDifficulty) {
            case 'easy':
                move = this.getRandomMove();
                break;
            case 'medium':
                move = this.getMediumMove();
                break;
            case 'hard':
                move = this.getHardMove();
                break;
        }
        
        if (move) {
            this.makeMove(move.fromRow, move.fromCol, move.toRow, move.toCol);
        }
    }

    // 简单AI：随机移动
    getRandomMove() {
        const availableMoves = [];
        
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && !this.isRedPiece(piece)) {
                    const possibleMoves = this.getPossibleMoves(piece, row, col);
                    possibleMoves.forEach(move => {
                        availableMoves.push({
                            fromRow: row,
                            fromCol: col,
                            toRow: move[0],
                            toCol: move[1],
                            piece: piece
                        });
                    });
                }
            }
        }
        
        if (availableMoves.length > 0) {
            return availableMoves[Math.floor(Math.random() * availableMoves.length)];
        }
        
        return null;
    }

    // 中等AI：优先吃子
    getMediumMove() {
        const availableMoves = [];
        const captureMoves = [];
        
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && !this.isRedPiece(piece)) {
                    const possibleMoves = this.getPossibleMoves(piece, row, col);
                    possibleMoves.forEach(move => {
                        const moveObj = {
                            fromRow: row,
                            fromCol: col,
                            toRow: move[0],
                            toCol: move[1],
                            piece: piece
                        };
                        
                        availableMoves.push(moveObj);
                        
                        // 如果能吃子，加入吃子列表
                        if (this.board[move[0]][move[1]]) {
                            captureMoves.push(moveObj);
                        }
                    });
                }
            }
        }
        
        // 优先选择吃子移动
        if (captureMoves.length > 0) {
            return captureMoves[Math.floor(Math.random() * captureMoves.length)];
        }
        
        if (availableMoves.length > 0) {
            return availableMoves[Math.floor(Math.random() * availableMoves.length)];
        }
        
        return null;
    }

    // 困难AI：简单的评估函数
    getHardMove() {
        const availableMoves = [];
        
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && !this.isRedPiece(piece)) {
                    const possibleMoves = this.getPossibleMoves(piece, row, col);
                    possibleMoves.forEach(move => {
                        availableMoves.push({
                            fromRow: row,
                            fromCol: col,
                            toRow: move[0],
                            toCol: move[1],
                            piece: piece,
                            score: this.evaluateMove(row, col, move[0], move[1])
                        });
                    });
                }
            }
        }
        
        if (availableMoves.length > 0) {
            // 排序并选择最佳移动
            availableMoves.sort((a, b) => b.score - a.score);
            return availableMoves[0];
        }
        
        return null;
    }

    // 评估移动分数
    evaluateMove(fromRow, fromCol, toRow, toCol) {
        let score = 0;
        
        // 吃子分数
        const capturedPiece = this.board[toRow][toCol];
        if (capturedPiece) {
            score += this.getPieceValue(capturedPiece);
        }
        
        // 位置分数（简单实现）
        score += this.getPositionValue(this.board[fromRow][fromCol], toRow, toCol);
        
        return score;
    }

    // 获取棋子价值
    getPieceValue(piece) {
        const values = {
            '帥': 1000, '将': 1000,
            '仕': 20, '士': 20,
            '相': 20, '象': 20,
            '馬': 40, '马': 40,
            '車': 90, '车': 90,
            '炮': 45, '砲': 45,
            '兵': 10, '卒': 10
        };
        
        return values[piece] || 0;
    }

    // 获取位置价值
    getPositionValue(piece, row, col) {
        // 简单的位置评估
        let value = 0;
        
        // 鼓励棋子向前移动
        if (piece === '兵' || piece === '卒') {
            value += this.isRedPiece(piece) ? (9 - row) : row;
        }
        
        return value;
    }

    // 悔棋
    undoMove() {
        if (this.moveHistory.length === 0) return;
        
        const lastMove = this.moveHistory.pop();
        
        // 恢复棋盘状态
        this.board[lastMove.from[0]][lastMove.from[1]] = lastMove.piece;
        this.board[lastMove.to[0]][lastMove.to[1]] = lastMove.capturedPiece;
        
        // 恢复玩家
        this.currentPlayer = lastMove.player;
        this.moveCount--;
        
        // 如果是AI模式，可能需要再悔一步
        if (this.gameMode === 'ai' && this.moveHistory.length > 0 && 
            this.moveHistory[this.moveHistory.length - 1].player === 'black') {
            const aiMove = this.moveHistory.pop();
            this.board[aiMove.from[0]][aiMove.from[1]] = aiMove.piece;
            this.board[aiMove.to[0]][aiMove.to[1]] = aiMove.capturedPiece;
            this.moveCount--;
        }
        
        this.gameStatus = 'playing';
        this.renderBoard();
        this.updateUI();
    }

    // 显示提示
    showHint() {
        if (this.gameMode === 'ai' && this.currentPlayer === 'black') return;
        
        let move;
        if (this.currentPlayer === 'red') {
            // 为红方获取最佳移动
            move = this.getBestMoveForRed();
        } else {
            move = this.getRandomMove();
        }
        
        if (move) {
            // 高亮提示移动
            this.highlightHint(move);
        }
    }

    // 为红方获取最佳移动
    getBestMoveForRed() {
        const availableMoves = [];
        
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && this.isRedPiece(piece)) {
                    const possibleMoves = this.getPossibleMoves(piece, row, col);
                    possibleMoves.forEach(move => {
                        availableMoves.push({
                            fromRow: row,
                            fromCol: col,
                            toRow: move[0],
                            toCol: move[1],
                            piece: piece,
                            score: this.evaluateMove(row, col, move[0], move[1])
                        });
                    });
                }
            }
        }
        
        if (availableMoves.length > 0) {
            availableMoves.sort((a, b) => b.score - a.score);
            return availableMoves[0];
        }
        
        return null;
    }

    // 高亮提示
    highlightHint(move) {
        // 清除现有高亮
        const hints = this.boardElement.querySelectorAll('.hint-highlight');
        hints.forEach(hint => hint.remove());
        
        // 高亮起始位置
        const fromElement = document.createElement('div');
        fromElement.className = 'hint-highlight';
        fromElement.style.position = 'absolute';
        fromElement.style.width = '60px';
        fromElement.style.height = '60px';
        fromElement.style.background = 'rgba(0, 255, 0, 0.3)';
        fromElement.style.border = '2px solid green';
        fromElement.style.left = (30 + move.fromCol * 60 - 30) + 'px';
        fromElement.style.top = (30 + move.fromRow * 60 - 30) + 'px';
        fromElement.style.borderRadius = '50%';
        fromElement.style.pointerEvents = 'none';
        
        // 高亮目标位置
        const toElement = document.createElement('div');
        toElement.className = 'hint-highlight';
        toElement.style.position = 'absolute';
        toElement.style.width = '60px';
        toElement.style.height = '60px';
        toElement.style.background = 'rgba(255, 0, 0, 0.3)';
        toElement.style.border = '2px solid red';
        toElement.style.left = (30 + move.toCol * 60 - 30) + 'px';
        toElement.style.top = (30 + move.toRow * 60 - 30) + 'px';
        toElement.style.borderRadius = '50%';
        toElement.style.pointerEvents = 'none';
        
        this.boardElement.appendChild(fromElement);
        this.boardElement.appendChild(toElement);
        
        // 3秒后移除高亮
        setTimeout(() => {
            fromElement.remove();
            toElement.remove();
        }, 3000);
    }

    // 新游戏
    newGame() {
        this.board = this.initializeBoard();
        this.currentPlayer = 'red';
        this.selectedPiece = null;
        this.moveHistory = [];
        this.gameStatus = 'playing';
        this.moveCount = 0;
        
        this.renderBoard();
        this.updateUI();
    }

    // 重置游戏
    resetGame() {
        this.newGame();
    }

    // 更新UI
    updateUI() {
        // 更新当前玩家显示
        this.currentPlayerElement.textContent = this.currentPlayer === 'red' ? '红方回合' : '黑方回合';
        this.currentPlayerElement.className = 'current-player ' + (this.currentPlayer === 'red' ? 'red-turn' : 'black-turn');
        
        // 更新游戏状态
        let statusText = '进行中';
        if (this.gameStatus === 'checkmate') {
            statusText = '游戏结束';
        }
        this.gameStatusElement.textContent = statusText;
        
        // 更新移动计数
        this.moveCountElement.textContent = this.moveCount;
        
        // 更新移动历史
        this.updateMoveHistory();
    }

    // 更新移动历史
    updateMoveHistory() {
        if (this.moveHistory.length === 0) {
            this.moveHistoryElement.innerHTML = '<div class="text-muted">暂无走法记录</div>';
            return;
        }
        
        let historyHtml = '';
        this.moveHistory.forEach((move, index) => {
            const player = move.player === 'red' ? '红' : '黑';
            const fromPos = String.fromCharCode(97 + move.from[1]) + (10 - move.from[0]);
            const toPos = String.fromCharCode(97 + move.to[1]) + (10 - move.to[0]);
            
            historyHtml += `
                <div class="move-item">
                    ${index + 1}. ${player}${move.piece} ${fromPos}-${toPos}
                    ${move.capturedPiece ? ' 吃' + move.capturedPiece : ''}
                </div>
            `;
        });
        
        this.moveHistoryElement.innerHTML = historyHtml;
        this.moveHistoryElement.scrollTop = this.moveHistoryElement.scrollHeight;
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    new XiangqiGame();
});
