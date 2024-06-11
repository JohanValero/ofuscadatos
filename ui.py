import uuid
import json
import random
import oracledb

import tkinter as tk
from tkinter import ttk, filedialog

gCONFIG : dict = {
    "connections": list(),
    "tables": list(),
    "transforms": list()
}
gUI_ELEMENTS : dict = dict()

gUI_CONSTANTS : dict = {
    "CONNECTION_TYPE": ["Clasica", "CLoud Wallet"],
    "ALGORITHMS": ["VIGENERE-CIPHER-ENCODE", "VIGENERE-CIPHER-MAIL-ENCODE", "RAND_DIGITS", "UUID", "XOR", "VIGENERE-CIPHER-DECODE", "X_MAIL", "VIGENERE-CIPHER-MAIL-DECODE"]
}

## CORE UTILS
def vigenere_cipher_encode(text, key):
    encoded = []
    key_length = len(key)
    key_as_int = [ord(i) for i in key]
    text_as_int = [ord(i) for i in text]
    for i in range(len(text_as_int)):
        value = (text_as_int[i] + key_as_int[i % key_length]) % 256
        encoded.append(chr(value))
    return ''.join(encoded)

def vigenere_cipher_decode(text, key):
    decoded = []
    key_length = len(key)
    key_as_int = [ord(i) for i in key]
    text_as_int = [ord(i) for i in text]
    for i in range(len(text_as_int)):
        value = (text_as_int[i] - key_as_int[i % key_length]) % 256
        decoded.append(chr(value))
    return ''.join(decoded)

def get_connection_by_name(p_name : str) -> dict:
    for c in gCONFIG["connections"]:
        if c["name"] == p_name:
            return c

def get_connection_by_id(p_id : int) -> dict:
    for c in gCONFIG["connections"]:
        if c["connection_id"] == p_id:
            return c

def remove_connection_by_name(p_name : int) -> bool:
    original_size : int = len(gCONFIG["connections"])
    gCONFIG["connections"] = [c for c in gCONFIG["connections"] if c["name"] != p_name]
    return original_size != len(gCONFIG["connections"])

def get_max_connection_id() -> int:
    if len(gCONFIG["connections"]) == 0:
        return 1
    return max([c["connection_id"] for c in gCONFIG["connections"]]) + 1

def get_max_table_id() -> int:
    if len(gCONFIG["tables"]) == 0:
        return 1
    return max([t["table_id"] for t in gCONFIG["tables"]]) + 1

def get_max_transform_id() -> int:
    if len(gCONFIG["transforms"]) == 0:
        return 1
    return max([t["transform_id"] for t in gCONFIG["transforms"]]) + 1

def get_connection(p_conn : dict):
    if p_conn["connection_type"] == "Clasica":
        return oracledb.connect(user=p_conn["user"], password=p_conn["pasw"], dsn=f'{p_conn["host"]}/{p_conn["service"]}')
    elif p_conn["connection_type"] == "CLoud Wallet":
        return oracledb.connect(
            config_dir=p_conn["wallet_path"],
            user=p_conn["user"],
            password=p_conn["pasw"],
            dsn=p_conn["wallet_service"],
            wallet_location=p_conn["wallet_path"],
            wallet_password=p_conn["wallet_password"]
        )

def test_connection(p_conn : dict) -> None:
    with get_connection(p_conn) as conn:
        with conn.cursor() as cu:
            r = cu.execute(f"SELECT 1 FROM DUAL")
            r.fetchone()

def read_schema_tables(p_conn : dict) -> list[tuple]:
    with get_connection(p_conn) as conn:
        with conn.cursor() as cu:
            r = cu.execute(f"SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE OWNER NOT IN ('SYS', 'XDB', 'SYSTEM', 'MDSYS')")
            return r.fetchall()

def read_fields_by_table(p_table : dict) -> list[tuple]:
    conn_info : dict = get_connection_by_id(p_table["connection_id"])
    with get_connection(conn_info) as conn:
        with conn.cursor() as cu:
            r = cu.execute(f"SELECT COLUMN_ID, COLUMN_NAME FROM ALL_TAB_COLS WHERE OWNER = COALESCE(:1, USER) AND TABLE_NAME = :2 ORDER BY COLUMN_ID ASC", [p_table["schema_name"], p_table["table_name"]])
            return r.fetchall()

def get_tables_by_connection(p_conn : dict) -> list[dict]:
    tables : list[dict] = [t for t in gCONFIG["tables"] if t["connection_id"] == p_conn["connection_id"]]
    return tables

def get_table_by_id(p_id : int) -> dict | None:
    for t in gCONFIG["tables"]:
        if t["table_id"] == p_id:
            return t

def get_table_by_name(p_conn_id : int, p_schema_name : str, p_table_name : str) -> dict | None:
    for t in gCONFIG["tables"]:
        if t["connection_id"] == p_conn_id and t["table_name"].strip().upper() == p_table_name.strip().upper() and t["schema_name"].strip().upper() == p_schema_name.strip().upper():
            return t

def get_table_by_whole_name(p_conn_id : int, p_whole_name : str) -> dict | None:
    for t in gCONFIG["tables"]:
        if t["connection_id"] == p_conn_id and t["schema_name"].strip().upper()+"."+t["table_name"].strip().upper() == p_whole_name.strip().upper():
            return t

def get_transform_by_name(p_name : str) -> dict | None:
    for tf in gCONFIG["transforms"]:
        if tf["transform_name"].strip().upper() == p_name.strip().upper():
            return tf

def safe_int_conversion(p_text : str, p_default : int = None) -> int | None:
    try:
        return int(p_text)
    except:
        return p_default

def apply_xor(p_value : int, p_key_1 : int, p_key_2 : int) -> int:
    return (p_value ^ (p_key_2 + p_key_1))

def apply_ofusca_mail(mail : str, p_key_1 : str, p_key_2 : str):
    parts = mail.split('@')
    part_1 = parts[0]
    new_part = p_key_1[0] * len(part_1)
    if p_key_2 is None:
        correo_ofuscado = new_part + '@' + parts[1]
    else:
        correo_ofuscado = new_part + '@' + p_key_2
    return correo_ofuscado

def apply_cipher_encode_mail(p_mail : str, p_key_1 : str, p_key_2 : str) -> str:
    parts = p_mail.split('@')
    part_1 = parts[0]
    new_part = vigenere_cipher_encode(part_1, p_key_1)
    if p_key_2 and len(p_key_2) > 0:
        correo_ofuscado = new_part + '@' + p_key_2
    else:
        correo_ofuscado = new_part + '@' + parts[1]
    return correo_ofuscado

def apply_cipher_decode_mail(p_mail : str, p_key_1 : str, p_key_2 : str) -> str:
    parts = p_mail.split('@')
    part_1 = parts[0]
    new_part = vigenere_cipher_decode(part_1, p_key_1)
    if p_key_2 and len(p_key_2) > 0:
        correo_ofuscado = new_part + '@' + p_key_2
    else:
        correo_ofuscado = new_part + '@' + parts[1]
    return correo_ofuscado

def apply_rand_digits(p_text : str):
    result : list = list()
    for ch in p_text:
        if ch.isdigit():
            result.append(str(random.randint(0, 9)))
        else:
            result.append(ch)
    return "".join(result)

