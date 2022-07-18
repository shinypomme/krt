import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import os
import unicodedata

list_store = ["大須サロン", "SKドックラン", "ローズマリー岡崎", "ローズマリー豊橋", "Floor岡崎", "クヌート土岐", "その他"]
list_columns = {0:"カルテNo.",1:"ワンちゃんの名前",2:"飼い主の名前",3:"電話番号", \
    4: "歴1:受診日", 5: "歴1:店舗", 6: "歴1:受診内容",   \
    7: "歴2:受診日", 8: "歴2:店舗", 9: "歴2:受診内容",   \
    10:"歴3:受診日", 11:"歴3:店舗", 12:"歴3:受診内容",   \
    13:"歴4:受診日", 14:"歴4:店舗", 15:"歴4:受診内容",   \
    16:"歴5:受診日", 17:"歴5:店舗", 18:"歴5:受診内容",   \
    19:"歴6:受診日", 20:"歴6:店舗", 21:"歴6:受診内容",   \
    22:"歴7:受診日", 23:"歴7:店舗", 24:"歴7:受診内容",   \
    25:"歴8:受診日", 26:"歴8:店舗", 27:"歴8:受診内容",   \
    28:"歴9:受診日", 29:"歴9:店舗", 30:"歴9:受診内容",   \
    31:"歴10:受診日",32:"歴10:店舗",33:"歴10:受診内容"
}
save_file_name = "カルテ.csv"
save_img_name = ".png"

N_HISTORY = 10
N_TERM_HISTORY = 3
LIST_HISTORY = [None] * (N_HISTORY * N_TERM_HISTORY)

def enter_client():
    st.info("顧客情報")
    if "change_column" in st.session_state:
        name_dog = st.text_input("ワンちゃんの名前", st.session_state.change_column.iloc[0]["ワンちゃんの名前"])
        owner = st.text_input("飼い主の名前", st.session_state.change_column.iloc[0]["飼い主の名前"])
        tel = st.text_input("電話番号", st.session_state.change_column.iloc[0]["電話番号"])
    else:
        name_dog = st.text_input("ワンちゃんの名前")
        owner = st.text_input("飼い主の名前")
        tel = st.text_input("電話番号")      
    
    if "img_read" in st.session_state:
        img_dog = st.file_uploader('写真を修正')
        if img_dog is not None:
            st.image(img_dog, use_column_width=True)
        elif st.session_state.img_read is not None:
            st.image(st.session_state.img_read, use_column_width=True)
    else:
        img_dog = st.file_uploader('写真を登録')
        if img_dog is not None:
            st.image(img_dog, use_column_width=True)
    
    return name_dog, owner, tel, img_dog

# 値からキーの取得関数
def get_key(list, val):
    for key, value in list.items():
         if val == value:
             return key

def check_number_history():
    for exist in range(1, N_HISTORY + 1):
        if type(st.session_state.change_column.loc[int(st.session_state.no_input),"歴" + str(exist) + ":受診日"]) != str:
            if np.isnan(st.session_state.change_column.loc[int(st.session_state.no_input),"歴" + str(exist) + ":受診日"]):
                break
    return exist - 1  

def show_history():
    do_delete_history = False
    delete_no = 0

    if "change_column" in st.session_state:
        st.info("過去の受診歴")
        exist = check_number_history()
        if exist > 0:
            i= 0
            list_show_history = []
            kye_start = get_key(list_columns, "歴1:受診日") - 1 # カルテNo.をインデックス化した分-1する
            while  i < (exist):
                key = kye_start + N_TERM_HISTORY * i
                i += 1
                list_show_history.append([st.session_state.change_column.iloc[0, key], st.session_state.change_column.iloc[0, key + 1], st.session_state.change_column.iloc[0, key + 2]])
            st.table(pd.DataFrame(list_show_history, columns=["受診日", "店舗", "受診内容"]))
            
            if st.checkbox('過去の受診内容を削除する'):
                do_delete_history = True
                delete_no = st.selectbox("削除する受診歴No.を選択", list(range(0,exist)))
        else:
            st.write("受診歴はありません")
    
    return do_delete_history, delete_no

def enter_history():
    st.info("今回の受診内容")
    date = st.date_input("受診日")
    store = st.selectbox("店舗", list_store)
    if store == "その他":
        store = st.text_input("その他の店舗名を入力")
    consultation = st.text_input("施術内容")
    
    return str(date), store, consultation

def change_number_top(letter, before_top, assign_top):
    if (letter[0] == before_top):
        letter = assign_top + letter
    return letter

def make_client_list(name_dog, owner, tel):
    return [name_dog, owner, change_number_top(tel, "0", "'")]

