import customtkinter as ctk
import psutil
import time
import platform
import distro
import datetime
import shutil
import subprocess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from config import *

class SystemFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Graphs area expands

        # --- Top Info Section ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.os_label = ctk.CTkLabel(self.info_frame, text="Loading OS Info...", font=FONT_SUBHEADER, anchor="w")
        self.os_label.pack(fill="x")
        
        self.hw_label = ctk.CTkLabel(self.info_frame, text="Loading Hardware Info...", font=FONT_BODY, text_color="gray70", anchor="w")
        self.hw_label.pack(fill="x")
        
        self.net_label = ctk.CTkLabel(self.info_frame, text="Network: Calculating...", font=FONT_BODY, text_color="gray70", anchor="w")
        self.net_label.pack(fill="x")

        # --- Graphs Section ---
        self.graphs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.graphs_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.graphs_frame.grid_columnconfigure(0, weight=1)
        self.graphs_frame.grid_columnconfigure(1, weight=1)
        self.graphs_frame.grid_rowconfigure(0, weight=1)
        self.graphs_frame.grid_rowconfigure(1, weight=1)

        # Data Lists
        self.cpu_data = [0] * 60
        self.ram_data = [0] * 60
        self.gpu_data = [0] * 60
        self.disk_data = [0] * 60
        
        # Create Charts (2x2 Grid)
        self.cpu_chart = self.create_chart(self.graphs_frame, 0, 0, "CPU Usage (%)", COLOR_ACCENT_1)
        self.ram_chart = self.create_chart(self.graphs_frame, 0, 1, "RAM Usage (%)", COLOR_ACCENT_2)
        self.gpu_chart = self.create_chart(self.graphs_frame, 1, 0, "GPU Usage (%)", COLOR_ACCENT_4)
        self.disk_chart = self.create_chart(self.graphs_frame, 1, 1, "Disk Usage (%)", COLOR_ACCENT_3)
        
        self.refresh_rate = 1000 # Default 1s

        self.update_stats()

    def create_chart(self, parent, row, col, title, color):
        frame = ctk.CTkFrame(parent, corner_radius=20, fg_color=COLOR_CARD)
        frame.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
        
        # Matplotlib Figure
        fig = Figure(figsize=(4, 2), dpi=100, facecolor=COLOR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLOR_CARD)
        ax.set_title(title, color=COLOR_TEXT, fontsize=10, pad=10)
        
        # Remove spines and ticks for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        ax.tick_params(axis='x', colors=COLOR_TEXT, labelsize=8, length=0)
        ax.tick_params(axis='y', colors=COLOR_TEXT, labelsize=8, length=0)
        
        # Initial empty plot
        line, = ax.plot([], [], color=color, linewidth=2)
        fill = ax.fill_between([], [], color=color, alpha=0.2)
        
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 60)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
        
        return fig, ax, line, fill, canvas

    def get_gpu_info(self):
        """
        Returns (utilization_percent, memory_used_mb, memory_total_mb, name) or None
        """
        if shutil.which("nvidia-smi"):
            try:
                # Query NVIDIA GPU
                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,name", "--format=csv,noheader,nounits"],
                    encoding="utf-8"
                )
                # Example output: "0, 100, 4096, GeForce GTX 1050"
                line = output.strip().split('\n')[0]
                parts = line.split(', ')
                if len(parts) >= 4:
                    util = float(parts[0])
                    mem_used = float(parts[1])
                    mem_total = float(parts[2])
                    name = parts[3]
                    return util, mem_used, mem_total, name
            except Exception:
                pass
        return None

    def set_refresh_rate(self, seconds):
        self.refresh_rate = int(seconds * 1000)

    def update_stats(self):
        if self.winfo_exists():
            # 1. Info Header
            distro_name = distro.name(pretty=True)
            kernel = platform.release()
            uptime = str(datetime.timedelta(seconds=int(time.time() - psutil.boot_time())))
            self.os_label.configure(text=f"{distro_name} | Kernel: {kernel} | Uptime: {uptime}")
            
            cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
            cores = psutil.cpu_count(logical=False)
            threads = psutil.cpu_count(logical=True)
            self.hw_label.configure(text=f"CPU: {cpu_freq:.0f}MHz ({cores}C/{threads}T)")

            # 2. Update Data
            # CPU
            cpu_pct = psutil.cpu_percent()
            self.cpu_data.append(cpu_pct)
            self.cpu_data.pop(0)
            self.update_chart(self.cpu_chart, self.cpu_data)

            # RAM
            ram = psutil.virtual_memory()
            self.ram_data.append(ram.percent)
            self.ram_data.pop(0)
            self.update_chart(self.ram_chart, self.ram_data)

            # GPU
            gpu_info = self.get_gpu_info()
            if gpu_info:
                util, mem_used, mem_total, name = gpu_info
                self.gpu_data.append(util)
                self.hw_label.configure(text=f"{self.hw_label.cget('text').split(' | GPU')[0]} | GPU: {name} ({int(mem_used)}MB/{int(mem_total)}MB)")
            else:
                self.gpu_data.append(0)
                # Keep CPU info but don't append GPU info if not found
                
            self.gpu_data.pop(0)
            self.update_chart(self.gpu_chart, self.gpu_data)

            # Disk
            disk = psutil.disk_usage('/')
            self.disk_data.append(disk.percent)
            self.disk_data.pop(0)
            self.update_chart(self.disk_chart, self.disk_data)

            # Network Speed
            net_io = psutil.net_io_counters()
            current_time = time.time()
            
            if hasattr(self, 'last_net_io') and hasattr(self, 'last_time'):
                time_diff = current_time - self.last_time
                if time_diff > 0:
                    bytes_sent = net_io.bytes_sent - self.last_net_io.bytes_sent
                    bytes_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
                    
                    upload_speed = (bytes_sent / time_diff) / 1024 # KB/s
                    download_speed = (bytes_recv / time_diff) / 1024 # KB/s
                    
                    up_unit = "KB/s"
                    down_unit = "KB/s"
                    
                    if upload_speed > 1024:
                        upload_speed /= 1024
                        up_unit = "MB/s"
                    if download_speed > 1024:
                        download_speed /= 1024
                        down_unit = "MB/s"
                        
                    self.net_label.configure(text=f"Network: ↓ {download_speed:.1f} {down_unit} | ↑ {upload_speed:.1f} {up_unit}")
            
            self.last_net_io = net_io
            self.last_time = current_time

            self.after(self.refresh_rate, self.update_stats)

    def update_chart(self, chart_tuple, data):
        fig, ax, line, fill, canvas = chart_tuple
        
        # Update line data
        x_data = range(len(data))
        line.set_data(x_data, data)
        
        # Update fill_between
        # Remove old fill collection
        if fill in ax.collections:
            fill.remove()
            
        # Create new fill
        # Get the color from the line to ensure consistency
        color = line.get_color()
        fill = ax.fill_between(x_data, data, color=color, alpha=0.2)
        
        # Update the tuple with the new fill object for next time
        # We need to modify the tuple in place or return it, but since tuples are immutable,
        # we rely on the fact that we are passing the components. 
        # Actually, we need to update the reference held by the class instance.
        # However, since we can't easily update the tuple in the caller, 
        # a better approach is to store these as objects or dictionaries.
        # For now, let's just update the chart_tuple list in the caller if possible, 
        # but here we can't. 
        # WORKAROUND: We will re-assign the fill object to the tuple index if it was a list.
        # But it is a tuple. 
        # Let's change the storage structure in __init__ to be a list or object.
        
        # Wait, simple fix: clear and redraw is expensive. 
        # Better: ax.collections.clear() then add new fill.
        # Better: remove all collections (fills)
        for collection in list(ax.collections):
            collection.remove()
        ax.fill_between(x_data, data, color=color, alpha=0.2)
        
        canvas.draw()