def apply_alogrithm(p_value, p_algorithm : str, p_1 : str, p_2 : str):
    if (not p_algorithm) or len(p_algorithm) == 0:
        return p_value
    if p_algorithm == "XOR":
        return apply_xor(int(p_value), int(p_1), int(p_2)) if p_value else None
    if p_algorithm == "VIGENERE-CIPHER-ENCODE":
        return vigenere_cipher_encode(p_value, p_1)
    if p_algorithm == "VIGENERE-CIPHER-DECODE":
        return vigenere_cipher_decode(p_value, p_1)
    if p_algorithm == "X_MAIL":
        return apply_ofusca_mail(p_value, p_1, p_2)
    if p_algorithm == "VIGENERE-CIPHER-MAIL-ENCODE":
        return apply_cipher_encode_mail(p_value, p_1, p_2)
    if p_algorithm == "VIGENERE-CIPHER-MAIL-DECODE":
        return apply_cipher_decode_mail(p_value, p_1, p_2)
    if p_algorithm == "RAND_DIGITS":
        return apply_rand_digits(p_value)
    if p_algorithm == "UUID":
        return uuid.uuid4().bytes

def process_row(p_transforms : dict, p_row : tuple) -> tuple:
    result : list = list()
    for t in p_transforms:
        source_position : int | None = safe_int_conversion(t["source_pos"])
        algorithm : str = t["algorithm"]
        source_value = p_row[source_position - 1] if source_position else None
        key_1 = t["key_1"]
        key_2 = t["key_2"]
        result.append(apply_alogrithm(source_value, algorithm, key_1, key_2))
    return tuple(result)

def get_data_block(p_table : dict, p_block_size : int | None = 100):
    conn_info   : dict = get_connection_by_id(p_table["connection_id"])
    schema_name : str = p_table["schema_name"] if p_table["schema_name"] is not None else ""
    table_name  : str = p_table['table_name']
    table_name  : str = f"{schema_name}{'.' if p_table['schema_name'] is not None else ''}{table_name}"
    
    if len(p_table["fields"]) == 0:
        fields : str = "*"
    else:
        fields : list = sorted(p_table["fields"], key = lambda x : x["field_pos"])
        fields : str = ", ".join(["t." + f["field_name"] for f in fields])

    with get_connection(conn_info) as conn:
        with conn.cursor() as cu:
            r = cu.execute(f"SELECT {fields} FROM {table_name} t")
            while True:
                rows = r.fetchmany(size = p_block_size)
                if rows:
                    yield rows
                else:
                    break

## UI UTILS
def get_ui_connection_info() -> dict:
    input_name : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_name/"]
    input_user : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_user/"]
    input_pasw : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_pasw/"]
    input_host : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_host/"]
    input_serv : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_serv/"]
    input_wpath : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_wallet_path/"]
    input_wserv : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_wallet_serv/"]
    input_wpasw : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_wallet_pasw/"]
    input_conn_type : ttk.Combobox = gUI_ELEMENTS["root/notebook/connections/input_conn_type/"]

    connection_info : dict = {
        "connection_id": None,
        "driver": "oracle",
        "name": input_name.get(),
        "user": input_user.get(),
        "pasw": input_pasw.get(),
        "connection_type": input_conn_type.get(),
        "host": input_host.get() if len(input_host.get()) > 0 else None,
        "service": input_serv.get() if len(input_serv.get()) > 0 else None,
        "wallet_path": input_wpath.get() if len(input_wpath.get()) > 0 else None,
        "wallet_service": input_wserv.get() if len(input_wserv.get()) > 0 else None,
        "wallet_password": input_wpasw.get() if len(input_wpasw.get()) > 0 else None
    }
    return connection_info

def get_ui_table_info() -> dict:
    input_connection : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_connection/"]
    input_schema     : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_schema/"]
    input_table      : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_table/"]
    tree            : ttk.Treeview = gUI_ELEMENTS["root/notebook/tables/tree_fields/"]
    
    conn_info : dict = get_connection_by_name(input_connection.get())
    conn_info : int | None = conn_info["connection_id"] if conn_info else None
    fields : list[dict] = [{"field_pos": tree.item(x)['values'][0], "field_name": tree.item(x)['values'][1]} for x in tree.get_children()]

    table_info : dict = {
        "table_id": None,
        "connection_id": conn_info,
        "schema_name": input_schema.get() if len(input_schema.get()) > 0 else None,
        "table_name": input_table.get() if len(input_table.get()) > 0 else None,
        "fields": fields
    }
    return table_info

def get_ui_transform_info() -> dict:
    input_name = gUI_ELEMENTS["root/notebook/transforms/entry_name/"]
    input_conn_source = gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"]
    input_table_source = gUI_ELEMENTS["root/notebook/transforms/box_table_source/"]
    input_conn_target = gUI_ELEMENTS["root/notebook/transforms/box_conn_target/"]
    input_table_target = gUI_ELEMENTS["root/notebook/transforms/box_table_target/"]
    input_block = gUI_ELEMENTS["root/notebook/transforms/entry_block/"]
    check_var_truncate = gUI_ELEMENTS["root/notebook/transforms/var_truncate/"]
    tree = gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"]

    source_id : int | None = None
    target_id : int | None = None

    conn_info : dict | None = get_connection_by_name(input_conn_source.get())
    if conn_info:
        table_info : dict | None = get_table_by_whole_name(conn_info["connection_id"], input_table_source.get())
        if table_info:
            source_id : int = table_info["table_id"]
    
    conn_info : dict | None = get_connection_by_name(input_conn_target.get())
    if conn_info:
        table_info : dict | None = get_table_by_whole_name(conn_info["connection_id"], input_table_target.get())
        if table_info:
            target_id : int = table_info["table_id"]
    
    list_fields : list[list] = [tree.item(x)['values'] for x in tree.get_children()]
    list_fields : list[dict] = [ {"source_pos": x[2], "target_pos": x[0], "algorithm": x[4], "key_1": x[5], "key_2": x[6]} for x in list_fields]

    ui_transform_info : dict = {
        "transform_id": None,
        "transform_name": input_name.get(),
        "source_id": source_id,
        "target_id": target_id,
        "block_size": safe_int_conversion(input_block.get()),
        "truncate": True if check_var_truncate.get() else False,
        "fields": list_fields
    }
    return ui_transform_info

def get_ui_transform_field_info() -> dict:
    ui_transform_info : dict = get_ui_transform_info()

    box_source : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/input_field_source/"]
    field_target : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/input_field_target/"]
    box_alg : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_algorithm/"]
    key1 : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/entry_key_1/"]
    key2 : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/entry_key_2/"]

    table_source : dict | None = get_table_by_id(ui_transform_info["source_id"])
    table_target : dict | None = get_table_by_id(ui_transform_info["target_id"])

    source_pos : int | None = None
    target_pos : int | None = None

    if table_source:
        field : list[dict] = [f for f in table_source["fields"] if f["field_name"].strip().upper() == box_source.get().strip().upper()]
        if len(field) > 0:
            source_pos = field[0]["field_pos"]
    
    if table_target:
        field : list[dict] = [f for f in table_target["fields"] if f["field_name"].strip().upper() == field_target.get().strip().upper()]
        if len(field) > 0:
            target_pos = field[0]["field_pos"]

    ui_field_info : dict = {
        "source_pos": source_pos,
        "target_pos": target_pos,
        "algorithm": box_alg.get(),
        "key_1": key1.get(),
        "key_2": key2.get()
    }
    return ui_field_info

