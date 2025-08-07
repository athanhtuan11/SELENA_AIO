import os
import sys
import json
import glob
import shutil
import threading
import subprocess
import tempfile
import re
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

class MF4ImporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MF4 Importer Guild")
        # Tạo layout chia 2 nửa: left_frame (thông tin), right_frame (trống cho mở rộng)
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right_frame = tk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right_frame.pack_propagate(False)
        # Thêm nút run_order và ô nhập vào hàng đầu tiên bên phải
        run_order_frame = tk.Frame(right_frame)
        run_order_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.run_order_var = tk.StringVar()
        self.run_order_button = tk.Button(run_order_frame, text="run_order", command=self.run_order_action)
        self.run_order_button.pack(side=tk.LEFT, padx=5)
        self.run_order_entry = tk.Entry(run_order_frame, textvariable=self.run_order_var, width=25)
        self.run_order_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        
        # Thêm hàng mới: Adapter File bên phải (sau Run Simulation)
        adapter_right_frame = tk.Frame(right_frame)
        adapter_right_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        tk.Label(adapter_right_frame, text="Adapter File:").pack(side=tk.LEFT)
        self.adapter_file_var = getattr(self, 'adapter_file_var', tk.StringVar())
        self.adapter_file_entry_right = tk.Entry(adapter_right_frame, textvariable=self.adapter_file_var, width=25)
        self.adapter_file_entry_right.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.open_adapter_file_button_right = tk.Button(adapter_right_frame, text="Chọn Adapter", command=self.open_adapter_file)
        self.open_adapter_file_button_right.pack(side=tk.LEFT, padx=5)


        # Thêm hàng mới: Nút Run Simulation bên phải
        simulation_frame = tk.Frame(right_frame)
        simulation_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.run_simulation_button = tk.Button(simulation_frame, text="Run Simulation", command=self.run_simulation_action)
        self.run_simulation_button.pack(side=tk.LEFT, padx=5)

        # Thêm hàng mới: GEN Runnable Level | Ô nhập
        runnable_level_frame = tk.Frame(right_frame)
        runnable_level_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.gen_runnable_level_button = tk.Button(runnable_level_frame, text="GEN Runnable Level", command=self.gen_runnable_level_template)
        self.gen_runnable_level_button.pack(side=tk.LEFT, padx=5)
        self.runnable_level_var = tk.StringVar()
        self.runnable_level_entry = tk.Entry(runnable_level_frame, textvariable=self.runnable_level_var, width=25)
        self.runnable_level_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        Gen_testplan_frame = tk.Frame(right_frame)
        Gen_testplan_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.Gen_testplan_button = tk.Button(Gen_testplan_frame, text="GEN Test Plan", command=self.Gen_testplan_action)
        self.Gen_testplan_button.pack(side=tk.LEFT, padx=5)

        # Thêm hàng mới: Split MF4
        split_mf4_frame = tk.Frame(right_frame)
        split_mf4_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.split_mf4_button = tk.Button(split_mf4_frame, text="Split MF4", command=self.open_split_mf4_dialog)
        self.split_mf4_button.pack(side=tk.LEFT, padx=5)

        # Thêm nút Load All Paths và Save All Paths
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.load_paths_button = tk.Button(btn_frame, text="Load All Paths", command=self.load_all_paths)
        self.load_paths_button.pack(side=tk.LEFT, padx=5)
        self.save_paths_button = tk.Button(btn_frame, text="Save All Paths", command=self.save_all_paths)
        self.save_paths_button.pack(side=tk.LEFT, padx=5)
        
        # Thêm 3 ô nhập Project, Variant, Release vào đầu left_frame
        project_info_frame = tk.Frame(left_frame)
        project_info_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        tk.Label(project_info_frame, text="Project:").pack(side=tk.LEFT)
        self.project_var = tk.StringVar()
        self.project_entry = tk.Entry(project_info_frame, textvariable=self.project_var, width=10)
        self.project_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(project_info_frame, text="Variant:").pack(side=tk.LEFT)
        self.variant_var = tk.StringVar()
        self.variant_entry = tk.Entry(project_info_frame, textvariable=self.variant_var, width=10)
        self.variant_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(project_info_frame, text="Release:").pack(side=tk.LEFT)
        self.release_var = tk.StringVar()
        self.release_entry = tk.Entry(project_info_frame, textvariable=self.release_var, width=10)
        self.release_entry.pack(side=tk.LEFT, padx=5)
        
        # Di chuyển toàn bộ các dòng thông tin sang left_frame
        repo_frame = tk.Frame(left_frame)
        repo_frame.pack(padx=0, pady=5, fill=tk.X)
        self.repo_button = tk.Button(repo_frame, text="Repository", command=self.repository_action)
        self.repo_button.pack(side=tk.LEFT)
        self.repo_path_var = tk.StringVar()
        self.repo_path_entry = tk.Entry(repo_frame, textvariable=self.repo_path_var, width=25)
        self.repo_path_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.open_repo_button = tk.Button(repo_frame, text="Open Repo", command=self.open_repo_folder)
        self.open_repo_button.pack(side=tk.LEFT, padx=5)
        # Dòng 2: OPEN BCT BUILD | ô nhập | RUN BCT BUILD
        bct_frame = tk.Frame(left_frame)
        bct_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.open_bct_build_button = tk.Button(bct_frame, text="OPEN BCT BUILD", command=self.open_bct_bat_file)
        self.open_bct_build_button.pack(side=tk.LEFT)
        self.bct_out_path_var = tk.StringVar()
        self.bct_out_entry = tk.Entry(bct_frame, textvariable=self.bct_out_path_var, width=25)
        self.bct_out_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.run_bct_button = tk.Button(bct_frame, text="RUN BCT BUILD", command=self.run_bct_bat)
        self.run_bct_button.pack(side=tk.LEFT, padx=5)
        # Dòng mới: A2L Config Path | Nút chọn folder | ô nhập | Quản lý Delivery Folder
        a2l_config_frame = tk.Frame(left_frame)
        a2l_config_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        # Nút quản lý delivery folder
        self.delivery_button = tk.Button(a2l_config_frame, text="Delivery Folders", command=self.delivery_folders)
        self.delivery_button.pack(   side=tk.LEFT, padx=(0, 10), pady=0)
        self.delivery_var = tk.StringVar()
        self.delivery_entry = tk.Entry(a2l_config_frame, textvariable=self.delivery_var, width=25)
        self.delivery_entry.pack(side=tk.LEFT, padx=0, fill=tk.X, expand=True)
        self.find_a2l_button = tk.Button(a2l_config_frame, text="Find_A2L", command=self.find_a2l_in_zip)
        self.find_a2l_button.pack(side=tk.LEFT, padx=5)
        # Khởi tạo biến cho A2L Table (dùng cho GEN A2L_Table)
        self.a2l_table_var = tk.StringVar()
        # Biến riêng cho đường dẫn .a2l thực tế (kết quả Find_A2L)
        self.a2l_actual_var = tk.StringVar()
        # Dòng mới: Hiển thị đường dẫn .a2l
        a2l_path_frame = tk.Frame(left_frame)
        a2l_path_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        tk.Label(a2l_path_frame, text="A2L Path:").pack(side=tk.LEFT)
        self.a2l_path_entry = tk.Entry(a2l_path_frame, textvariable=self.a2l_actual_var, width=40, state="readonly")
        self.a2l_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # Dòng mới: GEN A2L_Table | Ô Nhập | Open A2L_Table
        a2l_frame = tk.Frame(left_frame)
        a2l_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        self.gen_a2l_button = tk.Button(a2l_frame, text="GEN A2L_Table", command=self.gen_a2l_table)
        self.gen_a2l_button.pack(side=tk.LEFT)
        self.a2l_table_entry = tk.Entry(a2l_frame, textvariable=self.a2l_table_var, width=25)
        self.a2l_table_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.open_a2l_button = tk.Button(a2l_frame, text="Open A2L_Table", command=self.open_a2l_file)
        self.open_a2l_button.pack(side=tk.LEFT)
        # Dòng 3: Build_Selena | ô Nhập | Run
        build_selena_frame = tk.Frame(left_frame)
        build_selena_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.run_build_selena_button = tk.Button(build_selena_frame, text="BUILD SELENA", command=self.run_build_selena_bat)
        self.run_build_selena_button.pack(side=tk.LEFT, padx=5)
        self.build_selena_path_var = tk.StringVar()
        self.build_selena_entry = tk.Entry(build_selena_frame, textvariable=self.build_selena_path_var, width=25)
        self.build_selena_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Dòng 4: Env chọn conda
        env_frame = tk.Frame(left_frame)
        env_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.env_button = tk.Button(env_frame, text="Select Conda Env", command=self.show_conda_env_selector)
        self.env_button.pack(side=tk.LEFT)
        self.selected_env_var = tk.StringVar()
        self.selected_env_label = tk.Label(env_frame, textvariable=self.selected_env_var, fg="blue")
        self.selected_env_label.pack(side=tk.LEFT, padx=10)

        # Dòng 5: JSON | Nút chọn file
        json_frame = tk.Frame(left_frame)
        json_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        self.open_json_button = tk.Button(json_frame, text="OPEN JSON", command=self.open_json_file)
        self.open_json_button.pack(side=tk.LEFT)
        self.json_var = tk.StringVar()
        self.json_entry = tk.Entry(json_frame, textvariable=self.json_var, width=25)
        self.json_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # Dòng 6: SCOM | Nút chọn file | ô nhập | Find_SCOM
        scom_frame = tk.Frame(left_frame)
        scom_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.open_scom_button = tk.Button(scom_frame, text="OPEN SCOM", command=self.open_scom_file)
        self.open_scom_button.pack(side=tk.LEFT)
        self.scom_var = tk.StringVar()
        # Thêm nút Find_SCOM
        self.find_scom_button = tk.Button(scom_frame, text="Find_SCOM", command=self.find_scom_in_zip)
        self.find_scom_button.pack(side=tk.LEFT, padx=5)
        # Biến và Entry readonly cho SCOM thực tế
        self.scom_actual_var = tk.StringVar()
        self.scom_path_entry = tk.Entry(scom_frame, textvariable=self.scom_actual_var, width=40, state="readonly")
        self.scom_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # Dòng 7: MF4 | Nút chọn file | ô nhập
        mf4_frame = tk.Frame(left_frame)
        mf4_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        # Dòng mới: Thêm nút Choose MF4
        self.choose_mf4_button = tk.Button(mf4_frame, text="Choose MF4", command=self.choose_mf4_file)
        self.choose_mf4_button.pack(side=tk.LEFT, padx=5)
        self.mf4_var = tk.StringVar()
        self.mf4_entry = tk.Entry(mf4_frame, textvariable=self.mf4_var, width=25)
        self.mf4_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.open_mf4_button = tk.Button(mf4_frame, text="OPEN MF4", command=self.open_mf4_file)
        self.open_mf4_button.pack(side=tk.LEFT)
        # Dòng 8: Selena Toolbox | Nút chọn file | ô nhập
        toolbox_frame = tk.Frame(left_frame)
        toolbox_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        self.open_toolbox_button = tk.Button(toolbox_frame, text="OPEN SELENA TOOLBOX", command=self.open_toolbox_file)
        self.open_toolbox_button.pack(side=tk.LEFT)
        self.toolbox_var = tk.StringVar()
        self.toolbox_entry = tk.Entry(toolbox_frame, textvariable=self.toolbox_var, width=25)
        self.toolbox_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # Dòng 9: GEN Mem&Sequence
        self.gen_button = tk.Button(left_frame, text="GEN Mem&Sequence", command=self.gen_mem_sequence)
        self.gen_button.pack(padx=20, pady=(5,0))
        # Thêm các checkbox option
        option_frame = tk.Frame(left_frame)
        option_frame.pack(padx=0, pady=(0,5), fill=tk.X)
        self.ticket_vars = {
            'ALL': tk.BooleanVar(value=True),
            'sequence': tk.BooleanVar(value=False),
            'mempool': tk.BooleanVar(value=False),
            'systemtime': tk.BooleanVar(value=False),
        }
        self.ticket_boxes = {}
        def on_ticket_change(name):
            if name == 'ALL' and self.ticket_vars['ALL'].get():
                for k in ['sequence','mempool','systemtime']:
                    self.ticket_vars[k].set(False)
            elif name != 'ALL' and self.ticket_vars[name].get():
                self.ticket_vars['ALL'].set(False)
        for i, name in enumerate(['ALL','sequence','mempool','systemtime']):
            cb = tk.Checkbutton(option_frame, text=name, variable=self.ticket_vars[name],
                               command=lambda n=name: on_ticket_change(n))
            cb.pack(side=tk.LEFT, padx=5)
            self.ticket_boxes[name] = cb
        # Dòng 10: Systemtime | ô nhập
        systemtime_frame = tk.Frame(left_frame)
        systemtime_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        tk.Label(systemtime_frame, text="Systemtime:").pack(side=tk.LEFT)
        self.systemtime_var = tk.StringVar()
        self.systemtime_entry = tk.Entry(systemtime_frame, textvariable=self.systemtime_var, width=25)
        self.systemtime_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # Dòng 11: Sequence | ô nhập
        sequence_frame = tk.Frame(left_frame)
        sequence_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        tk.Label(sequence_frame, text="Sequence:").pack(side=tk.LEFT)
        self.sequence_var = tk.StringVar()
        self.sequence_entry = tk.Entry(sequence_frame, textvariable=self.sequence_var, width=25)
        self.sequence_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # Dòng 12: Mempool | ô nhập
        mempool_frame = tk.Frame(left_frame)
        mempool_frame.pack(padx=0, pady=(0, 10), fill=tk.X)
        tk.Label(mempool_frame, text="Mempool:").pack(side=tk.LEFT)
        self.mempool_var = tk.StringVar()
        self.mempool_entry = tk.Entry(mempool_frame, textvariable=self.mempool_var, width=25)
        self.mempool_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Dòng 13: Selena .EXE | Nút chọn file
        selena_exe_frame = tk.Frame(left_frame)
        selena_exe_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        self.open_selena_exe_button = tk.Button(selena_exe_frame, text="Selena .EXE", command=self.open_selena_exe_file)
        self.open_selena_exe_button.pack(side=tk.LEFT)
        self.selena_exe_var = tk.StringVar()
        self.selena_exe_entry = tk.Entry(selena_exe_frame, textvariable=self.selena_exe_var, width=25)
        self.selena_exe_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # Dòng 14: SOURCE | droplist | Add_command | ô nhập
        source_frame = tk.Frame(left_frame)
        source_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        tk.Label(source_frame, text="SOURCE:").pack(side=tk.LEFT)
        self.source_var = tk.StringVar(value="RadarFC")
        self.source_options = ["RadarFC", "RadarFL", "RadarFR", "RadarRL", "RadarRR"]
        self.source_menu = tk.OptionMenu(source_frame, self.source_var, *self.source_options)
        self.source_menu.pack(side=tk.LEFT, padx=5)
        # Khi đổi SOURCE thì tự động lấy delivery folder nếu có
        self.source_var.trace_add("write", lambda *args: self.update_a2l_config_by_project())
        # Dòng 15: Gen Runtime | Ô nhập | Open Runtime | Gen Runtime
        runtime_frame = tk.Frame(left_frame)
        runtime_frame.pack(padx=0, pady=(0, 5), fill=tk.X)
        self.gen_runtime_button = tk.Button(runtime_frame, text="Gen Runtime", command=self.run_gen_runtime)
        self.gen_runtime_button.pack(side=tk.LEFT, padx=5)
        # Thêm nút OLD IMPORT sau nút GEN RUNTIME
        self.old_import_button = tk.Button(runtime_frame, text="OLD IMPORT", command=self.old_import_action)
        self.old_import_button.pack(side=tk.LEFT, padx=5)
        self.open_runtime_button = tk.Button(runtime_frame, text="Open Runtime", command=self.open_runtime_file)
        self.open_runtime_button.pack(side=tk.LEFT)
        self.runtime_var = tk.StringVar()
        self.runtime_entry = tk.Entry(runtime_frame, textvariable=self.runtime_var, width=25)
        self.runtime_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # Dòng XX: Terminal (hiển thị log)
        terminal_frame = tk.Frame(left_frame)
        terminal_frame.pack(padx=0, pady=10, fill=tk.BOTH, expand=True)
        tk.Label(terminal_frame, text="Terminal:").pack(anchor=tk.W)
        self.terminal_text = tk.Text(terminal_frame, height=10, width=60, bg="#181818", fg="#e0e0e0", insertbackground="#e0e0e0", font=("Consolas", 10), wrap=tk.WORD)
        self.terminal_text.pack(fill=tk.BOTH, expand=True)
        # Thêm thanh cuộn ngang và dọc
        yscroll = tk.Scrollbar(terminal_frame, orient=tk.VERTICAL, command=self.terminal_text.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_text.config(yscrollcommand=yscroll.set)
        xscroll = tk.Scrollbar(terminal_frame, orient=tk.HORIZONTAL, command=self.terminal_text.xview)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.terminal_text.config(xscrollcommand=xscroll.set)

        # Placeholder cho ô nhập bct_out_path_var
        self.bct_out_placeholder = "path to bct.bat file"
        self.bct_out_entry.insert(0, self.bct_out_placeholder)
        self.bct_out_entry.config(fg="grey")

        # Không dùng self.bct_out_path_file và file txt nữa
        # Load bct_out_path từ all_paths.json nếu có
        import os
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        if os.path.isfile(all_paths_file) and key:
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                bct_path = data.get(key, {}).get("bct_out", "")
                if bct_path:
                    self.bct_out_entry.delete(0, tk.END)
                    self.bct_out_entry.insert(0, bct_path)
                    self.bct_out_entry.config(fg="black")
            except Exception:
                pass
        self.bct_out_path_var.trace_add("write", self.save_bct_out_path)

        # Bổ sung khởi tạo các biến còn thiếu
        self.bct_options = {}  # Để tránh lỗi khi dùng self.bct_options
        self.info_text = self.terminal_text  # Đảm bảo self.info_text luôn tồn tại
        self.adapter_file_var = tk.StringVar()  # Đảm bảo luôn có biến này
        self.source_command_var = tk.StringVar()  # Đảm bảo luôn có biến này
        # Thêm frame cho BCT options
        self.bct_options_frame = tk.Frame(left_frame)
        self.bct_options_frame.pack(padx=0, pady=(0, 5), fill=tk.X)


        # Khởi tạo dict chứa tất cả các biến path_var
        self.path_vars = {
            "project": self.project_var,
            "variant": self.variant_var,
            "release": self.release_var,
            "repo": self.repo_path_var,
            "toolbox": self.toolbox_var,
            "json": self.json_var,
            "scom": self.scom_var,
            "mf4": self.mf4_var,
            "exe": self.selena_exe_var,
            "build_selena": self.build_selena_path_var,
            "bct_out": self.bct_out_path_var,
            "runtime": self.runtime_var,
            "a2l_config": self.delivery_var,
            # Thêm các biến liên quan đến SCOM, systemtime, sequence, mempool
            "scom_actual": self.scom_actual_var,
            "systemtime": self.systemtime_var,
            "sequence": self.sequence_var,
            "mempool": self.mempool_var,
        }
        # Đảm bảo các biến path_vars luôn có đủ adapter
        self.path_vars["adapter"] = self.adapter_file_var
        # Thêm biến run_order vào path_vars để tiện lưu/khôi phục
        self.path_vars["run_order"] = self.run_order_var

        # Load giá trị từ all_paths.json nếu có, nếu chưa có thì tạo trường mới trong json
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        data = {}
        if os.path.isfile(all_paths_file):
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        if key:
            if key not in data:
                data[key] = {k: v.get() for k, v in self.path_vars.items()}
                with open(all_paths_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                for k, v in self.path_vars.items():
                    v.set(data[key].get(k, ""))

        # Tự động lưu vào all_paths.json khi bất kỳ path_var nào thay đổi
        for k, v in self.path_vars.items():
            v.trace_add("write", self.save_all_paths)

        # Load selena_env từ all_paths.json
        self.load_selena_env()
        self.selected_env_var.trace_add("write", self.save_selena_env)

        # Set delivery_folder to Delivery Folder from all_paths.json
        self.delivery_folder = ""
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        if key and os.path.isfile(all_paths_file):
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                delivery_folder = data.get(key, {}).get("a2l_config", "")
                self.delivery_folder = os.path.join(delivery_folder, "delivery_folders.json") if delivery_folder else ""
            except Exception:
                self.delivery_folder = ""

    def open_adapter_file(self):
        # Mở File Explorer để chọn file Adapter
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")], title="Select Adapter File")
        
        if file_path:
            # Cập nhật đường dẫn file vào adapter_file_var
            self.adapter_file_var.set(file_path)

    def open_mf4_file(self):
        current_file_path = self.mf4_var.get().strip()
        if current_file_path and os.path.isfile(current_file_path):
            folder_path = os.path.dirname(current_file_path)
            os.startfile(folder_path)
        else:
            file_path = filedialog.askopenfilename(filetypes=[("MF4 files", "*.mf4"), ("All files", "*.*")], title="Select MF4 File")
            if file_path:
                self.mf4_var.set(file_path)
                self.mf4_entry.config(fg="black")
                folder_path = os.path.dirname(file_path)
                os.startfile(folder_path)

    def list_virtual_envs(self):
        import glob
        result = []
        # Tìm các thư mục venv phổ biến trong thư mục hiện tại và home
        search_dirs = [os.getcwd(), os.path.expanduser('~')]
        found_envs = []
        for base in search_dirs:
            for env_name in [".venv", "venv", "env", "Envs"]:
                pattern = os.path.join(base, env_name, "*") if env_name == "Envs" else os.path.join(base, env_name)
                for path in glob.glob(pattern):
                    if os.path.isdir(path):
                        found_envs.append(path)
        if found_envs:
            result.append("Local virtual envs:\n" + "\n".join(found_envs))
        # Kiểm tra thư mục conda envs theo user
        user_home = os.path.expanduser('~')
        conda_envs_dir = os.path.join(user_home, ".conda", "envs")
        conda_envs_list = []
        if os.path.isdir(conda_envs_dir):
            for env in os.listdir(conda_envs_dir):
                env_path = os.path.join(conda_envs_dir, env)
                if os.path.isdir(env_path):
                    conda_envs_list.append(env_path)
        if conda_envs_list:
            result.append("Conda envs (from .conda/envs):\n" + "\n".join(conda_envs_list))
        # Nếu có conda, liệt kê env của conda (bổ sung cho chắc chắn)
        try:
            conda_envs = subprocess.check_output(["conda", "env", "list"], universal_newlines=True, stderr=subprocess.DEVNULL)
            result.append("Conda envs (from conda):\n" + conda_envs)
        except FileNotFoundError:
            result.append("Conda không được cài đặt hoặc không có trong PATH.")
        except Exception as e:
            result.append(f"Không thể lấy danh sách conda envs: {e}")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "\n\n".join(result) if result else "No virtual environments found.")

    def gen_mem_sequence(self):
        import threading
        def worker():
            # Lấy project, variant, release từ 3 ô nhập
            project = self.project_var.get().strip()
            variant = self.variant_var.get().strip()
            release = self.release_var.get().strip()
            key = f"{project}|{variant}|{release}" if project and variant and release else None
            record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
            all_paths_file = os.path.join(record_dir, "all_paths.json")
            # Nếu chưa có đủ, thực hiện gen ra output bằng subprocess
            toolbox_path = self.toolbox_var.get().strip()
            mf4_path = self.mf4_var.get().strip()
            if not toolbox_path or not os.path.isfile(toolbox_path):
                self.root.after(0, lambda: self.append_info_text("[ERROR] Chưa chọn đúng Selena Toolbox!\n"))
                return
            if not mf4_path or not os.path.isfile(mf4_path):
                self.root.after(0, lambda: self.append_info_text("[ERROR] Chưa chọn đúng file MF4!\n"))
                return
            # Đường dẫn output cho từng loại
            base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            outputs = {
                'systemtime': os.path.join(base_folder, 'systemtime', project, variant, release, 'systemtime.csv'),
                'sequence': os.path.join(base_folder, 'sequence', project, variant, release, 'sequence.csv'),
                'mempool': os.path.join(base_folder, 'mempool', project, variant, release, 'mempool.csv'),
            }

            # Đảm bảo các thư mục output tồn tại
            for out_path in outputs.values():
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
            # Mapping opt sang command đúng
            opt2cmd = {
                'systemtime': 'systemtimes',
                'sequence': 'sequencenumbers',
                'mempool': 'mempools',
            }
            results = {}
            for opt, out_path in outputs.items():
                cmd_name = opt2cmd.get(opt, opt)
                cmd = [sys.executable, toolbox_path, 'mdf', cmd_name, mf4_path, '-o', out_path]
                self.root.after(0, lambda c=cmd: self.append_info_text(f"[GEN] Đang chạy: {' '.join(c)}\n"))
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    self.root.after(0, lambda s=result.stdout: self.append_info_text(s))
                    if result.stderr:
                        self.root.after(0, lambda s=result.stderr: self.append_info_text(s))
                    # Đọc kết quả
                    if os.path.isfile(out_path):
                        with open(out_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        results[opt] = content
                    else:
                        results[opt] = ''
                except Exception as e:
                    self.root.after(0, lambda opt=opt, e=e: self.append_info_text(f"[ERROR] Lỗi khi gen {opt}: {e}\n"))
                    results[opt] = ''
            # Gán vào biến giao diện từ outputs
            self.root.after(0, lambda v=outputs.get('systemtime', ''): self.systemtime_var.set(v))
            self.root.after(0, lambda v=outputs.get('sequence', ''): self.sequence_var.set(v))
            self.root.after(0, lambda v=outputs.get('mempool', ''): self.mempool_var.set(v))
            self.root.after(0, lambda k=key: self.append_info_text(f"[INFO] Đã gen xong Systemtime, Sequence, Mempool cho {k}\n"))
            # Có thể bổ sung logic lưu lại vào all_paths.json nếu muốn tự động cập nhật
        threading.Thread(target=worker, daemon=True).start()

    def set_toolbox(self):
        # TODO: Thực hiện logic Set toolbox tại đây
        messagebox.showinfo("Set toolbox", "Đã thực thi Set toolbox!")

    def repository_action(self):
        from tkinter import filedialog
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.repo_path_var.set(folder_selected)
            print (self.repo_path_var)
        else:
            self.repo_path_var.set("")

    def open_repo_folder(self):
        path = self.repo_path_var.get()
        import os
        path = os.path.normpath(path)
        print(f"Repo path: {path}")
        if path and os.path.isdir(path):
            import subprocess
            try:
                subprocess.Popen(["explorer", path])
            except Exception as e:
                messagebox.showerror("Open Repo", f"Không thể mở thư mục: {e}")
        else:
            messagebox.showerror("Open Repo", "Đường dẫn không hợp lệ hoặc không tồn tại.")

    def open_bct_bat_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Batch files", "*.bat")])
        if file_path:
            self.bct_out_path_var.set(file_path)
            self.bct_out_entry.config(fg="black")
            self.show_bct_options(file_path, self.bct_options_frame, self.bct_options)

    def show_bct_options(self, file_path, bct_options_frame, bct_options_dict):
        # Xóa các option cũ
        for widget in bct_options_frame.winfo_children():
            widget.destroy()
        bct_options_dict.clear()
        # Đọc file .bat, tìm các dòng set /p VAR=...
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                match = re.match(r"\s*set\s+/p\s+(\w+)=", line, re.IGNORECASE)
                if match:
                    var = match.group(1)
                    label = tk.Label(bct_options_frame, text=f"{var}:")
                    label.pack(side=tk.LEFT)
                    entry = tk.Entry(bct_options_frame, width=10)
                    entry.pack(side=tk.LEFT, padx=2)
                    bct_options_dict[var] = entry
        except Exception as e:
            print(f"Không thể đọc option từ file .bat: {e}")

        def run_bct_bat(path, set_lines, info_callback):
            import tempfile
            def run_cmd():
                info_callback('clear')
                if path and os.path.isfile(path) and path.lower().endswith('.bat'):
                    try:
                        if set_lines:
                            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.bat', encoding='utf-8') as f:
                                for line in set_lines:
                                    f.write(line + '\n')
                                call_line = f'call "{path}"'
                                f.write(call_line + '\n')
                                temp_bat = f.name
                            bat_to_run = temp_bat
                        else:
                            bat_to_run = path
                        cmd = ["cmd.exe", "/c", bat_to_run]
                        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                        info_callback(f"Đang chạy: {bat_to_run}\n")
                        for line in proc.stdout:
                            info_callback(line)
                        for line in proc.stderr:
                            info_callback(line)
                        proc.wait()
                        info_callback(f"\n[Hoàn thành] Bạn có thể kiểm tra kết quả ở cửa sổ này hoặc cmd.")
                    except Exception as e:
                        messagebox.showerror("RUN BCT BUILD", f"Không thể chạy file: {e}")
                else:
                    messagebox.showerror("RUN BCT BUILD", "Đường dẫn không hợp lệ hoặc không phải file .bat.")
            threading.Thread(target=run_cmd, daemon=True).start()


    def run_bct_bat(self):
        path = self.bct_out_path_var.get()
        set_lines = []
        for var, entry in self.bct_options.items():
            value = entry.get().strip()
            if value:
                set_lines.append(f"set {var}={value}")
        import os
        if path and os.path.isfile(path) and path.lower().endswith('.bat'):
            # Gộp các lệnh set và chạy file .bat trong cmd mới
            set_cmd = ' && '.join(set_lines) if set_lines else ''
            if set_cmd:
                cmd = f'start cmd /k "{set_cmd} && \"{path}\""'
            else:
                cmd = f'start cmd /k "\"{path}\""'
            try:
                subprocess.Popen(cmd, shell=True)
                self.append_info_text(f"[BCT] Đã mở cmd với: {path}\nBạn có thể thao tác trực tiếp trong cửa sổ cmd mới.\n")
            except Exception as e:
                messagebox.showerror("RUN BCT BUILD", f"Không thể chạy file: {e}")
        else:
            messagebox.showerror("RUN BCT BUILD", "Đường dẫn không hợp lệ hoặc không phải file .bat.")

    def run_build_selena_bat(self):
        # Mở cmd mới để chạy file .bat, cho phép nhập từ bàn phím
        path = self.build_selena_path_var.get().strip()
        if path and os.path.isfile(path) and path.lower().endswith('.bat'):
            try:
                # Sử dụng start cmd để mở cửa sổ cmd mới, cho phép nhập từ bàn phím
                cmd = f'start cmd /k "{path}"'
                subprocess.Popen(cmd, shell=True)
                self.append_info_text(f"[Build Selena] Đã mở cửa sổ cmd với: {path}\nBạn có thể nhập trực tiếp trong cửa sổ cmd mới.\n")
            except Exception as e:
                messagebox.showerror("RUN Build Selena", f"Không thể chạy file: {e}")
        else:
            messagebox.showerror("RUN Build Selena", "Đường dẫn không hợp lệ hoặc không phải file .bat.")
    # ...existing code...

    def _info_callback(self, text):
        if text == 'clear':
            self.terminal_text.delete(1.0)
        else:
            self.append_info_text(text)

    def bct_build_action(self):
        # TODO: Thực hiện logic BCT BUILD tại đây
        messagebox.showinfo("BCT BUILD", "Đã thực thi BCT BUILD!")

    def build_selena_action(self):
        # TODO: Thực hiện logic build Selena tại đây
        value = self.build_selena_var.get().strip()
        messagebox.showinfo("Build Selena", f"Đã thực thi Build Selena với: {value}")

    def save_bct_out_path(self, *args):
        # Lưu bct_out_path vào all_paths.json
        path = self.bct_out_path_var.get()
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        # Lấy project, variant, release từ 3 ô nhập
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        if not key:
            return
        data = {}
        if os.path.isfile(all_paths_file):
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        if key not in data:
            data[key] = {k: v.get() for k, v in self.path_vars.items()}
        data[key]["bct_out"] = path
        try:
            with open(all_paths_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Không thể lưu bct_out_path vào all_paths.json: {e}")

    def load_selena_env(self):
        # Load selena_env from all_paths.json
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        # Lấy project, variant, release từ 3 ô nhập
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        if key and os.path.isfile(all_paths_file):
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                selena_env = data.get(key, {}).get("selena_env", "")
                self.selected_env_var.set(selena_env)
            except Exception:
                self.selected_env_var.set("")
        else:
            self.selected_env_var.set("")

    def save_selena_env(self, *args):
        # Save selena_env to all_paths.json
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        # Lấy project, variant, release từ 3 ô nhập
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        if not key:
            return
        data = {}
        if os.path.isfile(all_paths_file):
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        if key not in data:
            data[key] = {k: v.get() for k, v in self.path_vars.items()}
        data[key]["selena_env"] = self.selected_env_var.get()
        try:
            with open(all_paths_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Không thể lưu selena_env vào all_paths.json: {e}")

    def show_conda_env_selector(self):
        import os
        import tkinter as tk
        from tkinter import simpledialog
        envs = []
        user_home = os.path.expanduser('~')
        conda_envs_dir = os.path.join(user_home, ".conda", "envs")
        if os.path.isdir(conda_envs_dir):
            for env in os.listdir(conda_envs_dir):
                env_path = os.path.join(conda_envs_dir, env)
                if os.path.isdir(env_path):
                    envs.append(env)
        # Thử lấy thêm env từ lệnh conda
        try:
            import subprocess
            conda_envs = subprocess.check_output(["conda", "env", "list"], universal_newlines=True, stderr=subprocess.DEVNULL)
            for line in conda_envs.splitlines():
                if line and not line.startswith("#") and ("/" in line or "\\" in line):
                    env_name = line.split()[0]
                    if env_name not in envs:
                        envs.append(env_name)
        except Exception:
            pass
        if not envs:
            messagebox.showinfo("Conda Env", "Không tìm thấy conda env nào.")
            return
        # Hiển thị top-level chọn env
        top = tk.Toplevel(self.root)
        top.title("Chọn Conda Env")
        tk.Label(top, text="Chọn một conda env:").pack(padx=10, pady=10)
        listbox = tk.Listbox(top, width=40, height=10)
        for env in envs:
            listbox.insert(tk.END, env)
        listbox.pack(padx=10, pady=5)
        def select_env():
            sel = listbox.curselection()
            if sel:
                env_name = listbox.get(sel[0])
                self.selected_env_var.set(env_name)
                top.destroy()
        btn = tk.Button(top, text="Chọn", command=select_env)
        btn.pack(pady=10)
        listbox.bind('<Double-1>', lambda e: select_env())
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)

    def open_json_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            self.json_var.set(file_path)
            self.json_entry.config(fg="black")

    def open_scom_file(self):
        import os
        import subprocess
        path = self.scom_actual_var.get().strip()
        if path and os.path.isfile(path):
            folder = os.path.dirname(path)
            try:
                subprocess.Popen(["explorer", folder])
            except Exception as e:
                messagebox.showerror("Open Folder", f"Không thể mở thư mục: {e}")
        else:
            messagebox.showerror("Open Folder", "Không tìm thấy file SCOM để mở thư mục.")

    def open_toolbox_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file_path:
            self.toolbox_var.set(file_path)
            self.toolbox_entry.config(fg="black")

    def open_selena_exe_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EXE files", "*.exe")])
        if file_path and file_path.lower().endswith('.exe'):
            self.selena_exe_var.set(file_path)
            self.selena_exe_entry.config(fg="black")
        elif file_path:
            messagebox.showerror("Lỗi", "Chỉ được chọn file .exe")

    def add_source_command(self):
        # Ví dụ: khi nhấn Add_command, sẽ thêm tên source vào ô nhập (có thể tùy chỉnh logic này)
        current = self.source_command_var.get()
        selected = self.source_var.get()
        if current:
            new_val = current + ", " + selected
        else:
            new_val = selected
        self.source_command_var.set(new_val)

    def open_runtime_file(self):
        path = self.runtime_var.get().strip()
        if path and os.path.isfile(path):
            folder = os.path.dirname(path)
            try:
                subprocess.Popen(["explorer", folder])
            except Exception as e:
                messagebox.showerror("Open Folder", f"Không thể mở thư mục: {e}")
        else:
            file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
            if file_path:
                self.runtime_var.set(file_path)
                self.runtime_entry.config(fg="black")

    def run_gen_runtime(self):
        def worker():
            # Gather required variables
            toolbox_path = self.toolbox_var.get().strip()
            scom_path = self.scom_actual_var.get().strip()
            mempool_path = self.mempool_var.get().strip()
            sequence_path = self.sequence_var.get().strip()
            systemtime_path = self.systemtime_var.get().strip()
            run_order_path = self.run_order_var.get().strip()
            source_var_path = self.source_var.get().strip()            
            json_path = self.json_var.get().strip()
            mf4_path = self.mf4_var.get().strip()
            adapter_path = self.adapter_file_var.get().strip()
            env_name = self.selected_env_var.get().strip()
            # Resolve Conda environment Python path using gen_mem_sequence logic
            user_home = os.path.expanduser('~')
            conda_envs_dir = os.path.join(user_home, ".conda", "envs")
            env_path = os.path.join(conda_envs_dir, env_name)
            python_path = os.path.join(env_path, "python.exe")
            # Lấy project, variant, release từ 3 ô nhập
            project = self.project_var.get().strip()
            variant = self.variant_var.get().strip()
            release = self.release_var.get().strip()
            if not project or not variant or not release:
                self.root.after(0, lambda: messagebox.showerror("Error", "Không thể phân tích project/variant/release từ 3 ô nhập!"))
                return
            # Đường dẫn runtime.xml theo cấu trúc folder giống A2L
            base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            runtime_folder = os.path.join(base_folder, "Runtime", project, variant, release)
            os.makedirs(runtime_folder, exist_ok=True)
            runtime_output = os.path.join(runtime_folder, "runtime.xml")

            # Validate required arguments
            if not toolbox_path or not os.path.isfile(toolbox_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "Toolbox path is missing or invalid."))
                return
            if not scom_path or not os.path.isfile(scom_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "SCOM path is missing or invalid."))
                return
            if not mempool_path or not os.path.isfile(mempool_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "Mempool path is missing or invalid."))
                return
            if not sequence_path or not os.path.isfile(sequence_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "sequence path is missing or invalid."))
                return
            if not systemtime_path or not os.path.isfile(systemtime_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "Systemtime path is missing or invalid."))
                return
            if not run_order_path or not os.path.isfile(run_order_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "Run Order path is missing or invalid."))
                return
            # if not source_var_path or not os.path.isfile(source_var_path):
            #     self.root.after(0, lambda: messagebox.showerror("Error", "Source Var path is missing or invalid."))
            #     return
            if not json_path or not os.path.isfile(json_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "JSON path is missing or invalid."))
                return
            if not mf4_path or not os.path.isfile(mf4_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "MF4 path is missing or invalid."))
                return
            if not os.path.isfile(python_path):
                self.root.after(0, lambda: messagebox.showerror("Error", "Selected Conda environment is invalid or missing Python executable."))
                return
            
            

            # Construct the base command (add -u for unbuffered output)
            command = (
                f"{python_path} -u {toolbox_path} runtime create++ {scom_path} -c {json_path} "
                f"--run {run_order_path} "
                f"-s {source_var_path} "
                f"-mb -mp {mempool_path} "
                f"-sn {sequence_path} "
                f"-st {systemtime_path} "
                f"-o {runtime_output} "
                f"-dk -dr mat "
                f"-dr mdf -s mdf "
                f"-dp mdf mdfplayer"
            )
            if adapter_path:
                command += f" -a {adapter_path}"

            self.root.after(0, lambda: self.append_info_text(f"[COMMAND] {command}\n"))
            self.root.after(0, lambda: self.append_info_text("[PROGRESS] Đang chạy Gen Runtime...\n"))
            try:
                process = subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
                )
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.root.after(0, lambda l=line: self.append_info_text(l))
                process.stdout.close()
                process.wait()
                if process.returncode == 0:
                    self.root.after(0, lambda: self.append_info_text("[PROGRESS] Đã hoàn thành Gen Runtime!\n"))
                    self.root.after(0, lambda: self.runtime_var.set(runtime_output))
                    self.root.after(0, lambda: messagebox.showinfo("Gen Runtime", "Runtime generation completed successfully."))
                    # Thay thế <plugins> trong runtime.xml
                    try:
                        with open(runtime_output, 'r', encoding='utf-8') as f:
                            xml_text = f.read()
                        plugins_new = '''<plugins>
    <recorder id="matrecorder" plugin="DataRecorderPluginMAT" />
    <plugin name="pl1r1v_player_module_mdf">
      <player id="mdfplayer" plugin="PL1R1VDataPlayerPluginMDF" default="1" />
    </plugin>
    <plugin name="pl1r1v_recorder_module_mdf">
      <recorder id="mdfrecorder" plugin="PL1R1VDataRecorderPluginMDF" />
    </plugin>
    <plugin name="pl1r1v_scheduler_module_mdf">
      <scheduler id="mdfscheduler" plugin="PL1R1VSchedulerPluginMDF" />
    </plugin>
</plugins>'''
                        xml_text = re.sub(r'<plugins[\s\S]*?</plugins>', plugins_new, xml_text, flags=re.MULTILINE)
                        with open(runtime_output, 'w', encoding='utf-8') as f:
                            f.write(xml_text)
                        self.root.after(0, lambda: self.append_info_text("[INFO] Đã thay thế <plugins> trong runtime.xml!\n"))
                    except Exception as e:
                        self.root.after(0, lambda: self.append_info_text(f"[ERROR] Không thể thay thế <plugins>: {e}\n"))
                else:
                    self.root.after(0, lambda: self.append_info_text("[PROGRESS] Gen Runtime thất bại!\n"))
                    self.root.after(0, lambda: messagebox.showerror("Gen Runtime", "Runtime generation failed."))
            except Exception as e:
                self.root.after(0, lambda: self.append_info_text(f"[EXCEPTION] {e}\n"))
                self.root.after(0, lambda: messagebox.showerror("Gen Runtime", f"Error during runtime generation: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def gen_a2l_table(self):
        import threading
        def worker():
            a2l_path = os.path.normpath(self.a2l_actual_var.get().strip())
            if not a2l_path or not os.path.isfile(a2l_path):
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Vui lòng tìm đúng file .a2l trước khi chạy!"))
                return
            # Lấy project, variant, release từ 3 ô nhập
            project = self.project_var.get().strip()
            variant = self.variant_var.get().strip()
            release = self.release_var.get().strip()
            if not project or not variant or not release:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể phân tích project/variant/release từ 3 ô nhập!"))
                return
            repo_path = os.path.normpath(self.repo_path_var.get().strip())
            if not repo_path:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Vui lòng chọn Repository!"))
                return
            # Build im_lazy.py path dynamically
            im_lazy_path = os.path.normpath(os.path.join(repo_path, f"{project}_apl", "selena", "im_lazy.py"))
            cmd1 = [sys.executable, im_lazy_path]
            out_dir = os.path.normpath(os.path.join(repo_path, f"{project}_apl", "selena", "config", "mapping"))
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.normpath(os.path.join(out_dir, f"a2lTable_{variant}_{release}.txt"))
            parser_py = os.path.normpath(os.path.join(repo_path, "ip_dc", "dc_tools", "utils", "a2l_processing", "ASAPParser.py"))
            cmd2 = [sys.executable, parser_py, "-i", a2l_path, "-o", out_file]
            self.root.after(0, lambda: self.append_info_text(f"[GEN] Chạy: {' '.join(cmd1)}\n"))
            try:
                result1 = subprocess.run(cmd1, capture_output=True, text=True, check=True)
                self.root.after(0, lambda: self.append_info_text(result1.stdout))
                if result1.stderr:
                    self.root.after(0, lambda: self.append_info_text(result1.stderr))
            except Exception as e:
                self.root.after(0, lambda e=e: self.append_info_text(f"[GEN] Lỗi chạy im_lazy.py: {e}\n"))
                return
            self.root.after(0, lambda: self.append_info_text(f"[GEN] Chạy: {' '.join(cmd2)}\n"))
            try:
                result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)
                self.root.after(0, lambda: self.append_info_text(result2.stdout))
                if result2.stderr:
                    self.root.after(0, lambda: self.append_info_text(result2.stderr))
                self.root.after(0, lambda: self.a2l_table_var.set(out_file))
                self.root.after(0, lambda: self.append_info_text(f"[GEN] Đã tạo: {out_file}\n"))
            except Exception as e:
                self.root.after(0, lambda e=e: self.append_info_text(f"[GEN] Lỗi chạy ASAPParser.py: {e}\n"))
        threading.Thread(target=worker, daemon=True).start()

    def open_a2l_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("A2L Table files", "*.*"), ("All files", "*.*")])
        if file_path:
            self.a2l_table_var.set(file_path)
            self.a2l_table_entry.config(fg="black")

    def open_a2l_config_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.delivery_var.set(folder_path)
            self.delivery_entry.config(fg="black")

    def delivery_folders(self):
        import json
        import tkinter as tk
        from tkinter import messagebox, filedialog
        # Load danh sách folder
        folders = []
        if os.path.isfile(self.delivery_folder):
            try:
                with open(self.delivery_folder, "r", encoding="utf-8") as f:
                    folders = json.load(f)
                if not isinstance(folders, list):
                    folders = []
            except Exception:
                folders = []
        # Dialog
        top = tk.Toplevel(self.root)
        top.title("Quản lý Delivery Folders")
        tk.Label(top, text="Danh sách Delivery Folder:").pack(padx=10, pady=5)
        list_frame = tk.Frame(top)
        list_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        listbox = tk.Listbox(list_frame, width=70, height=8)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        def refresh_listbox():
            listbox.delete(0, tk.END)
            for folder in folders:
                listbox.insert(tk.END, folder)
        refresh_listbox()
        # Form nhập folder
        form_frame = tk.Frame(top)
        form_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Label(form_frame, text="Delivery Folder:").grid(row=0, column=0, sticky=tk.W)
        folder_var = tk.StringVar()
        folder_entry = tk.Entry(form_frame, textvariable=folder_var, width=60)
        folder_entry.grid(row=0, column=1, sticky=tk.W)
        def choose_folder():
            path = filedialog.askdirectory()
            if path:
                folder_var.set(path)
        choose_btn = tk.Button(form_frame, text="Chọn Folder", command=choose_folder)
        choose_btn.grid(row=0, column=2, padx=5)
        # Khi chọn listbox thì cập nhật form và set vào self.a2l_config_var
        def on_listbox_select(event):
            sel = listbox.curselection()
            if sel:
                value = listbox.get(sel[0])
                folder_var.set(value)
                self.delivery_var.set(value)
                self.delivery_entry.config(fg="black")
                top.destroy()
        listbox.bind('<<ListboxSelect>>', on_listbox_select)
        # Lưu/sửa folder
        def save_folder():
            folder = folder_var.get().strip()
            if not folder:
                messagebox.showerror("Lỗi", "Vui lòng nhập đường dẫn delivery folder!")
                return
            if folder not in folders:
                folders.append(folder)
                with open(self.delivery_folder, "w", encoding="utf-8") as f:
                    json.dump(folders, f, ensure_ascii=False, indent=2)
                refresh_listbox()
                messagebox.showinfo("Lưu thành công", f"Đã lưu folder:\n{folder}")
            else:
                messagebox.showinfo("Thông báo", "Folder đã có trong danh sách!")
        save_btn = tk.Button(top, text="Lưu/Sửa", command=save_folder)
        save_btn.pack(padx=10, pady=5)
        # Xoá folder
        def delete_folder():
            folder = folder_var.get().strip()
            if folder in folders:
                if messagebox.askyesno("Xác nhận xoá", f"Xoá folder:\n{folder}?"):
                    folders.remove(folder)
                    with open(self.delivery_folder, "w", encoding="utf-8") as f:
                        json.dump(folders, f, ensure_ascii=False, indent=2)
                    folder_var.set("")
                    refresh_listbox()
        del_btn = tk.Button(top, text="Xoá Folder", command=delete_folder)
        del_btn.pack(padx=10, pady=5)
        close_btn = tk.Button(top, text="Đóng", command=top.destroy)
        close_btn.pack(padx=10, pady=10)
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)
        # Đã loại bỏ các biến và hàm không còn dùng đến: folder_status_var, folder_status_label, check_a2l_file, project_var

    def update_a2l_config_by_project(self):
        import json
        project = self.source_var.get().strip()
        if not project:
            return
        if os.path.isfile(self.delivery_folder):
            try:
                with open(self.delivery_folder, "r", encoding="utf-8") as f:
                    mapping = json.load(f)
                folder = mapping.get(project, "")
                if folder:
                    self.delivery_var.set(folder)
            except Exception:
                pass
        # Sau khi cập nhật path, filter file luôn
        self.filter_a2l_file()

    def filter_a2l_file(self):
        import os
        config_path = self.delivery_var.get().strip()
        project = self.source_var.get().strip()
        if not config_path or not os.path.isdir(config_path):
            return
        a2l_filename = f"{project}.a2l"
        a2l_path = os.path.join(config_path, a2l_filename)
        if os.path.isfile(a2l_path):
            self.a2l_actual_var.set(a2l_path)
        else:
            self.a2l_actual_var.set("")
    def get_project_variant_release(self):
        # Trả về tuple (project, variant, release) từ 3 ô nhập
        return self.project_var.get().strip(), self.variant_var.get().strip(), self.release_var.get().strip()

    def find_a2l_in_zip(self):
        def worker():
            from tkinter import simpledialog, messagebox
            import glob
            self.append_info_text("[A2L] Bắt đầu tìm kiếm file A2L trong .zip/.7z...\n")
            delivery_path = self.delivery_var.get().strip()
            project = self.project_var.get().strip()
            variant = self.variant_var.get().strip()
            release = self.release_var.get().strip()
            source = self.source_var.get().strip() if hasattr(self, 'source_var') else ''
            if not project or not variant or not release or not source:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể phân tích được project/variant/release từ đường dẫn hoặc source!"))
                self.append_info_text("[A2L] Không thể phân tích project/variant/release từ đường dẫn hoặc source.\n")
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            a2l_folder = os.path.join(project_root, "A2L", project, variant, release)
            os.makedirs(a2l_folder, exist_ok=True)
            a2l_filename = f"{source}.a2l"
            dest_path = os.path.join(a2l_folder, a2l_filename)
            # Tìm cả .zip và .7z
            search_folders = [delivery_path] if os.path.isdir(delivery_path) else [os.path.dirname(delivery_path)]
            archive_files = []
            for folder in search_folders:
                archive_files.extend(glob.glob(os.path.join(folder, '*.zip')))
                archive_files.extend(glob.glob(os.path.join(folder, '*.7z')))
            if os.path.isfile(delivery_path) and (delivery_path.lower().endswith('.zip') or delivery_path.lower().endswith('.7z')):
                archive_files.insert(0, delivery_path)
            self.append_info_text(f"[A2L] Đang kiểm tra {len(archive_files)} file zip/7z trong thư mục: {delivery_path}\n")
            found = False
            for archive_path in archive_files:
                try:
                    self.append_info_text(f"[A2L] Đọc file archive: {archive_path}\n")
                    if archive_path.lower().endswith('.zip'):
                        import zipfile
                        with zipfile.ZipFile(archive_path, 'r') as zf:
                            a2l_files = [f for f in zf.namelist() if os.path.basename(f).lower() == a2l_filename.lower()]
                            if a2l_files:
                                a2l_file = a2l_files[0]
                                self.append_info_text(f"[A2L] Đang giải nén {a2l_file}...\n")
                                with zf.open(a2l_file) as src, open(dest_path, 'wb') as dst:
                                    shutil.copyfileobj(src, dst)
                                self.root.after(0, lambda: self.a2l_actual_var.set(dest_path))
                                self.append_info_text(f"[A2L] Đã giải nén thành công: {dest_path}\n")
                                found = True
                                break
                    elif archive_path.lower().endswith('.7z'):
                        import py7zr
                        with py7zr.SevenZipFile(archive_path, 'r') as zf:
                            all_files = zf.getnames()
                            a2l_files = [f for f in all_files if os.path.basename(f).lower() == a2l_filename.lower()]
                            if a2l_files:
                                a2l_file = a2l_files[0]
                                self.append_info_text(f"[A2L] Đang giải nén {a2l_file}...\n")
                                zf.extract(targets=[a2l_file], path=a2l_folder)
                                self.root.after(0, lambda: self.a2l_actual_var.set(os.path.join(a2l_folder, os.path.basename(a2l_file))))
                                self.append_info_text(f"[A2L] Đã giải nén thành công: {os.path.join(a2l_folder, os.path.basename(a2l_file))}\n")
                                found = True
                                break
                except Exception as e:
                    self.append_info_text(f"[A2L] Lỗi khi đọc {archive_path}: {e}\n")
            if not found:
                self.root.after(0, lambda: messagebox.showerror("A2L", "Không tìm thấy file .a2l phù hợp trong các archive!"))
                self.append_info_text("[A2L] Không tìm thấy file .a2l phù hợp trong các archive.\n")
        threading.Thread(target=worker, daemon=True).start()

    def find_scom_in_zip(self):
        import threading
        def worker():
            import zipfile
            import glob
            import shutil
            import os
            import json
            self.append_info_text("[SCOM] Bắt đầu tìm kiếm file SCOM trong .zip...\n")
            delivery_path = self.delivery_var.get().strip()
            project = self.project_var.get().strip()
            variant = self.variant_var.get().strip()
            release = self.release_var.get().strip()
            if not project or not variant or not release:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể phân tích được project/variant/release từ đường dẫn!"))
                self.append_info_text("[SCOM] Không thể phân tích project/variant/release từ đường dẫn.\n")
                return
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scom_folder = os.path.join(project_root, "SCOM", project, variant, release)
            os.makedirs(scom_folder, exist_ok=True)
            scom_filename = "scom.xml"
            dest_path = os.path.join(scom_folder, scom_filename)
            
            # Nếu chưa có file, thực hiện giải nén như cũ
            if os.path.isfile(delivery_path) and delivery_path.lower().endswith('.zip'):
                zip_files = [delivery_path]
                self.append_info_text(f"[SCOM] Đang kiểm tra file zip: {delivery_path}\n")
            elif os.path.isdir(delivery_path):
                zip_files = glob.glob(os.path.join(delivery_path, '*.zip'))
                self.append_info_text(f"[SCOM] Đang kiểm tra {len(zip_files)} file zip trong thư mục: {delivery_path}\n")
            else:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Đường dẫn không hợp lệ!"))
                self.append_info_text("[SCOM] Đường dẫn không hợp lệ!\n")
                return
            found = False
            for zip_path in zip_files:
                try:
                    self.append_info_text(f"[SCOM] Đọc file zip: {zip_path}\n")
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        scom_files = [f for f in zf.namelist() if os.path.basename(f).lower() == scom_filename.lower()]
                        if scom_files:
                            scom_file = scom_files[0]
                            self.append_info_text(f"[SCOM] Đang giải nén {scom_file}...\n")
                            with zf.open(scom_file) as src, open(dest_path, 'wb') as dst:
                                shutil.copyfileobj(src, dst)
                            def update_ui():
                                self.scom_actual_var.set(dest_path)
                                msg = f"Đã copy {scom_filename} vào: {dest_path}"
                                messagebox.showinfo("Thành công", msg)
                                self.append_info_text(f"[SCOM] {msg}\n")
                            self.root.after(0, update_ui)
                            found = True
                            break
                        else:
                            self.append_info_text(f"[SCOM] Không tìm thấy {scom_filename} trong {zip_path}\n")
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể đọc file zip: {zip_path}\n{e}"))
                    self.root.after(0, lambda: self.append_info_text(f"[SCOM] Lỗi đọc zip: {zip_path} - {e}\n"))
                    return
            if not found:
                def not_found():
                    msg = f"Không tìm thấy file {scom_filename} trong các file .zip!"
                    messagebox.showerror("Lỗi", msg)
                    self.append_info_text(f"[SCOM] {msg}\n")
                self.root.after(0, not_found)
        threading.Thread(target=worker, daemon=True).start()

    def run_python_in_conda_env(python_path, script_path, terminal_callback, done_callback=None):
        def run_cmd():
            terminal_callback(f"Đang chạy: {python_path} {script_path}\n")
            try:
                proc = subprocess.Popen([python_path, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                while True:
                    out = proc.stdout.readline()
                    if out:
                        terminal_callback(out)
                    err = proc.stderr.readline()
                    if err:
                        terminal_callback(err)
                    if out == '' and err == '' and proc.poll() is not None:
                        break
                proc.wait()
                terminal_callback(f"\n[Hoàn thành] Đã chạy xong.")
            except Exception as e:
                terminal_callback(f"Exception: {e}\n")
                messagebox.showerror("Lỗi chạy script", f"Không thể chạy file: {e}")
            if done_callback:
                done_callback()
        threading.Thread(target=run_cmd, daemon=True).start()

    def open_a2l_folder(self):
        import os
        import subprocess
        path = self.a2l_table_var.get().strip()
        if path and os.path.isfile(path):
            folder = os.path.dirname(path)
            try:
                subprocess.Popen(["explorer", folder])
            except Exception as e:
                messagebox.showerror("Open Folder", f"Không thể mở thư mục: {e}")
        else:
            messagebox.showerror("Open Folder", "Không tìm thấy file A2L để mở thư mục.")

    def append_info_text(self, text):
        # Chỉ cần insert từng dòng, Text widget sẽ tự động wrap theo chiều rộng hiện tại
        lines = text.splitlines()
        for line in lines:
            self.terminal_text.insert(tk.END, line + '\n')
        self.terminal_text.see(tk.END)

    def choose_mf4_file(self):
        # Mở File Explorer để chọn file .mf4
        file_path = filedialog.askopenfilename(filetypes=[("MF4 files", "*.mf4"), ("All files", "*.*")], title="Select MF4 File")
        
        if file_path:
            # Cập nhật đường dẫn file vào mf4_var và hiển thị trong mf4_entry
            self.mf4_var.set(file_path)
            self.mf4_entry.config(fg="black")

    def save_all_paths(self, *args):
        # Lưu tất cả các biến path_vars vào all_paths.json, bao gồm run_order và selena_env
       
       

       
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        project = self.project_var.get().strip()
        variant = self.variant_var.get().strip()
        release = self.release_var.get().strip()
        key = f"{project}|{variant}|{release}" if project and variant and release else None
        if not key:
            return
        data = {}
        if os.path.isfile(all_paths_file):
            try:
                with open(all_paths_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        # Lưu tất cả các biến path_vars, bao gồm run_order
        data[key] = {k: v.get() for k, v in self.path_vars.items()}
        # Lưu thêm trường selena_env
        data[key]["selena_env"] = self.selected_env_var.get()
        # Lưu thêm trường a2l_actual
        data[key]["a2l_actual"] = self.a2l_actual_var.get()
        try:
            with open(all_paths_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Không thể lưu all_paths.json: {e}")

    def load_all_paths(self):
        # Hàm này sẽ load all_paths.json, cho phép chọn, duplicate (load) và xoá các path không cần nữa (chỉ xoá key, không xoá file/folder ngoài ổ đĩa)
        import threading
        record_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "record")
        all_paths_file = os.path.join(record_dir, "all_paths.json")
        if not os.path.isfile(all_paths_file):
            messagebox.showinfo("Load All Paths", "Không tìm thấy all_paths.json!")
            return
        with open(all_paths_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        keys = list(data.keys())
        if not keys:
            messagebox.showinfo("Load All Paths", "Không có path nào để load!")
            return
        # Hiển thị dialog chọn/xoà/duplicate
        top = tk.Toplevel(self.root)
        top.title("Quản lý All Paths")
        tk.Label(top, text="Chọn các path muốn thao tác:").pack(padx=10, pady=5)
        listbox = tk.Listbox(top, selectmode=tk.MULTIPLE, width=60, height=10)
        for k in keys:
            listbox.insert(tk.END, k)
        listbox.pack(padx=10, pady=5)
        def duplicate_selected():
            selected = listbox.curselection()
            if not selected:
                messagebox.showinfo("Load Path", "Chưa chọn path nào để load!")
                return
            # Lấy thông tin của path đầu tiên được chọn
            k = keys[selected[0]]
            v = data.get(k, {})
            # Điền các thông tin đã lưu vào GUI
            for field, var in self.path_vars.items():
                if field in v:
                    var.set(v[field])
            # Điền các trường đặc biệt
            self.selected_env_var.set(v.get("selena_env", ""))
            self.a2l_actual_var.set(v.get("a2l_actual", ""))
            messagebox.showinfo("Load Path", f"Đã nạp thông tin từ: {k}")
            top.destroy()
        def delete_selected():
            def do_delete():
                selected = listbox.curselection()
                if not selected:
                    self.root.after(0, lambda: messagebox.showinfo("Xoá Path", "Chưa chọn path nào để xoá!"))
                    return
                to_delete = [keys[i] for i in selected]
                for k in to_delete:
                    data.pop(k, None)
                with open(all_paths_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.root.after(0, lambda: messagebox.showinfo("Xoá Path", f"Đã xoá {len(to_delete)} path khỏi all_paths.json!"))
                self.root.after(0, top.destroy)
            threading.Thread(target=do_delete, daemon=True).start()
        btn_dup = tk.Button(top, text="Nạp thông tin path đã chọn", command=duplicate_selected)
        btn_dup.pack(pady=5)
        btn_del = tk.Button(top, text="Xoá các path đã chọn", command=delete_selected)
        btn_del.pack(pady=5)
        close_btn = tk.Button(top, text="Đóng", command=top.destroy)
        close_btn.pack(pady=5)
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)

    def run_order_action(self):
        # TODO: Thực hiện logic run_order tại đây
        value = self.run_order_var.get().strip()
        messagebox.showinfo("Run Order", f"Đã thực thi Run Order với: {value}")

    def run_simulation_action(self):
        from tkinter import messagebox
        # Lấy các giá trị từ GUI
        exe_path = os.path.normpath(self.selena_exe_var.get().strip())
        runtime_xml = os.path.normpath(self.runtime_var.get().strip())
        mf4_path = os.path.normpath(self.mf4_var.get().strip())
        # Output MF4 và log file sẽ đặt cùng thư mục với MF4, thêm _output
        if mf4_path:
            base, ext = os.path.splitext(mf4_path)
            output_mf4 = os.path.normpath(base + '_output' + ext)
            output_log = os.path.normpath(base + '_log.txt')
        else:
            output_mf4 = ''
            output_log = ''
        source = self.source_var.get().strip() or 'RadarFC'
        # plugins_dir là folder chứa exe_path/plugins
        plugins_dir = os.path.normpath(os.path.join(os.path.dirname(exe_path), 'plugins'))
        # Các tham số bổ sung
        userparam = "BEPRuntimeLimitationLikeOnTarget=1"
        # Lấy conda env
        env_name = self.selected_env_var.get().strip()
        user_home = os.path.expanduser('~')
        conda_envs_dir = os.path.normpath(os.path.join(user_home, ".conda", "envs"))
        env_path = os.path.normpath(os.path.join(conda_envs_dir, env_name))
        python_path = os.path.normpath(os.path.join(env_path, "python.exe"))
        # Build command
        cmd = (
            f'"{exe_path}" -c "{runtime_xml}" --i_mdfplayer "{mf4_path}" -o "{output_mf4}" '
            f'--enable-doorkeeper --enable-multibuffer-border --nogui -l "{output_log}" -s {source} '
            f'--userparam {userparam} --plugins_directory "{plugins_dir}"'
        )
        def run():
            self.append_info_text(f"[SIM] Running: {cmd}\n")
            # Nếu có conda env, chạy trong conda env
            activate = os.path.normpath(os.path.join(env_path, "Scripts", "activate.bat"))
            if os.path.isfile(activate):
                full_cmd = f'cmd.exe /c "call \"{activate}\" && {cmd}"'
            else:
                full_cmd = cmd
            try:
                proc = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.root.after(0, lambda l=line: self.append_info_text(l))
                proc.wait()
                if proc.returncode == 0:
                    self.root.after(0, lambda: self.append_info_text("[SIM] Simulation completed successfully.\n"))
                else:
                    self.root.after(0, lambda: self.append_info_text(f"[SIM] Simulation failed with code {proc.returncode}.\n"))
            except Exception as e:
                self.root.after(0, lambda: self.append_info_text(f"[SIM][ERROR] {e}\n"))
        threading.Thread(target=run, daemon=True).start()

    def gen_runnable_level_template(self):
        from tkinter import messagebox
        import shutil
        try:
            # Lấy project, variant, release từ 3 ô nhập
            project = self.project_var.get().strip()
            variant = self.variant_var.get().strip()
            release = self.release_var.get().strip()
            if not project or not variant or not release:
                messagebox.showerror("Lỗi", "Không thể phân tích project/variant/release từ 3 ô nhập!")
                return
            # Đường dẫn output
            base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            out_folder = os.path.join(base_folder, "Runnable_Level", project, variant, release)
            os.makedirs(out_folder, exist_ok=True)
            out_file = os.path.join(out_folder, "runnable_level.json")
            # Nếu đã có file cũ thì xoá đi
            if os.path.isfile(out_file):
                os.remove(out_file)
            template_path = os.path.join(base_folder, "templates", "runable_level_MY22.json")
            # Đọc nội dung runable_level_MMC.json
            with open(template_path, "r", encoding="utf-8") as f:
                runnables_data = json.load(f)

            # Đường dẫn report và Justin đồng bộ theo yêu cầu, theo project/variant/release
            Justin_path = os.path.join(base_folder, "Justin", project, variant, release).replace("\\", "/")

            # Lấy các giá trị động từ GUI hoặc build từ project/variant/release
            runtime_path = os.path.join(Justin_path, "runtimes").replace("\\", "/")
            #path to json 
            json_path = os.path.join(self.json_var.get().strip()).replace("\\", "/")
            #path to selena.exe
            exe_path = os.path.normpath(self.selena_exe_var.get().strip()).replace("\\", "/")
            #path to repo 
            repo_path = os.path.normpath(self.repo_path_var.get().strip()).replace("\\", "/")
            #path to mf4 file
            mf4_path = self.mf4_var.get().strip().replace("\\", "/") if self.mf4_var.get().strip() else ""
            mf4_name = os.path.splitext(os.path.basename(mf4_path))[0] if mf4_path else "AEB"
            #path to data
            data_path = os.path.normpath(os.path.dirname(mf4_path)).replace("\\", "/")
            data_path = data_path + "/"

            # testplan_creation
            testplan_creation = {
                "comparer_type": "comparer_jenkins",   
                "ignore_signals": [
                    ".*m_sequenceNumber.*",
                    ".*m_referenceCounter.*",
                    ".*m_systemTime.*",
                    ".*freeHeadOffset.*"
                ],
                "justin_config_path": os.path.join(Justin_path, "justin_configs").replace("\\", "/"),
                "justin_path": os.path.join(repo_path, "ip_dc/dc_tools/justin").replace("\\", "/"),
                "report_path": os.path.join(Justin_path, "reports").replace("\\", "/"),
                "selena_args": "--enable-multibuffer-border --enable-doorkeeper",
                "selena_path": os.path.normpath(os.path.dirname(exe_path)).replace("\\", "/") if exe_path else "",
                "testplan_path": os.path.join(Justin_path, "testplan_path").replace("\\", "/"),
                "tolerance": 1e-5                           
            }
            # runtime_creation
            runtime_creation = {
                "config_path": os.path.join(json_path).replace("\\", "/"),
                "data_path": os.path.join(data_path).replace("\\", "/"),
                "player":{
                        "name": "pl1r1v_player_module_mdf",
                        "plugin": "PL1R1VDataPlayerPluginMDF"
                    },
                "recorder": {
                    "name": "pl1r1v_recorder_module_mdf",
                    "plugin": "PL1R1VDataRecorderPluginMDF"
                },
                "scheduler": {
                    "name": "pl1r1v_scheduler_module_mdf",
                    "plugin": "PL1R1VSchedulerPluginMDF"
                },
                "scom_xml_path": self.scom_actual_var.get().strip().replace("\\", "/") if self.scom_actual_var.get().strip() else "",
                "use_multibuffer": True,
                "use_systemtime": True
            }

            measurements_creation = {
                mf4_name: {
                    "file": mf4_path
                }
            }
            # Build template
            template = {
                "measurements": measurements_creation,
                "runnables": runnables_data,
                "runtime_creation": runtime_creation,
                "runtime_path": runtime_path,
                "testplan_creation": testplan_creation
            }
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            self.runnable_level_var.set(out_file)

            # --- Copy Runnable_Level/.../runtimes to Justin/.../runtimes ---
            src_runtimes = os.path.join(base_folder, "Runnable_Level", project, variant, release, "runtimes")
            dst_runtimes = os.path.join(base_folder, "Justin", project, variant, release, "runtimes")
            if os.path.isdir(src_runtimes):
                # Remove destination if exists, then copy
                if os.path.exists(dst_runtimes):
                    shutil.rmtree(dst_runtimes)
                shutil.copytree(src_runtimes, dst_runtimes)

            messagebox.showinfo("Thành công", f"Đã tạo file runnable_level.json hoàn chỉnh tại:\n{out_file}\nĐã copy runtimes sang: {dst_runtimes}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo file template: {e}")

        self.gen_runnable_level_button.config(command=self.gen_runnable_level_template)
  
    def Gen_testplan_action(self):
        import threading
        def worker():
            try:
                env_name = self.selected_env_var.get().strip()
                user_home = os.path.expanduser('~')
                conda_envs_dir = os.path.join(user_home, ".conda", "envs")
                env_path = os.path.join(conda_envs_dir, env_name)
                python_path = os.path.join(env_path, "python.exe")
                if not os.path.isfile(python_path):
                    self.append_info_text(f"[Gen testplan] Không tìm thấy python.exe trong env: {env_path}\n")
                    return
                toolbox_path = self.toolbox_var.get().strip()
                if not toolbox_path or not os.path.isfile(toolbox_path):
                    self.append_info_text("[Gen testplan] Vui lòng chọn đúng file selena-toolbox.py!\n")
                    return
                toolbox_dir = os.path.dirname(toolbox_path)
                selena_toolbox_py = os.path.join(toolbox_dir, "selena-toolbox.py")
                if not os.path.isfile(selena_toolbox_py):
                    self.append_info_text(f"[Gen testplan] Không tìm thấy selena-toolbox.py trong {toolbox_dir}\n")
                    return
                runnable_level_path = self.runnable_level_var.get().strip()
                if not runnable_level_path or not os.path.isfile(runnable_level_path):
                    self.append_info_text("[Gen testplan] Vui lòng tạo file runnable_level.json trước!\n")
                    return
                project = self.project_var.get().strip()
                variant = self.variant_var.get().strip()
                release = self.release_var.get().strip()
                base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                Justin_path = os.path.join(base_folder, "Justin", project, variant, release).replace("\\", "/")
                cmd = [
                    python_path,
                    selena_toolbox_py,
                    "validate", "runnable-level",
                    runnable_level_path,
                    "-rt", "-tp", "-em",
                    "--scripts-path", Justin_path
                ]
                self.append_info_text("[Gen testplan] Running: " + ' '.join(f'\"{c}\"' if ' ' in c else c for c in cmd) + "\n")
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    self.append_info_text(line)
                process.wait()
                if process.returncode == 0:
                    self.append_info_text("[Gen testplan] Đã thực thi Gen testplan thành công!\n")
                else:
                    self.append_info_text(f"[Gen testplan] Gen testplan thất bại với mã lỗi {process.returncode}!\n")
            except Exception as e:
                self.append_info_text(f"[Gen testplan] Lỗi khi chạy Gen testplan: {e}\n")
        threading.Thread(target=worker, daemon=True).start()

    def split_mf4_file(self):
        from tkinter import messagebox
        import datetime
        import os
        def worker():
            try:
                import asammdf
            except ImportError:
                self.root.after(0, lambda: self.append_info_text("[Split MF4] Chưa cài đặt asammdf. Vui lòng chạy: pip install asammdf\n"))
                messagebox.showerror("Split MF4", "Chưa cài đặt asammdf. Vui lòng chạy: pip install asammdf")
                return
            file_path = self.mf4_var.get().strip()
            if not file_path or not os.path.isfile(file_path):
                self.root.after(0, lambda: self.append_info_text("[Split MF4] Vui lòng chọn đúng file MF4!\n"))
                messagebox.showerror("Split MF4", "Vui lòng chọn đúng file MF4!")
                return
            try:
                self.root.after(0, lambda: self.append_info_text(f"[Split MF4] Đang tách file: {file_path}\n"))
                mdf = asammdf.MDF(file_path)
                # --- Tách MF4 theo dung lượng file (100-300MB mỗi file) ---
                target_mb = 200  # Đổi giá trị này nếu muốn 100-300MB
                file_size = os.path.getsize(file_path)
                n_parts = max(1, int(file_size // (target_mb * 1024 * 1024)) + (1 if file_size % (target_mb * 1024 * 1024) else 0))
                out_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                # Chia theo tỉ lệ phần trăm dữ liệu
                for i in range(n_parts):
                    start_frac = i / n_parts
                    end_frac = (i + 1) / n_parts
                    self.root.after(0, lambda i=i+1: self.append_info_text(f"[Split MF4] Đang tạo file {base_name}_part{i}.mf4 (tỉ lệ {start_frac:.2f} đến {end_frac:.2f})...\n"))
                    split_mdf = mdf.cut(start=start_frac, stop=end_frac)
                    # Tìm tên file không bị trùng
                    out_file_base = f"{base_name}_part{i+1}.mf4"
                    out_file = os.path.join(out_dir, out_file_base)
                    count = 1
                    while os.path.exists(out_file):
                        out_file_base = f"{base_name}_part{i+1}_{count}.mf4"
                        out_file = os.path.join(out_dir, out_file_base)
                        count += 1
                    split_mdf.save(out_file)
                    self.root.after(0, lambda out_file=out_file: self.append_info_text(f"[Split MF4] Đã tạo: {out_file}\n"))
                self.root.after(0, lambda: self.append_info_text(f"[Split MF4] Hoàn thành! Đã tách thành {n_parts} file (~{target_mb}MB mỗi file) tại: {out_dir}\n"))
                messagebox.showinfo("Split MF4", f"Đã tách thành {n_parts} file (~{target_mb}MB mỗi file)!\nThư mục: {out_dir}")
            except Exception as e:
                self.root.after(0, lambda: self.append_info_text(f"[Split MF4] Lỗi khi tách file: {e}\n"))
                messagebox.showerror("Split MF4", f"Lỗi khi tách file: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def open_split_mf4_dialog(self):
        self.split_mf4_file()

    def old_import_action(self):
        from tkinter import messagebox
        runtime_path = self.runtime_var.get().strip()
        if not runtime_path or not os.path.isfile(runtime_path):
            messagebox.showerror("OLD IMPORT", "Không tìm thấy file runtime.xml!")
            return
        try:
            tree = ET.parse(runtime_path)
            root = tree.getroot()
            connections = root.findall('.//connection')
            count = 0
            debug_log = []
            for conn in connections:
                outport = conn.find('outport')
                inport = conn.find('inport')
                if outport is None or inport is None:
                    debug_log.append(f"[SKIP] Connection missing outport/inport: {ET.tostring(conn, encoding='unicode')}")
                    continue
                # Bỏ qua nếu inport có newdatacheck
                if inport.get('newdatacheck') is not None:
                    debug_log.append(f"[SKIP] inport has newdatacheck: {ET.tostring(inport, encoding='unicode')}")
                    continue
                # Bỏ qua nếu outport có doorkeeper modus="sequence_number"
                doorkeeper = outport.find('doorkeeper')
                if doorkeeper is not None and doorkeeper.get('modus') == 'sequence_number':
                    debug_log.append(f"[SKIP] Outport doorkeeper sequence_number: {ET.tostring(outport, encoding='unicode')}")
                    continue
                # Bỏ qua nếu connection có multibuffer sequencenumbersignal
                multibuffer = conn.find('multibuffer')
                if multibuffer is not None and multibuffer.get('sequencenumbersignal'):
                    debug_log.append(f"[SKIP] Connection has multibuffer sequencenumbersignal: {ET.tostring(multibuffer, encoding='unicode')}")
                    continue
                outport_runnable = outport.get('runnable')
                inport_runnable = inport.get('runnable')
                if outport_runnable == 'DataPlayer' and inport_runnable != 'DataRecorder':
                    inport.attrib = {**inport.attrib, 'old': '1'}
                    count += 1
                    debug_log.append(f"[SET OLD] inport runnable={inport_runnable}, outport runnable=DataPlayer, port={outport.get('port')}")
                else:
                    debug_log.append(f"[SKIP] inport runnable={inport_runnable}, outport runnable={outport_runnable}")
            tree.write(runtime_path, encoding='utf-8', xml_declaration=True)
            # Ghi log ra file để debug
            log_path = runtime_path + '.oldimport.log.txt'
            with open(log_path, 'w', encoding='utf-8') as f:
                for line in debug_log:
                    f.write(line + '\n')
            messagebox.showinfo("OLD IMPORT", f"Đã cập nhật runtime.xml: thêm old=\"1\" cho {count} inport (bỏ qua inport newdatacheck, doorkeeper sequence_number, multibuffer sequencenumbersignal). Log: {log_path}")
        except Exception as e:
            messagebox.showerror("OLD IMPORT", f"Lỗi khi xử lý runtime.xml: {e}")

def run_gui():
    root = tk.Tk()
    app = MF4ImporterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()