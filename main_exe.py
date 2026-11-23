import subprocess
import math
import shutil
from mutagen.easyid3 import EasyID3
import boundary_scoring as bs
import time
import pathlib as plib
import json as json
import requests as rq
import tkinter as tk
from tkinter import filedialog, ttk

ffmpeg_path = plib.Path(__file__).parent / 'tools' / 'ffmpeg.exe'
ffprobe_path = plib.Path(__file__).parent / 'tools' / 'ffprobe.exe'
ico_path = plib.Path(__file__).parent / 'assets' / 'kyokuwari.ico'

count = 0
root = tk.Tk()
root.iconbitmap(str(ico_path))
root.title('音楽分割プログラム')
root.geometry('860x660+500+100')
root.minsize(640, 480)
selected_path = tk.StringVar()
shibakari_checker = tk.BooleanVar(value=False)
sort_conf = tk.BooleanVar(value=False)
path = tk.StringVar()
state = None
result_candidates = None


selection = 0

def file_selector():

    file_path = filedialog.askopenfilename(
    filetypes=[("音声ファイル", "*.mp3 *.wav *.m4a")],
    parent = root
    )

    return file_path

def on_click():
     selected_path.set(file_selector())
    
def get_path ():
    if selected_path.get() == '':
        label3.config(text='ファイルを選択してください')
        return False
    else:
        label3.config(text='ファイルが選択されました')
        label4.config(text=f'パスは{selected_path.get()}です')
        return True

def analysis_click():
    global error
    global state
    global selection
    global result_candidates
    global storage_original
    global result_duration


    if not get_path():
        result_candidates = None
        selection = None
        state = None
        listbox.delete(0,tk.END)
        return

    if error == 1:
        result_candidates = None
        label7.config(text='ffmpegとffprobeの両方、またはどちらかが実行できません。解析を中止します')
        selection = None
        state = None
        listbox.delete(0,tk.END)
        return
 
    label2.config(text="解析開始")
    

    result_candidates , result_duration = analyze_audio(selected_path.get())
    if result_candidates is None:
        label2.config(text='解析が中止されました。リストの作成はされません。')
        selection = None
        state = None
        listbox.delete(0,tk.END)
        return
    storage_original = result_candidates.copy()
    label2.config(text=("解析終了"))
    if sort_conf.get():
        result_candidates.sort(key=lambda c: c['boundary_score'])
    selection = None
    state = 0
    listbox.delete(0,tk.END)
    for i,one_list in enumerate(result_candidates):
        if one_list['confidence'] == 2:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:high')
        if one_list['confidence'] == 1: 
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:medium')
        if one_list['confidence'] == 0:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:low')

def write_output():
        if result_candidates == None:
            label7.config(text='先に解析してください')
            return
        candidates = sorted(result_candidates,key=lambda c: c['position'])
        file = folder_selector(0)
        if not candidates:
            label7.config(text='作成できません')
            return
        try:
            with open(file, "w", encoding="utf-8") as f:
                for i,contents in enumerate(candidates,start=1) :
                    if contents['duration'] >= 2:
                        f.write(f"{contents['start']+0.5}\t{contents['end']-0.5}\t曲間候補{i}\n")
                    else : 
                        f.write(f"{contents['position']}\t{contents['position']}\t曲間候補{i}\n")
        except FileNotFoundError as err:
            label7.config(text=f'保存先フォルダが存在しません:{err}')
            return
        except PermissionError as err:
            label7.config(text=f'選択フォルダへの書き込み権限がありません:{err}')
            return
        except IsADirectoryError as err:
            label7.config(text=f'同名のフォルダが存在します:{err}')
            return
        except OSError as err:
            label7.config(text=f'エラーが発生しました:{err}')
            return
        else:
            label7.config(text='ファイルが作成されました')
            return 

            
def list_click(event):
    global selection
    selection=listbox.curselection()

def list_click_pritn():
    if not selection:
        label6.config(text='リストから選択してください')
        return
    label3.config(text='')
    label4.config(text='')
    label6.config(text='')
    label5.config(text=f'現在選択しているのは{result_candidates[selection[0]]['position']}です\n選択したものを消去するなら、消去ボタンを押してください')    