def make_consultation_list(date, store, consultation):
    
    if "change_column" in st.session_state:
        list_history = []
        for i in range(get_key(list_columns, "歴1:受診日") - 1 , get_key(list_columns, "歴10:受診内容")):
            list_history.append(st.session_state.change_column.iloc[0][i])
        index_start = N_TERM_HISTORY * check_number_history()
    else:
        list_history = LIST_HISTORY
        index_start = 0
    
    if type(date) == str:
        list_history[index_start] = date
        list_history[index_start + 1] = store
        list_history[index_start + 2] = consultation
    return list_history

def delete_history(list_save, delete_no):
    start_index = get_key(list_columns, "歴" + str(delete_no + 1) + ":受診日")
    for i in range(0, N_TERM_HISTORY):
        del list_save[start_index]
        list_save.append(None)
    return list_save

def over_save(name_dog, owner, tel, date, store, consultation, do_delete_history, delete_no):
    df_save = pd.read_csv('カルテ.csv', index_col=0)
    if "change_column" in st.session_state:
        no = st.session_state.no_input
    else:
        no = df_save.index.max() + 1
    list_save = make_client_list(name_dog, owner, tel) + make_consultation_list(date, store, consultation)
    if do_delete_history:
        list_save = delete_history(list_save, delete_no)
    df_save.loc[int(no)] = list_save
    df_save.to_csv(save_file_name, index=True)
    return no

def new_save(name_dog, owner, tel, date, store, consultation):
    no = 1
    list_save = make_client_list(name_dog, owner, tel) + make_consultation_list(date, store, consultation)
    list_save = [no] + list_save
    df_save = (pd.DataFrame(list_save)).T
    df_save = df_save.rename(columns = list_columns)
    df_save = df_save.set_index("カルテNo.")
    df_save.to_csv(save_file_name, index=True)
    return no

def save_img(img_dog, no):
    if img_dog:
        img_path = os.path.join(str(no) + save_img_name)
        with open(img_path, 'wb') as f:
            f.write(img_dog.read())

def change_letter_width_f_to_h(letter):
    if unicodedata.east_asian_width(letter) == "F":
        letter = unicodedata.normalize("NFKC", letter)
    return letter

def new_form():
    name_dog, owner, tel, img_dog = enter_client()
    do_delete_history, delete_no = show_history()
    if st.checkbox('今回の受診内容を入力する'):
        date, store, consultation = enter_history()
    else:
        date = np.nan
        store = np.nan
        consultation = np.nan
    
    if st.button("保存"):
        # try:
        is_file = os.path.isfile(save_file_name)
        if is_file:
            no = over_save(name_dog, owner, tel, date, store, consultation, do_delete_history, delete_no)
        else:
            no = new_save(name_dog, owner, tel, date, store, consultation)
        save_img(img_dog, no)
        # except Exception as e:
        #     st.error("エラーです。ページをリロードし初めからやり直してください")
        # else:
        st.success("カルテNo." + str(no) + '、保存できました')


is_file = os.path.isfile(save_file_name)
if is_file:
    df = pd.read_csv('カルテ.csv')
    df = df.set_index("カルテNo.")
    st.sidebar.write("カルテ一覧")
    st.sidebar.dataframe(df[["ワンちゃんの名前", "飼い主の名前", "電話番号"]])
    if st.sidebar.button("新規作成"):
        if "change_column" in st.session_state:
            del st.session_state.change_column
        if "img_read" in st.session_state:
            del st.session_state.img_read
        if "no_input" in st.session_state:
            del st.session_state.no_input
        if "df_delete" in st.session_state:
            del st.session_state.df_delete

    no_input = st.sidebar.text_input("編集するカルテNo.を入力")

    if st.sidebar.button("編集"):
        no_input = change_letter_width_f_to_h(str(no_input))
        if df.index.isin([int(no_input)]).any():
            change_column = df[df.index.get_loc(int(no_input)) : df.index.get_loc(int(no_input)) + 1]
            is_img = os.path.isfile(str(no_input) + save_img_name)
            img_read = Image.open(str(no_input) + save_img_name) if is_img else None
            st.session_state.change_column = change_column
            st.session_state.img_read = img_read
            st.session_state.no_input = no_input
        else:
            st.sidebar.error("カルテが存在しません")

    no_delete = st.sidebar.text_input("削除するカルテNo.を入力")
    if st.sidebar.button("削除"):
        st.session_state.df_delete = df.drop(int(no_delete))
        st.session_state.df_delete.to_csv(save_file_name, index=True)
        # is_img = os.path.isfile(str(no_input) + save_img_name)
        # if is_img:
        #     os.remove(str(no_input) + save_img_name)
        st.sidebar.success("カルテNo." + str(no_delete) + '、削除できました')

if "change_column" in st.session_state:
    st.title("カルテNo." + str(st.session_state.no_input) + "の編集")
else:
    st.title("新規カルテの作成")
img = Image.open('カルテ.jpg')
st.image(img, use_column_width=True)

new_form()



# 編集ボタン押して、やはり新規に戻すボタン
# 消去ボタン