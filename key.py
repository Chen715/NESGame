from pynput.keyboard import Key, Listener

# 导入KeyCode
from pynput.keyboard import KeyCode


class KeyboardController:
    def __init__(self, emulator):
        self.emulator = emulator
        self.controller_state = {
            'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False,
            'A': False, 'B': False, 'START': False, 'SELECT': False,
        }
        self.listener = None
        self.running = False
        
        # pynput按键到字符串的映射
        self.pynput_key_mapping = {
            Key.up: 'up',
            Key.down: 'down',
            Key.left: 'left',
            Key.right: 'right',
            Key.enter: 'enter',
            Key.shift: 'shift',
        }
        
        # 字母键的映射
        for char in 'abcdefghijklmnopqrstuvwxyz':
            self.pynput_key_mapping[KeyCode.from_char(char)] = char
        
    def on_press(self, key):
        """按键按下事件处理"""
        try:
            # 获取按键名称
            key_name = self._get_key_name(key)
            
            # 如果按键在映射表中，更新控制器状态
            if key_name in self.emulator.key_mapping:
                button_name = self.emulator.key_mapping[key_name]
                self.controller_state[button_name] = True
                
                # 更新模拟器的控制器状态
                self.emulator.update_controller_state(self.controller_state)
                
                #print(f"按键按下: {key_name} -> {button_name}")
            
        except Exception as e:
            print(f"按键处理错误: {e}")
    
    def on_release(self, key):
        """按键释放事件处理"""
        try:
            # 获取按键名称
            key_name = self._get_key_name(key)
            
            # 如果按键在映射表中，更新控制器状态
            if key_name in self.emulator.key_mapping:
                button_name = self.emulator.key_mapping[key_name]
                self.controller_state[button_name] = False
                
                # 更新模拟器的控制器状态
                self.emulator.update_controller_state(self.controller_state)
                
                #print(f"按键释放: {key_name} -> {button_name}")
            
            # 如果是ESC键，停止监听
            if key == Key.esc:
                self.running = False
                return False
                
        except Exception as e:
            print(f"按键处理错误: {e}")
    
    def _get_key_name(self, key):
        """从pynput的Key对象获取按键名称"""
        if key in self.pynput_key_mapping:
            return self.pynput_key_mapping[key]
        
        try:
            # 尝试获取字符
            if hasattr(key, 'char'):
                return key.char
        except:
            pass
        
        return str(key)
    
    def update_state_from_external(self, external_state):
        """
        从外部数组更新控制器状态
        external_state: 包含按钮状态的字典，格式与controller_state相同
        """
        # 验证输入格式
        required_keys = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'B', 'START', 'SELECT']
        
        # 检查是否有缺失的键
        for key in required_keys:
            if key not in external_state:
                print(f"警告: 外部输入缺少键 '{key}'，将使用默认值False")
                external_state[key] = False
        
        # 检查是否有额外的键
        for key in list(external_state.keys()):
            if key not in required_keys:
                print(f"警告: 外部输入包含未知键 '{key}'，已忽略")
                external_state.pop(key)
        
        # 更新控制器状态
        for key in required_keys:
            # 确保值是布尔类型
            self.controller_state[key] = bool(external_state[key])
        
        # 更新模拟器的控制器状态
        self.emulator.update_controller_state(self.controller_state)
        
        return True
    
    def get_current_state(self):
        """获取当前控制器状态"""
        return self.controller_state.copy()
    
    def reset_state(self):
        """重置所有按钮状态为False"""
        for key in self.controller_state:
            self.controller_state[key] = False
        
        # 更新模拟器的控制器状态
        self.emulator.update_controller_state(self.controller_state)
        
        return True
    
    def start(self):
        """启动键盘监听"""
        self.running = True
        
        # 创建监听器
        self.listener = Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        
        # 启动监听线程
        self.listener.start()
        print("键盘监听已启动，按ESC键退出")
    
    def stop(self):
        """停止键盘监听"""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.running = False
        print("键盘监听已停止")