def delete_click():
    global state
    global selection
    if not selection:
        return
    label3.config(text='')
    label4.config(text='')
    listbox.delete(0,tk.END)
    result_candidates.pop(selection[0])
    selection = None
    if sort_conf.get():
        result_candidates.sort(key=lambda c: c['boundary_score'])
    state = 0
    for i,one_list in enumerate(result_candidates):
        if one_list['confidence'] == 2:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:high')
        if one_list['confidence'] == 1:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:medium')
        if one_list['confidence'] == 0:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:low')

def restore_click():
    global result_candidates
    global state
    global selection
    if result_candidates == None:
        label7.config(text='先に解析してください')
        return
    storgae = storage_original.copy()
    result_candidates = storage_original.copy()
    if sort_conf.get():
        result_candidates.sort(key=lambda c: c['boundary_score'])
        storgae.sort(key=lambda c: c['boundary_score'])
    selection = None
    listbox.delete(0,tk.END)
    state = 1
    for i,one_list in enumerate(storgae):
        if one_list['confidence'] == 2:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:high')
        if one_list['confidence'] == 1:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:medium')
        if one_list['confidence'] == 0:
            listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:low')

def list_update():
    global selection
    selection = None
    if state == None:
        label7.config(text='先に解析してください')
        return
    if state == 0:
        if sort_conf.get():
            result_candidates.sort(key=lambda c: c['boundary_score'])
        else:
            result_candidates.sort(key=lambda c: c['position'])
        listbox.delete(0,tk.END)
        for i,one_list in enumerate(result_candidates):
            if one_list['confidence'] == 2:
                listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:high')
            if one_list['confidence'] == 1:
                listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:medium')
            if one_list['confidence'] == 0:
                listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:low')
    elif state == 1:
        storage = storage_original.copy()
        if sort_conf.get() :
            result_candidates.sort(key=lambda c: c['boundary_score'])
            storage.sort(key=lambda c: c['boundary_score'])    
        else:
            result_candidates.sort(key=lambda c: c['position'])
            storage.sort(key=lambda c: c['position'])
        listbox.delete(0,tk.END)
        for i,one_list in enumerate(storage):
            if one_list['confidence'] == 2:
                listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:high')
            if one_list['confidence'] == 1:
                listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:medium')
            if one_list['confidence'] == 0:
                listbox.insert(tk.END,f'候補{i+1}:{int(one_list['position'])}秒:low')

def folder_selector(mode):
    out_dir = filedialog.askdirectory(parent=root)
    file_name_result = file_name_entry(None)
    if not out_dir:
        label7.config(text='プログラムの位置にファイルが作成されます')
    if mode == 0: # Mode for .txt
        return plib.Path(out_dir) / f'{file_name_result}.txt'
    if mode == 1: # Mode for .mp3
        return plib.Path(out_dir) / f'{file_name_result}',file_name_result

def file_name_entry(event):
        file_name_result = entry.get()
        if not file_name_result:
            root_second = tk.Toplevel(root)
            root_second.title('second window')
            root_second.geometry('400x200')

            entry_second = tk.Entry(root_second)
            entry_second.pack()

            def confirm(event):
                nonlocal file_name_result
                file_name_result = entry_second.get()
                if not file_name_result.strip():
                    return
                root_second.destroy()

            entry_second.bind('<Return>',confirm)
            root.wait_window(root_second)
            if not file_name_result.strip():
                label7.config(text='名前が入力されませんでした。「name」というファイル名で作成します')
                file_name_result = 'name'
        return file_name_result