def reset_ui_connection_info() -> None:
    gUI_ELEMENTS["root/notebook/connections/input_name/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_user/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_pasw/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_host/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_serv/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_wallet_path/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_wallet_serv/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/input_wallet_pasw/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/connections/label_status/"].config(text="Estado:")

def reload_tree_connections() -> None:
    tree_1 = gUI_ELEMENTS["root/notebook/connections/tree_connections/"]
    tree_1.delete(*tree_1.get_children())
    for c in gCONFIG["connections"]:
        tree_1.insert("", 'end', values=(c["name"], ))
    reload_tree_tables()

def reload_tree_tables() -> None:
    tree_1 = gUI_ELEMENTS["root/notebook/tables/tree_tables/"]
    tree_1.delete(*tree_1.get_children())
    for c in gCONFIG["connections"]:
        item = tree_1.insert("", tk.END, text=c["name"])
        list_tables : list[dict] = [t for t in gCONFIG["tables"] if t["connection_id"] == c["connection_id"]]
        for t in list_tables:
            tree_1.insert(item, tk.END, text = t["table_name"], iid = t["table_id"])
    reload_tab2_combobox_connections()
    reload_tab3_combobox_connections()

def reload_tab2_combobox_connections() -> None:
    box_conn : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_connection/"]
    box_conn['values'] = [c["name"] for c in gCONFIG["connections"]]

def reload_tab3_combobox_connections() -> None:
    list_conn_names = [c["name"] for c in gCONFIG["connections"]]
    gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"]["values"] = list_conn_names
    gUI_ELEMENTS["root/notebook/transforms/box_conn_target/"]["values"] = list_conn_names
    reload_tab3_combobox_tables()

def reload_tab3_combobox_tables() -> None:
    input_conn_source  : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"]
    input_conn_target  : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_conn_target/"]
    input_table_source : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_table_source/"]
    input_table_target : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_table_target/"]

    if input_conn_source.get() and len(input_conn_source.get()) > 0:
        conn_source_info : dict = get_connection_by_name(input_conn_source.get())
        list_tables : list[dict] = get_tables_by_connection(conn_source_info)
        input_table_source["values"] = [x["schema_name"]+"."+x["table_name"] for x in list_tables]
    
    if input_conn_target.get() and len(input_conn_target.get()) > 0:
        conn_target_info : dict = get_connection_by_name(input_conn_target.get())
        list_tables : list[dict] = get_tables_by_connection(conn_target_info)
        input_table_target["values"] = [x["schema_name"]+"."+x["table_name"] for x in list_tables]

def reload_tab2_combobox_schema(p_query_data : bool = False) -> None:
    box_conn   : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_connection/"]
    box_schema : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_schema/"]
    
    if (not box_conn.get()) or len(box_conn.get()) == 0 or box_conn.get() == "" or box_conn.get() == 0:
        box_schema["values"] = list()
    elif p_query_data:
        conn_info : dict = get_connection_by_name(box_conn.get())
        tables : list[tuple] = read_schema_tables(conn_info)
        box_schema["values"] = list(set([x[0] for x in tables]))
    else:
        conn_info : dict = get_connection_by_name(box_conn.get())
        list_tables : list[dict] = get_tables_by_connection(conn_info)
        box_schema["values"] = list(set([t["schema_name"] for t in list_tables if t["schema_name"] is not None]))

def reload_tab2_combobox_table(p_query_data : bool = False) -> None:
    box_conn   : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_connection/"]
    box_table  : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_table/"]
    
    if (not box_conn.get()) or len(box_conn.get()) == 0 or box_conn.get() == "" or box_conn.get() == 0:
        box_table["values"] = list()
    elif p_query_data:
        conn_info : dict = get_connection_by_name(box_conn.get())
        tables : list[tuple] = read_schema_tables(conn_info)
        box_table["values"] = list(set([x[1] for x in tables]))
    else:
        conn_info : dict = get_connection_by_name(box_conn.get())
        list_tables : list[dict] = get_tables_by_connection(conn_info)
        box_table["values"] = list(set([t["table_name"] for t in list_tables]))

def reload_tab2_treeview_fields(p_query_data : bool = False) -> None:
    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/tables/tree_fields/"]
    tree.delete(*tree.get_children())

    ui_table_info : dict = get_ui_table_info()

    if p_query_data:
        fields : list[tuple] = read_fields_by_table(ui_table_info)
        for f in fields:
            tree.insert("", 'end', values=(f[0], f[1]))
    else:
        table_info : dict = get_table_by_name(ui_table_info["connection_id"], ui_table_info["schema_name"], ui_table_info["table_name"])
        for f in table_info["fields"]:
            tree.insert("", 'end', values=(f["field_pos"], f["field_name"]))

def reload_tab3_treeview_transforms() -> None:
    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_transforms/"]
    tree.delete(*tree.get_children())

    transforms_info : list[dict] = [t for t in gCONFIG["transforms"]]
    for tf in transforms_info:
        tree.insert("", 'end', values=(tf["transform_name"], ))

def reset_tab2() -> None:
    input_connection : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_connection/"]
    input_schema     : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_schema/"]
    input_table      : ttk.Combobox = gUI_ELEMENTS["root/notebook/tables/box_table/"]
    tree             : ttk.Treeview = gUI_ELEMENTS["root/notebook/tables/tree_fields/"]

    input_connection.set("")
    input_schema.set("")
    input_table.set("")
    tree.delete(*tree.get_children())

def reset_tab3() -> None:
    gUI_ELEMENTS["root/notebook/transforms/entry_name/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"].set("")
    gUI_ELEMENTS["root/notebook/transforms/box_table_source/"].set("")
    gUI_ELEMENTS["root/notebook/transforms/box_conn_target/"].set("")
    gUI_ELEMENTS["root/notebook/transforms/box_table_target/"].set("")
    gUI_ELEMENTS["root/notebook/transforms/box_algorithm/"].set("")
    gUI_ELEMENTS["root/notebook/transforms/entry_key_1/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/transforms/entry_key_2/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/transforms/entry_block/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/transforms/var_truncate/"].set(False)
    gUI_ELEMENTS["root/notebook/transforms/input_field_target/"].delete(0, tk.END)
    gUI_ELEMENTS["root/notebook/transforms/input_field_source/"].set("")

    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"]
    tree.delete(*tree.get_children())

## UI CALLBACKS
def ui_load_json_configuration() -> None:
    global gCONFIG
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path) as f:
            gCONFIG = json.loads(f.read())
        
        reload_tree_connections()
        reload_tab3_treeview_transforms()

def ui_save_json_configuration() -> None:
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        print("Guardar archivo en:", file_path)

