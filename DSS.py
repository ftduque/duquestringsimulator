import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
import serial.tools.list_ports
import time
import datetime
import math
import threading
import serial
import socket
import json
import struct
import random

class StringSimulator:
    def __init__(self, master):
        # Inicializa o tema usando a janela root existente
        self.root = root
        self.root.title("Duque String Simulator")
        self.root.iconbitmap('C:/DuqueStringSimulator/ic.ico')  # Substitua pelo caminho correto do ícone
        self.root.resizable(False, False)
        self.configurations = []  # Inicializa a lista de configurações
        self.master = master
        self.sending = False  # Adicione esta linha para inicializar a variável sending

        # Definir estilo para os widgets
        style = ttk.Style(self.root)
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25)

        # Criação das abas
        self.tab_control = ttk.Notebook(self.root)
        self.config_tab = ttk.Frame(self.tab_control)
        self.position_tab = ttk.Frame(self.tab_control)
        self.attitude_tab = ttk.Frame(self.tab_control)
        self.wind_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.config_tab, text='Configurações')
        self.tab_control.add(self.position_tab, text='Posição')
        self.tab_control.add(self.attitude_tab, text='Attitude')
        self.tab_control.add(self.wind_tab, text='Vento')
        self.tab_control.pack(expand=1, fill="both")

        # Configuração da tabela
        self.tree = ttk.Treeview(self.config_tab, columns=("String Type", "Telegrama Rate (Hz)", "Port Type", "Port Configuration"), show="headings")
        self.tree.heading("String Type", text="Tipo de String")
        self.tree.heading("Telegrama Rate (Hz)", text="Taxa de Telegrama (Hz)")
        self.tree.heading("Port Type", text="Tipo de Porta")
        self.tree.heading("Port Configuration", text="Configuração da Porta")
        self.tree.grid(row=0, column=0, columnspan=5, padx=5, pady=5)

        self.tree.column("String Type", width=130, minwidth=130, stretch=False, anchor='w')  # Ajuste o valor conforme necessário
        self.tree.column("Telegrama Rate (Hz)", width=180, minwidth=180, stretch=False, anchor='center')  # Ajuste o valor conforme necessário
        self.tree.column("Port Type", width=100, minwidth=100, stretch=False, anchor='center')  # Ajuste o valor conforme necessário
        self.tree.column("Port Configuration", width=335, minwidth=335, stretch=False, anchor='center')  # Ajuste o valor conforme necessário

        # Desabilitando o redimensionamento com o mouse
        def disable_resize(event):
            return "break"  # Ignora o evento

        # Bind para o evento de redimensionamento
        self.tree.bind("<B1-Motion>", disable_resize)

        # Botões
        ttk.Button(self.config_tab, text="Adicionar Configuração", command=self.open_add_config).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.config_tab, text="Deletar Configuração", command=self.delete_configuration).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.config_tab, text="Iniciar Envio", command=self.start_sending).grid(row=1, column=3, padx=5, pady=5)
        #ttk.Button(self.config_tab, text="Parar Envio", command=self.stop_sending).grid(row=1, column=4, padx=5, pady=5)

        # Criar abas
        self.create_position_tab()
        self.create_attitude_tab()
        self.create_wind_tab()

        # Criação da barra de menu
        menubar = tk.Menu(self.root)

        # Criação do menu Arquivo
        arquivo_menu = tk.Menu(menubar, tearoff=0)
        arquivo_menu.add_command(label="Abrir Projeto", command=self.open_project)
        arquivo_menu.add_command(label="Salvar Projeto", command=self.save_project)
        arquivo_menu.add_command(label="Salvar Como", command=self.save_project_as)
        arquivo_menu.add_command(label="Fechar", command=self.exit)
        menubar.add_cascade(label="Arquivo", menu=arquivo_menu)

        # Criação do menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_help)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

        # Configurando a barra de menu na janela principal
        self.root.config(menu=menubar)

    def create_position_tab(self):
        ttk.Label(self.position_tab, text="Latitude").grid(column=0, row=0, padx=5, pady=5)
        self.latitude_entry = ttk.Entry(self.position_tab)
        self.latitude_entry.grid(column=1, row=0, padx=5, pady=5)

        ttk.Label(self.position_tab, text="Longitude").grid(column=0, row=1, padx=5, pady=5)
        self.longitude_entry = ttk.Entry(self.position_tab)
        self.longitude_entry.grid(column=1, row=1, padx=5, pady=5)

    def create_attitude_tab(self):
        ttk.Label(self.attitude_tab, text="Heading").grid(column=0, row=0, padx=5, pady=5)
        self.heading_entry = ttk.Entry(self.attitude_tab)
        self.heading_entry.grid(column=1, row=0, padx=5, pady=5)

        ttk.Label(self.attitude_tab, text="Pitch").grid(column=0, row=1, padx=5, pady=5)
        self.pitch_entry = ttk.Entry(self.attitude_tab)
        self.pitch_entry.grid(column=1, row=1, padx=5, pady=5)

        ttk.Label(self.attitude_tab, text="Roll").grid(column=0, row=2, padx=5, pady=5)
        self.roll_entry = ttk.Entry(self.attitude_tab)
        self.roll_entry.grid(column=1, row=2, padx=5, pady=5)

    def create_wind_tab(self):
        ttk.Label(self.wind_tab, text="Vento (km/h)").grid(column=0, row=0, padx=5, pady=5)
        self.wind_entry = ttk.Entry(self.wind_tab)
        self.wind_entry.grid(column=1, row=0, padx=5, pady=5)

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Sobre")
        help_window.geometry("485x120")
        help_window.resizable(False, False)
        help_window.iconbitmap('C:/DuqueStringSimulator/ic.ico')

        # Carregar o logo
        try:
            logo = Image.open("C:/DuqueStringSimulator/icon.jpg")
            logo = logo.resize((135, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(help_window, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(side=tk.LEFT, padx=8, pady=0)  # Adiciona o logo à esquerda
        except FileNotFoundError:
            print("Logo não encontrado. Verifique o caminho da imagem.")

        # Frame para o logo e o texto
        logo_frame = tk.Frame(help_window)
        logo_frame.pack(side=tk.TOP, padx=5, pady=5)  # Adiciona um padding

        # Título
        title_label = tk.Label(logo_frame, text="Duque String Simulator", font=("Arial", 12, "bold"))
        title_label.pack(anchor="center")  # Alinha à esquerda

        # Informações
        info_text = (
            "Versão 1.1\n"
            "Licença: 20250514-00 (Permanente)\n"
            "Licenciado para C-Innovation\n"
            "© Filipe Terra Duque (filipeterraduque@gmail.com)"
        )
        info_label = tk.Label(logo_frame, text=info_text, font=("Arial", 10))
        info_label.pack(anchor="center")  # Alinha à esquerda

        # Variáveis para configuração da porta
        self.serial_port = None
        self.tcp_socket = None
        self.udp_socket = None

        # Variáveis de estado
        self.sending = False
        self.send_thread = None

        # Dados da Posição, Attitude e Vento
        self.create_position_tab()
        self.create_attitude_tab()
        self.create_wind_tab()

        # Armazenamento das configurações
        self.configurations = []

    def create_position_tab(self):
        ttk.Label(self.position_tab, text="Latitude  Longitude").grid(column=0, row=0, columnspan=2)
        ttk.Label(self.position_tab, text="Latitude:").grid(column=0, row=1)
        self.position_latitude = tk.Entry(self.position_tab)
        self.position_latitude.grid(column=1, row=1)

        ttk.Label(self.position_tab, text="Longitude:").grid(column=0, row=2)
        self.position_longitude = tk.Entry(self.position_tab)
        self.position_longitude.grid(column=1, row=2)

        ttk.Label(self.position_tab, text="Velocidade (nós):").grid(column=0, row=3)
        self.position_speed_knots = tk.Entry(self.position_tab)
        self.position_speed_knots.grid(column=1, row=3)

        ttk.Label(self.position_tab, text="Hidroacústico").grid(column=0, row=4, columnspan=2)
        ttk.Label(self.position_tab, text="Quantos transponders? (1-10)").grid(column=0, row=5)
        self.position_transponders = tk.Entry(self.position_tab)
        self.position_transponders.grid(column=1, row=5)

        ttk.Label(self.position_tab, text="Profundidade:").grid(column=0, row=6)
        self.position_depth = tk.Entry(self.position_tab)
        self.position_depth.grid(column=1, row=6)

    def create_attitude_tab(self):
        ttk.Label(self.attitude_tab, text="Dados de Attitude").grid(column=0, row=0, columnspan=2)

        ttk.Label(self.attitude_tab, text="Roll:").grid(column=0, row=1)
        self.attitude_roll = tk.Entry(self.attitude_tab)
        self.attitude_roll.grid(column=1, row=1)

        ttk.Label(self.attitude_tab, text="Pitch:").grid(column=0, row=2)
        self.attitude_pitch = tk.Entry(self.attitude_tab)
        self.attitude_pitch.grid(column=1, row=2)

        ttk.Label(self.attitude_tab, text="Heave:").grid(column=0, row=3)
        self.attitude_heave = tk.Entry(self.attitude_tab)
        self.attitude_heave.grid(column=1, row=3)

        ttk.Label(self.attitude_tab, text="Aproamento:").grid(column=0, row=4)
        self.attitude_heading = tk.Entry(self.attitude_tab)
        self.attitude_heading.grid(column=1, row=4)

    def create_wind_tab(self):
        ttk.Label(self.wind_tab, text="Dados do Vento").grid(column=0, row=0, columnspan=2)
        ttk.Label(self.wind_tab, text="Velocidade do Vento:").grid(column=0, row=1)
        self.wind_speed = tk.Entry(self.wind_tab)
        self.wind_speed.grid(column=1, row=1)

        ttk.Label(self.wind_tab, text="Direção do Vento:").grid(column=0, row=2)
        self.wind_direction = tk.Entry(self.wind_tab)
        self.wind_direction.grid(column=1, row=2)

    def open_add_config(self):
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Configuração")
        self.config_window.resizable(False, False)
        self.config_window.iconbitmap('C:/DuqueStringSimulator/ic.ico')
        self.config_window_width = 280
        self.config_window_height = 105
        self.config_window.geometry(f"{self.config_window_width}x{self.config_window_height}")
        

        # Taxa de Telegrama (Hz)
        ttk.Label(self.config_window, text=" Taxa de Telegrama (Hz):").grid(column=0, row=0)
        self.telegrame_rate = tk.Entry(self.config_window)
        self.telegrame_rate.grid(column=1, row=0)
        self.telegrame_rate.insert(0, "10")

        # Tipo de String
        ttk.Label(self.config_window, text=" Tipo de String:").grid(column=0, row=1)
        self.string_type = tk.StringVar()
        self.string_type_combobox = ttk.Combobox(self.config_window, textvariable=self.string_type, values=["$GPGGA", "$INS_GGA", "$LNAV", "$GPGLL", "$GPZDA", "$GPVTG", "$HEHDT", "EM3000 HQ GYRO", "EM3000 RPH", "TSS DMS05/TSS 335", "$PRDID", "$PSONUSBL", "$PSIMSSB", "$WIMWV", "AIS", "$PSONDEP", "Digiquartz Depth", "DVL RDI PD0", "DVL RDI PD4", "DVL RDI PD5", "ROV STRING", "CP PROBE", "UT PROBE"])
        self.string_type_combobox.grid(column=1, row=1)
        self.string_type_combobox.bind("<<ComboboxSelected>>", self.update_string_type)

        # Tipo de Porta
        ttk.Label(self.config_window, text=" Tipo de Porta:").grid(column=0, row=2)
        self.port_type = tk.StringVar()
        port_combobox = ttk.Combobox(self.config_window, textvariable=self.port_type, values=["Serial", "TCP", "UDP"])
        port_combobox.grid(column=1, row=2)
        port_combobox.bind("<<ComboboxSelected>>", self.open_port_config)

        # Botão para adicionar configuração
        ttk.Button(self.config_window, text="Adicionar", command=self.add_configuration).grid(column=0, row=3, columnspan=2)

    def update_string_type(self, event):
        string_type = self.string_type.get()
        if string_type == "$GPGGA":
            self.generated_string = self.generate_gpgga_string()
        if string_type == "$INS_GGA":
            self.generated_string = self.generate_ins_gga_string()            
            print(self.generated_string)  # Para testes; você pode querer enviar isso para um campo de texto ou exibi-lo na GUI
        if string_type == "$LNAV":
            self.generated_string = self.generate_lnav_string()            
            print(self.generated_string)
        elif string_type == "$GPGLL":
            self.generated_string = self.generate_gpgll_string()
            print(self.generated_string)
        elif string_type == "$GPVTG":
            self.generated_string = self.generate_gpvtg_string()
            print(self.generated_string)            
        elif string_type == "$GPZDA":
            self.generated_string = self.generate_gpzda_string()
            print(self.generated_string)
        elif string_type == "$HEHDT":
            self.generated_string = self.generate_hehdt_string()
            print(self.generated_string)
        elif string_type == "EM3000 HQ GYRO":
            self.generated_string = self.generate_em3000hqgyro_string()
            print(self.generated_string)
        elif string_type == "EM3000 RPH":
            self.generated_string = self.generate_em3000rph_string()
            print(self.generated_string)
        elif string_type == "TSS DMS05/TSS 335":
            self.generated_string = self.generate_tss_string()
            print(self.generated_string)
        elif string_type == "$PRDID":
            self.generated_string = self.generate_prdid_string()
            print(self.generated_string)
        elif string_type == "$PSONUSBL":
            self.generated_string = self.generate_psonusbl_string()
            print(self.generated_string)
        elif string_type == "$PSIMSSB":
            self.generated_string = self.generate_psimssb_string()
            print(self.generated_string)
        elif string_type == "$WIMWV":
            self.generated_string = self.generate_wimwv_string()
            print(self.generated_string) 
        elif string_type == "AIS":
            self.generated_string = self.generate_ais_string()
            print(self.generated_string)        
        elif string_type == "$PSONDEP":
            self.generated_string = self.generate_psondep_string()
            print(self.generated_string)
        elif string_type == "Digiquartz Depth":
            self.generated_string = self.generate_digiquartz_string()
            print(self.generated_string)
        elif string_type == "DVL RDI PD0":
            self.generated_string = self.generate_dvlpd0_string()
            print(self.generated_string)
        elif string_type == "DVL RDI PD4":
            self.generated_string = self.generate_dvlpd4_string()
            print(self.generated_string)
        elif string_type == "DVL RDI PD5":
            self.generated_string = self.generate_dvlpd5_string()
            print(self.generated_string)
        elif string_type == "ROV STRING":
            self.generated_string = self.generate_rovstring_string()
            print(self.generated_string)
        elif string_type == "CP PROBE":
            self.generated_string = self.generate_cp_string()
            print(self.generated_string)
        elif string_type == "UT PROBE":
            self.generated_string = self.generate_ut_string()
            print(self.generated_string)

    def open_port_config(self, event):
        port_type = self.port_type.get()
        if port_type == "Serial":
            self.open_serial_config()
        elif port_type == "TCP":
            self.open_tcp_config()
        elif port_type == "UDP":
            self.open_udp_config()

    def open_serial_config(self):
        self.serial_window = tk.Toplevel(self.config_window)
        self.serial_window.title("Serial")
        self.serial_window.resizable(False, False)
        self.serial_window.iconbitmap('C:/DuqueStringSimulator/ic.ico')
        self.serial_window_width = 232
        self.serial_window_height = 108
        self.serial_window.geometry(f"{self.serial_window_width}x{self.serial_window_height}")
        
        # Portas COM disponíveis
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.selected_port = tk.StringVar()
        ttk.Label(self.serial_window, text=" Porta:").grid(column=0, row=0)
        ttk.Combobox(self.serial_window, textvariable=self.selected_port, values=ports).grid(column=1, row=0)

        # Baud Rate
        self.baud_rate = tk.StringVar()
        baud_options = [110, 300, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]
        ttk.Label(self.serial_window, text=" Baud Rate:").grid(column=0, row=1)
        ttk.Combobox(self.serial_window, textvariable=self.baud_rate, values=baud_options).grid(column=1, row=1)

        # Configurações adicionais
        self.settings = tk.StringVar()
        settings_options = ["8,None,1", "8,Odd,2", "7,Even,1"]        
        ttk.Label(self.serial_window, text=" Configurações:").grid(column=0, row=2)
        ttk.Combobox(self.serial_window, textvariable=self.settings, values=settings_options).grid(column=1, row=2)

        ttk.Button(self.serial_window, text="Ok", command=self.close_serial_config).grid(column=0, row=3, columnspan=2)

    def close_serial_config(self):
        self.serial_window.destroy()

    def open_tcp_config(self):
        self.tcp_window = tk.Toplevel(self.root)
        self.tcp_window.title("TCP")
        self.tcp_window.resizable(False, False)
        self.tcp_window.iconbitmap('C:/DuqueStringSimulator/ic.ico')
        self.tcp_window_width = 200
        self.tcp_window_height = 115
        self.tcp_window.geometry(f"{self.tcp_window_width}x{self.tcp_window_height}")

        # Variável para o checkbox de usar localhost
        self.use_localhost_tcp = tk.BooleanVar()

        # Endereço IP e Porta
        self.tcp_ip = tk.StringVar()
        self.tcp_port = tk.StringVar()

        ttk.Label(self.tcp_window, text=" Endereço IP:").grid(column=0, row=0)
        ip_entry = tk.Entry(self.tcp_window, textvariable=self.tcp_ip)
        ip_entry.grid(column=1, row=0)

        # Checkbox para usar localhost
        ttk.Checkbutton(self.tcp_window, text=" Usar Localhost", variable=self.use_localhost_tcp, command=lambda: self.toggle_localhost(ip_entry, self.use_localhost_tcp)).grid(column=0, row=1, columnspan=2)

        ttk.Label(self.tcp_window, text=" Porta:").grid(column=0, row=2)
        tk.Entry(self.tcp_window, textvariable=self.tcp_port).grid(column=1, row=2)

        # Cliente / Servidor
        self.is_cliente = tk.BooleanVar()
        self.is_servidor = tk.BooleanVar()

        # Checkbuttons para Cliente e Servidor
        ttk.Checkbutton(self.tcp_window, text="Cliente", variable=self.is_cliente, command=self.update_checkbuttons).grid(column=0, row=3)
        ttk.Checkbutton(self.tcp_window, text="Servidor", variable=self.is_servidor, command=self.update_checkbuttons).grid(column=1, row=3)

        ttk.Button(self.tcp_window, text="Ok", command=self.close_tcp_config).grid(column=0, row=4, columnspan=2)

    def update_checkbuttons(self):
        # Verifica se Cliente está marcado e desmarcar Servidor, e vice-versa
        if self.is_cliente.get() and self.is_servidor.get():
            # Se ambos estiverem marcados, desmarcar ambos
            self.is_cliente.set(False)
            self.is_servidor.set(False)
        elif self.is_cliente.get():
            # Se Cliente estiver marcado, desmarcar Servidor
            self.is_servidor.set(False)
        elif self.is_servidor.get():
            # Se Servidor estiver marcado, desmarcar Cliente
            self.is_cliente.set(False)

    def close_tcp_config(self):
        self.tcp_window.destroy()

    def open_udp_config(self):
        self.udp_window = tk.Toplevel(self.config_window)
        self.udp_window.title("UDP")
        self.udp_window.resizable(False, False)
        self.udp_window.iconbitmap('C:/DuqueStringSimulator/ic.ico')
        self.udp_window_width = 200
        self.udp_window_height = 95
        self.udp_window.geometry(f"{self.udp_window_width}x{self.udp_window_height}")

    # Variável para o checkbox
        self.use_localhost_udp = tk.BooleanVar()

    # Endereço IP e Porta
        self.udp_ip = tk.StringVar()
        self.udp_port = tk.StringVar()

        ttk.Label(self.udp_window, text=" Endereço IP:").grid(column=0, row=0)
        ip_entry = tk.Entry(self.udp_window, textvariable=self.udp_ip)
        ip_entry.grid(column=1, row=0)

    # Checkbox para usar localhost
        ttk.Checkbutton(self.udp_window, text=" Usar Localhost", variable=self.use_localhost_udp, command=lambda: self.toggle_localhost(ip_entry, self.use_localhost_udp)).grid(column=0, row=1, columnspan=2)

        ttk.Label(self.udp_window, text=" Porta:").grid(column=0, row=2)
        tk.Entry(self.udp_window, textvariable=self.udp_port).grid(column=1, row=2)

        ttk.Button(self.udp_window, text="Ok", command=self.close_udp_config).grid(column=0, row=3, columnspan=2)

    def toggle_localhost(self, entry, localhost_var):
        if localhost_var.get():
            entry.delete(0, tk.END)
            entry.insert(0, "127.0.0.1")
            entry.config(state='disabled')  # Desativa o campo de entrada
        else:
            entry.config(state='normal')  # Reativa o campo de entrada

    def close_udp_config(self):
        self.udp_window.destroy()

    def add_configuration(self):
        new_config = {
            "string_type": self.string_type.get(),
            "telegrame_rate": self.telegrame_rate.get(),
            "port_type": self.port_type.get(),
            "port_configuration": self.get_port_configuration()
        }
        self.configurations.append(new_config)
        self.update_treeview()
        self.config_window.destroy()

    def get_port_configuration(self):
        port_type = self.port_type.get()
        if port_type == "Serial":
            return {
                "port": self.selected_port.get(),
                "baud_rate": self.baud_rate.get(),
                "settings": self.settings.get()
            }
        elif port_type == "TCP":
            return {
                "ip": self.tcp_ip.get(),
                "port": self.tcp_port.get()
            }
        elif port_type == "UDP":
            return {
                "ip": self.udp_ip.get(),
                "port": self.udp_port.get()
            }

    def update_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for config in self.configurations:
            self.tree.insert("", "end", values=(config["string_type"], config["telegrame_rate"], config["port_type"], json.dumps(config["port_configuration"])))

    def delete_configuration(self):
        selected_item = self.tree.selection()
        if selected_item:
            for item in selected_item:
                index = self.tree.index(item)
                self.configurations.pop(index)
                self.tree.delete(item)
            self.update_treeview()

    def edit_configuration(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item[0])
            config = self.configurations[index]
            self.open_add_config()  # Open the add config window
            self.config_window.wait_window()  # Wait for the config window to close

            # Atualiza a configuração com os dados editados
            self.configurations[index] = {
                "string_type": self.string_type.get(),
                "telegrame_rate": self.telegrame_rate.get(),
                "port_type": self.port_type.get(),
                "port_configuration": self.get_port_configuration()
            }
            self.update_treeview()

    def start_sending(self):
        if self.sending:
            messagebox.showwarning("Aviso", "Envio já em andamento.")
            return

        self.sending = True
        self.send_thread = threading.Thread(target=self.send_data)
        self.send_thread.start()

    def stop_sending(self):
        self.sending = False
        if self.send_thread is not None:
            self.send_thread.join()  # Espera a thread terminar

    def send_data(self):
        while self.sending:
            for config in self.configurations:
                self.send_telegrams(config)
                time.sleep(1.0 / float(config["telegrame_rate"]))

    def send_telegrams(self, config):
        formatted_string = self.generate_string_based_on_type(config["string_type"])  # Corrigido o nome da variável
        print(f"Enviando: {formatted_string}")  # Para verificar a string gerada
        if config["port_type"] == "Serial":
            self.send_serial(formatted_string, config)
        elif config["port_type"] == "TCP":
            self.send_tcp(formatted_string, config)
        elif config["port_type"] == "UDP":
            self.send_udp(formatted_string, config)

    # Adicione esta linha para verificar se a string é gerada corretamente.
    def generate_string_based_on_type(self, string_type):
        if string_type == "$GPGGA":
            return self.generate_gpgga_string()
        elif string_type == "$INS_GGA":
            return self.generate_ins_gga_string()
        elif string_type == "$LNAV":
            return self.generate_lnav_string()            
        elif string_type == "$GPGLL":
            return self.generate_gpgll_string()
        elif string_type == "$GPVTG":
            return self.generate_gpvtg_string()            
        elif string_type == "$GPZDA":
            return self.generate_gpzda_string()
        elif string_type == "$HEHDT":
            return self.generate_hehdt_string()
        elif string_type == "EM3000 HQ GYRO":
            return self.generate_em3000hqgyro_string()       
        elif string_type == "EM3000 RPH":
            return self.generate_em3000rph_string()      
        elif string_type == "TSS DMS05/TSS 335":
            return self.generate_tss_string()       
        elif string_type == "$PRDID":
            return self.generate_prdid_string()      
            return self.generate_tss_string()       
        elif string_type == "$PSONUSBL":
            return self.generate_psonusbl_string()
        elif string_type == "$PSIMSSB":
            return self.generate_psimssb_string()
        elif string_type == "$WIMWV":
            return self.generate_wimwv_string()
        elif string_type == "AIS":
            return self.generate_ais_string()            
        elif string_type == "$PSONDEP":
            return self.generate_psondep_string()
        elif string_type == "Digiquartz Depth":
            return self.generate_digiquartz_string()
        elif string_type == "DVL RDI PD0":
            return self.generate_dvlpd0_string()
        elif string_type == "DVL RDI PD4":
            return self.generate_dvlpd4_string()
        elif string_type == "DVL RDI PD5":
            return self.generate_dvlpd5_string()
        elif string_type == "ROV STRING":
            return self.generate_rovstring_string()
        elif string_type == "CP PROBE":
            return self.generate_cp_string()
        elif string_type == "UT PROBE":
            return self.generate_ut_string()  # Exemplo de outro tipo de string 
        # Adicione mais elif para outros tipos de string conforme necessário
        return ""
    
    def send_with_rate(self, rate_hz):
        interval = 1 / rate_hz
        while self.running:
            start_time = time.time()
            
            # Envio do pacote
            self.send_data()
            
            # Ajusta o tempo de espera para a próxima iteração
            time.sleep(max(0, interval - (time.time() - start_time)))

    def send_serial(self, formatted_string, config):
        with serial.Serial(config["port_configuration"]["port"], config["port_configuration"]["baud_rate"]) as ser:
            if isinstance(formatted_string, bytes) and formatted_string.startswith(b'\x90\x90'):
                ser.write(formatted_string)  # Envia diretamente se for binário EM3000
            else:
                ser.write(f"{formatted_string}\r\n".encode())  # Adiciona \r\n para strings textuais

    def send_tcp(self, formatted_string, config):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((config["port_configuration"]["ip"], int(config["port_configuration"]["port"])))
            if isinstance(formatted_string, bytes) and formatted_string.startswith(b'\x90\x90'):
                s.sendall(formatted_string)  # Envia diretamente se for binário EM3000
            else:
                s.sendall(f"{formatted_string}\r\n".encode())  # Adiciona \r\n para strings textuais

    def send_udp(self, formatted_string, config):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Checa se o formato é binário (EM3000 ou TSS) e não deve adicionar '\r\n'
            if isinstance(formatted_string, bytes) and formatted_string.startswith(b'\x90\x90'):
            # Para strings EM3000 (ou outras em binário)
                s.sendto(formatted_string, (config["port_configuration"]["ip"], int(config["port_configuration"]["port"])))
            elif isinstance(formatted_string, bytes):
            # Para strings binárias TSS
                s.sendto(formatted_string, (config["port_configuration"]["ip"], int(config["port_configuration"]["port"])))
            else:
            # Para outros formatos de string (textuais), adiciona o \r\n
                s.sendto(f"{formatted_string}\r\n".encode(), (config["port_configuration"]["ip"], int(config["port_configuration"]["port"])))

    def save_project(self):
        project_data = {
            "configurations": self.configurations,
            "position": {
                "latitude": self.position_latitude.get(),
                "longitude": self.position_longitude.get(),
                "speed_knots": self.position_speed_knots.get(),
                "transponders": self.position_transponders.get(),
                "depth": self.position_depth.get(),
            },
            "attitude": {
                "heading": self.attitude_heading.get(),
                "pitch": self.attitude_pitch.get(),
                "roll": self.attitude_roll.get(),
                "heave": self.attitude_heave.get(),
            },
            "wind": {
                "speed": self.wind_speed.get(),
                "direction": self.wind_direction.get(),
            }
        }
        with open("project.json", "w") as f:
            json.dump(project_data, f)  # Salva todo o dicionário project_data
            messagebox.showinfo("Salvar Projeto", "Projeto salvo com sucesso!")

    def save_project_as(self):
        project_data = {
            "configurations": self.configurations,
            "position": {
                "latitude": self.position_latitude.get(),
                "longitude": self.position_longitude.get(),
                "speed_knots": self.position_speed_knots.get(),
                "transponders": self.position_transponders.get(),
                "depth": self.position_depth.get(),
            },
            "attitude": {
                "heading": self.attitude_heading.get(),
                "pitch": self.attitude_pitch.get(),
                "roll": self.attitude_roll.get(),
                "heave": self.attitude_heave.get(),
            },
            "wind": {
                "speed": self.wind_speed.get(),
                "direction": self.wind_direction.get(),
            }
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(project_data, f)  # Salva todo o dicionário project_data
            messagebox.showinfo("Salvar Como", "Projeto salvo com sucesso!")

    def open_project(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                project_data = json.load(file)
                
                # Carregar as configurações salvas
                self.configurations = project_data.get("configurations", [])
                self.tree.delete(*self.tree.get_children())  # Limpa a árvore antes de adicionar novas entradas
                
                # Assumindo que cada item em `self.configurations` é um dicionário com chaves correspondentes às colunas da tree
                for config in self.configurations:
                    self.tree.insert("", "end", values=(
                        config.get("string_type", ""),
                        config.get("telegrame_rate", ""),
                        config.get("port_type", ""),
                        config.get("port_configuration", ""),
                        # Acrescente outras colunas conforme necessário
                    ))
                #self.tree.insert("", "end", values=(config["string_type"], config["telegrame_rate"], config["port_type"], json.dumps(config["port_configuration"])))
                # Limpar e carregar os valores das abas
                position_data = project_data.get("position", {})
                self.position_latitude.delete(0, tk.END)
                self.position_latitude.insert(0, position_data.get("latitude", ""))
                
                self.position_longitude.delete(0, tk.END)
                self.position_longitude.insert(0, position_data.get("longitude", ""))
                
                self.position_speed_knots.delete(0, tk.END)
                self.position_speed_knots.insert(0, position_data.get("speed_knots", ""))
                
                self.position_transponders.delete(0, tk.END)
                self.position_transponders.insert(0, position_data.get("transponders", ""))
                
                self.position_depth.delete(0, tk.END)
                self.position_depth.insert(0, position_data.get("depth", ""))

                attitude_data = project_data.get("attitude", {})
                self.attitude_heading.delete(0, tk.END)
                self.attitude_heading.insert(0, attitude_data.get("heading", ""))
                
                self.attitude_pitch.delete(0, tk.END)
                self.attitude_pitch.insert(0, attitude_data.get("pitch", ""))
                
                self.attitude_roll.delete(0, tk.END)
                self.attitude_roll.insert(0, attitude_data.get("roll", ""))
                
                self.attitude_heave.delete(0, tk.END)
                self.attitude_heave.insert(0, attitude_data.get("heave", ""))

                wind_data = project_data.get("wind", {})
                self.wind_speed.delete(0, tk.END)
                self.wind_speed.insert(0, wind_data.get("speed", ""))
                
                self.wind_direction.delete(0, tk.END)
                self.wind_direction.insert(0, wind_data.get("direction", ""))

            tk.messagebox.showinfo("Projeto carregado", "O projeto foi carregado com sucesso.")

    def exit(self):
        if messagebox.askokcancel("Fechar", "Deseja realmente fechar o aplicativo?"):
            root.quit()

    def generate_gpgga_string(self):
        latitude = float(self.position_latitude.get())
        longitude = float(self.position_longitude.get())
        fix_quality = "1"  # Qualidade do fix (ajustar conforme necessário)
        num_sats = "08"  # Número de satélites (ajustar conforme necessário)
        hdop = "0.9"  # Diluição horizontal de posição
        altitude = "1.0,M"  # Altitude (ajustar conforme necessário)
        height_of_geoid = "31.9,M"  # Altura do geóide (ajustar conforme necessário)

        # Função para converter coordenadas decimais para graus e minutos
        def decimal_to_gps(coord, is_latitude=True):
            degrees = int(abs(coord))
            minutes = (abs(coord) - degrees) * 60
            if is_latitude:
                formatted_coord = f"{degrees:02d}{minutes:07.4f}"
            else:
                formatted_coord = f"{degrees:03d}{minutes:07.4f}"
            return formatted_coord

        # Formatar latitude e determinar direção
        lat_direction = "N" if latitude >= 0 else "S"
        formatted_latitude = f"{decimal_to_gps(latitude, is_latitude=True)},{lat_direction}"

        # Formatar longitude e determinar direção
        lon_direction = "E" if longitude >= 0 else "W"
        formatted_longitude = f"{decimal_to_gps(longitude, is_latitude=False)},{lon_direction}"

        # Formatação da string GPGGA
        gpgga_string = (
            f"$GPGGA,{time.strftime('%H%M%S')},{formatted_latitude},{formatted_longitude},"
            f"{fix_quality},{num_sats},{hdop},{altitude},{height_of_geoid},,,*47"
        )
        return gpgga_string

    def generate_ins_gga_string(self):
        try:
            # Posição de referência da embarcação (latitude e longitude em graus decimais)
            latitude_ref = float(self.position_latitude.get())
            longitude_ref = float(self.position_longitude.get())
            heading = float(self.attitude_heading.get())  # Heading da embarcação em graus
            transponder_depth = float(self.position_depth.get())  # Profundidade fixa do Transponder 1 em metros

            # Coordenadas do transponder 1 em relação ao centro da embarcação (em metros)
            x_transponder = 0  # Posição do transponder ao longo do eixo X (proa-popa)
            y_transponder = 0  # Posição do transponder ao longo do eixo Y (boreste-bombordo)

            # Converter o heading para radianos
            heading_rad = math.radians(heading)

            # Aplicar rotação nas coordenadas do transponder em relação ao heading
            x_rotated = x_transponder * math.cos(heading_rad) - y_transponder * math.sin(heading_rad)
            y_rotated = x_transponder * math.sin(heading_rad) + y_transponder * math.cos(heading_rad)

            # Converter as coordenadas rotacionadas para deslocamentos em latitude e longitude
            earth_radius = 6378137  # Raio médio da Terra em metros

            # Conversão de deslocamento para latitude
            delta_lat = y_rotated / earth_radius
            latitude_transponder = latitude_ref + math.degrees(delta_lat)

            # Conversão de deslocamento para longitude, ajustando pelo cosseno da latitude de referência
            delta_lon = x_rotated / (earth_radius * math.cos(math.radians(latitude_ref)))
            longitude_transponder = longitude_ref + math.degrees(delta_lon)

            # Função auxiliar para formatar latitude e longitude no formato GPS
            def decimal_to_gps(coord, is_latitude=True):
                degrees = int(abs(coord))
                minutes = (abs(coord) - degrees) * 60
                if is_latitude:
                    formatted_coord = f"{degrees:02d}{minutes:07.4f}"
                else:
                    formatted_coord = f"{degrees:03d}{minutes:07.4f}"
                return formatted_coord

            # Formatar latitude e definir o hemisfério
            lat_direction = "N" if latitude_transponder >= 0 else "S"
            formatted_latitude = f"{decimal_to_gps(latitude_transponder, is_latitude=True)},{lat_direction}"

            # Formatar longitude e definir o hemisfério
            lon_direction = "E" if longitude_transponder >= 0 else "W"
            formatted_longitude = f"{decimal_to_gps(longitude_transponder, is_latitude=False)},{lon_direction}"

            # Parâmetros fixos da string INS_GGA
            fix_quality = "1"
            num_sats = "08"
            hdop = "0.9"
            altitude = f"-{transponder_depth:.1f},M"
            height_of_geoid = "0.0,M"

            # Montar a string INS_GGA
            ins_gga_string = (
                f"$INS_GGA,{datetime.datetime.utcnow().strftime('%H%M%S')},{formatted_latitude},{formatted_longitude},"
                f"{fix_quality},{num_sats},{hdop},{altitude},{height_of_geoid},,,"
            )

            # Calcular o checksum
            checksum = 0
            for char in ins_gga_string[1:]:
                checksum ^= ord(char)

            # Adicionar o checksum à string
            ins_gga_string += f"*{checksum:02X}"

            # Exibir a string INS_GGA gerada
            print("String $INS_GGA gerada:")
            print(ins_gga_string)

            return ins_gga_string

        except Exception as e:
            print(f"Erro ao gerar a string $INS_GGA: {e}")
            return ''

    def generate_gpgll_string(self):
        # Obter dados de posição
        latitude = float(self.position_latitude.get())
        longitude = float(self.position_longitude.get())
        
        # Verifica se as entradas não estão vazias
        if not latitude or not longitude:
            return "Erro: Latitude e Longitude devem ser preenchidos."
        
        try:
            lat_value = float(latitude)
            lon_value = float(longitude)
        except ValueError:
            return "Erro: Latitude e Longitude devem ser numéricas."
        
        # Função para converter coordenadas decimais para graus e minutos
        def decimal_to_gps(coord, is_latitude=True):
            degrees = int(abs(coord))
            minutes = (abs(coord) - degrees) * 60
            if is_latitude:
                formatted_coord = f"{degrees:02d}{minutes:07.4f}"
            else:
                formatted_coord = f"{degrees:03d}{minutes:07.4f}"
            return formatted_coord

        # Formatar latitude e determinar direção
        lat_direction = "N" if latitude >= 0 else "S"
        formatted_latitude = f"{decimal_to_gps(latitude, is_latitude=True)},{lat_direction}"

        # Formatar longitude e determinar direção
        lon_direction = "E" if longitude >= 0 else "W"
        formatted_longitude = f"{decimal_to_gps(longitude, is_latitude=False)},{lon_direction}"
        
        # Obter o tempo em UTC
        current_time_utc = time.strftime('%H%M%S')  # Formato hhmmss
        
        # Status da fixação (A = válido)
        fix_status = "A"
        
        # Formatação da string GPGLL
        gpgll_string = f"$GPGLL,{formatted_latitude},{formatted_longitude},{current_time_utc},{fix_status}"
        
        # Calcula o checksum
        checksum = 0
        for char in gpgll_string[1:]:  # ignora o símbolo $
            checksum ^= ord(char)
        gpgll_string += f"*{checksum:02X}"
        
        # Retorna a string formatada completa com checksum
        return f"{gpgll_string}*{checksum}"

    def generate_gpvtg_string(self):
        try:
            # Obtenha o valor de heading e adicione a variação aleatória
            course = float(self.attitude_heading.get()) #+ random.uniform(-0.1, 0.1)
            
            # Obtenha o valor de speed_knots e adicione a variação aleatória
            speed_knots = float(self.position_speed_knots.get()) #+ random.uniform(-0.1, 0.1)
            
            # Converta speed_knots para km/h (1 nó = 1.852 km/h)
            speed_kmh = speed_knots * 1.852

            # Defina o modo de operação como 'D' (DGPS)
            mode = 'D'

            # Monte a string base antes do checksum
            gpvtg_string = f"$GPVTG,{course:.2f},T,,M,{speed_knots:.2f},N,{speed_kmh:.2f},K,{mode}"

            # Calcule o checksum da string
            checksum = 0
            for char in gpvtg_string[1:]:  # Não incluímos o caractere '$' no cálculo
                checksum ^= ord(char)
            
            # Adicione o checksum no formato hexadecimal
            gpvtg_string += f"*{checksum:02X}"
            
            return gpvtg_string
        except Exception as e:
            print(f"Erro ao gerar a string GPVTG: {e}")
            return ''

    def generate_gpzda_string(self):
        # Obtendo a hora atual
        current_time = time.strftime('%H%M%S')  # HHMMSS
        # Obtendo a data atual
        current_day = time.strftime('%d')  # Dia (01 a 31)
        current_month = time.strftime('%m')  # Mês (01 a 12)
        current_year = time.strftime('%Y')  # Ano (ex: 2023)
        # Exemplo de descrição do fuso horário
        local_zone_hours = "00"  # Exemplo: UTC±0
        local_zone_minutes = "00"  # Exemplo: sem minutos adicionais
        # Formatação da string
        gpzda_string = f"$GPZDA,{current_time},{current_day},{current_month},{current_year},{local_zone_hours},{local_zone_minutes}*00"
        return gpzda_string

    def generate_hehdt_string(self):
        heading = self.attitude_heading.get()  # Obtendo o valor do heading
        if not heading:
            return "Erro: Heading deve ser preenchido."
        try:
            heading_value = float(heading)
        except ValueError:
            return "Erro: Heading deve ser numérico."

    # Formatação da string HEHDT
        hehdt_string = f"$HEHDT,{heading_value},T"  # O valor T indica que é em graus
        
        # Calcula o checksum
        checksum = 0
        for char in hehdt_string[1:]:  # ignora o símbolo $
            checksum ^= ord(char)
        hehdt_string += f"*{checksum:02X}"

        # Retorna a string formatada completa com checksum
        return f"{hehdt_string}*{checksum}"

    def generate_em3000hqgyro_string(self):
        try:
        # Obtenha os valores
            heading = int(float(self.attitude_heading.get()) * 100)  # Multiplica por 100 para decimal
            pitch = int(float(self.attitude_pitch.get()) * 100)  # Multiplica por 100 para decimal
            roll = int(float(self.attitude_roll.get()) * 100)    # Multiplica por 100 para decimal
        # Verifique se os valores estão dentro do intervalo permitido
            if not all(-32768 <= val <= 32767 for val in [pitch, roll]) or not (0 <= heading <= 36000):
                raise ValueError("Certifique-se de que todos os valores são numéricos e dentro do intervalo permitido.")
        # Empacote os dados corretamente
        # A ordem deve ser: 0x90, 0x90, roll, pitch, heading
            binary_data = struct.pack('<BBHhh', 0x90, 0x90, heading, roll, pitch)
        # Converta o heading para bytes e substitua TV
            heading_bytes = struct.pack('<H', heading)  # Converte heading para 2 bytes
        # Crie a string final com o heading em vez de 'TV'
            final_string = binary_data + heading_bytes + b'\x00'  # Use b'\x00' para finalizar
            return final_string
        except Exception as e:
            print(f"Erro ao gerar a string EM3000 HQ GYRO: {e}")
            return b''

    def generate_em3000rph_string(self):
        try:
            # Obtenha os valores de entrada e aplique o fator de escala
            roll = int(float(self.attitude_roll.get()) * 100)
            pitch = int(float(self.attitude_pitch.get()) * 100)
            heave = int(float(self.attitude_heave.get()) * -100)
            heading = int(float(self.attitude_heading.get()) * 100)

            # Verifique se os valores estão dentro do intervalo permitido
            if not all(-32768 <= val <= 32767 for val in [pitch, roll, heave]) or not (0 <= heading <= 36000):
                raise ValueError("Certifique-se de que todos os valores são numéricos e dentro do intervalo permitido.")

            # Gera valores randômicos entre -0.2 e 0.2, multiplicando por 100 para manter a precisão decimal
            random_roll = int(random.uniform(-0.2, 0.2) * 100)
            random_pitch = int(random.uniform(-0.2, 0.2) * 100)
            random_heave = int(random.uniform(-0.2, 0.2) * 100)
            random_heading = int(random.uniform(-0.2, 0.2) * 100)

            # Adiciona os valores randômicos aos valores originais
            roll += random_roll
            pitch += random_pitch
            heave += random_heave
            heading += random_heading

            # Empacote os dados na ordem correta: 0x90, 0x90, roll, pitch, heave
            binary_data = struct.pack('<BBhhh', 0x90, 0x90, roll, pitch, heave)

            # Converta o heading para bytes e substitua TV
            heading_bytes = struct.pack('<H', heading)  # Converte heading para 2 bytes

            # Crie a string final com o heading em vez de 'TV'
            final_string = binary_data + heading_bytes + b'\x00'  # Use b'\x00' para finalizar
            return final_string
        except Exception as e:
            print(f"Erro ao gerar a string EM3000 RPH: {e}")
            return b''

    def generate_tss_string(self):
        try:
            # Obtenha os valores de pitch, roll e heave com a variação randômica
            pitch = float(self.attitude_pitch.get()) + random.uniform(-0.3, 0.3)
            roll = float(self.attitude_roll.get()) + random.uniform(-0.3, 0.3)
            heave = float(self.attitude_heave.get()) + random.uniform(-0.3, 0.3)

            # Defina os valores de num, num2 e num3, adaptando-os conforme a lógica original
            num = 10
            num2 = 20
            num3 = 0  # Esse valor pode ser ajustado conforme a necessidade

            # Escolha o caractere de status com base em alguma condição
            c = 'F'  # Ou 'H', dependendo da lógica que você deseja implementar

            # Monte a string inicial com num e num2 formatados como hexadecimais
            tss_string = f":{num:02X}{num2:04X} "

            # Adicione o sinal para num3 (posição longitudinal) e formate o valor absoluto com 4 dígitos
            if num3 < 0:
                tss_string += "-"
            else:
                tss_string += " "
            tss_string += f"{abs(num3):04d}{c}"

            # Adicione o valor de roll com o sinal e o valor formatado para 4 dígitos
            if roll < 0.0:
                tss_string += "-"
            else:
                tss_string += " "
            tss_string += f"{int(abs(roll) / 0.01):04d} "

            # Adicione o valor de pitch com o sinal e o valor formatado para 4 dígitos
            if pitch < 0.0:
                tss_string += "-"
            else:
                tss_string += " "
            tss_string += f"{int(abs(pitch) / 0.01):04d} "

            # Adicione o valor de heave com o sinal e o valor formatado para 4 dígitos
            if heave < 0.0:
                tss_string += "-"
            else:
                tss_string += " "
            tss_string += f"{int(abs(heave) / 0.01):04d}"

            # Retorne a string gerada
            return tss_string
        except Exception as e:
            print(f"Erro ao gerar a string TSS: {e}")
            return ''

    def generate_prdid_string(self):
        try:
            # Obtenha os valores de pitch, roll e heading com a variação randômica
            pitch = float(self.attitude_pitch.get()) + random.uniform(-0.2, 0.2)
            roll = float(self.attitude_roll.get()) + random.uniform(-0.2, 0.2)
            heading = float(self.attitude_heading.get()) + random.uniform(-0.1, 0.1)

            # Monte a string no formato $PRDID,Pitch,Roll,Heading
            prdid_string = f"$PRDID,{pitch:.2f},{roll:.2f},{heading:.2f}*53"

            # Retorne a string gerada
            return prdid_string
        except Exception as e:
            print(f"Erro ao gerar a string PRDID: {e}")
            return ''

    def generate_psonusbl_string(self):
        try:
        # Obtém a quantidade de transponders da aba Posição
            num_transponders = int(self.position_transponders.get())
        
        # Limita o valor de transponders entre 1 e 10
            if num_transponders < 1:
                num_transponders = 1
            elif num_transponders > 10:
                num_transponders = 10
        
        # Obtém a hora UTC atual no formato HHMMSS.ss
            utc_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S.%f")[:-3]

        # Obtém o valor de profundidade configurado pelo usuário
            depth = float(self.position_depth.get())  # Ajuste conforme o método que você usa para obter a profundidade

        # Define 10 posições pré-definidas dentro do intervalo de -50 a 50
            predefined_positions = [
                (-40.0, -40.0),
                (-15.0, -10.0),
                (-41.0, -41.0),
                (-16.0, -10.0),
                (0.0, -65.0),
                (15.0, -10.0),
                (16.0, -10.0),
                (35.0, 35.0),
                (36.0, 36.0),
                (20.0, -30.0),
            ]

        # Inicializa a lista de strings
            strings = []

        # Garante que o número de transponders não exceda 10
            num_transponders = min(num_transponders, 10)

            for transponder_id in range(1, num_transponders + 1):
            # Pega a posição pré-definida correspondente ao transponder
                x_ref, y_ref = predefined_positions[transponder_id - 1]

            # Adiciona variações de -1 a 1 a cada posição
                x_value = round(x_ref + random.uniform(-1.5, 1.5), 1)
                y_value = round(y_ref + random.uniform(-1.5, 1.5), 1)

            # Gera quatro valores aleatórios
                random_values = [round(random.uniform(0, 1), 1) for _ in range(4)]

            # Monta a string para cada transponder
                psonusbl_string = (
                    f"$PSONUSBL,{utc_time},{transponder_id},H,{x_value:.2f},{y_value:.2f},{depth:.2f},"
                    f"{random_values[0]:.2f},{random_values[1]:.2f},{random_values[2]:.2f},{random_values[3]:.2f},*"
                )

            # Calcula o checksum
                checksum = sum(ord(c) for c in psonusbl_string[1:]) % 256
                psonusbl_string += f"{checksum:02X}"

            # Adiciona a string gerada à lista
                strings.append(psonusbl_string)

            return '\r\n'.join(strings)  # Retorna todas as strings concatenadas

        except Exception as e:
            print(f"Erro ao gerar a string $PSONUSBL: {e}")
            return ''

    def generate_psimssb_string(self):
        try:
        # Obtém a quantidade de transponders da aba Posição
            num_transponders = int(self.position_transponders.get())
        
        # Limita o valor de transponders entre 1 e 10
            if num_transponders < 1:
                num_transponders = 1
            elif num_transponders > 10:
                num_transponders = 10
        
        # Obtém a hora UTC atual no formato HHMMSS.ss
            utc_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S.%f")[:-3]

        # Obtém o valor de profundidade configurado pelo usuário
            depth = float(self.position_depth.get())  # Ajuste conforme o método que você usa para obter a profundidade

        # Define 10 posições pré-definidas dentro do intervalo de -50 a 50
            predefined_positions = [
                (-40.0, -40.0),
                (-15.0, -10.0),
                (-41.0, -41.0),
                (-16.0, -10.0),
                (0.0, -65.0),
                (15.0, -10.0),
                (16.0, -10.0),
                (35.0, 35.0),
                (36.0, 36.0),
                (20.0, -30.0),
            ]

        # Inicializa a lista de strings
            strings = []

        # Garante que o número de transponders não exceda 10
            num_transponders = min(num_transponders, 10)

            for transponder_id in range(1, num_transponders + 1):
            # Pega a posição pré-definida correspondente ao transponder
                x_ref, y_ref = predefined_positions[transponder_id - 1]

            # Adiciona variações de -1 a 1 a cada posição
                x_value = round(x_ref + random.uniform(-1.5, 1.5), 1)
                y_value = round(y_ref + random.uniform(-1.5, 1.5), 1)

            # Gera quatro valores aleatórios
                random_values = [round(random.uniform(0, 1), 1) for _ in range(4)]

            # Monta a string para cada transponder
                psimssb_string = (
                    f"$PSIMSSB,{utc_time},B0{transponder_id},A,Rej,C,H,M,{x_value:.2f},{y_value:.2f},{depth:.2f},"
                    f"0.180,T,{random_values[1]:.6f},*"
                )

            # Calcula o checksum
                checksum = sum(ord(c) for c in psimssb_string[1:]) % 256
                psimssb_string += f"{checksum:02X}"

            # Adiciona a string gerada à lista
                strings.append(psimssb_string)

            return '\r\n'.join(strings)  # Retorna todas as strings concatenadas

        except Exception as e:
            print(f"Erro ao gerar a string $PSIMSSB: {e}")
            return ''

    def generate_wimwv_string(self):
        try:
        # Captura os valores de entrada
            wind_angle = float(self.wind_direction.get())
            wind_speed = float(self.wind_speed.get())

        # Aplica variação constante de +1.5 a -1.5
            wind_angle += random.uniform(-1.5, 1.5)
            wind_speed += random.uniform(-1.5, 1.5)

        # Ajusta o ângulo de vento entre 0 e 359.9 graus
            wind_angle = max(0.0, min(359.9, wind_angle))
            wind_speed = max(0.0, wind_speed)

        # Define os parâmetros de referência, unidades e status
            reference = 'R'  # ou 'T', conforme desejado
            speed_units = 'N'  # por exemplo, 'N' para nós
            status = 'A'  # Dados válidos

        # Monta a string NMEA
            wimwv_string = f"$WIMWV,{wind_angle:.1f},{reference},{wind_speed:.1f},{speed_units},{status}"

        # Calcula o checksum
            checksum = 0
            for char in wimwv_string[1:]:  # ignora o símbolo $
                checksum ^= ord(char)
            wimwv_string += f"*{checksum:02X}"

            return wimwv_string

        except Exception as e:
            print(f"Erro ao gerar a string WIMWV: {e}")
            return ""

    def generate_ais_string(self):
    # Lista de strings AIS com checksums pré-calculados (sem recalcular)
        ais_messages = [
            "!AIVDM,1,1,,A,1:U8KJ0Oi5u4P2GkP51mB3h426iP,0*44",
            "!AIVDM,1,1,,A,3:U77F5000M4>s5kOJ19GbH40Ddr,0*65",
            "!AIVDM,1,1,,A,1:U73IP000M4?aCkO@GrjJB60<1=,0*34",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@F5Qr40000,0*14",
            "!AIVDM,1,1,,A,3:U8ieQ7h3M4dtkkNuWmTQD60Dob,0*15",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2kkNuV8ewv42@1e,0*56",
            "!AIVDM,1,1,,A,2:U7:o1005M4BUUkNcvSh2D80@1q,0*53",
            "!AIVDM,1,1,,A,3:U8CL1009M4Nh7kNfAek@N80E1b,0*31",
            "!AIVDO,1,1,,,1:U7AQi000M4AkakOa@V5Qr60000,0*04",
            "!AIVDM,1,1,,B,1:U7Ok0P01M4BqkkNUN8>gv82@2K,0*32",
            "!AIVDM,1,1,,B,3:U7@T0Oh>M4WKSkNmIka1b:01=@,0*5B",
            "!AIVDM,1,1,,A,3:U7N:<Oh2u4BQMkNUQE1B060Qw@,0*48",
            "!AIVDM,1,1,,B,1:U7DlPP02M4Go5kPKVaqgv:00RO,0*02",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@V5Qr80000,0*08",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@V5Qr:0000,0*0A",
            "!AIVDM,1,1,,B,3596Wp5000M4AVckOn0rCGt>0DoJ,0*14",
            "!AIVDM,1,1,,B,277De55000M4IUKkQFOIT:mf0@3r,0*06",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@V5Qr<0000,0*0C",
            "!AIVDM,1,1,,B,3:U7N:<Oh2u4BQSkNUPlu24<0Q3P,0*13",
            "!AIVDM,1,1,,A,1:U8QsP002u4B7ikObW=lQl82@4Q,0*0F",
            "!AIVDM,1,1,,B,1:U7eP`P01u4BqAkNUTcf?vf2l11,0*2B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@n5Qr>0000,0*36",
            "!AIVDM,1,1,,A,1533381003u4PkCkOW7djPF@0000,0*0E",
            "!AIVDM,1,1,,A,2:U7:o1004M4BUqkNcvSm2F@084i,0*6C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@n5Qr@0000,0*4E",
            "!AIVDM,1,1,,A,1:U8N90P02M4@@=kOS;al?vD2D0d,0*7F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@n5QrB0000,0*4A",
            "!AIVDM,1,1,,B,406iKEAvRdFH9u4BAokOtPO0085o,0*46",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@n5QrD0000,0*4C",
            "!AIVDM,1,1,,A,1:U7N:<Oh2u4BQckNUP4e28D0h6i,0*1B",
            "!AIVDM,1,1,,B,1:U8KJ0PA5u4P7MkP4RU83fH2H6n,0*32",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@n5QrF0000,0*48",
            "!AIVDM,1,1,,B,B>pf7jP00OA4JjLouEv?CwV20000,0*52",
            "!AIVDM,1,1,,A,B>pf7jP00OA4JjLouEv?CwV20000,0*51",
            "!AIVDM,1,1,,B,H>pf7jPJ04pA8DU>1PV22222220,2*17",
            "!AIVDM,1,1,,A,H>pf7jTl00`0000@CokohP0PD448,0*0F",
            "!AIVDM,1,1,,B,3:U7@T0Oh<M4WL9kNmElGAlJ01o@,0*45",
            "!AIVDO,1,1,,,1:U7AQi000M4AkckOa@F5QrH0000,0*68",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2kkNuU`ewvH2@7V,0*47",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@65QrJ0000,0*1C",
            "!AIVDM,1,1,,A,2:U7:o1004M4BV=kNcvSjRDL0889,0*16",
            "!AIVDM,1,1,,A,1:U7Ok0P01M4BqkkNUM`q?vN288J,0*78",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QrL0000,0*18",
            "!AIVDM,1,1,,A,1:U7DlPP02M4GoAkPKUr0wvN0@8h,0*7D",
            "!AIVDM,1,1,,A,3:U7@T0Oh9M4WLKkNmElUApP00l@,0*27",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QrN0000,0*1A",
            "!AIVDM,1,1,,A,277De55000M4IUQkQFOaT:l80<0w,0*12",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@F5QrP0000,0*74",
            "!AIVDM,1,1,,A,1:U7eP`P01u4BqAkNUTcf?w22U98,0*45",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QrR0000,0*06",
            "!AIVDM,1,1,,B,1533381008u4Pk1kOW9KWhJT0000,0*48",
            "!AIVDM,1,1,,A,3:U7N:<Oh3u4BQokNUNl`B@R0Pjh,0*2C",
            "!AIVDM,1,1,,A,2:U7:o1004M4BV=kNcvSV2DV0D13,0*2F",
            "!AIVDM,1,1,,A,1:UEGH0008M4WJEkOnJaGA2V0D1R,0*0F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QrT0000,0*00",
            "!AIVDM,1,1,,B,1:U8N90P01M4@@CkOS;Ivgv`2<0d,0*37",
            "!AIVDM,1,1,,A,1:U7Gg@Oh<M4GkskPKJ91DhT06iP,0*67",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@F5QrV0000,0*7C",
            "!AIVDM,1,1,,A,1:U713P000M4?A=kODtVHQpR00RI,0*75",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@F5Qr`0000,0*4A",
            "!AIVDM,1,1,,A,1:U73IP000M4?aIkO@CrjJDd0<1>,0*6D",
            "!AIVDM,1,1,,A,1:U8KJ0Oi2u4P;akP46E3kjd2@<a,0*2B",
            "!AIVDM,1,1,,B,1:U7N:<Oh3u4BQukNUNT:BB`0l0t,0*1F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@65Qrb0000,0*38",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@F5Qrd0000,0*4C",
            "!AIVDM,1,1,,A,2:U7:o1004M4BV=kNcvSL2Bf0<14,0*7C",
            "!AIVDM,1,1,,B,1:U7DlPP03M4Go7kPKT:Rwvh0H=h,0*09",
            "!AIVDM,1,1,,A,3:U7N:<Oh3u4BR1kNUNTQRBd0Qu@,0*6A",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2kkNuU8ewvd26iP,0*1E",
            "!AIVDM,1,1,,A,3815H71005M4iBSkNpD;`Q0h0Dvb,0*70",
            "!AIVDM,1,1,,B,1:U7Ok0P01M4BqqkNUN9Nwvh28=t,0*51",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@65Qrf0000,0*3E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@65Qrh0000,0*30",
            "!AIVDM,1,1,,B,3:U7@T0Oh;M4WM=kNm@mK24l00o0,0*33",
            "!AIVDM,1,1,,B,277De55000M4IUWkQFOQOrlN0<0w,0*02",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@65Qrj0000,0*32",
            "!AIVDM,1,1,,A,1:U8QsP002u4B7kkObU=N1nf2D2P,0*12",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@65Qrl0000,0*34",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BqUkNUTcf?wF2U98,0*27",
            "!AIVDM,1,1,,B,3:U7N:<Oh3u4BR7kNUN3ljDl0Q6h,0*68",
            "!AIVDM,1,1,,A,3:U7V31404u4Qd;kNOS@66Rn:D`:,0*07",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@65Qrn0000,0*36",
            "!AIVDM,1,1,,A,1:U7@T0Oh:M4WMEkNm>5NR8r0@@U,0*20",
            "!AIVDM,1,1,,A,2:U7:o1004M4BVQkNcvS?R@r0H@l,0*48",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5Qrp0000,0*0F",
            "!AIVDM,1,1,,B,1:UEGH0004M4WJOkOnG:U10r0@A3,0*0D",
            "!AIVDM,1,1,,A,1:U8N90P01M4@@=kOS;r1gvr2D0d,0*5C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5Qrr0000,0*0D",
            "!AIVDM,1,1,,A,B:U7Dn001GA5vgtp6cAPq=f02h06,0*03",
            "!AIVDM,1,1,,B,1:U713PP00M4?AakODtVHgvl08AS,0*45",
            "!AIVDM,1,1,,B,406iKEAvRdFHMu4BB3kOtNw00<0g,0*42",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?V5Qrt0000,0*33",
            "!AIVDM,1,1,,B,3:U7@T0Oh?M4WMakNm:Ue2<v01u0,0*0E",
            "!AIVDM,1,1,,A,1:U7N:<003u4BR=kNUMSnRDt0pBQ,0*69",
            "!AIVDM,1,1,,A,1:U8w4PP0OM4m>MkNH19Jgvr0@BU,0*30",
            "!AIVDM,1,1,,B,1:U8KJ0016u4P@AkP3MmJ3i028BW,0*42",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2wkNuV8ewvv28Ba,0*04",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa?n5Qrv0000,0*0B",
            "!AIVDM,1,1,,B,1:U73IP000M4?aIkO@CbjJC208C1,0*56",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa?n5Qs00000,0*4C",
            "!AIVDM,1,1,,A,3815DI50h0M4IHQkQF=`fbk20Dib,0*53",
            "!AIVDM,1,1,,A,3:U8N41P@7M4Wd3kO9Ihw0u40DoJ,0*3C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa?n5Qs20000,0*4E",
            "!AIVDM,1,1,,A,1:U7Ok0P01u4Br;kNUKajww42HCo,0*12",
            "!AIVDM,1,1,,A,3:U7@T0Oh;M4WMckNm:5ejA4018h,0*19",
            "!AIVDM,1,1,,A,1:U7DlPP03M4GoCkPKT;OOw40L1O,0*28",
            "!AIVDM,1,1,,A,2:U7:o1004M4BVQkNd13?RA400Ra,0*48",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65Qs40000,0*61",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@65Qs60000,0*61",
            "!AIVDM,1,1,,A,277De55001M4IUKkQFNtjblj0<0w,0*29",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@F5Qs80000,0*1D",
            "!AIVDM,1,1,,B,3:U8QsP001u4B7okObSh01q4205j,0*3D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@F5Qs:0000,0*1D",
            "!AIVDM,1,1,,B,B:U88b000OA4JitouCL07wk4oP06,0*34",
            "!AIVDM,1,1,,A,2:U7:o1003M4BVmkNct3IR?>0D14,0*71",
            "!AIVDM,1,1,,B,1:U7@T0Oh?M4WN9kNm4Eo2E>08Fh,0*10",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@F5Qs<0000,0*1B",
            "!AIVDM,1,1,,A,1:U7Gg@P@6M4GkwkPKHmnTa:08Fw,0*26",
            "!AIVDM,1,1,,A,1:UEGH0006M4WJUkOnIahQ5@0@G9,0*25",
            "!AIVDO,1,1,,,1:U7AQi000M4AkekOa@F5Qs>0000,0*19",
            "!AIVDM,1,1,,B,1:U8N90P00M4@@5kOS;r;?wB20R9,0*7E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@F5Qs@0000,0*65",
            "!AIVDM,1,1,,A,1:U73IP000M4?aCkO@CJjJCB0D1>,0*06",
            "!AIVDM,1,1,,A,1:U713PP00M4?AOkODu6Hgw<00Rm,0*7D",
            "!AIVDM,1,1,,A,3:U7@T0Oh<M4WN?kNm3EnjID01lh,0*1F",
            "!AIVDM,1,1,,B,1:U7N:<004u4BROkNUMThjC@0hHN,0*18",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@65QsB0000,0*19",
            "!AIVDM,1,1,,A,1:U8w4PP0NM4m<AkNGt9W?w@0<0n,0*36",
            "!AIVDM,1,1,,B,B:U78k@00gA49:toq?RfOwm7GP06,0*2F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa?n5QsD0000,0*36",
            "!AIVDM,1,1,,A,2:U7:o1003M4BW9kNcqSQ2?F0<14,0*39",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2skNuUHewwD2<17,0*62",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QsF0000,0*13",
            "!AIVDM,1,1,,B,1:U7Ok0P01M4BrMkNUKIl?wJ26iP,0*2C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@65QsH0000,0*13",
            "!AIVDM,1,1,,B,277De55000M4IU;kQFMLBrm40<0w,0*07",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QsJ0000,0*1F",
            "!AIVDM,1,1,,A,1:U8QsP000u4B7skObSP01qD2<2P,0*58",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@65QsL0000,0*19",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@F5QsN0000,0*6B",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BqUkNUTa7gv82d12,0*60",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@F5QsP0000,0*75",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@F5QsR0000,0*79",
            "!AIVDM,1,1,,B,1:U713PP00M4?AAkODt6HgwL08MB,0*39",
            "!AIVDM,1,1,,B,406iKEAvRdFHiu4BB9kOtNw008MC,0*31",
            "!AIVDM,1,1,,A,1:U8N90P00M4@@3kOS<b:OwV26iP,0*5D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@V5QsT0000,0*61",
            "!AIVDM,1,1,,A,1:U8w4PP0PM4m:5kNGj9R?wP0@Mu,0*4B",
            "!AIVDM,1,1,,A,1:U7N:<004u4BRekNUKUJBET0`N1,0*5F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@V5QsV0000,0*6D",
            "!AIVDM,1,1,,B,3:U7@T0Oh@M4WNqkNlo60RQ`01rh,0*44",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2skNuTpewwV2<17,0*4A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@n5Qs`0000,0*6D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkgkOa@n5Qsb0000,0*6F",
            "!AIVDM,1,1,,A,3:U7@T0Oh@M4WO9kNlkF52Qd01;h,0*52",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@n5Qsd0000,0*67",
            "!AIVDM,1,1,,A,1:U7DlPP02M4GnekPKS<B?wf0@PB,0*41",
            "!AIVDM,1,1,,B,3:U8WSU000M4?H7kOCTcViwh0DTJ,0*03",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@n5Qsf0000,0*65",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaA65Qsh0000,0*30",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAF5Qsj0000,0*42",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BqUkNUT``gvL2d12,0*41",
            "!AIVDM,1,1,,A,2:U7:o1P@3M4BWMkNclSjR;n06iP,0*01",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAF5Qsl0000,0*44",
            "!AIVDM,1,1,,B,1:U8N90P04M4@?qkOS;rIOv02<0d,0*03",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaA65Qsn0000,0*36",
            "!AIVDM,1,1,,B,1:U:8`000UM4MCukPJ:BtQQl0H01,0*16",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAF5Qr00000,0*19",
            "!AIVDM,1,1,,B,1:U7N:<003u4BS3kNUI4qjB00h11,0*68",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAF5Qr20000,0*1B",
            "!AIVDM,1,1,,A,1:U8KJ0OhwM4PN7kP23U7kb420SS,0*16",
            "!AIVDM,1,1,,A,3:U7@T000AM4WP1kNlWUwRT601fP,0*5C",
            "!AIVDM,1,1,,A,1:U73IP000M4?aAkO@D:jJD6081D,0*06",
            "!AIVDM,1,1,,A,1:U8w4PP0OM4m6ukNG`9Tgv006iT,0*5E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaA65Qr40000,0*6D",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2qkNuUpewv42<17,0*29",
            "!AIVDM,1,1,,B,1:U7DlPP02M4GnekPKTtJOv80<1O,0*3A",
            "!AIVDM,1,1,,B,B:U8seP00?A45otoprTOswQVSP06,0*62",
            "!AIVDM,1,1,,A,B:U8seP00?A45otoprTOswQVSP06,0*61",
            "!AIVDM,1,1,,A,3:U7N:<P@3u4BS7kNUHlbj@40Qu0,0*4D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaA65Qr60000,0*6F",
            "!AIVDM,1,1,,B,H:U8seP>1@Dm0E=@4@F22222220,2*20",
            "!AIVDM,1,1,,A,H:U8seTl00`0000@ColjqP000008,0*34",
            "!AIVDM,1,1,,B,3:U7N:<P@3u4BS7kNUHTbj@60PIh,0*11",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@n5Qr80000,0*3C",
            "!AIVDM,1,1,,B,3:U7@T000BM4WP7kNlU5qjV:00tP,0*1B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@V5Qr:0000,0*02",
            "!AIVDM,1,1,,B,277De55001M4ISwkQFHM`rmf0<0v,0*39",
            "!AIVDM,1,1,,B,3:U7N:<P@3u4BS;kNUHDDR>:0Pwh,0*5F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@V5Qr<0000,0*04",
            "!AIVDM,1,1,,B,1:U7eP`P01u4BqUkNUT`:Ovf2h4T,0*74",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@F5Qr>0000,0*16",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@65Qr@0000,0*1C",
            "!AIVDM,1,1,,A,1:U7@T000BM4WPQkNlOUnRTB0<1a,0*23",
            "!AIVDM,1,1,,A,1:U8N90P01M4@?skOS=rOgvD2@5N,0*08",
            "!AIVDM,1,1,,B,1:UEGH0004M4WJakOnQ6<i2D0D1R,0*29",
            "!AIVDM,1,1,,B,1:U713PP00M4?AQkODuVHgv<0L0p,0*02",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa?n5QrB0000,0*39",
            "!AIVDM,1,1,,B,406iKEAvRdFI9u4BB9kOtOg006iT,0*4C",
            "!AIVDM,1,1,,B,33nSn:5000M4?nkkO=UI8lfF0Db:,0*57",
            "!AIVDM,1,1,,B,1:U73IP000M4?aCkO@CrjJDF06iT,0*7E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa?n5QrD0000,0*3F",
            "!AIVDM,1,1,,A,1:U7N:<P@3u4BSAkNUHD;B8D0d0t,0*5C",
            "!AIVDM,1,1,,B,3:U7@T0P@CM4WPakNlLUsjTH01u0,0*37",
            "!AIVDM,1,1,,B,1:U8KJ0Oi1M4PRikP1S57SjH2D2E,0*5C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa?n5QrF0000,0*3D",
            "!AIVDM,1,1,,B,B:U7RM0017A4n?toa2btJFUP2h06,0*09",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa?V5QrH0000,0*0B",
            "!AIVDM,1,1,,A,2:U7:o1P@2M4B`IkNcgSIR4L06iT,0*32",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa?F5QrJ0000,0*07",
            "!AIVDM,1,1,,A,3:U7@T0P@BM4WPkkNlJmuBRL014@,0*1C",
            "!AIVDM,1,1,,A,1:U7Ok0P02M4Br1kNUKI7OvN26iT,0*7A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?F5QrL0000,0*03",
            "!AIVDM,1,1,,A,3:U8KJ0Oi1M4PT3kP1G5>SnN21uh,0*01",
            "!AIVDM,1,1,,A,1:U7DlPP02M4GnikPKSsugvN0<1O,0*54",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?F5QrN0000,0*01",
            "!AIVDM,1,1,,A,277De55001M4IU1kQFEttrl80D0v,0*7D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?65QrP0000,0*6F",
            "!AIVDM,1,1,,B,H:U8e;P>0`4@D00000000000000,2*68",
            "!AIVDM,1,1,,A,3:U7N:<P@3u4BSKkNUHT7j0P0Pqh,0*15",
            "!AIVDM,1,1,,A,3:U8RIQOh3M4WdIkOJmU70vR0Do:,0*4B",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BqUkNUTWf?w22PRn,0*5C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?F5QrR0000,0*1D",
            "!AIVDM,1,1,,A,H:U7Dn4lC81>G59@Ijhkm0000000,0*46",
            "!AIVDM,1,1,,A,1:UEGH0004M4WJskOnQU=A6V0@;2,0*0A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?F5QrT0000,0*1B",
            "!AIVDM,1,1,,B,3:U8KJ0012u4PUwkP1;5:3r`20s@,0*5E",
            "!AIVDM,1,1,,B,1:U8N90P01M4@?kkOS>:0Ov`28;M,0*5E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?65QrV0000,0*69",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?65Qr`0000,0*5F",
            "!AIVDM,1,1,,A,1:U8w4PP0QM4m1akNGAaOgvT06iT,0*55",
            "!AIVDM,1,1,,A,1:U73IP000M4?aGkO@CbjJBd08<P,0*12",
            "!AIVDM,1,1,,B,H:U8e;Tl0000000@IJ?000000000,0*20",
            "!AIVDM,1,1,,A,1:U8KJ0Oi1M4PVmkP14E@l0d2<2E,0*0E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa?65Qrb0000,0*5D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa>n5Qrd0000,0*02",
            "!AIVDM,1,1,,A,2:U7:o1002M4B`IkNce41R2f08=V,0*4B",
            "!AIVDM,1,1,,A,3:U7N:<P@2u4BSWkNUGl;1pd0R3P,0*64",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2skNuV`ewvd20R4,0*04",
            "!AIVDM,1,1,,B,1:U7Ok0P00M4BqwkNUJq7wvh26iT,0*19",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa>F5Qrf0000,0*28",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5Qrh0000,0*24",
            "!AIVDM,1,1,,B,3:U8KJ0Oi2u4P`ukP0l5BT6l21tP,0*59",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>65Qrj0000,0*56",
            "!AIVDM,1,1,,B,277De55001M4IUukQFGe0blL0D0v,0*09",
            "!AIVDM,1,1,,A,1:U8QsP001u4B7WkObTh01nd2@?F,0*1A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=n5Qrl0000,0*0B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=n5Qrn0000,0*09",
            "!AIVDM,1,1,,B,3:U7N:<P@3u4BSgkNUGlTAjn0Phh,0*38",
            "!AIVDM,1,1,,A,1:U7@T0P@CM4WR9kNl=UcjHr0<1a,0*33",
            "!AIVDM,1,1,,A,2:U7:o1001M4B`IkNcgT920r0D14,0*46",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=V5Qrp0000,0*2F",
            "!AIVDM,1,1,,B,1:UEGH0008M4WKAkOnQ3aA6r0<1R,0*3E",
            "!AIVDM,1,1,,A,1:U8N90P00M4@?ekOS;:FOvt2@A7,0*4D",
            "!AIVDM,1,1,,A,B:U8e;P00WA4cLLoaI80;wfToP06,0*74",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=V5Qrr0000,0*2D",
            "!AIVDM,1,1,,B,1:U713PP00M4?AikODwFHQpl06iT,0*4F",
            "!AIVDM,1,1,,B,406iKEAvRdFIMu4BB9kOtPO008AU,0*28",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=V5Qrt0000,0*2B",
            "!AIVDM,1,1,,A,1:U8w4PP0SM4lvmkNG2aEgvr0<0o,0*2A",
            "!AIVDM,1,1,,B,1:U8KJ0Oi4u4Pc;kP0L5Tl?026iT,0*55",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2mkNuUpewvv26iT,0*45",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=V5Qrv0000,0*29",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=n5Qs00000,0*56",
            "!AIVDM,1,1,,A,2:U7:o1001M4B`5kNcj4JQw20@CK,0*49",
            "!AIVDM,1,1,,B,3:U7N:<P@2u4BSmkNUFlcAg00Qsh,0*4C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>65Qs20000,0*0F",
            "!AIVDM,1,1,,A,1:U7Ok0P01M4Br9kNUKIbgw42D1D,0*4D",
            "!AIVDM,1,1,,A,1:U7DlPP02M4GnokPKRd2gw40HCr,0*43",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>65Qs40000,0*09",
            "!AIVDM,1,1,,A,3:U8KJ0Oi0M4PdKkP0@UN4E6222@,0*06",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5Qs60000,0*7B",
            "!AIVDM,1,1,,A,277De55000M4IVmkQFJLWblh0D0v,0*77",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5Qs80000,0*75",
            "!AIVDM,1,1,,A,3:U7N:<P@2u4BSokNUFU3Qc80Q40,0*27",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BqAkNUTWf?wb2d12,0*13",
            "!AIVDM,1,1,,B,1:U8QsP002u4B7IkObUP01o420Rc,0*54",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>n5Qs:0000,0*5F",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNclTC1u>0@Ff,0*70",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>n5Qs<0000,0*59",
            "!AIVDM,1,1,,B,1:U7@T000EM4WS3kNl65TRI>06iT,0*63",
            "!AIVDM,1,1,,B,1:U8N90P02M4@?MkOS9rROw>2HFr,0*3B",
            "!AIVDM,1,1,,B,3:U8KJ0Oi6u4PeakOwsmkDK>214h,0*3D",
            "!AIVDM,1,1,,A,1:U7Gg@Oh9M4GlEkPKE0@Dg:06iT,0*41",
            "!AIVDM,1,1,,A,1:UEGH0005M4WKCkOnMT6Q5@0<1R,0*3F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>n5Qs>0000,0*5B",
            "!AIVDM,1,1,,A,406iKEAvRdFIWu4BB9kOtPO006iT,0*16",
            "!AIVDM,1,1,,A,1:U713PP00M4?AckODv6Hgw:0L0p,0*57",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5Qs@0000,0*0D",
            "!AIVDM,1,1,,A,1:U73IP000M4?aOkO@BbjJCB0@Gu,0*1A",
            "!AIVDM,1,1,,B,3:U74Tm0@1u4?v9kO<ArC:AB2E6J,0*69",
            "!AIVDM,1,1,,B,1:U7N:<P@2u4BSqkNUFU?1W@0d0t,0*6D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5QsB0000,0*0F",
            "!AIVDM,1,1,,A,1:U8w4PP0aM4lr9kNFfaC?w@08Ht,0*17",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5QsD0000,0*09",
            "!AIVDM,1,1,,A,1:U8KJ0Oi3u4PfwkOwf5hTUF2@I;,0*4B",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNclTH1sF08I?,0*2B",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2okNuU8ewwD28IF,0*03",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5QsF0000,0*0B",
            "!AIVDM,1,1,,A,3:U7N:<P@2u4BSwkNUFEOAUF0QtP,0*2B",
            "!AIVDM,1,1,,B,1:U7Ok0P02M4BqakNULs7gwJ20Rl,0*3F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5QsH0000,0*05",
            "!AIVDM,1,1,,B,277De55000M4IWAkQFK<Wbm40D0u,0*76",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa>F5QsJ0000,0*19",
            "!AIVDM,1,1,,A,1:U8QsP002u4B7KkObU@01oF28K9,0*7C",
            "!AIVDM,1,1,,B,3:U8KJ0Oi4u4Ph5kOwMErTcN21h@,0*55",
            "!AIVDM,1,1,,B,3:U7N:<P@2u4BT1kNUF5F1SJ0Q4P,0*2A",
            "!AIVDM,1,1,,B,3:U7@T0P@>M4WSmkNl0E72;N00i@,0*31",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa>65QsL0000,0*6F",
            "!AIVDM,1,1,,B,353<TP1Oh;M4QkmkO@:HwhgN0D`r,0*6D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>65QsN0000,0*73",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNclTn1qR00Rt,0*43",
            "!AIVDM,1,1,,A,3:U8KJ0Oi2u4PhUkOwDEuDiR20p@,0*21",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa=n5QsP0000,0*28",
            "!AIVDM,1,1,,B,3:U7sn5000M4>KAkOMsq4isT0E1r,0*3C",
            "!AIVDM,1,1,,B,1:UEGH0006M4WKQkOnI5<15T0<1R,0*36",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=n5QsR0000,0*34",
            "!AIVDM,1,1,,B,1:U713PP00M4?AckODtFHQqL06iT,0*67",
            "!AIVDM,1,1,,B,406iKEAvRdFIiu4BB9kOtQ?006iT,0*5A",
            "!AIVDM,1,1,,A,1:U8N90P01M4@?;kOS8:LOwV20Ri,0*05",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=V5QsT0000,0*0A",
            "!AIVDM,1,1,,A,1:U8w4PP0cM4loEkNFR9C?wP0<0n,0*6E",
            "!AIVDM,1,1,,A,1:U7N:<P@2u4BT7kNUDmIAOT0W3h,0*33",
            "!AIVDM,1,1,,B,1:U73IP000M4?aKkO@ArjJE`08N:,0*14",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=V5QsV0000,0*08",
            "!AIVDM,1,1,,B,3:U7@T0P@@M4WTKkNksU6Aw`01mP,0*3F",
            "!AIVDM,1,1,,B,1:U8KJ0Oi4u4PiQkOw1F6lqb26iT,0*1D",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2ukNuTHewwV28Nj,0*52",
            "!AIVDM,1,1,,A,1:U7Ok0P02M4BqikNUIctOwb2<1D,0*25",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=F5Qs`0000,0*2E",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNclUFQob0D14,0*73",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=F5Qsb0000,0*2C",
            "!AIVDM,1,1,,B,3:U7N:<P@2u4BT7kNUDUaQM`0Qo@,0*76",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=F5Qsd0000,0*2A",
            "!AIVDM,1,1,,A,1:U7DlPP01M4GoIkPKNK:?wf0<1O,0*6D",
            "!AIVDM,1,1,,A,277De55000M4IWCkQFL6u:mF0D0u,0*72",
            "!AIVDM,1,1,,A,3:U7@T0P@;M4WTKkNksE51oh00q0,0*49",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=F5Qsf0000,0*28",
            "!AIVDM,1,1,,B,38Hupk5w00M4F8qkPHAqDRAf0Dtr,0*3C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=65Qsh0000,0*56",
            "!AIVDM,1,1,,B,1:U8QsP001u4B7KkObTh01od20Rh,0*37",
            "!AIVDM,1,1,,A,3:U7N:<P@2u4BT7kNUDEIiIh0Pu0,0*12",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa<n5Qsj0000,0*0D",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BqAkNUW;;wvL2`R:,0*29",
            "!AIVDM,1,1,,B,3:U8KJ0Oi4u4PjIkOvbn?m3n21;0,0*09",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa<V5Qsl0000,0*33",
            "!AIVDM,1,1,,B,1:U7@T0P@<M4WTgkNkr56Agn0<1a,0*72",
            "!AIVDM,1,1,,A,1:UEGH0005M4WKakOnG5>A200<1R,0*19",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<V5Qsn0000,0*2F",
            "!AIVDM,1,1,,A,406iKEAvRdFIsu4BB9kOtQ?006i`,0*77",
            "!AIVDM,1,1,,A,1:U713PP00M4?AUkODtVHgwj06i`,0*60",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<V5Qr00000,0*70",
            "!AIVDM,1,1,,A,3:U7@T0P@9M4WTikNkpm:1`401ph,0*46",
            "!AIVDM,1,1,,B,1:U7N:<P@2u4BT9kNUDEIiF00d0t,0*7F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<65Qr20000,0*12",
            "!AIVDM,1,1,,A,1:U8KJ0PA5u4PkQkOvE6Dm462L2D,0*7C",
            "!AIVDM,1,1,,A,1:U8w4PP0dM4ljEkNF@aM?v000RQ,0*18",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa;n5Qr40000,0*4B",
            "!AIVDM,1,1,,A,1:U7URgP00M4A33kNuTHewv4281e,0*05",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNclVLQj8081q,0*1C",
            "!AIVDM,1,1,,B,1:U7DlPP02M4GoGkPKNK3Ov80823,0*3E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa;V5Qr60000,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa;V5Qr80000,0*7F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa;F5Qr:0000,0*6D",
            "!AIVDM,1,1,,B,3:U8KJ0Oi4u4PkqkOv8nLE8>21fh,0*6F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa;V5Qr<0000,0*7B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa;V5Qr>0000,0*79",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<65Qr@0000,0*60",
            "!AIVDM,1,1,,B,1:UEGH0P@6M4WKQkOnDV3A0D0@5U,0*5D",
            "!AIVDM,1,1,,B,1:U713P000M4?AUkODunHQp<0H5c,0*7C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<V5QrB0000,0*02",
            "!AIVDM,1,1,,B,406iKEAvRdFJ9u4BB9kOtQ?000S:,0*5B",
            "!AIVDM,1,1,,B,1:U73IP000M4?aAkO@A:jJDF00Sk,0*35",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<65QrD0000,0*64",
            "!AIVDM,1,1,,B,3:U7@T0P@5M4WU3kNkl5TQ@H026@,0*69",
            "!AIVDM,1,1,,A,1:U7N:<P@1u4BT?kNUCmIi<D0`6i,0*47",
            "!AIVDM,1,1,,B,1:U8KJ0PA5u4Pm1kOudFGU8H2@6n,0*20",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<V5QrF0000,0*06",
            "!AIVDM,1,1,,A,1:U8w4PP0fM4leEkNEw9M?vD0@7Q,0*18",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa<V5QrH0000,0*16",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2okNuS`ewvH287V,0*3D",
            "!AIVDM,1,1,,B,3:U7N:<P@1u4BT?kNUCUIi:H0R4h,0*45",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa<V5QrJ0000,0*14",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNclW<1fL00S;,0*55",
            "!AIVDM,1,1,,A,3:U7@T0P@7M4WU;kNkjEf1:N016P,0*2B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa<V5QrL0000,0*12",
            "!AIVDM,1,1,,A,1:U7DlPP01M4GoCkPKOc@?vN088h,0*37",
            "!AIVDM,1,1,,A,3:U8KJ0Oi5u4PmGkOuN6Qm8N220P,0*58",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa<n5QrN0000,0*36",
            "!AIVDM,1,1,,B,1:U8QsP001u4B7CkObU001nH289L,0*0C",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BqAkNUW;;ww02d12,0*3B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa<n5QrP0000,0*36",
            "!AIVDM,1,1,,A,3:U7N:<P@1u4BT?kNUCEIi6P0Po@,0*33",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa=65QrR0000,0*73",
            "!AIVDM,1,1,,B,1:U7@T0P@8M4WU1kNkjF1A0T00S@,0*6F",
            "!AIVDM,1,1,,B,3:U8KJ0Oi6u4Pn;kOu@nJ5:V21>@,0*35",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4BWikNcj7RQdV0D14,0*57",
            "!AIVDM,1,1,,A,1:UEGH0004M4WKSkOnD6uhvV0<1R,0*6A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa=F5QrT0000,0*05",
            "!AIVDM,1,1,,A,1:U713P000M4?ASkODsnHQpP0@;G,0*31",
            "!AIVDM,1,1,,B,1:U8N90P02M4@??kOS7brOv`26i`,0*6B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa=F5QrV0000,0*19",
            "!AIVDM,1,1,,A,1:U7Gg@P@7M4GlEkPKFLvD`T0@;g,0*4F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa=V5Qr`0000,0*21",
            "!AIVDM,1,1,,B,3533381002u4PhAkOW@`L@Tb0DWr,0*2B",
            "!AIVDM,1,1,,A,1:U8w4PP0gM4laqkNEjaR?vT00SV,0*70",
            "!AIVDM,1,1,,B,1:U:8`000QM4MdckPKDBUALV0@<I,0*36",
            "!AIVDM,1,1,,A,1:U8KJ0016u4PnOkOu1nP5:d28<a,0*14",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa=n5Qrb0000,0*1B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa>65Qrd0000,0*46",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4BWikNcj7nQbf06i`,0*23",
            "!AIVDM,1,1,,B,1:U7DlPP02M4Go9kPKPL2Ovh0@=h,0*24",
            "!AIVDM,1,1,,A,3:U7N:<P@1u4BTCkNUCEIhvd0R:0,0*1D",
            "!AIVDM,1,1,,B,1:U7Ok0P00u4BqwkNULe:Ovh20SI,0*27",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa>F5Qrf0000,0*34",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa>F5Qrh0000,0*3A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>n5Qrj0000,0*0E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa>F5Qrl0000,0*20",
            "!AIVDM,1,1,,B,3:U7N:<P@1u4BTEkNUCEIhnl0PwP,0*27",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BqAkNUW;;wwF2p@C,0*5A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa>n5Qrn0000,0*08",
            "!AIVDO,1,1,,B,3:U7AQi000M4AkqkOa>F5Qrl0000,0*60",
            "!AIVDM,1,1,,A,1:U7@T0P@:M4WTakNkeWj0`r08@U,0*73",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNcg`m1Vr0@@l,0*02",
            "!AIVDM,1,1,,A,3:U8KJ0Oi7u4PoOkOtJn`5Br2130,0*42",
            "!AIVDO,1,1,,,1:U7AQi000M4AkukOa>n5Qrp0000,0*10",
            "!AIVDM,1,1,,A,1:U8N90P02M4@?GkOS8K0wvt2<0d,0*0F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOa>n5Qrr0000,0*10",
            "!AIVDM,1,1,,B,1:U713PP00M4?AUkODsnHgvl00Rs,0*75",
            "!AIVDM,1,1,,B,406iKEAvRdFJMu4BB3kOtQ?006i`,0*43",
            "!AIVDM,1,1,,B,3:U7@T0P@;M4WTkkNkcoE@Rv025@,0*44",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa?65Qrt0000,0*0C",
            "!AIVDM,1,1,,A,1:U7N:<P@2u4BTEkNUCEIhft0hBQ,0*39",
            "!AIVDM,1,1,,A,1:U8w4PP0iM4lVMkNESaOgvr08BU,0*35",
            "!AIVDM,1,1,,B,1:U8KJ0Oi5u4PoakOt=FfmI020S0,0*46",
            "!AIVDM,1,1,,B,1:U7URgP00M4A3?kNuRHewvv20SJ,0*0B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al5kOa?F5Qrv0000,0*78",
            "!AIVDM,1,1,,B,1:U73IP000M4?a5kO@A:jJE200Rw,0*29",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa?V5Qs00000,0*23",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4B`5kNcga41U20<14,0*4C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@65Qs20000,0*3E",
            "!AIVDM,1,1,,A,3:U7Ok0P01M4Br1kNUMdv?w4263C,0*57",
            "!AIVDM,1,1,,A,1:U7DlPP02M4Go9kPKPLGgw40D1N,0*09",
            "!AIVDM,1,1,,B,3:U7N:<P@1u4BTAkNUCEIha20Qlh,0*50",
            "!AIVDM,1,1,,A,3:U7@T0P@?M4WT9kNkbHAhM6012@,0*40",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@F5Qs40000,0*48",
            "!AIVDM,1,1,,B,35MCqF50@0M4?3gkOGgFh1w80DNb,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOa@F5Qs60000,0*48",
            "!AIVDM,1,1,,A,277De55001M4IVekQFOL7blh0@E3,0*2F",
            "!AIVDM,1,1,,A,3:U8KJ0Oi7M4Pp1kOspVdmO8223h,0*5E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOa@V5Qs80000,0*50",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BqAkNUW;;wwb2`Eu,0*5E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOa@F5Qs:0000,0*44",
            "!AIVDM,1,1,,A,3:U7N:<P@2u4BTCkNUCK=PQ:0PhP,0*15",
            "!AIVDM,1,1,,B,1:U7@T0P@=M4WTMkNk``7hC>00S0,0*7D",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOa@F5Qs<0000,0*44",
            "!AIVDM,1,1,,B,1:U8N90P02M4@?CkOS7;3ww>2D0d,0*47",
            "!AIVDM,1,1,,A,1:U7Gg@007M4GlEkPKFr2Tc:00SP,0*77",
            "!AIVDM,1,1,,A,3:UEGH0007M4WKUkOnCFAi1@07G3,0*62",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@F5Qs>0000,0*44",
            "!AIVDM,1,1,,A,406iKEAvRdFJWu4BB3kOtQ?000S:,0*3C",
            "!AIVDM,1,1,,B,3:U8KJ0Oi5u4Pp;kOsUngmS@20p@,0*7E",
            "!AIVDM,1,1,,A,1:U713PP00M4?AOkODt6Hgw:0HGl,0*16",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@V5Qs@0000,0*2A",
            "!AIVDM,1,1,,A,3:U73IP000M4?a3kO@A:jJEB06QC,0*6F",
            "!AIVDM,1,1,,A,3:U7@T0P@AM4WSkkNkU`C0=D00v@,0*69",
            "!AIVDM,1,1,,B,1:U7N:<P@2u4BTAkNUC;=PK@0`HN,0*08",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@V5QsB0000,0*28",
            "!AIVDM,1,1,,A,1:U8w4PP0kM4lPmkNE=9R?w@06i`,0*41",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@V5QsD0000,0*2E",
            "!AIVDM,1,1,,A,1:U8KJ0Oi6u4Pp;kOsEVq5WF2<2C,0*55",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4BWikNcj9;QQF06i`,0*6B",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2wkNuR8ewwD26i`,0*14",
            "!AIVDM,1,1,,A,3:U7N:<P@2u4BT?kNUC;V@ID0QwP,0*1A",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@F5QsF0000,0*3C",
            "!AIVDM,1,1,,B,1:U7Ok0P01u4BqskNUN<W?wH2D1B,0*58",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@F5QsH0000,0*32",
            "!AIVDM,1,1,,B,3:U7@T0P@?M4WSekNkT8Q05J00n0,0*3F",
            "!AIVDM,1,1,,B,277De55001M4IVUkQFOL9bm40@Jl,0*1F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@F5QsJ0000,0*30",
            "!AIVDM,1,1,,B,3:U8KJ0PA7u4Pp?kOs5ntmWL21n@,0*2B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOa@65QsL0000,0*46",
            "!AIVDM,1,1,,B,3:U7N:<P@2u4BT9kNUCKRhCL0Q;P,0*0D",
            "!AIVDM,1,1,,B,39NS`<1002M4T`AkOKo<LA7J0DbJ,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4AlAkOa@65QsN0000,0*3A",
            "!AIVDM,1,1,,A,2:U7:o1P@1M4BWMkNcla6QOR0HLB,0*6F",
            "!AIVDM,1,1,,B,1:U7eP`P01u4BpukNUW:7Ov82U9D,0*7F",
            "!AIVDM,1,1,,A,3:U7@T0P@?M4WRskNkSpCK?R0101,0*41",
            "!AIVDO,1,1,,,1:U7AQi000M4AlCkOa@65QsP0000,0*26",
            "!AIVDM,1,1,,B,1:UEGH0006M4WKakOnDUhQ1T08M8,0*49",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@65QsR0000,0*22",
            "!AIVDM,1,1,,A,1:U8N90P00M4@?ekOS=:f?wT2HM?,0*36",
            "!AIVDM,1,1,,B,1:U713PP00M4?AGkODunHgwL00Sg,0*55",
            "!AIVDM,1,1,,B,406iKEAvRdFJiu4BB9kOtQ?000S:,0*0B",
            "!AIVDM,1,1,,A,3:U8KJ0Oi6u4PpakOrjFgUaT20fP,0*2A",
            "!AIVDM,1,1,,B,3:U7@T0P@BM4WRMkNkSpps;V01u@,0*3E",
            "!AIVDO,1,1,,,1:U7AQi000M4AlGkOa@65QsT0000,0*26",
            "!AIVDM,1,1,,A,1:U8w4PP0mM4lMekNE0aR?wP08Mu,0*28",
            "!AIVDM,1,1,,A,1:U7N:<P@2u4BT1kNUCd:P9T0PRq,0*50",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@65QsV0000,0*26",
            "!AIVDM,1,1,,B,1:U8KJ0Oi7u4PowkOrRo0Egb20Sa,0*41",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2skNuQ`ewwV26i`,0*5A",
            "!AIVDM,1,1,,A,1:U7Ok0P01u4BqqkNUNdDOwb28Nq,0*78",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@65Qs`0000,0*10",
            "!AIVDM,1,1,,A,3:U7Q`U000M4>eskOLpqi:?b0DR:,0*33",
            "!AIVDM,1,1,,A,2:U7:o1P@2M4BWMkNcl`m1Mb0@O8,0*15",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@65Qsb0000,0*12",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@F5Qsd0000,0*64",
            "!AIVDM,1,1,,A,3:U8KJ0018u4PpCkOrHVwmgf21tP,0*1C",
            "!AIVDM,1,1,,B,3:U7N:<P@3u4BSskNUD<Bh5d0Qv0,0*52",
            "!AIVDM,1,1,,A,3:U7DlPP02M4GnkkPKPskOwf05cC,0*1F",
            "!AIVDM,1,1,,A,3:U7@T0P@=M4WR7kNkR`uK3h00ph,0*0E",
            "!AIVDM,1,1,,A,277De55001M4IVIkQFNul:mH0@PN,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@F5Qsf0000,0*66",
            "!AIVDM,1,1,,B,1:U8QsP001u4B6akObVP01ob2L2P,0*04",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@F5Qsh0000,0*68",
            "!AIVDM,1,1,,A,3:U7N:<P@3u4BSqkNUDdiP1h0Q30,0*55",
            "!AIVDM,1,1,,A,3:U8TvQ001M4U6mkN9?ImQ7j0Dg:,0*55",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@F5Qsj0000,0*6A",
            "!AIVDM,1,1,,A,2:U7:o1P@2M4BWikNcg`tQIn0@R8,0*56",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BpukNUTb7OvL2U9D,0*52",
            "!AIVDM,1,1,,B,3:U8KJ0Oi7u4Pp=kOr4G5Ein214@,0*18",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@V5Qsl0000,0*7C",
            "!AIVDM,1,1,,B,1:U7@T0P@=M4WQakNkPID;1n08RU,0*23",
            "!AIVDM,1,1,,A,1:U7Gg@004M4Gl7kPKF;I4al0D1M,0*0B",
            "!AIVDM,1,1,,B,1:U8N90P01M4@@1kOS?JTwv026id,0*73",
            "!AIVDM,1,1,,A,1:UEGH0005M4WKUkOnBUb10008S3,0*61",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@V5Qsn0000,0*7E",
            "!AIVDM,1,1,,B,H:U7RM0hR0<thu=<t0000000000,2*32",
            "!AIVDM,1,1,,A,1:U713PP00M4?AGkODunHgwj00SL,0*5B",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@n5Qr00000,0*19",
            "!AIVDM,1,1,,B,3:U8ieQq02M4dv7kNuIUO1820Dpr,0*7D",
            "!AIVDM,1,1,,A,3:U7@T0P@:M4WQgkNkNqArv401oP,0*65",
            "!AIVDM,1,1,,A,1:U8w4PP0nM4lGikNDdaTgwn0D0n,0*02",
            "!AIVDM,1,1,,B,1:U7N:<P@3u4BSmkNUE<us>00`11,0*4B",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@n5Qr20000,0*1B",
            "!AIVDM,1,1,,A,H:U7RM4l?>G1000@@E=000000000,0*7E",
            "!AIVDM,1,1,,A,1:U8KJ0Oi9u4PomkOqgG<Un62H1P,0*22",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOa@n5Qr40000,0*1D",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2skNuQpewv426id,0*2E",
            "!AIVDM,1,1,,A,2:U7:o1P@2M4BWikNcga1QF806id,0*5A",
            "!AIVDM,1,1,,B,1:U7DlPP02M4GnukPKPKR?v806id,0*00",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOaA65Qr60000,0*46",
            "!AIVDM,1,1,,B,1:U7Ok0P01u4BqekNULswwv826id,0*16",
            "!AIVDM,1,1,,B,3:U7@T000<M4WQCkNkMaSc08012P,0*53",
            "!AIVDM,1,1,,A,3:U7N:<P@3u4BSkkNUEu6s<60Qk@,0*58",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOaA65Qr80000,0*48",
            "!AIVDM,1,1,,B,3:U77F5000M4>rskOJ39GbH<0Dr:,0*75",
            "!AIVDO,1,1,,,1:U7AQi000M4AlGkOaA65Qr:0000,0*48",
            "!AIVDM,1,1,,B,3:U8KJ0019u4PomkOqPW8Ul<221@,0*45",
            "!AIVDM,1,1,,B,277De55001M4IVAkQFN=Qbmf0@3r,0*26",
            "!AIVDO,1,1,,,1:U7AQi000M4AlKkOaA65Qr<0000,0*42",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUTb7Ovf2`4T,0*47",
            "!AIVDO,1,1,,,1:U7AQi000M4AlKkOaA65Qr>0000,0*40",
            "!AIVDO,1,1,,,1:U7AQi000M4AlKkOaAF5Qr@0000,0*4E",
            "!AIVDM,1,1,,A,1:U8N90P01M4@@7kOS>b?gvD285N,0*28",
            "!AIVDM,1,1,,B,1:UEGH0005M4WKOkOnDV;@vD0<1R,0*60",
            "!AIVDM,1,1,,B,1:U713PP00M4?ASkODuFHgv<0D0p,0*18",
            "!AIVDO,1,1,,,1:U7AQi000M4AlKkOaAF5QrB0000,0*4C",
            "!AIVDM,1,1,,B,406iKEAvRdFK9u4BB9kOtQ?00L0f,0*19",
            "!AIVDO,1,1,,,1:U7AQi000M4AlGkOaAV5QrD0000,0*56",
            "!AIVDM,1,1,,B,3:U7@T000@M4WPmkNkLqkrvH01o@,0*43",
            "!AIVDM,1,1,,A,1:U7N:<P@4u4BSakNUGu7c8D0W3h,0*44",
            "!AIVDM,1,1,,B,1:U8KJ0019u4PoAkOq1W@UrH2<2B,0*17",
            "!AIVDM,1,1,,B,1:U73IP000M4?a5kO@ArjJBH0@6t,0*0B",
            "!AIVDO,1,1,,,1:U7AQi000M4AlKkOaAV5QrF0000,0*58",
            "!AIVDM,1,1,,B,B>pf7jP00OA4JjtouF5>SwUR0000,0*58",
            "!AIVDM,1,1,,A,B>pf7jP01?A4JjtouF1SkwV20000,0*18",
            "!AIVDM,1,1,,B,B>pf7jP01?A4JjtouF1SkwV20000,0*1B",
            "!AIVDM,1,1,,A,1:U8w4PP0oM4lB9kNDHaR?vD0<0n,0*77",
            "!AIVDO,1,1,,,1:U7AQi000M4AlGkOaAV5QrH0000,0*5A",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2okNuR8ewvH26id,0*06",
            "!AIVDM,1,1,,A,1:U7Ok0P01u4BqQkNULceOvL2@7o,0*4C",
            "!AIVDM,1,1,,B,3:U7N:<P@4u4BSakNUHeEK8H0R0P,0*32",
            "!AIVDO,1,1,,,1:U7AQi000M4AlGkOaA65QrJ0000,0*38",
            "!AIVDM,1,1,,A,2:U7:o1P@3M4BW9kNcg`tQ@L0D13,0*40",
            "!AIVDM,1,1,,A,3:U7@T0P@@M4WPWkNkKqqrtL013P,0*3D",
            "!AIVDO,1,1,,,1:U7AQi000M4AlEkOaA65QrL0000,0*3C",
            "!AIVDM,1,1,,A,1:U7DlPP03M4GnkkPKQctgvN06id,0*3D",
            "!AIVDM,1,1,,A,3:U8KJ0018u4PnwkOpkWBmpP21w@,0*11",
            "!AIVDO,1,1,,,1:U7AQi000M4AlAkOa@n5QrN0000,0*63",
            "!AIVDM,1,1,,A,277De55001M4IVAkQFNt<rl80L0w,0*44",
            "!AIVDM,1,1,,B,1:U8QsP002u4B6OkObW0cQnH26id,0*45",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@V5QrP0000,0*3D",
            "!AIVDO,1,1,,,1:U7AQi000M4Al5kOa@F5QrR0000,0*23",
            "!AIVDM,1,1,,B,1:U7@T0Oh<M4WPEkNkMJIbvT0@:W,0*15",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa@V5QrT0000,0*33",
            "!AIVDM,1,1,,A,1:U713PP00M4?AOkODs6HgvP0<0p,0*65",
            "!AIVDM,1,1,,B,1:U8N90P01M4@@=kOS>akOv`20S<,0*66",
            "!AIVDO,1,1,,,1:U7AQi000M4Al5kOa@V5QrV0000,0*37",
            "!AIVDM,1,1,,A,406iKEAvRdFKCu4BB3kOtQ?000S:,0*29",
            "!AIVDM,1,1,,A,1:U7Gg@P@4M4Gl=kPKG:DD`T0<1M,0*2D",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa@V5Qr`0000,0*07",
            "!AIVDM,1,1,,A,3:U7@T000=M4WOwkNkMbqrvd01v@,0*05",
            "!AIVDM,1,1,,B,1:U7N:<004u4BSSkNUJLfK6`0`<f,0*34",
            "!AIVDM,1,1,,A,1:U8w4PP0qM4l>5kND<9R?vV0H<g,0*56",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2okNuRpewvb2L17,0*16",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa@V5Qrb0000,0*05",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@n5Qrd0000,0*39",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@n5Qrf0000,0*3B",
            "!AIVDM,1,1,,B,3:U7@T0Oh@M4WOUkNkMbtK2h010P,0*5C",
            "!AIVDM,1,1,,B,3:U8KJ0Oi8M4PmokOowWKF2j226@,0*0D",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaA65Qrh0000,0*6C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaA65Qrj0000,0*6E",
            "!AIVDM,1,1,,B,277De55001M4IV?kQFNuK:lL0L0v,0*72",
            "!AIVDM,1,1,,A,1:U8QsP001u4B6QkObW001pf28?G,0*23",
            "!AIVDM,1,1,,B,B:V3wjh00OA3nMtoo>?Q3we4WP06,0*63",
            "!AIVDM,1,1,,B,3:U7V31sP4u4QdskNO`L1nNl:Dhr,0*55",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaA65Qrl0000,0*68",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUW:7OwF2l11,0*51",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaA65Qrn0000,0*6A",
            "!AIVDM,1,1,,A,1:U7@T0Oh=M4WOQkNkPsec4r06id,0*67",
            "!AIVDM,1,1,,A,2:U7:o1P@3M4BVQkNcgaEQ6r0<13,0*29",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaA65Qrp0000,0*35",
            "!AIVDM,1,1,,B,1:UEGH0004M4WKWkOnE95Q2r06id,0*1E",
            "!AIVDM,1,1,,B,1:U713PP00M4?AGkODr6HQpl0D0p,0*1B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaA65Qrr0000,0*37",
            "!AIVDM,1,1,,B,406iKEAvRdFKMu4BB3kOtQ?000S:,0*24",
            "!AIVDO,1,1,,,1:U7AQi000M4AkukOa@n5Qrt0000,0*6A",
            "!AIVDM,1,1,,B,1:U8KJ0PA;M4PlukOoOWQ6902@BM,0*28",
            "!AIVDM,1,1,,A,1:U8w4PP0qM4l8MkNCmaOgvr06id,0*6F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkukOaA65Qrv0000,0*31",
            "!AIVDM,1,1,,B,1:U73IP000M4?a=kO@EbjJE00D1=,0*22",
            "!AIVDM,1,1,,B,B:U7<;h00?A3wULopN2gswgVSP06,0*47",
            "!AIVDO,1,1,,,1:U7AQi000M4AkukOaA65Qs00000,0*76",
            "!AIVDM,1,1,,A,2:U7:o1P@3M4BV=kNcgaW13208CK,0*7C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa@n5Qs20000,0*2B",
            "!AIVDM,1,1,,A,1:U7Ok0P02u4Bq?kNUOKEOw42<1B,0*04",
            "!AIVDM,1,1,,A,1:U7DlPP01M4GnwkPKRtdww40@Cr,0*06",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa@V5Qs40000,0*17",
            "!AIVDM,1,1,,A,3:U8KJ0Oi:u4PlIkOo;7Pn=8227h,0*78",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa@V5Qs60000,0*15",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@V5Qs80000,0*05",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@F5Qs:0000,0*17",
            "!AIVDM,1,1,,A,2:U7:o1P@3M4BUqkNcgan0w>08Ff,0*6B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@V5Qs<0000,0*01",
            "!AIVDM,1,1,,B,1:U8N90P01M4@@EkOS>qcgw>2@Fr,0*5A",
            "!AIVDM,1,1,,B,3:U8KJ0Oi;u4PkikOnn7QV?>20vh,0*77",
            "!AIVDM,1,1,,A,3:U7@T0OhHM4WMekNkbct@1@00H@,0*02",
            "!AIVDM,1,1,,A,1:UEGH0004M4WKakOnEHw13@06id,0*4B",
            "!AIVDM,1,1,,A,1:U7Gg@003M4GlAkPKGUo4c<0HGE,0*13",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@n5Qs>0000,0*3F",
            "!AIVDM,1,1,,A,406iKEAvRdFKWu4BB3kOtQ?00L0k,0*73",
            "!AIVDM,1,1,,B,3:U7@T0OhHM4WMekNkbct@1@00fP,0*3F",
            "!AIVDM,1,1,,A,1:U713PP00M4?AGkODs6HQq:0D0o,0*51",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@V5Qs@0000,0*7D",
            "!AIVDM,1,1,,A,1:U73IP000M4?a?kO@CbjJCB08Gu,0*13",
            "!AIVDM,1,1,,B,1:U:8`000PM4N2SkPLKBV1M>00SF,0*50",
            "!AIVDM,1,1,,A,B:U88b000gA4JhtouCg;owlToP06,0*01",
            "!AIVDM,1,1,,B,1:U7N:<004u4BS;kNUML9s1@0W3h,0*2D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@n5QsB0000,0*43",
            "!AIVDM,1,1,,A,B:U78k@00gA49ltoq?Hw3wm7GP06,0*0D",
            "!AIVDM,1,1,,A,1:U8w4PP0rM4l4IkNCVaR?w@00S5,0*44",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@V5QsD0000,0*7D",
            "!AIVDM,1,1,,A,1:U8KJ0Oi:u4PjqkOnSGbFEF28I;,0*66",
            "!AIVDM,1,1,,A,2:U7:o1P@3M4BUqkNce9uPuF00SJ,0*01",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@n5QsF0000,0*43",
            "!AIVDM,1,1,,B,1:U7Ok0P02M4BpskNUPKE?wH2@Ii,0*4E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@n5QsH0000,0*4D",
            "!AIVDM,1,1,,B,3:U7@T000BM4WMOkNkg=7P1J00uP,0*29",
            "!AIVDM,1,1,,B,3:U8KJ0Oi;u4Pj7kOnD7fVIL21q0,0*6F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaA65QsJ0000,0*16",
            "!AIVDM,1,1,,A,1:U8QsP001u4B6QkObWP01mF20Sm,0*30",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaA65QsL0000,0*10",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa@n5QsN0000,0*55",
            "!AIVDM,1,1,,A,2:U7:o1P@4M4BUqkNce:00qR0D13,0*5F",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpEkNUab7Ov82PRW,0*5D",
            "!AIVDM,1,1,,A,1:U7@T0OhIM4WL=kNkkd8P5R0HLF,0*66",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOaA65QsP0000,0*12",
            "!AIVDM,1,1,,B,1:UEGH0003M4WKkkOnGpj13T06id,0*76",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOaA65QsR0000,0*10",
            "!AIVDM,1,1,,A,1:U8N90P02u4@@QkOS?:5gwT2D0e,0*65",
            "!AIVDM,1,1,,B,406iKEAvRdFKiu4BAukOtQw00L0k,0*43",
            "!AIVDM,1,1,,A,3:U8KJ0Oi;u4PiMkOmvoc6QT20uh,0*44",
            "!AIVDM,1,1,,A,1:U7N:<003u4BRqkNUO<=:wR0t0t,0*35",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAF5QsT0000,0*78",
            "!AIVDM,1,1,,A,1:U8w4PP0rM4l0akNCE9R?wP06id,0*5E",
            "!AIVDM,1,1,,B,1:U73IP000M4?a;kO@CbjJC`00R2F",
            "!AIVDM,1,1,,B,3:U7@T000AM4WLqkNkluJP5`0210,0*23",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOaAF5QsV0000,0*64",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2UkNuR8ewwV20Sa,0*1A",
            "!AIVDM,1,1,,A,1:U7Ok0P02u4BpkkNUP;=wwb26id,0*5C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOaAF5Qs`0000,0*52",
            "!AIVDM,1,1,,A,2:U7:o1P@4M4BUUkNce9uPmb0<13,0*09",
            "!AIVDM,1,1,,B,1:U8KJ0Oi8u4PhIkOmiGsVgd2L2B,0*13",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOaAF5Qsb0000,0*50",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAV5Qsd0000,0*58",
            "!AIVDM,1,1,,A,1:U7DlPP02M4GnwkPKQ=Hwwf06id,0*7B",
            "!AIVDM,1,1,,A,277De55001M4IUEkQFKMabmH0L0v,0*42",
            "!AIVDM,1,1,,A,3:U7@T0OhHM4WKkkNkptQP7h00nh,0*1A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAV5Qsf0000,0*5A",
            "!AIVDM,1,1,,B,1:U8QsP003u4B6ckObWA71m`2HQ3,0*17",
            "!AIVDM,1,1,,A,3:U8KJ0Oi6u4Pg;kOmP826qj21oh,0*14",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAF5Qsh0000,0*44",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAF5Qsj0000,0*46",
            "!AIVDM,1,1,,A,3:U7:o1P@4M4BUUkNce9uPgn00=P,0*6D",
            "!AIVDM,1,1,,A,1:U7eP`P01u4BpEkNUadBgvL2PSB,0*64",
            "!AIVDM,1,1,,B,3:U8KJ0Oi5u4PfekOmGWvo3n2180,0*67",
            "!AIVDM,1,1,,A,3:U8WSU000M4?HOkOCTcViwn0Dab,0*63",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAF5Qsl0000,0*40",
            "!AIVDM,1,1,,B,1:U7@T000BM4WL7kNkre2P9n06id,0*18",
            "!AIVDM,1,1,,A,1:U7Gg@006M4Gl=kPKFmNlWl0@Rq,0*67",
            "!AIVDM,1,1,,A,3:U7:o1P@4M4BUAkNce:50f000@h,0*40",
            "!AIVDM,1,1,,B,1:U8N90P01M4@@mkOS@:L?v020SE,0*6D",
            "!AIVDM,1,1,,A,1:UEGH0007M4WKokOnBpPQ2006ih,0*43",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAV5Qsn0000,0*52",
            "!AIVDM,1,1,,A,406iKEAvRdFKsu4BB3kOtQw00L0k,0*1F",
            "!AIVDM,1,1,,B,1:U:8`000KM4N7GkPLWRv1Ol0<1O,0*41",
            "!AIVDM,1,1,,A,1:U713PP00M4?AUkODr6Hgwj0D0o,0*22",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAV5Qr00000,0*0D",
            "!AIVDM,1,1,,A,1:U8w4PP0sM4krekNBt9Ogwn0@0r,0*6C",
            "!AIVDM,1,1,,B,1:U7N:<003u4BRSkNUPss:t00W3h,0*57",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAn5Qr20000,0*37",
            "!AIVDM,1,1,,A,1:U73IP000M4?a;kO@C:jJD40<1=,0*04",
            "!AIVDM,1,1,,A,1:U8KJ0Ohwu4Pe3kOm;pLoF62D2B,0*31",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOaAV5Qr40000,0*09",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2WkNuR`ewv420SV,0*17",
            "!AIVDM,1,1,,A,2:U7:o1P@4M4BTukNcgb?0b800SO,0*1C",
            "!AIVDM,1,1,,B,1:U7DlPP01M4Go7kPKPu??v800Sw,0*3C",
            "!AIVDM,1,1,,B,B:U8seP00?A45rLoprilGwQVSP06,0*6D",
            "!AIVDM,1,1,,A,B:U8seP00?A45rLoprilGwQVSP06,0*6E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAV5Qr60000,0*0F",
            "!AIVDM,1,1,,B,1:U7Ok0P03u4BpWkNUPcA?v820RM,0*41",
            "!AIVDM,1,1,,A,3:U7:o1P@4M4BTukNcgbI0`:00F0,0*01",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAF5Qr80000,0*11",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOaAF5Qr:0000,0*11",
            "!AIVDM,1,1,,B,3:U8KJ0Ohuu4PcskOm4HU7`>21pP,0*09",
            "!AIVDM,1,1,,B,277De55000M4IUGkQFKat:mf0L0v,0*0D",
            "!AIVDM,1,1,,A,33nSn:5000M4?o7kO=S98lf>0E9:,0*5D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOaAF5Qr<0000,0*15",
            "!AIVDM,1,1,,A,3:U7:o1P@4M4BTukNcgbe0V>00HP,0*71",
            "!AIVDM,1,1,,A,1:U8QsP002u4B6skObVP01n82000,0*53",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUd<swvf2U9H,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOaAV5Qr>0000,0*05",
            "!AIVDM,1,1,,A,2:U7:o1P@4M4BTukNcgbt0T@0D13,0*73",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOaAF5Qr@0000,0*6B",
            "!AIVDM,1,1,,A,1:U7@T000BM4WKGkNl6u?@:B00S4,0*61",
            "!AIVDM,1,1,,A,1:U8N90P01M4@@SkOS?:P?vD26ih,0*56",
            "!AIVDM,1,1,,A,3:U8KJ0Ohou4Pc1kOls`UWpD213@,0*65",
            "!AIVDM,1,1,,B,1:UEGH0007M4WL5kOn@pKA4D085U,0*09",
            "!AIVDM,1,1,,A,3:U7:o1P@4M4BTukNcgc8PTD00?P,0*42",
            "!AIVDM,1,1,,B,1:U713P000M4?AUkODonHQp<0@5c,0*6E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOaA65QrB0000,0*19",
            "!AIVDM,1,1,,A,B:V3wo000gA3n2Loo;WQ3wTTWP06,0*6E",
            "!AIVDM,1,1,,B,406iKEAvRdFL9u4BB3kOtQw00H5o,0*54",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOaA65QrD0000,0*1F",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BTakNcj;;0RH00V0,0*62",
            "!AIVDM,1,1,,A,3:U7N:<Oh3u4BRIkNUR<6;0D0Puh,0*13",
            "!AIVDM,1,1,,B,1:U8KJ0Ohlu4PawkOlo`fp2H286n,0*47",
            "!AIVDM,1,1,,B,1:U73IP000M4?a=kO@BrjJDH0<1=,0*34",
            "!AIVDM,1,1,,B,3:U7N:<Oh3u4BRIkNUR<6;0D0P?0,0*02",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@n5QrF0000,0*44",
            "!AIVDM,1,1,,A,1:U8w4PP0sM4km5kNBS9M?vD087Q,0*29",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@V5QrH0000,0*72",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2ekNuRHewvH20S8,0*1C",
            "!AIVDM,1,1,,A,1:U7Ok0P02u4BpgkNUN;B?vL2<1B,0*22",
            "!AIVDM,1,1,,B,3:U7N:<Oh3u4BREkNURL:s0H0Qw0,0*7F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@V5QrJ0000,0*70",
            "!AIVDM,1,1,,A,2:U7:o1P@5M4BTakNcj;BPNL0@8:,0*76",
            "!AIVDO,1,1,,,1:U7AQi000M4AkikOa@F5QrL0000,0*66",
            "!AIVDM,1,1,,A,1:U7DlPP01M4Go1kPKRdpwvN00RW,0*7A",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BTakNcj;LPNP00B@,0*15",
            "!AIVDM,1,1,,B,3:U8RIQ003M4We9kOJbtrPHP0DUb,0*4B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@V5QrN0000,0*76",
            "!AIVDM,1,1,,B,1:U8QsP003u4B6skObVhS1pH20Sj,0*5D",
            "!AIVDM,1,1,,A,3:U8KJ0OhWu4P`=kOlkqCpNR21fP,0*07",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BpakNUd=6gw02U9H,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa@65QrP0000,0*08",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5QrR0000,0*2D",
            "!AIVDM,1,1,,A,1:UEGH0007M4WKukOn=81A2V06ih,0*79",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5QrT0000,0*2B",
            "!AIVDM,1,1,,B,3:U8KJ0OhUu4PWkkOlha?`d`212P,0*54",
            "!AIVDM,1,1,,A,1:U713PP00M4?AakODoFHgvP08;G,0*1F",
            "!AIVDM,1,1,,B,1:U8N90P00M4@@EkOS;rcOv`2<0e,0*37",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5QrV0000,0*29",
            "!AIVDM,1,1,,A,1:U7Gg@00:M4GlKkPKF29DbT08;g,0*17",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5Qr`0000,0*1F",
            "!AIVDM,1,1,,B,1:U:8`0P@JM4N<5kPLi2rADV08<I,0*3D",
            "!AIVDM,1,1,,A,1:U8KJ0OhSu4PWCkOlfq>ppd20SA,0*15",
            "!AIVDM,1,1,,B,1:U7N:<Oh3u4BR7kNUSL2K6`0W3h,0*0A",
            "!AIVDM,1,1,,A,1:U8w4PP0tM4ki1kNBAaJgvV0D0n,0*6D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?n5Qrb0000,0*1D",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BTEkNcj;a0Fd00K0,0*39",
            "!AIVDM,1,1,,A,1:U73IP000M4?a;kO@BJjJBf0D1=,0*59",
            "!AIVDO,1,1,,,1:U7AQi000M4AkkkOa?V5Qrd0000,0*23",
            "!AIVDM,1,1,,B,1:U7DlPP02M4Go9kPKPLV?vh08=h,0*48",
            "!AIVDM,1,1,,A,3:U7N:<Oh2u4BR3kNUSdDs8d0R60,0*3A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa?V5Qrf0000,0*25",
            "!AIVDM,1,1,,B,1:U7Ok0P02M4BpWkNULs@wvh2H>;,0*0F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa?n5Qrh0000,0*13",
            "!AIVDM,1,1,,A,8:U7RM00G@:?>G1?6600,0*2C",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BT1kNclca0Dj00A0,0*15",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@65Qrj0000,0*36",
            "!AIVDM,1,1,,B,3:U8KJ0OhIu4PVOkOlj9wa@n21kh,0*35",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@F5Qrl0000,0*40",
            "!AIVDM,1,1,,B,B:U8e;P01WA4csLoaGl0Kwe4oP06,0*00",
            "!AIVDM,1,1,,B,H:U7<;ll>OwJ1CA@CjnmoP2@633G,0*1B",
            "!AIVDM,1,1,,B,3:U7eP`P00u4BpakNUd=6gwF2VLC,0*7B",
            "!AIVDO,1,1,,,1:U7AQi000M4AkokOa@65Qrn0000,0*32",
            "!AIVDM,1,1,,A,3:U8KJ0OhGu4PV;kOlfqvIJr20w@,0*02",
            "!AIVDM,1,1,,A,2:U7:o1P@5M4BSekNclchP@r08@l,0*67",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa@65Qrp0000,0*32",
            "!AIVDM,1,1,,B,1:U713PP00M4?AikODp6Hgvl0@AD,0*46",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa@65Qrr0000,0*30",
            "!AIVDM,1,1,,B,406iKEAvRdFLMu4BB3kOtQw00L0c,0*2D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkqkOa@65Qrt0000,0*36",
            "!AIVDM,1,1,,B,1:U8KJ0OhFu4PUekOlgqnqc02<2A,0*5D",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BSekNco;u0?000QP,0*58",
            "!AIVDM,1,1,,A,1:U7N:<Oh2u4BQukNUTKg00t0`BQ,0*0A",
            "!AIVDM,1,1,,A,1:U8w4PP0tM4kcekNAs9H?vr00Rf,0*3A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkskOa@V5Qrv0000,0*56",
            "!AIVDM,1,1,,B,1:U73IP000M4?a5kO@B:jJC00@Bn,0*57",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2KkNuT8ewvv2<17,0*1B",
            "!AIVDM,1,1,,A,2:U7:o1P@5M4BSekNco<9P?206ih,0*76",
            "!AIVDO,1,1,,,1:U7AQi000M4AkukOaAF5Qs20000,0*04",
            "!AIVDM,1,1,,A,1:U7DlPP02M4Go9kPKQ<e?w40<1O,0*7B",
            "!AIVDM,1,1,,B,3:U7N:<Oh2u4BQskNUTd60320QjP,0*2E",
            "!AIVDO,1,1,,,1:U7AQi000M4AkukOaAV5Qs40000,0*12",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BSekNco<A0=600Ah,0*47",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaAn5Qs60000,0*2A",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaAn5Qs80000,0*65",
            "!AIVDM,1,1,,B,1:U8QsP002u4B6akOb`001o22d2P,0*29",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaAn5Qs:0000,0*67",
            "!AIVDM,1,1,,A,3:U7N:<Oh2u4BQqkNUU;o0780Pwh,0*02",
            "!AIVDM,1,1,,B,1:U7@T000CM4WI=kNlVdsP;>0<1a,0*70",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaB65Qs<0000,0*3A",
            "!AIVDM,1,1,,B,1:U8N90P02M4@?okOS>:cgw>2<0e,0*5A",
            "!AIVDM,1,1,,A,1:U7Gg@000M4GlOkPKE<W4e<0D1M,0*39",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaB65Qs>0000,0*79",
            "!AIVDM,1,1,,A,406iKEAvRdFLWu4BB3kOtQw00HGL,0*68",
            "!AIVDM,1,1,,A,1:U713PP00M4?AMkODoFHgw:0@Gl,0*77",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaB65Qs@0000,0*07",
            "!AIVDM,1,1,,B,3815JT1202M4d;1kNCFb`hd<0Dg:,0*19",
            "!AIVDM,1,1,,A,1:U73IP000M4?`skO@ArjJCB06ih,0*71",
            "!AIVDM,1,1,,B,1:U:8`0OhKM4N@akPLsBc1C>0@HH,0*4A",
            "!AIVDM,1,1,,B,1:U7N:<Oh2u4BQmkNUUso0;@0PRL,0*22",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaB65QsB0000,0*44",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BSIkNcqdRP9F00H@,0*0B",
            "!AIVDM,1,1,,A,1:U8w4PP0uM4kWakNAaaEgw@0D0n,0*39",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaAn5QsD0000,0*58",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2akNuT8ewwD2@I>,0*0C",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaAn5QsF0000,0*5A",
            "!AIVDM,1,1,,B,1:U7Ok0P01M4BoqkNUQ;JwwH2<1B,0*49",
            "!AIVDM,1,1,,A,3:U7N:<Oh2u4BQikNUVJoh=F0Qw0,0*1D",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaAF5QsH0000,0*7C",
            "!AIVDM,1,1,,B,3:U8KJ0Oh<u4PU1kOlaI8r?L2210,0*46",
            "!AIVDM,1,1,,A,3:U74Tmw@0u4?vAkO<>L4rAL2Dar,0*4A",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOaAF5QsJ0000,0*7E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOaA65QsL0000,0*49",
            "!AIVDM,1,1,,B,3:U7N:<Oh2u4BQekNUV;Ch?L0Q0h,0*58",
            "!AIVDM,1,1,,A,353<TP1P@;M4QiMkO@3b1@9P0DSb,0*55",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUfe6gv62d11,0*6F",
            "!AIVDO,1,1,,,1:U7AQi000M4AkwkOa@n5QsN0000,0*53",
            "!AIVDM,1,1,,A,2:U7:o1P@5M4BSIkNct<l05R0@LB,0*67",
            "!AIVDM,1,1,,A,1:U7@T000@M4WHQkNlfdgh7R0D1a,0*19",
            "!AIVDM,1,1,,A,3:U8wK5000M4@j5kOWa`dJER0Dor,0*3F",
            "!AIVDM,1,1,,A,3:U8KJ0OhBu4PTakOlRHUbER20qP,0*63",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@V5QsP0000,0*34",
            "!AIVDM,1,1,,B,1:UEGH0005M4WKkkOn@8013T00RT,0*68",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@V5QsR0000,0*36",
            "!AIVDM,1,1,,B,406iKEAvRdFLiu4BB3kOtQw00HMC,0*50",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BSIkNct<nP5V00;P,0*15",
            "!AIVDM,1,1,,A,39NS@O1001u4iVAkNNv74PuR0000,0*68",
            "!AIVDM,1,1,,A,1:U7N:<Oh2u4BQakNUUrl0AR0pMh,0*5C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@V5QsT0000,0*30",
            "!AIVDM,1,1,,B,1:U713PP00M4?AakODp6HgwN0<0o,0*4B",
            "!AIVDM,1,1,,B,1:U73IP000M4?`okO@AbjJCV0L1=,0*1D",
            "!AIVDM,1,1,,A,1:U8w4PP0uM4kRakNAH9JgwP00S2,0*19",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BS5kNcvdnP3`00V@,0*7E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@V5QsV0000,0*32",
            "!AIVDM,1,1,,A,1:U7Ok0P00M4BoukNUQs`Owb20T6,0*22",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@V5Qs`0000,0*04",
            "!AIVDM,1,1,,A,2:U7:o1P@5M4BS5kNcvdq03b08O8,0*6B",
            "!AIVDM,1,1,,B,1:U8KJ0Oh>u4PTokOlO7rrKd2HO@,0*2B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@F5Qsb0000,0*16",
            "!AIVDM,1,1,,A,3:U7sn5000M4>LukOMwI4isd0DU:,0*2D",
            "!AIVDM,1,1,,A,3:U8KJ0Oh?u4PTokOlLoLbMf229h,0*7E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa@V5Qsd0000,0*02",
            "!AIVDM,1,1,,A,1:U7DlPP02M4GoCkPKLurOwf00RE,0*05",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BS5kNcvdnP1h009@,0*1B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al1kOa@V5Qsf0000,0*02",
            "!AIVDM,1,1,,B,1:U8QsP001u4B6ckOb`P01ob2l2P,0*10",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BS5kNcvdnP1j00?@,0*1F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa@n5Qsh0000,0*36",
            "!AIVDO,1,1,,,1:U7AQi000M4Al3kOa@n5Qsj0000,0*34",
            "!AIVDM,1,1,,A,3:U7N:<Oh3u4BQOkNUUb10Gj0Puh,0*1A",
            "!AIVDM,1,1,,A,1:U7eP`P00u4BpakNUfe6gvL2t11,0*06",
            "!AIVDO,1,1,,,1:U7AQi000M4Al5kOa@n5Qsl0000,0*34",
            "!AIVDM,1,1,,B,1:U7@T000EM4WGCkNlnd;@5n00Rr,0*44",
            "!AIVDM,1,1,,B,3:U8KJ0OhGu4PT=kOlDp4JQn211h,0*0F",
            "!AIVDM,1,1,,A,1:UEGH0007M4WL1kOn@nvA0000S?,0*59",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@V5Qsn0000,0*02",
            "!AIVDM,1,1,,A,406iKEAvRdFLsu4BB9kOtQw00H00,0*4D",
            "!AIVDM,1,1,,B,1:U8N90P01M4@?SkOS=ro?v02H03,0*57",
            "!AIVDM,1,1,,A,3:U7:o1P@5M4BS5kNd1<nc>000Ah,0*37",
            "!AIVDM,1,1,,A,1:U713P000M4?AUkODqVHQqj0@0K,0*31",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@V5Qr00000,0*5D",
            "!AIVDM,1,1,,A,1:U8w4PP0uM4kLekN@w9Jgwn0<0n,0*30",
            "!AIVDM,1,1,,B,1:U7N:<Oh3u4BQKkNUUr7hJ00PRa,0*28",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@n5Qr20000,0*67",
            "!AIVDM,1,1,,A,1:U73IP000M4?`mkO@ArjJD4081:,0*1A",
            "!AIVDM,1,1,,B,39NSI6U000M4>I9kOf1piop60Dv:,0*64",
            "!AIVDM,1,1,,A,1:U8KJ0OhAu4PTikOlBnvrR62@1P,0*2C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOa@n5Qr40000,0*61",
            "!AIVDM,1,1,,B,1:U7Ok0P00M4BoqkNUScsOv62D1A,0*17",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2SkNuSHewv42H29,0*4C",
            "!AIVDM,1,1,,A,2:U7:o1P@5M4BRikNd3dnc<80@2>,0*6E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaA65Qr60000,0*38",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaA65Qr80000,0*36",
            "!AIVDM,1,1,,A,3:U7N:<Oh2u4BQGkNUUb4hL60PqP,0*25",
            "!AIVDM,1,1,,B,1:U7DlPP03M4GoAkPKN=Vgv:0D1O,0*03",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaAF5Qr:0000,0*42",
            "!AIVDM,1,1,,B,3:U8KJ0OhHu4PSwkOl;WPrT<21hh,0*47",
            "!AIVDM,1,1,,A,3:U8QsP001u4B6UkObaP01n62P30,0*2E",
            "!AIVDM,1,1,,A,3:U8QsP001u4B6UkObaP01n62P01,0*2C",
            "!AIVDM,1,1,,B,277De55001M4IUmkQFL@6rmf0H3r,0*09",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaAF5Qr<0000,0*42",
            "!AIVDM,1,1,,B,3:U7N:<Oh3u4BQAkNUUIr0N<0Q20,0*3E",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUfe6gvf2PRb,0*3B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaAF5Qr>0000,0*40",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaAV5Qr@0000,0*2E",
            "!AIVDM,1,1,,A,1:U7@T0P@?M4WFOkNlpscP0B0<1a,0*34",
            "!AIVDM,1,1,,A,1:U8N90P01M4@?ckOS?brOvD20Si,0*2E",
            "!AIVDM,1,1,,B,1:UEGH0008M4WKkkOn>GLhvD06il,0*11",
            "!AIVDM,1,1,,A,3:U8KJ000HM4PSukOl87p:VD20n@,0*07",
            "!AIVDM,1,1,,B,1:U713PP00M4?AekODp6Hgv<0<0o,0*3C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaAn5QrB0000,0*14",
            "!AIVDM,1,1,,B,406iKEAvRdFM9u4BB9kOtQ?00D0j,0*1B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaB65QrD0000,0*4F",
            "!AIVDM,1,1,,B,1:U8KJ000EM4PTMkOl5Fo:VH26il,0*76",
            "!AIVDM,1,1,,B,1:U73IP000M4?`wkO@BbjJDH086t,0*25",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaAn5QrF0000,0*16",
            "!AIVDM,1,1,,B,3770<<1005M4iJGkO`p<8Q2F0000,0*2A",
            "!AIVDM,1,1,,A,1:U8w4PP0uM4kFMkN@V9H?vD06il,0*13",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaB65QrH0000,0*43",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2OkNuTHewvH2<17,0*51",
            "!AIVDM,1,1,,A,1:U7Ok0P01M4Bp;kNUT<H?vL287o,0*7D",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaB65QrJ0000,0*43",
            "!AIVDM,1,1,,A,2:U7:o1005M4BRMkNd6<sc8L0<14,0*1F",
            "!AIVDM,1,1,,A,1:U7DlPP02M4Go9kPKNMNwvL0<1O,0*0F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaB65QrL0000,0*45",
            "!AIVDM,1,1,,A,3:U8KJ0OhOu4PS=kOkv`Ar`P2200,0*3E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaB65QrN0000,0*47",
            "!AIVDM,1,1,,A,277De55001M4IUokQFHh0:l80H9D,0*09",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBV5QrP0000,0*39",
            "!AIVDM,1,1,,A,3:U7N:<Oh2u4BQ7kNUTIlhbP0Pu0,0*0B",
            "!AIVDM,1,1,,B,1:U8QsP001u4B6QkObah11nJ2d2P,0*3B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBn5QrR0000,0*03",
            "!AIVDM,1,1,,B,1:U7@T0Oh?M4WEUkNlsKVh6T08:W,0*06",
            "!AIVDM,1,1,,B,3:U8KJ000LM4PSikOku`4J`V21?h,0*69",
            "!AIVDM,1,1,,A,2:U7:o1005M4BRMkNd8e=;8V0@;1,0*37",
            "!AIVDM,1,1,,A,1:UEGH0005M4WKkkOn=FmPvV00S7,0*71",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBF5QrT0000,0*2D",
            "!AIVDM,1,1,,A,1:U713PP00M4?AGkODqFHgvP06il,0*50",
            "!AIVDM,1,1,,B,1:U8N90P01M4@?WkOS>ruOv`28;O,0*6D",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaBF5QrV0000,0*2D",
            "!AIVDM,1,1,,A,1:U7Gg@Oh0M4GlEkPKE4BTdT06il,0*0B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBF5Qr`0000,0*19",
            "!AIVDM,1,1,,B,1:U:8`000JM4NIqkPMH2HQ<V06il,0*10",
            "!AIVDM,1,1,,A,3533381002u4Pg1kOW4q00Vd0Dmr,0*00",
            "!AIVDM,1,1,,B,1:U7N:<Oh2u4BQ7kNUTalhh`0PRd,0*6B",
            "!AIVDM,1,1,,A,1:U8w4PP0uM4kBIkN@IaJgvV0@<g,0*34",
            "!AIVDM,1,1,,A,1:U8KJ000HM4PS=kOkmoCr`d2D2A,0*03",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2GkNuS8ewvb2D17,0*7F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaB65Qrb0000,0*69",
            "!AIVDM,1,1,,A,1:U73IP000M4?`ukO@@JjJBf0@=@,0*61",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBF5Qrd0000,0*1D",
            "!AIVDM,1,1,,B,1:U7DlPP02M4Go9kPKNLD?vh06il,0*1A",
            "!AIVDM,1,1,,A,3:U7N:<Oh1u4BQ5kNUTIlhld0QsP,0*57",
            "!AIVDM,1,1,,A,2:U7:o1005M4BRMkNd8eG;8h0D14,0*78",
            "!AIVDM,1,1,,A,3:U79R5000M4AKKkOWbW>WRh0Dwb,0*6F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaB65Qrf0000,0*6F",
            "!AIVDM,1,1,,B,1:U7Ok0P00M4BpckNUU<h?vh2D1A,0*76",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaB65Qrh0000,0*61",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBF5Qrj0000,0*13",
            "!AIVDM,1,1,,B,277De55000M4IUokQFGtbJlL0H?:,0*36",
            "!AIVDM,1,1,,A,1:U8QsP000u4B6QkObaP01nd20Ss,0*38",
            "!AIVDM,1,1,,B,3:U8KJ0P@Gu4PSMkOkgW<JVn21o0,0*45",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBF5Qrl0000,0*15",
            "!AIVDM,1,1,,B,3:U8SC1004M4Oq1kNp1@m@tn0Dfb,0*41",
            "!AIVDM,1,1,,B,3:U7N:<Oh1u4BQ5kNUT9lhrl0Q2h,0*4B",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUfe6gwF2d11,0*1E",
            "!AIVDO,1,1,,A,3:U7AQi000M4Al?kOaBF5Qrl0000,0*56",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBV5Qrn0000,0*07",
            "!AIVDM,1,1,,A,2:U7:o1005M4BRMkNd;=Nc8r06il,0*1A",
            "!AIVDM,1,1,,A,1:U7@T0Oh;M4WDQkNlwc`P<r0D1a,0*4B",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBn5Qrp0000,0*21",
            "!AIVDM,1,1,,A,1:U8N90P01M4@?QkOS=bwgvr20T1,0*5A",
            "!AIVDM,1,1,,B,1:UEGH0Oh4M4WKakOn@oR0vt0L1S,0*0D",
            "!AIVDM,1,1,,B,1:U713PP00M4?AGkODpnHgvl0<0o,0*16",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBn5Qrr0000,0*23",
            "!AIVDM,1,1,,B,406iKEAvRdFMMu4BB?kOtQ?00HAU,0*2B",
            "!AIVDM,1,1,,B,3:U7@T0Oh:M4WDKkNm0cc@@v00>P,0*36",
            "!AIVDM,1,1,,A,3:U7@T0Oh:M4WDKkNm0cc@@v00eP,0*6E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaC65Qrt0000,0*7C",
            "!AIVDM,1,1,,A,1:U8w4PP0tM4k>EkN@:aJgvp0@B9,0*30",
            "!AIVDM,1,1,,B,1:U8KJ0OhOu4PRIkOkV`::c028BM,0*3F",
            "!AIVDM,1,1,,A,1:U7N:<Oh1u4BQ5kNUT9li2t0W3h,0*14",
            "!AIVDM,1,1,,B,3:U7@T0Oh;M4WDEkNm1KrhC001wP,0*24",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaCV5Qrv0000,0*1E",
            "!AIVDM,,B,1:U73IP000M4?a=kO@@bjJC00<1=,0*59",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2?kNuRHewvv28Bq,0*28",
            "!AIVDO,1,1,,A,8:U7AQhj2P00000001mQO005@p00,0*43",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaC65Qs00000,0*39",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaCV5Qs20000,0*5B",
            "!AIVDM,1,1,,A,1:U7Ok0P00M4BpkkNUSLWww426il,0*26",
            "!AIVDM,1,1,,A,1:U7DlPP02M4Go9kPKOc7Ow408Cr,0*53",
            "!AIVDM,1,1,,B,3:U7N:<Oh1u4BQ5kNUSqli920Qh@,0*62",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaC65Qs40000,0*3D",
            "!AIVDM,1,1,,A,3:U7@T0Oh:M4WD1kNm2Kj@I800i@,0*6C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaCV5Qs60000,0*5D",
            "!AIVDM,1,1,,A,277De55000M4IUqkQFGtbJlj0HE3,0*7E",
            "!AIVDM,1,1,,A,B:U7<;h07gA3wWtopQPIowiVSP06,0*60",
            "!AIVDM,1,1,,A,3:U7N:<Oh1u4BQ3kNUSali=60Q;P,0*34",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaC65Qs80000,0*31",
            "!AIVDM,1,1,,B,1:U8QsP001u4B6ckOba001o22`Ea,0*6B",
            "!AIVDM,1,1,,A,35MCqF5000M4?3akOGfVh1w<0Dpb,0*2F",
            "!AIVDM,1,1,,A,B:V426h01WA6OQLpDM=?OwjUkP06,0*62",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaCV5Qs:0000,0*51",
            "!AIVDM,1,1,,B,1:U7@T0Oh;M4WCokNm3sihS>08FV,0*0A",
            "!AIVDM,1,1,,A,1:UEGH0003M4WKQkOn>`li1>0@FW,0*7A",
            "!AIVDM,1,1,,A,2:U7:o1005M4BRMkNd=eNc7>00Rq,0*27",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaC65Qs<0000,0*35",
            "!AIVDM,1,1,,B,1:U8N90P01M4@?UkOS>:nww>28Fr,0*1B",
            "!AIVDM,1,1,,A,1:U7Gg@Oh6M4Gl=kPKFeQ4s<0@GE,0*5A",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaC65Qs>0000,0*35",
            "!AIVDM,1,1,,B,1:U7N:<Oh2u4BPokNUSqliE>0pGh,0*6E",
            "!AIVDM,1,1,,A,3:U7@T0Oh:M4WCwkNm3csPWB023h,0*19",
            "!AIVDM,1,1,,A,1:U713PP00M4?AKkODpnHgw:0<0o,0*4E",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaC65Qs@0000,0*4B",
            "!AIVDM,1,1,,B,1:U:8`0OhKM4NN1kPMaj?Q=>0<1O,0*6F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaBn5QsB0000,0*16",
            "!AIVDM,1,1,,A,1:U8w4PP0uM4k8IkN?g9Jgw@0@Ho,0*2C",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaBn5QsD0000,0*10",
            "!AIVDM,1,1,,A,1:U8KJ000Iu4PRGkOkDGI:cF20S4,0*43",
            "!AIVDM,1,1,,A,1:U7URgP00M4A2=kNuSHewwD2<17,0*2A",
            "!AIVDM,1,1,,A,2:U7:o1005M4BR9kNd@=Ic7H0@IO,0*52",
            "!AIVDO,1,1,,,1:U7AQi000M4Al9kOaBV5QsF0000,0*28",
            "!AIVDM,1,1,,B,1:U7Ok0P01M4BpmkNURt<OwH28Ii,0*1F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaBV5QsH0000,0*24",
            "!AIVDM,1,1,,A,3:U7N:<Oh1u4BPqkNUSaliMF0Qth,0*00",
            "!AIVDM,1,1,,B,3:U7@T0Oh;M4WCSkNm4tvPiL00qh,0*5A",
            "!AIVDM,1,1,,B,277De55001M4IUqkQFGon:m40HJl,0*14",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaBV5QsJ0000,0*26",
            "!AIVDM,1,1,,B,3:U7N:<Oh2u4BPukNUSIliQJ0PtP,0*05",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaBn5QsL0000,0*18",
            "!AIVDM,1,1,,B,1:U7eP`P00u4BpakNUfe6gv62`Kj,0*4A",
            "!AIVDM,1,1,,A,1:U8QsP001u4B6kkObaP01oF2@Kn,0*55",
            "!AIVDO,1,1,,,1:U7AQi000M4Al;kOaBV5QsN0000,0*22",
            "!AIVDM,1,1,,A,2:U7:o1004M4BR9kNd@=B;5R0<14,0*67",
            "!AIVDM,1,1,,A,1:U7@T0Oh;M4WCukNm1tWhmR0@LF,0*18",
            "!AIVDM,1,1,,B,1:UEGH0003M4WKUkOn=HEQ3R0D1R,0*5F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al=kOaBn5QsP0000,0*02",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBn5QsR0000,0*02",
            "!AIVDM,1,1,,A,39NS`<1002M4Tc3kOKeUphoP0DpJ,0*25",
            "!AIVDM,1,1,,B,406iKEAvRdFMiu4BBEkOtPO00D0n,0*42",
            "!AIVDM,1,1,,A,1:U7N:<Oh2u4BPwkNUSIliaR0l0v,0*70",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaBn5QsT0000,0*04",
            "!AIVDM,1,1,,A,1:U8w4PP0vM4k4EkN?MaEgwP0@Mm,0*45",
            "!AIVDM,1,1,,B,1:U713PP00M4?AIkODpnHgwN08Mo,0*42",
            "!AIVDM,1,1,,B,1:U73IP000M4?a9kO@=bjJEV0HMq,0*04",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaCV5QsV0000,0*3F",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaC65Qs`0000,0*69",
            "!AIVDM,1,1,,B,1:U8KJ0OhEu4PQmkOk77?:gd2D2@,0*70",
            "!AIVDM,1,1,,B,1:U7URgP00M4A2=kNuS8eww`2<17,0*7D",
            "!AIVDM,1,1,,A,1:U7DlPP01M4GoMkPKTrA?wd0HOM,0*3B",
            "!AIVDO,1,1,,,1:U7AQi000M4AlAkOaCV5Qsb0000,0*75",
            "!AIVDM,1,1,,A,1:U7Ok0P01M4Bq9kNUT;nOwf2L1A,0*58",
            "!AIVDM,1,1,,A,3:U7@T0Oh9M4WCSkNm2aF0wf012@,0*46",
            "!AIVDO,1,1,,,1:U7AQi000M4AlAkOaCV5Qsd0000,0*73",
            "!AIVDM,1,1,,A,3:U8ieQ:03M4dvAkNuJ=31=h0E=b,0*56",
            "!AIVDM,1,1,,A,277De55001M4IUokQFFoW:mH0HPN,0*75",
            "!AIVDM,1,1,,A,35BUcH100>M4TE=kS5fKv@?b0000,0*0D",
            "!AIVDO,1,1,,,1:U7AQi000M4AlCkOaCV5Qsf0000,0*73",
            "!AIVDM,1,1,,B,1:U8QsP001u4B6mkObah01o`2@Q4,0*0E",
            "!AIVDO,1,1,,,1:U7AQi000M4AlAkOaCn5Qsh0000,0*47",
            "!AIVDM,1,1,,B,3:U8TvQ005M4U65kN9:M1A7j0Dg:,0*47",
            "!AIVDO,1,1,,,1:U7AQi000M4Al?kOaCn5Qsj0000,0*3B",
            "!AIVDO,1,1,,,1:U7AQi000M4AlAkOaCV5Qsl0000,0*7B",
            # Adicione mais strings conforme necessário
        ]

        # Seleciona uma string aleatória da lista e retorna sem alterar o checksum
        selected_message = random.choice(ais_messages)
        return selected_message

    def generate_psondep_string(self):
        try:
        # Obtém o valor de profundidade configurado pelo usuário
            depth = float(self.position_depth.get())  # Ajuste conforme o método que você usa para obter a profundidade
        # Monte a string no formato $PRDID,Pitch,Roll,Heading
            psondep_string = f"$PSONDEP,{depth:.2f},,M*"
        # Calcula o checksum
            checksum = sum(ord(c) for c in psondep_string[1:]) % 256
            psondep_string += f"{checksum:02X}"

        # Retorne a string gerada
            return psondep_string
        except Exception as e:
            print(f"Erro ao gerar a string PSONDEP: {e}")
            return ''

    def generate_digiquartz_string(self):
        try:
            # Obtém o valor de profundidade configurado pelo usuário (em metros)
            depth_meters = float(self.position_depth.get())

            # Converte profundidade para PSI (aproximação)
            depth_psi = depth_meters * 1.422

            # Formata o valor de profundidade em PSI com até 6 casas decimais
            depth_formatted = f"{depth_psi:.6f}"

            # Constrói a string no formato Digiquartz Depth
            digiquartz_string = f"*0001{depth_formatted}"

            return digiquartz_string

        except Exception as e:
            print(f"Erro ao gerar a string Digiquartz Depth: {e}")
            return ''

    def calculate_checksum(self, data):
        return sum(data) % 256

    def generate_dvlpd0_string(self):
        try:
            # Obtém os valores de entrada do usuário
            depth = int(float(self.position_depth.get()))  # profundidade em mm
            heading = int(float(self.attitude_heading.get()) * 10)  # heading em décimos de grau
            pitch = int(float(self.attitude_pitch.get()) * 10)      # pitch em décimos de grau
            roll = int(float(self.attitude_roll.get()) * 10)        # roll em décimos de grau

            # Velocidades aleatórias
            north_velocity = int(random.uniform(-0.005, 0.005) * 1000)  # mm/s
            east_velocity = int(random.uniform(-0.005, 0.005) * 1000)   # mm/s
            up_velocity = depth  # ou outro valor que você deseje usar

            # Novos parâmetros para PD0
            sv = 1500  # Velocidade do som em mm/s
            salinity = 35.00  # Salinidade em ppt
            temperature = 4.05  # Temperatura em °C

            # Inicializa o bytearray para o pacote PD0
            data = bytearray(40)  # Tamanho total do pacote PD0

            # Preenche o pacote com dados usando struct.pack_into
            struct.pack_into('>H', data, 0, 0x7F7F)          # Cabeçalho
            struct.pack_into('>H', data, 2, 0x0000)          # ID do Pacote PD0
            struct.pack_into('>H', data, 4, len(data))       # Número de Bytes
            struct.pack_into('>h', data, 6, north_velocity)  # North Velocity
            struct.pack_into('>h', data, 8, east_velocity)   # East Velocity
            struct.pack_into('>h', data, 10, up_velocity)    # Up Velocity
            struct.pack_into('>h', data, 12, 0)              # Error Velocity (se aplicável)
            struct.pack_into('>H', data, 14, heading)        # Heading
            struct.pack_into('>h', data, 16, pitch)          # Pitch
            struct.pack_into('>h', data, 18, roll)           # Roll
            struct.pack_into('>H', data, 20, sv)             # Velocidade do som
            struct.pack_into('>f', data, 22, salinity)       # Salinidade (float)
            struct.pack_into('>f', data, 26, temperature)    # Temperatura (float)
            data[39] = self.calculate_checksum(data[:-1])    # Checksum

            return data  # Retorna a string em formato binário (bytearray)

        except Exception as e:
            print(f"Erro ao gerar a string DVL PD0: {e}")
            return bytearray()  # Retorna um bytearray vazio em caso de erro

    def print_binary_representation(self, byte_data):
        binary_string = ''.join(format(byte, '08b') for byte in byte_data)
        print("DVL PD0 String (Binary):", binary_string)

    def generate_and_print_dvlpd0_string(self):
        dvlpd0 = self.generate_dvlpd0_string()  # Chama a função para obter os dados
        self.print_binary_representation(dvlpd0)  # Imprime a representação binária

    def generate_dvlpd4_string(self):
        try:
            # Obtém os valores de entrada do usuário
            depth = int(float(self.position_depth.get()))  # profundidade em mm
            heading = int(float(self.attitude_heading.get()) * 10)  # heading em décimos de grau
            pitch = int(float(self.attitude_pitch.get()) * 10)      # pitch em décimos de grau
            roll = int(float(self.attitude_roll.get()) * 10)        # roll em décimos de grau

            # Velocidades aleatórias
            north_velocity = int(random.uniform(-0.005, 0.005) * 1000)  # mm/s
            east_velocity = int(random.uniform(-0.005, 0.005) * 1000)   # mm/s
            up_velocity = depth  # ou outro valor que você deseje usar

            # Inicializa o bytearray para o pacote PD4
            data = bytearray(30)  # Tamanho total do pacote PD4

            # Preenche o pacote com dados usando struct.pack_into
            struct.pack_into('>H', data, 0, 0x7F7F)          # Cabeçalho
            struct.pack_into('>H', data, 2, 0x0004)           # ID do Pacote PD4
            struct.pack_into('>H', data, 4, len(data))        # Número de Bytes
            struct.pack_into('>h', data, 6, north_velocity)   # North Velocity
            struct.pack_into('>h', data, 8, east_velocity)    # East Velocity
            struct.pack_into('>h', data, 10, up_velocity)     # Up Velocity
            struct.pack_into('>h', data, 12, 0)               # Error Velocity (se aplicável)
            struct.pack_into('>H', data, 14, heading)         # Heading
            struct.pack_into('>h', data, 16, pitch)           # Pitch
            struct.pack_into('>h', data, 18, roll)            # Roll
            data[29] = self.calculate_checksum(data[:-1])     # Checksum

            return data  # Retorna a string em formato binário (bytearray)

        except Exception as e:
            print(f"Erro ao gerar a string DVL PD4: {e}")
            return bytearray()  # Retorna um bytearray vazio em caso de erro

    def print_binary_representation(self, byte_data):
        binary_string = ''.join(format(byte, '08b') for byte in byte_data)
        print("DVL PD4 String (Binary):", binary_string)

    def generate_and_print_dvlpd4_string(self):
        dvlpd4 = self.generate_dvlpd4_string()  # Chama a função para obter os dados
        self.print_binary_representation(dvlpd4)  # Imprime a representação binária

    def generate_dvlpd5_string(self):
        try:
            # Obtém os valores de entrada do usuário
            depth = int(float(self.position_depth.get()))  # profundidade em mm
            heading = int(float(self.attitude_heading.get()) * 10)  # heading em décimos de grau
            pitch = int(float(self.attitude_pitch.get()) * 10)      # pitch em décimos de grau
            roll = int(float(self.attitude_roll.get()) * 10)        # roll em décimos de grau

            # Velocidades aleatórias
            north_velocity = int(random.uniform(-0.005, 0.005) * 1000)  # mm/s
            east_velocity = int(random.uniform(-0.005, 0.005) * 1000)   # mm/s
            up_velocity = depth  # ou outro valor que você deseje usar

            # Novos parâmetros para PD5
            sv = 1500  # Velocidade do som em mm/s
            salinity = 35.00  # Salinidade em ppt
            temperature = 4.05  # Temperatura em °C

            # Inicializa o bytearray para o pacote PD5
            data = bytearray(40)  # Tamanho total do pacote PD5

            # Preenche o pacote com dados usando struct.pack_into
            struct.pack_into('>H', data, 0, 0x7F7F)          # Cabeçalho
            struct.pack_into('>H', data, 2, 0x0005)           # ID do Pacote PD5
            struct.pack_into('>H', data, 4, len(data))        # Número de Bytes
            struct.pack_into('>h', data, 6, north_velocity)   # North Velocity
            struct.pack_into('>h', data, 8, east_velocity)    # East Velocity
            struct.pack_into('>h', data, 10, up_velocity)     # Up Velocity
            struct.pack_into('>h', data, 12, 0)               # Error Velocity (se aplicável)
            struct.pack_into('>H', data, 14, heading)         # Heading
            struct.pack_into('>h', data, 16, pitch)           # Pitch
            struct.pack_into('>h', data, 18, roll)            # Roll
            struct.pack_into('>H', data, 20, sv)              # Velocidade do som
            struct.pack_into('>f', data, 22, salinity)        # Salinidade (float)
            struct.pack_into('>f', data, 26, temperature)     # Temperatura (float)
            data[39] = self.calculate_checksum(data[:-1])     # Checksum

            return data  # Retorna a string em formato binário (bytearray)

        except Exception as e:
            print(f"Erro ao gerar a string DVL PD5: {e}")
            return bytearray()  # Retorna um bytearray vazio em caso de erro

    def print_binary_representation(self, byte_data):
        binary_string = ''.join(format(byte, '08b') for byte in byte_data)
        print("DVL PD5 String (Binary):", binary_string)

    def generate_and_print_dvlpd5_string(self):
        dvlpd5 = self.generate_dvlpd5_string()  # Chama a função para obter os dados
        self.print_binary_representation(dvlpd5)  # Imprime a representação binária

    def generate_rovstring_string(self):
        # Obter os valores de entrada do usuário
        depth = int(float(self.position_depth.get()))  # profundidade
        heading = int(float(self.attitude_heading.get()))  # heading
        altitude = round(random.uniform(-2.05, 2.05), 2)
        pitch = int(float(self.attitude_pitch.get()))  # pitch
        roll = int(float(self.attitude_roll.get()))  # roll

        # Adicionar variação aleatória entre -0.05 e 0.05
        depth += random.uniform(-0.05, 0.05)
        heading += random.uniform(-0.05, 0.05)
        pitch += random.uniform(-0.05, 0.05)
        roll += random.uniform(-0.05, 0.05)

        # Criar a string ROV
        rov_string = f"UHD2 105,{heading:.2f},{depth:.2f},{altitude:.2f},{pitch:.2f},{roll:.2f}"

        return rov_string

    def generate_cp_string(self):
        # Valores iniciais
        cp_value1 = -0.800
        cp_value2 = -0.800

        # Variação máxima
        variation = 0.010

        # Gerar novos valores com variação aleatória
        cp_value1 += random.uniform(-variation, variation)
        cp_value2 += random.uniform(-variation, variation)

        # Garantir que os valores estejam dentro do intervalo permitido
        cp_value1 = max(-1.100, min(cp_value1, -0.800))
        cp_value2 = max(-1.100, min(cp_value2, -0.800))

        # Criar a string CP PROBE
        cp_string = f"{cp_value1:.3f},{cp_value2:.3f}"

        return cp_string

    def generate_ut_string(self):
        # Definindo os valores de UT Probe
        values = [5.0, 8.0, 13.0, 21.0, 35.0, 50.0]

        # Selecionar um valor aleatório da lista para cada chamada da função
        selected_value = random.choice(values)

        # Criar a string UT PROBE
        ut_string = f"{selected_value:.1f}"

        return ut_string
    
    def generate_lnav_string(self):
        # -----------------------------
        # Entradas da interface
        # -----------------------------
        # Dados principais das abas
        latitude_deg = float(self.position_latitude.get())
        longitude_deg = float(self.position_longitude.get())
        depth_m = float(self.position_depth.get())
        altitude_m = round(random.uniform(1.1, 20.7), 3)
        roll_deg = float(self.attitude_roll.get())
        pitch_deg = float(self.attitude_pitch.get())
        heading_deg = float(self.attitude_heading.get())

        # -----------------------------
        # Valores fixos ou randômicos
        # -----------------------------
        velocity_north = 0.01
        velocity_east = -0.005
        velocity_down = 0.002
        ang_rate_fwd = 0.01
        ang_rate_stbd = -0.01
        ang_rate_down = 0.005
        acc_fwd = 0.001
        acc_stbd = -0.002
        acc_down = 0.003
        hpe_major = 0.1
        hpe_minor = 0.05
        hpe_dir = 45.0
        vpe = 0.2
        level_error_north = 0.3
        level_error_east = -0.3
        heading_error = 0.4
        hve_major = 0.1
        hve_minor = 0.1
        hve_dir = 90.0
        vve = 0.3
        status_flags = 0b00000001
        orientation_status = 0b00000010
        position_status = 0b00000011

        # -----------------------------
        # Conversões de unidades
        # -----------------------------
        latitude = int(latitude_deg * (2**31) / 90.0)
        longitude = int(longitude_deg * (2**31) / 180.0)
        depth = int(depth_m * 1000)
        altitude = int(altitude_m * 1000)

        roll = max(min(int(roll_deg * 100), 32767), -32768)
        pitch = max(min(int(pitch_deg * 100), 32767), -32768)
        heading = max(min(int(heading_deg * 100), 35999), 0)

        vel_n = int(velocity_north * 1000)
        vel_e = int(velocity_east * 1000)
        vel_d = int(velocity_down * 1000)
        ang_fwd = int(ang_rate_fwd * 100)
        ang_stbd = int(ang_rate_stbd * 100)
        ang_down = int(ang_rate_down * 100)
        acc_fwd = int(acc_fwd * 1000)
        acc_stbd = int(acc_stbd * 1000)
        acc_down = int(acc_down * 1000)
        hpe_major = int(hpe_major * 1000)
        hpe_minor = int(hpe_minor * 1000)
        hpe_dir = int(hpe_dir * 100)
        vpe = int(vpe * 1000)
        lvl_err_n = int(level_error_north * 1000)
        lvl_err_e = int(level_error_east * 1000)
        hdg_err = int(heading_error * 1000)
        hve_major = int(hve_major * 1000)
        hve_minor = int(hve_minor * 1000)
        hve_dir = int(hve_dir * 100)
        vve = int(vve * 1000)

        # -----------------------------
        # Novo formato: sem timestamp
        # -----------------------------
        lnav_format = '<iiii hhh hhh hhh hhh HHHH hhh HHHH BBB'

        return struct.pack(
            lnav_format,
            latitude,
            longitude,
            depth,
            altitude,
            roll,
            pitch,
            heading,
            vel_n,
            vel_e,
            vel_d,
            ang_fwd,
            ang_stbd,
            ang_down,
            acc_fwd,
            acc_stbd,
            acc_down,
            hpe_major,
            hpe_minor,
            hpe_dir,
            vpe,
            lvl_err_n,
            lvl_err_e,
            hdg_err,
            hve_major,
            hve_minor,
            hve_dir,
            vve,
            status_flags,
            orientation_status,
            position_status
        )

if __name__ == "__main__":
    root = ThemedTk(theme="plastik")  # Usar tema
    app = StringSimulator(root)
    root.mainloop()