def make_mp3():
    global result_candidates
    global result_duration
    global music_data
    if result_candidates == None:
        label7.config(text='先に解析してください')
        return
    music_data = list()
    file_path = selected_path.get()
    
    file_name , title = folder_selector(1)
    
    put_candidates = sorted(result_candidates,key=lambda c: c['position'])
    
    segments = make_segments(put_candidates,result_duration)

    if not segments:
        label7.config(text='segmentsが空です')
        return
    
    for i in range(len(segments)):
        try:
            result = subprocess.run(
                [
                    str(ffmpeg_path),
                    '-y',
                    '-ss', f'{segments[i]['start']}',
                    '-i', file_path,
                    '-t', f'{segments[i]['length']}',
                    '-c:a', 'libmp3lame',
                    '-q:a', '2',
                    '-metadata', f'title={title}{i+1}',
                    '-metadata', f'track={i+1}',
                    f'{file_name}_{i+1}.mp3',
                ],
                capture_output=True,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except OSError as err:
            label8.config(text=f'{i+1}番目のファイル出力時にエラーが発生しました:{err}')
            return
        except UnicodeDecodeError as err:
            label8.config(text=f'{i+1}番目のファイル出力時にエラーが発生しました:{err}')
            return

        if result.returncode!=0:
            label8.config(text=f'{i+1}番目のファイルの出力に失敗しました')
            return
        else:
            data_duration , data_fingerprint = get_music_info(f'{file_name}_{i+1}.mp3')
            if data_duration != '' and data_fingerprint != '':
                music_data.append({'file_name':f'{file_name}_{i+1}.mp3','duration':data_duration,'fingerprint': data_fingerprint})
                data_judge = music_api(music_data[i]['duration'],music_data[i]['fingerprint'])
                if data_judge !=0:
                    music_data[i]['title'] = data_judge if data_judge != '' else f'仮name{i+1}'
                    try:
                        audio = EasyID3(music_data[i]['file_name'])
                    except Exception as err:
                        label7.config(text=f'{i+1}番目でエラーが発生しました:{err}')
                        continue
                    try:
                        audio['title'] = music_data[i]['title']
                    except Exception as err:
                        label7.config(text=f'{i+1}番目でエラーが発生しました:{err}')
                        continue
                    try:
                        audio.save()
                    except Exception as err:
                        label7.config(text=f'{i+1}番目でエラーが発生しました:{err}')
                        continue
                    label7.config(text=f'{music_data[i]['title']}')  
            else:
                return
        if i == len(segments)-1:
            label4.config(text='終了しました')

def get_music_info(file_path):
    tool_path = plib.Path(__file__).parent / 'tools' / 'fpcalc.exe'
    try:   
        result = subprocess.run(
            [
            str(tool_path) ,
            '-json', 
            file_path,
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except OSError as err:
        label3.config(text=f'toolの呼び出しが正常に行われませんでした:{err}')
        return '' , ''
    except UnicodeDecodeError as err:
        label3.config(text=f'toolの呼び出しが正常に行われませんでした:{err}')
        return '' , ''
    if result.returncode !=0:
        label3.config(text='toolの呼び出しが正常に行われませんでした。結果を保存する前に終了します')
        return '' , ''
    try:
        data = json.loads(result.stdout)
    except ValueError as err:
        label3.config(text=f'エラーが発生しました:{err}')
        return '' , ''
    else:
        if type(data) != dict:
            label3.config(text='データに辞書が入りませんでした')
            return '' , '' 
    try:
        test = data['duration']
    except KeyError as err:
        label3.config(text=f'エラーが発生しました:{err}')
        return '' , ''
    else:
        if (data['duration'] is None) or type(data['duration']) == str or type(data['duration']) == list or type(data['duration']) == dict or type(data['duration']) == bool or data['duration'] <= 0:
            label3.config(text='データが異常値を取りました')
            return '' , ''
        if math.isnan(data['duration']) or math.isinf(data['duration']):
            label3.config(text='データが異常値を取りました')
            return '' , ''
    try:
        test = data['fingerprint']
    except KeyError as err:
        label3.config(text=f'エラーが発生しました:{err}')
        return '' , ''
    else:
        if (data['fingerprint'] is None) or type(data['fingerprint']) != str or data['fingerprint'] == '':
            label3.config(text='データが異常値を取りました')
            return '' , ''

    return data['duration'],data['fingerprint']

def music_api(duration,fingerprint):
    url = 'https://api.acoustid.org/v2/lookup'
    datas={
        'client':'5Xr8BrIoRu',
        'duration': int(duration),
        'fingerprint': fingerprint,
        'meta':'recordings',
    }
    wati_time_api()
    try:
        res = rq.post(url,data=datas,timeout=10)
        res.raise_for_status()
        data = res.json()
    except rq.exceptions.RequestException as err:
        label7.config(text='エラーが発生しました')
        return 0
    else:
        if type(data) != dict:
            label7.config(text='エラーが発生しました')
            return 0
    if data.get('status') !='ok':
        label7.config(text='エラーが発生しました')
        return 0
    elif type(data.get('results')) != list:
        label7.config(text='エラーが発生しました')
        return 0
    elif not data.get('results') :
        return ''
    
    return_data = caunt_and_select(data['results'])
    
    return return_data

def caunt_and_select(candidate):
    try:
        candidate_sorted = sorted(candidate,key=lambda c :c['score'],reverse=True)
    except Exception as err:
        label7.config(text=f'エラーが発生しました:{err}')
        return 0

    for i,results in enumerate(candidate_sorted):
        if type(results) == dict and results != {}:
            if results.get('recordings') and type(results.get('recordings')) == list:
                if isinstance(results.get('score'),(int,float)) and type(results.get('score')) != bool and (0<= results.get('score') <=1):
                    if len(results['recordings']) == 1:
                        try:
                            test = results['recordings'][0]['title']
                        except Exception as err:
                            label7.config(text=f'{i+1}番目の候補でエラーが発生しました:{err}')
                            continue
                        else: 
                            if (results['recordings'][0]['title'] is not None) and type(results['recordings'][0]['title']) == str and results['recordings'][0]['title'] != '' :
                                return results['recordings'][0]['title']
                            else:
                                label7.config(text=f'{i+1}番目の候補のタイトルが「None」でした')
                                continue
                    else:
                        select_result = ()
                        return_title = ''
                        def select_click():
                            if not select_result:
                                return
                            nonlocal return_title
                            number = select_result[0]
                            try:
                                test = results['recordings'][number]['title']
                            except Exception as err:
                                label7.config(text=f'エラーが発生しました:{err}')
                                return 0
                            else:
                                if type(results['recordings'][number]['title']) == str:
                                    return_title = results['recordings'][number]['title']
                            root_3.destroy()

                        def select_candidates(event):
                            nonlocal select_result
                            select_result = listbox_second.curselection()


                        root_3 = tk.Toplevel(root)
                        root_3.title('second 3')
                        root_3.geometry('400x200')
                        button_second = tk.Button(root_3,text='確定',command=select_click)
                        button_second.pack()
                        listbox_second = tk.Listbox(root_3,exportselection=False)
                        listbox_second.pack()
                        listbox_second.bind('<<ListboxSelect>>',select_candidates)

                        for i in range(len(results['recordings'])):
                            try:
                                test = results['recordings'][i]['title']
                            except Exception as err:
                                label7.config(text=f'{i}番目のタイトルの楽曲情報でエラーが発生しました:{err}')
                                listbox_second.insert(tk.END,f'error:{i+1}')
                            else:
                                listbox_second.insert(tk.END,f'{results['recordings'][i]['title']}')

                        root.wait_window(root_3)
                        return return_title
                else:
                    continue       
            else:
                continue
        else:
            continue
    else:    
        return ''



last_rq = 0.0
def wati_time_api():
    wati_time = 0.35
    global last_rq
    elapsed = time.monotonic() - last_rq
    if elapsed < wati_time:
        time.sleep(wati_time-elapsed)
    last_rq = time.monotonic()

# ================= GUI =================
style = ttk.Style(root)
if 'vista' in style.theme_names():
    style.theme_use('vista')      
else:
    style.theme_use('clam')
UI_FONT = ('Yu Gothic UI', 10)
style.configure('.', font=UI_FONT)
style.configure('TButton', padding=(10, 4))
style.configure('Accent.TButton', font=('Yu Gothic UI', 10, 'bold'))
style.configure('Status.TLabel', foreground='#2c6fbb', font=('Yu Gothic UI', 10, 'bold'))
style.configure('Error.TLabel', foreground='#c0392b')
style.configure('TLabelframe.Label', font=('Yu Gothic UI', 10, 'bold'))

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)  

# --- 上段: 操作 ---
top = ttk.LabelFrame(root, text='操作', padding=(10, 6))
top.grid(row=0, column=0, sticky='ew', padx=12, pady=(12, 6))
top.columnconfigure(7, weight=1)

check = tk.Checkbutton(top,text='芝刈り',variable=shibakari_checker)
check.grid(row=0,column=2,padx=6)
check_sort = tk.Checkbutton(top,text='ソート',variable=sort_conf)
check_sort.grid(row=0,column=3,padx=6)
button = ttk.Button(top, text='ファイル選択', command=on_click)
button2 = ttk.Button(top, text='解析開始', command=analysis_click)
button6 = ttk.Button(top, text='ファイル作成', command=write_output)
button7 = ttk.Button(top, text='mp3作成', style='Accent.TButton', command=make_mp3)
button.grid(row=0, column=0, padx=(0, 6))
button2.grid(row=0, column=1, padx=6)
ttk.Separator(top, orient='vertical').grid(row=0, column=4, sticky='ns', padx=10)
button6.grid(row=0, column=5, padx=6)
button7.grid(row=0, column=8, padx=(6, 0), sticky='e')
button_list_update = ttk.Button(top,text='リスト更新',command=list_update)
button_list_update.grid(row=0,column=6,padx=6)

label2 = ttk.Label(top, text='待機中', style='Status.TLabel')
label2.grid(row=0, column=7, sticky='e', padx=12)

# --- 中段: 曲間候補 ---
mid = ttk.LabelFrame(root, text='曲間候補', padding=(10, 6))
mid.grid(row=1, column=0, sticky='nsew', padx=12, pady=6)
mid.columnconfigure(0, weight=1)
mid.rowconfigure(0, weight=1)

listbox = tk.Listbox(
    mid,
    font=UI_FONT,
    exportselection=False,
    activestyle='none',
    relief='flat',
    highlightthickness=1,
    highlightcolor='#2c6fbb',
    highlightbackground='#c8c8c8',
    selectbackground='#2c6fbb',
    selectforeground='white',
)
listbox.bind('<<ListboxSelect>>',list_click)
listbox.grid(row=0, column=0, sticky='nsew')

scroll = ttk.Scrollbar(mid, orient='vertical', command=listbox.yview)
scroll.grid(row=0, column=1, sticky='ns')
listbox.config(yscrollcommand=scroll.set)

side = ttk.Frame(mid)
side.grid(row=0, column=2, sticky='n', padx=(10, 0))
button3 = ttk.Button(side, text='確認', width=8, command=list_click_pritn)
button4 = ttk.Button(side, text='消去', width=8, command=delete_click)
button5 = ttk.Button(side, text='復元', width=8, command=restore_click)
button3.pack(fill='x', pady=(0, 4))
button4.pack(fill='x', pady=4)
button5.pack(fill='x', pady=4)

# --- 下段: 出力設定 ---
bottom = ttk.LabelFrame(root, text='出力設定', padding=(10, 6))
bottom.grid(row=2, column=0, sticky='ew', padx=12, pady=6)
bottom.columnconfigure(1, weight=1)

ttk.Label(bottom, text='出力ファイル名:').grid(row=0, column=0, sticky='w')
entry = ttk.Entry(bottom)
entry.grid(row=0, column=1, sticky='ew', padx=(8, 0))
entry.bind('<Return>',file_name_entry)

# --- メッセージ ---
msg = ttk.LabelFrame(root, text='メッセージ', padding=(10, 4))
msg.grid(row=3, column=0, sticky='ew', padx=12, pady=(6, 12))
msg.columnconfigure(0, weight=1)

label3 = ttk.Label(msg, text='', wraplength=760, justify='left')
label4 = ttk.Label(msg, text='', wraplength=760, justify='left')
label5 = ttk.Label(msg, text='', wraplength=760, justify='left')
label6 = ttk.Label(msg, text='', wraplength=760, justify='left')
label7 = ttk.Label(msg, text='', wraplength=760, justify='left')
label8 = ttk.Label(msg, text='', wraplength=760, justify='left', style='Error.TLabel')
for r, lb in enumerate((label3, label4, label5, label6, label7, label8)):
    lb.grid(row=r, column=0, sticky='w')


def analyze_audio(file_path):
    try:
        result_long = subprocess.run(
            [    str(ffprobe_path),
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
            ], 
            capture_output=True, 
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW
            )
    except UnicodeDecodeError as err:
        label7.config(text=f'エラーが発生しました:{err}')
        return None,None
    except OSError as err:
        label7.config(text=f'エラーが発生しました:{err}')
        return None,None
    else:
        label7.config(text='')

    if result_long.returncode == 0:
        if result_long.stdout == "":
            label7.config(text='ffprobeが正常に解析しませんでした。処理を中止します')    
            return None,None
        try:
            duration = float(result_long.stdout)
        except ValueError as err:
            label7.config(text=f'エラーが発生しました。:{err}')
            return None,None
        else:
            if duration <= 0 or math.isinf(duration) or math.isnan(duration) :
                label7.config(text='ffprobeが正常に解析しませんでした。処理を中止します')
                return None,None
    else:
        label7.config(text='ffprobeが正常に解析しませんでした。処理を中止します')
        return None,None


    
    try:
        result = subprocess.run(
            [str(ffmpeg_path),'-i',file_path,'-af','silencedetect=noise=-35dB:d=0.5','-f','null','-'], 
            capture_output=True, 
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW
            )
    except UnicodeDecodeError as err:
        label7.config(text=f'エラーが発生しました:{err}')
        return None,None
    except OSError as err:
        label7.config(text=f'エラーが発生しました:{err}')
        return None,None
    except Exception as err:
        label7.config(text=f'予期せぬエラーが発生しました:{err}')
        return None,None
    else:
        if result.returncode != 0:
            label7.config(text=f'エラーが発生しました')
            return None,None
        
    
    stderr_lines = result.stderr.splitlines()

    include = []
    for line in stderr_lines:
        judge = "silence_start:"in line or "silence_end" in line
        if judge : include.append(line)


    starts = []
    ends = []
    for line in include :
        judge_start = 'silence_start:' in line
        judge_end = 'silence_end:' in line
        if judge_start :
            starts.append(float(line.split(':')[1]))
        elif judge_end:
            before, separator, after = line.partition("|")
            ends.append(float(before.split(':')[1]))

    intervals = []
    for start, end in zip(starts, ends):
        data = {}
        data['start'] = start
        data["end"] = end
        data["duration"] = end - start
        intervals.append(data)

    candidates = []

    for data in intervals :
        time = data['duration']
        if time >= 0.5 and data['start']> 0 and abs(duration-data['end'])>0.1 :
            candidates.append(data)


    for data in candidates :
        data['position'] = (data['start']+data['end'])/2

    candidates = bs.score(candidates)

    candidates,err = bs.score_absolute(candidates,duration)

    if candidates is None:
        label7.config(text=f'ファイルが長すぎます。処理を中止します。:{err}')
        return None,None

    candidates = bs.filter_nearby(candidates)

    candidates,err = bs.score_silence(candidates)

    if candidates is None:
        label7.config(text=f'無音区間が長すぎます。処理を中止します。:{err}')
        return None , None

    candidates,err = bs.score_relative(candidates,duration)

    if candidates is None:
        label7.config(text=f'ファイルが長すぎます。処理を中止します。:{err}')
        return None , None

    # candidates = bs.detect_diviation(candidates)

    candidates = bs.classify_conf(candidates)
    if shibakari_checker.get():
        candidates = bs.shibakari(candidates)


    return candidates , duration
    
def make_segments(candidates,duration):
    segments = [] 

    if not len(candidates):
        return segments

    if len(candidates)==1 :
        segments.append({'start':0,'end':candidates[0]['position'],'length':candidates[0]['position']})
        segments.append({'start':candidates[0]['position'],'end':duration,'length':duration-candidates[0]['position']})
        return segments
    
    for i in range(len(candidates)):
        if i == 0:
            segments.append({'start':0,'end':candidates[0]['position'],'length':candidates[0]['position']})
        elif i == len(candidates)-1:
            segments.append({'start':candidates[i-1]['position'],'end':candidates[i]['position'],'length':candidates[i]['position']-candidates[i-1]['position']})
            segments.append({'start':candidates[i]['position'],'end':duration,'length':duration-candidates[i]['position']})
        else:
            segments.append({'start':candidates[i-1]['position'],'end':candidates[i]['position'],'length':candidates[i]['position']-candidates[i-1]['position']})
    
    return segments

error = 0
if (not shutil.which('ffmpeg')) and (not shutil.which('ffprobe')):
    error = 1
    label7.config(text='ffmpegとffprobeが見つかりません')
else:
    if not shutil.which('ffmpeg'):
        error = 1
        label7.config(text='ffmpegが見つかりません。')
    if not shutil.which('ffprobe'):
        error = 1
        label7.config(text='ffprobeが見つかりません')

root.mainloop()