def ui_load_excel_configuration() -> None:
    import pandas as pd

    file_path = filedialog.askopenfilename(filetypes=[("EXCEL files", "*.xsl *.xlsx")])
    if file_path:
        df = pd.read_excel(file_path, sheet_name="connections")
        df = df.where(pd.notna(df), None)
        gCONFIG["connections"] = df.to_dict('records')
        
        df = pd.read_excel(file_path, sheet_name="tables")
        df = df.where(pd.notna(df), None)
        gCONFIG["tables"] = df.to_dict('records')

        df = pd.read_excel(file_path, sheet_name="fields")
        df = df.where(pd.notna(df), None)
        fields : list[dict] = df.to_dict('records')
        for t in gCONFIG["tables"]:
            f : list[dict] = [x for x in fields if x["table_id"] == t["table_id"]]
            t["fields"] = f
        
        df = pd.read_excel(file_path, sheet_name="transforms")
        df = df.where(pd.notna(df), None)
        gCONFIG["transforms"] = df.to_dict('records')

        df = pd.read_excel(file_path, sheet_name="tranform_field")
        df = df.where(pd.notna(df), None)
        transf_field : list[dict] = df.to_dict('records')
        for t in gCONFIG["transforms"]:
            f : list[dict] = [{
                    "source_pos": safe_int_conversion(x["source_pos"]),
                    "target_pos": safe_int_conversion(x["target_pos"]),
                    "algorithm": x["algorithm"],
                    "key_1": x["key_1"],
                    "key_2": x["key_2"]
                } for x in transf_field if x["transform_id"] == t["transform_id"]]
            t["fields"] = f

        reload_tree_connections()
        reload_tab3_treeview_transforms()

def ui_save_excel_configuration() -> None:
    import pandas as pd

    excel_path = filedialog.asksaveasfilename(defaultextension=".xslx", filetypes=[("EXCEL files", "*.xlsx *.xls")])
    if excel_path:
        df_connections = pd.DataFrame(gCONFIG["connections"])
        df_connections.to_excel(excel_path, sheet_name='connections', index=False)
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            info_tables : list[dict] = [{
                    "table_id": x["table_id"],
                    "connection_id": x["connection_id"],
                    "schema_name": x["schema_name"],
                    "table_name": x["table_name"]
                } for x in gCONFIG["tables"]]

            info_table_field : list[dict] = list()
            for t in gCONFIG["tables"]:
                info_table_field.extend([{"table_id": t["table_id"], **f} for f in t["fields"]])

            info_transformations : list[dict] = [{
                    "transform_id": t["transform_id"],
                    "transform_name": t["transform_name"],
                    "source_id": t["source_id"],
                    "target_id": t["target_id"],
                    "block_size": t["block_size"],
                    "truncate": t["truncate"
                ]} for t in gCONFIG["transforms"]]
            
            info_transf_fields : list[dict] = list()
            for tf in gCONFIG["transforms"]:
                info_transf_fields.extend([{"transform_id": tf["transform_id"], **f} for f in tf["fields"]])

            df_tables = pd.DataFrame(info_tables)
            df_tab_field = pd.DataFrame(info_table_field)
            df_transforms = pd.DataFrame(info_transformations)
            df_transf_field = pd.DataFrame(info_transf_fields)

            df_tables.to_excel(writer, sheet_name='tables', index=False)
            df_tab_field.to_excel(writer, sheet_name="fields", index=False)
            df_transforms.to_excel(writer, sheet_name="transforms", index=False)
            df_transf_field.to_excel(writer, sheet_name="tranform_field", index=False)

def ui_connection_type_change(event = None) -> None:
    frame_classic : ttk.Frame = gUI_ELEMENTS["root/notebook/connections/frame_classic/"]
    frame_cloud   : ttk.Frame = gUI_ELEMENTS["root/notebook/connections/frame_cloud/"]
    input_conn_type : ttk.Combobox = gUI_ELEMENTS["root/notebook/connections/input_conn_type/"]
    conn_type = input_conn_type.get()
    
    if conn_type == "Clasica":
        frame_classic.grid()
        frame_cloud.grid_remove()
    else:
        frame_classic.grid_remove()
        frame_cloud.grid()

def ui_tab1_click_add_connection(event = None) -> None:
    ui_conn_info : dict = get_ui_connection_info()
    conn_info : dict = get_connection_by_name(ui_conn_info["name"])
    if conn_info:
        conn_info["user"] = ui_conn_info["user"]
        conn_info["pasw"] = ui_conn_info["pasw"]
        conn_info["connection_type"] = ui_conn_info["connection_type"]
        conn_info["host"] = ui_conn_info["host"]
        conn_info["service"] = ui_conn_info["service"]
        conn_info["wallet_path"] = ui_conn_info["wallet_path"]
        conn_info["wallet_service"] = ui_conn_info["wallet_service"]
        conn_info["wallet_password"] = ui_conn_info["wallet_password"]
    else:
        ui_conn_info["connection_id"] = get_max_connection_id()
        gCONFIG["connections"].append(ui_conn_info)
    
    reload_tree_connections()

def ui_tab1_click_remove_connection(event = None) -> None:
    ui_conn_info : dict = get_ui_connection_info()
    flag : bool = remove_connection_by_name(ui_conn_info["name"])
    reload_tree_connections()
    reset_ui_connection_info()

def ui_tab1_click_test_connection(event = None) -> None:
    ui_conn_info : dict = get_ui_connection_info()
    try:
        test_connection(ui_conn_info)
        gUI_ELEMENTS["root/notebook/connections/label_status/"].config(text="Estado: OK")
    except Exception as ex:
        gUI_ELEMENTS["root/notebook/connections/label_status/"].config(text="Estado: " + str(ex))

def ui_tab1_click_tree(event = None) -> None:
    input_name : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_name/"]
    input_user : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_user/"]
    input_pasw : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_pasw/"]
    input_host : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_host/"]
    input_serv : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_serv/"]
    input_wpath : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_wallet_path/"]
    input_wserv : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_wallet_serv/"]
    input_wpasw : ttk.Entry = gUI_ELEMENTS["root/notebook/connections/input_wallet_pasw/"]
    input_conn_type : ttk.Combobox = gUI_ELEMENTS["root/notebook/connections/input_conn_type/"]
    
    tree_1 : ttk.Treeview = gUI_ELEMENTS["root/notebook/connections/tree_connections/"]

    if tree_1.focus():
        item_selected = tree_1.item(tree_1.focus(), 'values')[0]
        ci : dict = get_connection_by_name(item_selected)

        reset_ui_connection_info()
        input_name.insert(0, ci["name"])
        input_user.insert(0, ci["user"])
        input_pasw.insert(0, ci["pasw"])
        input_host.insert(0, ci["host"] if ci["host"] is not None else "")
        input_serv.insert(0, ci["service"] if ci["service"] is not None else "")
        input_wpath.insert(0, ci["wallet_path"] if ci["wallet_path"] is not None else "")
        input_wserv.insert(0, ci["wallet_service"] if ci["wallet_service"] is not None else "")
        input_wpasw.insert(0, ci["wallet_password"] if ci["wallet_password"] is not None else "")
        input_conn_type.set(ci["connection_type"])
        ui_connection_type_change()

def ui_tab2_click_tree(event = None) -> None:
    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/tables/tree_tables/"]
    table_index : int = tree.focus()
    if table_index:
        try:
            table_index : int = int(table_index)
        except:
            return
        
        table_info : dict = get_table_by_id(table_index)
        conn_info  : dict = get_connection_by_id(table_info["connection_id"])

        gUI_ELEMENTS["root/notebook/tables/box_connection/"].set(conn_info["name"])
        gUI_ELEMENTS["root/notebook/tables/box_schema/"].set(table_info["schema_name"] if table_info["schema_name"] is not None else "")
        gUI_ELEMENTS["root/notebook/tables/box_table/"].set(table_info["table_name"])
        
        reload_tab2_combobox_schema(False)
        reload_tab2_combobox_table(False)
        reload_tab2_treeview_fields(False)

