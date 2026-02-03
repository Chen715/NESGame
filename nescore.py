import os
import libretro
import numpy as np
from libretro.api import retro_game_info
from ctypes import c_uint8


class RetroEmulator:
    def __init__(self, core_path, rom_path):
        self.core_path = core_path
        self.rom_path = rom_path
        self.core = None
        self.frame_count = 0
        self.video_frame = None
        self.running = False
        
        # 控制器状态
        self.controller_state = {
            'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False,
            'A': False, 'B': False, 'START': False, 'SELECT': False,
        }
        
        # 键盘到NES按键映射
        self.key_mapping = {
            'up': 'UP',
            'down': 'DOWN',
            'left': 'LEFT',
            'right': 'RIGHT',
            'z': 'A',           # Z键映射为A
            'x': 'B',           # X键映射为B
            'enter': 'START',   # Enter键映射为START
            'shift': 'SELECT',  # Shift键映射为SELECT
        }
    
    def init_core(self):
        """初始化核心"""
        self.core = libretro.Core(self.core_path)
        
        # 设置回调
        def env_callback(cmd, data):
            return False
        
        def video_callback(data, width, height, pitch):
            try:
                self.frame_count += 1
                if data and width > 0 and height > 0:
                    arr = np.frombuffer((c_uint8 * (height * pitch)).from_address(data), 
                                        dtype=np.uint8).reshape((height, pitch))
                    if pitch == width * 4:
                        rgb = arr[:, :width*4].reshape((height, width, 4))
                        self.video_frame = rgb
            except:
                pass
        
        def audio_callback(left, right):
            pass
        
        def audio_batch_callback(data, frames):
            return frames
        
        def input_poll():
            pass
        
        def input_state(port, device, index, id):
            if port == 0 and device == 1:
                button_map = {0: 'B', 1: 'Y', 2: 'SELECT', 3: 'START',
                              4: 'UP', 5: 'DOWN', 6: 'LEFT', 7: 'RIGHT',
                              8: 'A', 9: 'X'}
                button_name = button_map.get(id)
                if button_name in self.controller_state:
                    return 1 if self.controller_state[button_name] else 0
            return 0
        
        self.core.set_environment(env_callback)
        self.core.set_video_refresh(video_callback)
        self.core.set_audio_sample(audio_callback)
        self.core.set_audio_sample_batch(audio_batch_callback)
        self.core.set_input_poll(input_poll)
        self.core.set_input_state(input_state)
        
        self.core.init()
        return True
    
    def load_game(self):
        """加载游戏ROM"""
        if not os.path.exists(self.rom_path):
            return False
        
        with open(self.rom_path, 'rb') as f:
            rom_data = f.read()
        
        game_info = retro_game_info()
        game_info.path = self.rom_path.encode('utf-8')
        game_info.data = None
        game_info.size = 0
        game_info.meta = None
        
        return self.core.load_game(game_info)
    
    def run(self):
        """运行模拟器一帧并返回当前帧图像"""
        # 运行一帧
        if self.core:
            self.core.run()
        
        # 返回当前视频帧
        return self.video_frame
    
    def update_controller_state(self, controller_state_dict):
        """更新控制器状态，接收完整的控制器状态字典"""
        self.controller_state = controller_state_dict.copy()
    
    def shutdown(self):
        """关闭模拟器"""
        if self.core:
            try:
                self.core.unload_game()
                self.core.deinit()
            except:
                pass
