import tkinter as tk
from tkinter import font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import socket
import math
import threading
import paramiko

RASPBERRY_IP = "192.168.0.4"
RASPBERRY_USER = "bitirme"
RASPBERRY_PASS = "1234"
REMOTE_MAIN_PATH = "~/Desktop/robot_code/main.py"

class RobotStatusUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Otonom Araç Durum Arayüzü")
        self.root.configure(bg="#2e2e2e")
        self.root.geometry("1280x900")
        self.yaw = 0
        self.x_loc = 0

        button_frame = tk.Frame(root, bg="#2e2e2e")
        button_frame.pack(fill=tk.X, padx=20, pady=(20, 5))

        self.btn_start = tk.Button(button_frame, text="BAŞLAT", command=self.start_main,
                                   bg="green", fg="white", font=("Arial", 14, "bold"), height=2)
        self.btn_start.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.btn_stop = tk.Button(button_frame, text="DURDUR", command=self.stop_main,
                                  bg="darkred", fg="white", font=("Arial", 14, "bold"), height=2)
        self.btn_stop.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.btn_reset = tk.Button(button_frame, text="RESETLE", command=self.reset_all,
                                   bg="gray40", fg="white", font=("Arial", 14, "bold"), height=2)
        self.btn_reset.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.cmd_status_var = tk.StringVar(value="🔴 Komut Verilemez")
        self.cmd_status_label = tk.Label(root, textvariable=self.cmd_status_var, fg="red",
                                         bg="#2e2e2e", font=("Arial", 30, "bold"))
        self.cmd_status_label.pack(pady=5)

        speaker_frame = tk.LabelFrame(root, text="Komut Veren Kişi", bg="#2e2e2e", fg="white",
                                      font=("Arial", 12, "bold"), labelanchor="n")
        speaker_frame.pack(fill=tk.X, padx=20, pady=5)

        speaker_inner = tk.Frame(speaker_frame, bg="#2e2e2e")
        speaker_inner.pack(anchor="center")

        self.speaker_buttons = {}
        for name in ["bulent", "gokhan", "emre", "eda"]:
            btn = tk.Button(speaker_inner, text=name.capitalize(), width=12, height=2,
                            font=("Arial", 12, "bold"), bg="gray40", fg="white")
            btn.pack(side=tk.LEFT, padx=15, pady=5)
            self.speaker_buttons[name] = btn

        info_frame = tk.LabelFrame(root, text="Araç Durum ve Komut Bilgileri", bg="#2e2e2e", fg="white",
                           font=("Arial", 12, "bold"), labelanchor="n")
        info_frame.pack(fill=tk.X, padx=20)

        self.status_var = tk.StringVar(value="Komut Durumu:")
        tk.Label(info_frame, textvariable=self.status_var, fg="lightblue", bg="#2e2e2e",
                font=("Consolas", 20, "bold"), anchor="w").pack(fill="x", padx=5)

        self.speech_var = tk.StringVar(value="Sesli Verilen Komut:")
        self.speech_label = tk.Label(info_frame, textvariable=self.speech_var,
                             fg="lightgreen", bg="#2e2e2e", anchor="w")
        self.speech_label.pack(fill="x", padx=5)

        self.command_var = tk.StringVar(value="Araca Verilen Komut: ")
        self.command_label = tk.Label(info_frame, textvariable=self.command_var,
                                    fg="orange", bg="#2e2e2e", anchor="w")
        self.command_label.pack(fill="x", padx=5)

        def update_font_size(*args):
            label_width = self.command_label.winfo_width()
            text = self.command_var.get()
            for size in range(20, 9, -1):
                test_font = tkfont.Font(family="Consolas", size=size, weight="bold")
                if test_font.measure(text) <= label_width:
                    self.command_label.configure(font=test_font)
                    break
        
        def update_speech_font_size(*args):
            label_width = self.speech_label.winfo_width()
            text = self.speech_var.get()
            for size in range(20, 9, -1):
                test_font = tkfont.Font(family="Consolas", size=size, weight="bold")
                if test_font.measure(text) <= label_width:
                    self.speech_label.configure(font=test_font)
                    break
        
        self.speech_var.trace_add("write", update_speech_font_size)
        self.speech_label.bind("<Configure>", update_speech_font_size)

        self.command_var.trace_add("write", update_font_size)
        self.command_label.bind("<Configure>", update_font_size)

        self.task_var = tk.StringVar(value="Araç Durumu:")
        tk.Label(info_frame, textvariable=self.task_var, fg="yellow", bg="#2e2e2e",
                font=("Consolas", 20, "bold"), anchor="w").pack(fill="x", padx=5)

        bottom_frame = tk.Frame(root, bg="#2e2e2e")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        history_frame = tk.LabelFrame(bottom_frame, text="Görev Geçmişi", bg="#2e2e2e", fg="white",
                                      font=("Arial", 12, "bold"))
        history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        text_frame = tk.Frame(history_frame, bg="#2e2e2e")
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, 
                         bg="#2e2e2e", 
                         troughcolor="#3a3a3a", 
                         activebackground="#cccccc", 
                         highlightbackground="#2e2e2e",
                         width=14)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_box = tk.Text(text_frame,
                           width=32, height=30,  
                           bg="gray40", fg="#cccccc",
                           wrap="word", font=("Consolas", 20),
                           yscrollcommand=scrollbar.set)
        
        self.history_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.history_box.yview)

        map_frame = tk.LabelFrame(bottom_frame, text="Araç Haritası", bg="#2e2e2e", fg="white",
                                  font=("Arial", 12, "bold"))
        map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(5, 5), dpi=100, facecolor="#2e2e2e")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor("#cccccc")
        self.ax.grid(True, color="gray")
        self.ax.tick_params(colors="lightgray")
        self.arrow = self.ax.arrow(-0.25, 0, 0.5, 0, head_width=0.1, head_length=0.1, fc='black', ec='black', linewidth=4)

        self.canvas = FigureCanvasTkAgg(self.figure, master=map_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        threading.Thread(target=self.listen_tcp, daemon=True).start()
        threading.Thread(target=self.listen_for_map_data, daemon=True).start()

        self.arrow_refresh_loop()

    def arrow_refresh_loop(self):
            self.ax.cla()
            self.ax.set_xlim(-3, 3)
            self.ax.set_ylim(-3, 3)
            self.ax.set_aspect("equal")
            self.ax.set_facecolor("#cccccc")
            self.ax.grid(True, color="gray")
            self.ax.tick_params(colors="lightgray")

            arrow_length = 0.26

            yaw_rad = math.radians(self.yaw)
            dx = math.cos(yaw_rad) * arrow_length
            dy = math.sin(yaw_rad) * arrow_length

            x = self.x_loc / 100 * dx
            y = self.x_loc / 100 * dy

            self.ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1,
                        fc='black', ec='black', linewidth=4)

            self.canvas.draw()
            self.root.after(33, self.arrow_refresh_loop) 

    def update_speaker(self, speaker_name):
        speaker_name = speaker_name.lower()
        for name, button in self.speaker_buttons.items():
            if name == speaker_name:
                button.configure(bg="green")
            else:
                button.configure(bg="darkred")

    def update_command_status(self, can_give_command: bool):
        if can_give_command:
            self.cmd_status_var.set("🟢 Komut Verilebilir")
            self.cmd_status_label.config(fg="lime")
            for btn in self.speaker_buttons.values():
                btn.configure(bg="gray40")
        else:
            self.cmd_status_var.set("🔴 Komut Verilemez")
            self.cmd_status_label.config(fg="red")
            for btn in self.speaker_buttons.values():
                btn.configure(bg="gray40")

    def update_status(self, msg): self.status_var.set(f"Komut Durumu: {msg}")
    def update_speech(self, text): self.speech_var.set(f"Sesli Verilen Komut: {text}")
    def update_command(self, cmd): self.command_var.set(f"Araca Verilen Komut: {cmd}")
    def update_active_task(self, task_text): self.task_var.set(f"Araç Durumu: {task_text}")

    def reset_map(self):
        self.ax.cla()  
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_aspect("equal")
        self.ax.set_facecolor("#cccccc")
        self.ax.grid(True, color="gray")
        self.ax.tick_params(colors="lightgray")

        self.arrow = self.ax.arrow(-0.25, 0, 0.5, 0, head_width=0.1, head_length=0.1,
                                fc='black', ec='black', linewidth=4)
        self.canvas.draw()


    def update_arrow(self, yaw_deg, x_loc):
        self.yaw = yaw_deg
        self.x_loc = x_loc


    def add_to_history(self, log):
        self.history_box.insert(tk.END, f"• {log}\n")
        self.history_box.see(tk.END)

    def reset_yaw(self):
        self.yaw = 0
        self.x_loc = 0

    def start_main(self):
        self.history_box.delete("1.0", tk.END)
        self.add_to_history("Mini robot araç başlatılıyor.")
        self.add_to_history("Komut verilebilir olana kadar bekleyiniz.")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(RASPBERRY_IP, username=RASPBERRY_USER, password=RASPBERRY_PASS)
            stdin, stdout, stderr = ssh.exec_command(
                f"nohup /home/bitirme/Desktop/bitirme_env/bin/python {REMOTE_MAIN_PATH} > /home/bitirme/main_log.txt 2>&1 &"
            )
            err = stderr.read().decode()
            out = stdout.read().decode()
            if err.strip():
                self.add_to_history(f"[stderr] {err}")
            if out.strip():
                self.add_to_history(f"[stdout] {out}")

            ssh.close()
        except Exception as e:
            self.add_to_history(f"HATA: {e}")

    def stop_main(self):
        self.add_to_history("Robot mini araç durduruldu.")
        self.yaw = 0
        self.x_loc = 0
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(RASPBERRY_IP, username=RASPBERRY_USER, password=RASPBERRY_PASS)
            ssh.exec_command("pkill -f main.py")
            ssh.close()
            self.update_command_status(False)
        except Exception as e:
            self.add_to_history(f"HATA: {e}")

    def reset_all(self):
        self.reset_yaw()
        self.reset_map()
        self.stop_main()
        self.update_command("")
        self.update_active_task("")
        self.update_speech("")
        self.update_status("")
        self.history_box.delete("1.0", tk.END)
        self.update_command_status(False)
        for btn in self.speaker_buttons.values():
            btn.configure(bg="gray40")
        self.start_main()

    def listen_for_map_data(self):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("0.0.0.0", 5051))  
            server.listen(5)
            while True:
                conn, addr = server.accept()
                try:
                    data = conn.recv(1024).decode().strip()
                    if data:
                        try:
                            yaw_str, dist_str = data.split(",")
                            yaw = float(yaw_str)
                            dist = float(dist_str)
                            self.yaw = yaw
                            self.x_loc = dist
                        except Exception as parse_err:
                            print("hata")
                except Exception as e:
                    print("hata")
                finally:
                    conn.close()

    def listen_tcp(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 5050))
        server.listen(5)
        while True:  
            conn, addr = server.accept()
            try:
                data = conn.recv(1024).decode().strip()
                if data:
                    lines = data.split("\n")
                    for line in lines:
                        if line.startswith("Arac Durum: "):
                            self.update_status(line[12:])
                        if line.startswith("Sesli Komut: "):
                            self.update_speech(line[13:])
                        if line.startswith("Arac Komut: "):
                            self.update_command(line[12:])
                        if line.startswith("Komut Veren: "):
                            sender = line.split(":")[1].strip().lower()
                            self.update_speaker(sender)
                        if line.startswith("Komut Durumu: "):
                            status = line.split(":")[1].strip().lower()
                            self.update_command_status(status == "true")
                        if line.startswith("Gecmis Komut: "):
                            self.add_to_history(line[14:])
                        if line.startswith("Aktif Komut: "):
                            self.update_active_task(line[13:])
            except Exception as e:
                self.add_to_history(f"TCP Hatası: {e}")
            finally:
                conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotStatusUI(root)
    root.mainloop()