def ui_tab2_change_connection(event = None) -> None:
    reload_tab2_combobox_schema(False)
    reload_tab2_combobox_table(False)

def ui_tab2_click_load_schema(event = None) -> None:
    reload_tab2_combobox_schema(True)
    reload_tab2_combobox_table(True)

def ui_tab2_click_load_fields(event = None) -> None:
    reload_tab2_treeview_fields(True)

def ui_tab2_click_save_table(event = None) -> None:
    ui_table_info : dict = get_ui_table_info()
    table_info : dict = get_table_by_name(ui_table_info["connection_id"], ui_table_info["schema_name"], ui_table_info["table_name"])
    if table_info:
        table_info["connection_id"] = ui_table_info["connection_id"]
        table_info["schema_name"] = ui_table_info["schema_name"]
        table_info["table_name"] = ui_table_info["table_name"]
        table_info["fields"] = ui_table_info["fields"]
    else:
        ui_table_info["table_id"] = get_max_table_id()
        gCONFIG["tables"].append(ui_table_info)
    reload_tree_tables()

def ui_tab2_click_del_table(event = None) -> None:
    ui_table_info : dict = get_ui_table_info()
    table_info : dict = get_table_by_name(ui_table_info["connection_id"], ui_table_info["schema_name"], ui_table_info["table_name"])
    if table_info:
        gCONFIG["tables"] = [t for t in gCONFIG["tables"] if t["table_id"] != table_info["table_id"]]
        reset_tab2()
        reload_tree_tables()

def ui_tab3_click_tree(event = None) -> None:
    tree_tf : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_transforms/"]
    tree_f  : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"]
    
    input_name           : ttk.Entry    = gUI_ELEMENTS["root/notebook/transforms/entry_name/"]
    input_conn_source    : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"]
    input_table_source   : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_table_source/"]
    input_conn_target    : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_conn_target/"]
    input_table_target   : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_table_target/"]
    input_block          : ttk.Entry    = gUI_ELEMENTS["root/notebook/transforms/entry_block/"]
    check_var_truncate   : tk.IntVar    = gUI_ELEMENTS["root/notebook/transforms/var_truncate/"]

    if tree_tf.focus():
        transform_name : tuple = tree_tf.item(tree_tf.focus(), 'values')[0]
        transform_info : dict = get_transform_by_name(transform_name)
        table_source : dict = get_table_by_id(transform_info["source_id"])
        table_target : dict = get_table_by_id(transform_info["target_id"])
        conn_source : dict = get_connection_by_id(table_source["connection_id"])
        conn_target : dict = get_connection_by_id(table_target["connection_id"])
        reset_tab3()
        
        input_name.insert(0, transform_info["transform_name"])
        input_conn_source.set(conn_source["name"])
        input_table_source.set(table_source["schema_name"]+"."+table_source["table_name"])
        input_conn_target.set(conn_target["name"])
        input_table_target.set(table_target["schema_name"]+"."+table_target["table_name"])
        input_block.insert(0, "100")
        check_var_truncate.set(transform_info["truncate"])

        for f in transform_info["fields"]:
            field_target_name : str = [x["field_name"] for x in table_target["fields"] if x["field_pos"] == f["target_pos"]][0]
            field_source_name : str = [x["field_name"] for x in table_source["fields"] if x["field_pos"] == f["source_pos"]][0] if f["source_pos"] is not None else ""
            tree_values : tuple = (
                f["target_pos"],
                field_target_name,
                f["source_pos"] if f["source_pos"] is not None else "",
                field_source_name,
                f["algorithm"] if f["algorithm"] is not None else "",
                f["key_1"] if f["key_1"] is not None else "",
                f["key_2"] if f["key_2"] is not None else ""
            )
            tree_f.insert("", "end", values = tree_values)
        
        reload_tab3_combobox_tables()
        ui_tab3_click_box_table_source()

def ui_tab3_click_tree_field(event = None) -> None:
    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"]

    input_field_target : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/input_field_target/"]
    input_field_source : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/input_field_source/"]
    input_conn_algorithn : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_algorithm/"]
    input_key_1 : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/entry_key_1/"]
    input_key_2 : ttk.Entry = gUI_ELEMENTS["root/notebook/transforms/entry_key_2/"]

    if tree.focus():
        ui_field_info : tuple = tree.item(tree.focus(), 'values')

        input_field_target.delete(0, tk.END)
        input_key_1.delete(0, tk.END)
        input_key_2.delete(0, tk.END)

        input_field_target.insert(0, ui_field_info[1])
        input_field_source.set(ui_field_info[3])
        input_conn_algorithn.set(ui_field_info[4])
        input_key_1.insert(0, ui_field_info[5])
        input_key_2.insert(0, ui_field_info[6])

def ui_tab3_click_box_connections(event = None) -> None:
    reload_tab3_combobox_tables()

def ui_tab3_click_box_table_source(event = None) -> None:
    input_conn_source  : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"]
    input_table_source : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/box_table_source/"]
    box_field_source   : ttk.Combobox = gUI_ELEMENTS["root/notebook/transforms/input_field_source/"]

    conn_source : dict = get_connection_by_name(input_conn_source.get())
    list_fields : list[str] = list()
    if conn_source:
        table_source : dict = get_table_by_whole_name(conn_source["connection_id"], input_table_source.get())
        if table_source:
            list_fields : list[str] = [x["field_name"] for x in table_source["fields"]]
    box_field_source["values"] = list_fields

def ui_tab3_click_reload_fields(event = None) -> None:
    ui_transform_info : dict = get_ui_transform_info()
    target_info : dict = get_table_by_id(ui_transform_info["target_id"])
    source_info : dict = get_table_by_id(ui_transform_info["source_id"])
    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"]
    tree.delete(*tree.get_children())

    if target_info:
        fields : list[dict] = target_info["fields"]
        for f in fields:
            auto_source : tuple = ("", "")
            if source_info:
                auto_source : list[dict] = [x for x in source_info["fields"] if x["field_name"] == f["field_name"]]
                auto_source : tuple = (auto_source[0]["field_pos"], auto_source[0]["field_name"]) if len(auto_source) > 0 else ("", "")
            tree_values : tuple = (f["field_pos"], f["field_name"], auto_source[0], auto_source[1], "", "", "")
            tree.insert("", "end", values = tree_values)

def ui_tab3_click_update_field(event = None) -> None:
    tree : ttk.Treeview = gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"]
    ui_transform_info : dict = get_ui_transform_info()
    ui_field_info : dict = get_ui_transform_field_info()

    if ui_field_info["target_pos"]:
        for child_id in tree.get_children():
            item = tree.item(child_id)
            if item["values"][0] == ui_field_info["target_pos"]:
                source_table : dict | None = get_table_by_id(ui_transform_info["source_id"])
                source_name : str = ""
                if source_table:
                    source_name : list[dict] = [x for x in source_table["fields"] if x["field_pos"] == ui_field_info["source_pos"]]
                    source_name : str = source_name[0]["field_name"] if len(source_name) > 0 else ""
                new_values = (
                    item["values"][0],
                    item["values"][1],
                    ui_field_info["source_pos"] if ui_field_info["source_pos"] is not None else "",
                    source_name,
                    ui_field_info["algorithm"],
                    ui_field_info["key_1"],
                    ui_field_info["key_2"]
                )
                tree.item(child_id, values=new_values)

def ui_tab3_click_save_transform(event = None) -> None:
    ui_transf_info : dict = get_ui_transform_info()
    transf_info : dict | None = get_transform_by_name(ui_transf_info["transform_name"])
    if transf_info:
        transf_info["source_id"]  = ui_transf_info["source_id"]
        transf_info["target_id"]  = ui_transf_info["target_id"]
        transf_info["truncate"]   = ui_transf_info["truncate"]
        transf_info["fields"]     = ui_transf_info["fields"]
        transf_info["block_size"] = ui_transf_info["block_size"]
    else:
        ui_transf_info["transform_id"] = get_max_transform_id()
        gCONFIG["transforms"].append(ui_transf_info)
    
    reload_tab3_treeview_transforms()

def ui_tab3_execute_transformation():
    ui_transf_info : dict = get_ui_transform_info()
    info_transformation : dict | None = get_transform_by_name(ui_transf_info["transform_name"])
    
    info_table_target : dict = get_table_by_id(info_transformation["target_id"])
    info_table_source : dict = get_table_by_id(info_transformation["source_id"])
    
    info_conn_source : dict = get_connection_by_id(info_table_source["connection_id"])
    info_conn_target : dict = get_connection_by_id(info_table_target["connection_id"])

    target_fields : list[int] = [int(tf["target_pos"]) for tf in info_transformation["fields"]]
    target_fields : list[str] = [info_table_target["fields"][x - 1]["field_name"] for x in target_fields]

    insert_fields : str = ", ".join(target_fields)
    bind_fields : str = ", ".join([":" + str(i + 1) for i, x in enumerate(target_fields)])

    with get_connection(info_conn_target) as conn_target:
        with conn_target.cursor() as cu:
            if info_transformation["truncate"]:
                cu.execute(f"TRUNCATE TABLE {info_table_target['schema_name']}.{info_table_target['table_name']} DROP STORAGE")
            for x in get_data_block(info_table_source, info_transformation["block_size"]):
                rt = [process_row(ui_transf_info["fields"], row) for row in x]
                sql : str = f"INSERT INTO {info_table_target['schema_name']}.{info_table_target['table_name']} ({insert_fields}) VALUES ({bind_fields})"
                print("sql:", sql)
                cu.executemany(sql, rt)
                conn_target.commit()

### CONFIGURE UI ELEMENTS
def configure_tab_home() -> None:
    notebook : ttk.Notebook = gUI_ELEMENTS["root/notebook/"]
    frame : ttk.Frame = ttk.Frame(notebook)
    notebook.add(frame, text="Inicio")
    paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    gUI_ELEMENTS["root/notebook/home/"] = paned_window

    load_button = ttk.Button(paned_window, text="Cargar configuración JSON", command=ui_load_json_configuration)
    load_button.grid(row=0, column=0, padx=1, columnspan=1, sticky=tk.W)

    save_button = ttk.Button(paned_window, text="Guardar configuración JSON", command=ui_save_json_configuration)
    save_button.grid(row=0, column=1, padx=1, columnspan=1, sticky=tk.W)

    load_button = ttk.Button(paned_window, text="Cargar configuración EXCEL", command=ui_load_excel_configuration)
    load_button.grid(row=1, column=0, padx=1, columnspan=1, sticky=tk.W)

    save_button = ttk.Button(paned_window, text="Guardar configuración EXCEL", command=ui_save_excel_configuration)
    save_button.grid(row=1, column=1, padx=1, columnspan=1, sticky=tk.W)

def configure_tab_connections() -> None:
    notebook : ttk.Notebook = gUI_ELEMENTS["root/notebook/"]
    frame : ttk.Frame = ttk.Frame(notebook)
    notebook.add(frame, text="Conexiones")
    paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    tree_connections = ttk.Treeview(paned_window, columns=("name"), show='headings')
    tree_connections.heading('name', text='Conexión')
    tree_connections.column('name', width=100)
    tree_connections.bind("<<TreeviewSelect>>", ui_tab1_click_tree)
    paned_window.add(tree_connections, weight=1)

    r_frame : ttk.Frame = ttk.Frame(paned_window)
    paned_window.add(r_frame, weight=2)

    ttk.Label(r_frame, text="Alias de la conexión:").grid(row=0, column=0, pady=1, sticky=tk.EW)
    input_name = ttk.Entry(r_frame)
    input_name.grid(row=0, column=1, pady=1, sticky=tk.EW)

    ttk.Label(r_frame, text="Usuario:").grid(row=1, column=0, pady=1, sticky=tk.EW)
    input_user = ttk.Entry(r_frame)
    input_user.grid(row=1, column=1, pady=1, sticky=tk.EW)
    
    ttk.Label(r_frame, text="Contraseña:").grid(row=2, column=0, pady=1, sticky=tk.EW)
    input_pasw = ttk.Entry(r_frame, show="*")
    input_pasw.grid(row=2, column=1, pady=1, sticky=tk.EW)

    ttk.Label(r_frame, text="Tipo de conexión:").grid(row=3, column=0, pady=1, sticky=tk.EW)
    input_conn_type = ttk.Combobox(r_frame, values=gUI_CONSTANTS["CONNECTION_TYPE"], state="readonly")
    input_conn_type.grid(row=3, column=1, pady=1, sticky=tk.EW)
    input_conn_type.set(gUI_CONSTANTS["CONNECTION_TYPE"][0])
    input_conn_type.bind("<<ComboboxSelected>>", ui_connection_type_change)

    ## Inputs de conexión clasica.
    frame_classic = ttk.Frame(r_frame)
    ttk.Label(frame_classic, text="Host:").grid(row=4, column=0, pady=1, sticky=tk.EW)
    input_host = ttk.Entry(frame_classic)
    input_host.grid(row=4, column=1, columnspan=1, pady=1, sticky=tk.EW)
    ttk.Label(frame_classic, text="Service name:").grid(row=5, column=0, pady=1, sticky=tk.EW)
    input_serv = ttk.Entry(frame_classic)
    input_serv.grid(row=5, column=1, columnspan=1, pady=1, sticky=tk.EW)
    frame_classic.grid(columnspan=2, rowspan=3, pady=10, sticky=tk.EW)
    #frame_classic.grid_remove()

    ## Inputs de conexión por wallet.
    frame_cloud = ttk.Frame(r_frame)

    ttk.Label(frame_cloud, text="Walleth path:").grid(row=4, column=0, pady=1, sticky=tk.EW)
    input_wpath = ttk.Entry(frame_cloud)
    input_wpath.grid(row=4, column=1, columnspan=1, pady=1, sticky=tk.EW)
    ttk.Label(frame_cloud, text="Service name:").grid(row=5, column=0, pady=1, sticky=tk.EW)
    input_wserv = ttk.Entry(frame_cloud)
    input_wserv.grid(row=5, column=1, columnspan=1, pady=1, sticky=tk.EW)
    ttk.Label(frame_cloud, text="Wallet password:").grid(row=6, column=0, pady=1, sticky=tk.EW)
    input_wpasw = ttk.Entry(frame_cloud, show="*")
    input_wpasw.grid(row=6, column=1, columnspan=1, pady=1, sticky=tk.EW)
    frame_cloud.grid(columnspan=2, rowspan=3, pady=10, sticky=tk.W)
    #frame_cloud.grid_remove()

    frame_buttons : ttk.Frame = ttk.Frame(r_frame)
    label_status = ttk.Label(frame_buttons, text="Estado: ")
    label_status.grid(row=0, column=0, padx=1, pady=1, columnspan=3, sticky=tk.EW)
    ttk.Button(frame_buttons, text="Agregar", command=ui_tab1_click_add_connection).grid(row=1, column=0, padx=1, pady=1)
    ttk.Button(frame_buttons, text="Borrar", command=ui_tab1_click_remove_connection).grid(row=1, column=1, padx=1, pady=1)
    ttk.Button(frame_buttons, text="Probar", command=ui_tab1_click_test_connection).grid(row=1, column=2, padx=1, pady=1)
    frame_buttons.grid(columnspan=3, pady=1, sticky=tk.W)
    
    gUI_ELEMENTS["root/notebook/connections/"] = paned_window
    gUI_ELEMENTS["root/notebook/connections/tree_connections/"] = tree_connections
    gUI_ELEMENTS["root/notebook/connections/input_name/"] = input_name
    gUI_ELEMENTS["root/notebook/connections/input_user/"] = input_user
    gUI_ELEMENTS["root/notebook/connections/input_pasw/"] = input_pasw
    gUI_ELEMENTS["root/notebook/connections/input_host/"] = input_host
    gUI_ELEMENTS["root/notebook/connections/input_serv/"] = input_serv
    gUI_ELEMENTS["root/notebook/connections/input_wallet_path/"] = input_wpath
    gUI_ELEMENTS["root/notebook/connections/input_wallet_serv/"] = input_wserv
    gUI_ELEMENTS["root/notebook/connections/input_wallet_pasw/"] = input_wpasw
    gUI_ELEMENTS["root/notebook/connections/input_conn_type/"] = input_conn_type
    gUI_ELEMENTS["root/notebook/connections/frame_classic/"] = frame_classic
    gUI_ELEMENTS["root/notebook/connections/frame_cloud/"] = frame_cloud
    gUI_ELEMENTS["root/notebook/connections/label_status/"] = label_status

def configure_tab_tables() -> None:
    notebook : ttk.Notebook = gUI_ELEMENTS["root/notebook/"]
    frame : ttk.Frame = ttk.Frame(notebook)
    notebook.add(frame, text="Tables")
    paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    
    tree_tables = ttk.Treeview(paned_window)
    tree_tables.column('#0', width=120)
    tree_tables.heading('#0', text='Nombre de la Tabla', anchor=tk.W)
    tree_tables.pack()
    tree_tables.bind("<<TreeviewSelect>>", ui_tab2_click_tree)
    paned_window.add(tree_tables, weight=1)

    r_frame : ttk.Frame = ttk.Frame(paned_window)
    paned_window.add(r_frame, weight=2)

    ttk.Label(r_frame, text="Conexión:").grid(row=0, column=0, pady=1, sticky=tk.W)
    input_connection : ttk.Combobox = ttk.Combobox(r_frame, values=[], state="readonly")
    input_connection.grid(row=1, column=0, pady=1, sticky=tk.EW)
    input_connection.bind("<<ComboboxSelected>>", ui_tab2_change_connection)
    ttk.Button(r_frame, text="Cargar tablas", command=ui_tab2_click_load_schema).grid(row=1, column=1, padx=1, pady=1, sticky=tk.EW)

    input_schema : ttk.Combobox = ttk.Combobox(r_frame, values=[])
    ttk.Label(r_frame, text="Esquema:").grid(row=2, column=0, pady=1, sticky=tk.W)
    input_schema.grid(row=3, column=0, pady=1, sticky=tk.EW)

    input_table : ttk.Combobox = ttk.Combobox(r_frame, values=[])
    ttk.Label(r_frame, text="Tabla:").grid(row=2, column=1, pady=1, sticky=tk.W)
    input_table.grid(row=3, column=1, pady=1, sticky=tk.EW)

    ttk.Label(r_frame, text="Campos:").grid(row=4, column=0, pady=1, sticky=tk.EW)
    ttk.Button(r_frame, text="Cargar campos", command=ui_tab2_click_load_fields).grid(row=4, column=1, padx=1, pady=1, sticky=tk.EW)
    tree_fields : ttk.Treeview = ttk.Treeview(r_frame, columns=("field_pos", "field_name"))
    tree_fields.heading('field_pos', text="Posición", anchor=tk.W)
    tree_fields.heading('field_name', text="Nombre", anchor=tk.W)
    tree_fields.column('#0', width=0)
    tree_fields.grid(row=5, column=0, pady=1, columnspan=2, sticky=tk.W)

    ttk.Button(r_frame, text="Guardar tabla", command=ui_tab2_click_save_table).grid(row=6, column=0, padx=1, pady=1, sticky=tk.EW)
    ttk.Button(r_frame, text="Borrar tabla", command=ui_tab2_click_del_table).grid(row=6, column=1, padx=1, pady=1, sticky=tk.EW)
    
    gUI_ELEMENTS["root/notebook/tables/"] = paned_window
    gUI_ELEMENTS["root/notebook/tables/tree_tables/"] = tree_tables
    gUI_ELEMENTS["root/notebook/tables/tree_fields/"] = tree_fields
    gUI_ELEMENTS["root/notebook/tables/box_connection/"] = input_connection
    gUI_ELEMENTS["root/notebook/tables/box_schema/"] = input_schema
    gUI_ELEMENTS["root/notebook/tables/box_table/"] = input_table

def configure_tab_transforms() -> None:
    notebook : ttk.Notebook = gUI_ELEMENTS["root/notebook/"]
    frame : ttk.Frame = ttk.Frame(notebook)
    notebook.add(frame, text="Transforms")
    paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    tree_transforms = ttk.Treeview(paned_window, columns=("name"), show='headings')
    tree_transforms.heading('name', text='Transformaciones')
    tree_transforms.column('name', width=100)
    tree_transforms.bind("<<TreeviewSelect>>", ui_tab3_click_tree)
    paned_window.add(tree_transforms, weight=1)

    c_frame : ttk.Frame = ttk.Frame(paned_window)
    paned_window.add(c_frame, weight=1)

    ttk.Label(c_frame, text="Nombre de la transformación:").grid(row=0, column=0, pady=1, sticky=tk.EW)
    input_name = ttk.Entry(c_frame)
    input_name.grid(row=1, column=0, pady=1, columnspan=2, sticky=tk.EW)
    
    ttk.Label(c_frame, text="Conexión destino:").grid(row=2, column=0, pady=1, sticky=tk.EW)
    input_conn_target : ttk.Combobox = ttk.Combobox(c_frame, values=[], state="readonly")
    input_conn_target.grid(row=3, column=0, pady=1, sticky=tk.EW)
    input_conn_target.bind("<<ComboboxSelected>>", ui_tab3_click_box_connections)

    ttk.Label(c_frame, text="Tabla destino:").grid(row=2, column=1, pady=1, sticky=tk.EW)
    input_table_target : ttk.Combobox = ttk.Combobox(c_frame, values=[], state="readonly")
    input_table_target.grid(row=3, column=1, pady=1, sticky=tk.EW)
    #input_table_target.bind("<<ComboboxSelected>>", ui_tab3_change_connection)

    ttk.Label(c_frame, text="Conexión origen:").grid(row=4, column=0, pady=1, sticky=tk.EW)
    input_conn_source : ttk.Combobox = ttk.Combobox(c_frame, values=[], state="readonly")
    input_conn_source.grid(row=5, column=0, pady=1, sticky=tk.EW)
    input_conn_source.bind("<<ComboboxSelected>>", ui_tab3_click_box_connections)

    ttk.Label(c_frame, text="Tabla origen:").grid(row=4, column=1, pady=1, sticky=tk.EW)
    input_table_source : ttk.Combobox = ttk.Combobox(c_frame, values=[], state="readonly")
    input_table_source.grid(row=5, column=1, pady=1, sticky=tk.EW)
    input_table_source.bind("<<ComboboxSelected>>", ui_tab3_click_box_table_source)

    ttk.Label(c_frame, text="Block size:").grid(row=6, column=0, pady=1, sticky=tk.EW)
    input_block = ttk.Entry(c_frame)
    input_block.grid(row=7, column=0, pady=1, sticky=tk.EW)

    check_var_truncate = tk.IntVar(value = True)
    checkbox_truncate = ttk.Checkbutton(c_frame, text="Truncar la tabla", variable=check_var_truncate)
    checkbox_truncate.grid(row=7, column=1, pady=1, sticky=tk.EW)

    ttk.Button(c_frame, text="Guardar transformación", command=ui_tab3_click_save_transform).grid(row=8, column=0, padx=1, pady=1, sticky=tk.EW)
    ttk.Button(c_frame, text="Ejecutar transformación", command=ui_tab3_execute_transformation).grid(row=8, column=1, padx=1, pady=1, sticky=tk.EW)
    
    ## FRAME DE CAMPOS DE PROCESAMIENTO.
    r_frame : ttk.Frame = ttk.Frame(paned_window)
    paned_window.add(r_frame, weight=2)
    
    ttk.Label(r_frame, text="Campo destino").grid(row=6, column=0, pady=1, sticky=tk.EW)
    input_field_target = ttk.Entry(r_frame)
    input_field_target.grid(row=7, column=0, pady=1, sticky=tk.EW)
    
    ttk.Label(r_frame, text="Campo origen").grid(row=6, column=1, pady=1, sticky=tk.EW)
    input_field_source : ttk.Combobox = ttk.Combobox(r_frame, values=[], state="readonly")
    input_field_source.grid(row=7, column=1, pady=1, sticky=tk.EW)
    #input_conn_target.bind("<<ComboboxSelected>>", ui_tab3_change_connection)

    ttk.Label(r_frame, text="Algoritmo:").grid(row=8, column=0, pady=1, sticky=tk.EW)
    input_conn_algorithn : ttk.Combobox = ttk.Combobox(r_frame, values=gUI_CONSTANTS["ALGORITHMS"], state="readonly")
    input_conn_algorithn.grid(row=9, column=0, columnspan=2, pady=1, sticky=tk.EW)
    #input_conn_target.bind("<<ComboboxSelected>>", ui_tab3_change_connection)
    
    ttk.Label(r_frame, text="Key 1:").grid(row=10, column=0, pady=1, sticky=tk.EW)
    input_key_1 = ttk.Entry(r_frame)
    input_key_1.grid(row=11, column=0, pady=1, sticky=tk.EW)
    
    ttk.Label(r_frame, text="Key 2:").grid(row=10, column=1, pady=1, sticky=tk.EW)
    input_key_2 = ttk.Entry(r_frame)
    input_key_2.grid(row=11, column=1, pady=1, sticky=tk.EW)

    ttk.Button(r_frame, text="Actualizar campo", command=ui_tab3_click_update_field).grid(row=12, column=0, padx=1, pady=1, sticky=tk.EW)
    ttk.Button(r_frame, text="Recargar campos", command=ui_tab3_click_reload_fields).grid(row=12, column=1, padx=1, pady=1, sticky=tk.EW)

    tree_tf_fields = ttk.Treeview(r_frame, columns=("pos_target", "field_target", "pos_source", "field_source", "alg", "key1", "key2"), show='headings')
    tree_tf_fields.grid(row=13, column=0, columnspan=2, pady=1, sticky=tk.EW)

    tree_tf_fields.heading("pos_target", text="")
    tree_tf_fields.heading("pos_source", text="")
    tree_tf_fields.heading("field_target", text="Campo destino")
    tree_tf_fields.heading("field_source", text="Campo fuente")
    tree_tf_fields.heading("alg", text="Algoritmo")
    tree_tf_fields.heading("key1", text="Key 1")
    tree_tf_fields.heading("key2", text="Key 2")
    
    tree_tf_fields.column("pos_target", width=10)
    tree_tf_fields.column("pos_source", width=10)
    tree_tf_fields.column("field_target", width=100)
    tree_tf_fields.column("field_source", width=100)
    tree_tf_fields.column("alg", width=150)
    tree_tf_fields.column("key1", width=60)
    tree_tf_fields.column("key2", width=60)
    tree_tf_fields.bind("<<TreeviewSelect>>", ui_tab3_click_tree_field)
    
    gUI_ELEMENTS["root/notebook/transforms/"] = paned_window
    gUI_ELEMENTS["root/notebook/transforms/tree_transforms/"] = tree_transforms
    gUI_ELEMENTS["root/notebook/transforms/tree_tf_fields/"] = tree_tf_fields
    gUI_ELEMENTS["root/notebook/transforms/entry_name/"] = input_name
    gUI_ELEMENTS["root/notebook/transforms/box_conn_source/"] = input_conn_source
    gUI_ELEMENTS["root/notebook/transforms/box_table_source/"] = input_table_source
    gUI_ELEMENTS["root/notebook/transforms/box_conn_target/"] = input_conn_target
    gUI_ELEMENTS["root/notebook/transforms/box_table_target/"] = input_table_target
    gUI_ELEMENTS["root/notebook/transforms/entry_block/"] = input_block
    gUI_ELEMENTS["root/notebook/transforms/var_truncate/"] = check_var_truncate
    gUI_ELEMENTS["root/notebook/transforms/input_field_target/"] = input_field_target
    gUI_ELEMENTS["root/notebook/transforms/input_field_source/"] = input_field_source
    gUI_ELEMENTS["root/notebook/transforms/box_algorithm/"] = input_conn_algorithn
    gUI_ELEMENTS["root/notebook/transforms/entry_key_1/"] = input_key_1
    gUI_ELEMENTS["root/notebook/transforms/entry_key_2/"] = input_key_2

def main() -> None:
    root = tk.Tk()
    root.title("Ofuscador de datos")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    gUI_ELEMENTS["root/"] = root
    gUI_ELEMENTS["root/notebook/"] = notebook

    configure_tab_home()
    configure_tab_connections()
    configure_tab_tables()
    configure_tab_transforms()

    notebook.pack()

    gUI_ELEMENTS["root/notebook/connections/frame_cloud/"].grid_remove()
    root.mainloop()

main()