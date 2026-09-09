import streamlit as st
from datetime import date

# -----------------------------------------------------------------------------
# 1. データの初期化（セッション状態で保持）
# -----------------------------------------------------------------------------
if "users" not in st.session_state:
    st.session_state["users"] = {
        "admin": {"password": "admin", "role": "教師"}
    }

if "evaluations" not in st.session_state:
    st.session_state["evaluations"] = []

# ログイン状態の管理
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

st.title("🏫 生徒評価管理アプリ (完全管理版)")

# -----------------------------------------------------------------------------
# 2. ログイン画面
# -----------------------------------------------------------------------------
if st.session_state["logged_in_user"] is None:
    st.subheader("ログイン")
    
    login_id = st.text_input("ユーザーID", key="login_id")
    login_pw = st.text_input("パスワード", type="password", key="login_pw")
    
    if st.button("ログイン"):
        if login_id in st.session_state["users"] and st.session_state["users"][login_id]["password"] == login_pw:
            st.session_state["logged_in_user"] = login_id
            st.session_state["user_role"] = st.session_state["users"][login_id]["role"]
            st.success(f"{login_id} としてログインしました！")
            st.rerun()
        else:
            st.error("ユーザーIDまたはパスワードが正しくありません。")
            st.info("※初期ログイン用 ＞ ID: admin / パスワード: admin")

# -----------------------------------------------------------------------------
# 3. ログイン後のメイン画面
# -----------------------------------------------------------------------------
else:
    current_user = st.session_state["logged_in_user"]
    current_role = st.session_state["user_role"]
    
    col_header, col_logout = st.columns()
    with col_header:
        st.write(f"ログイン中: **{current_user}** さん（権限: {current_role}）")
    with col_logout:
        if st.button("ログアウト"):
            st.session_state["logged_in_user"] = None
            st.session_state["user_role"] = None
            st.rerun()
            
    st.divider()

    # -------------------------------------------------------------------------
    # 【生徒側画面】
    # -------------------------------------------------------------------------
    if current_role == "生徒":
        st.subheader("📝 評価の入力・修正")
        
        # 過去データも含めて、いつでも日付を選んで入力・変更可能に
        selected_date = st.date_input("評価を入力・修正する日付を選択してください", date.today())
        date_str = selected_date.strftime("%Y-%m-%d")
        
        # すでにその日のデータがあるか探す
        existing_index = None
        existing_eval = {"q1": 3, "q2": 3, "q3": 3, "q4": 3}
        
        for i, ev in enumerate(st.session_state["evaluations"]):
            if ev["user_id"] == current_user and ev["date"] == date_str:
                existing_index = i
                existing_eval = {
                    "q1": ev["授業態度"],
                    "q2": ev["学習に必要ないものは見ていないか"],
                    "q3": ev["挨拶の大きさ"],
                    "q4": ev["2分前に準備ができているか"]
                }
                break
        
        if existing_index is not None:
            st.warning(f"⚠️ {date_str} の評価データはすでに登録されています。内容を書き換えて保存すると更新されます。")
        else:
            st.info(f"📅 {date_str} の新規評価を入力しています。")

        # 4つの評価基準 (1〜5点の選択肢を配置)
        q1 = st.selectbox("1. 授業態度", options=[1, 2, 3, 4, 5], index=existing_eval["q1"] - 1, key="q1")
        q2 = st.selectbox("2. 学習に必要ないものは見ていないか", options=[1, 2, 3, 4, 5], index=existing_eval["q2"] - 1, key="q2")
        q3 = st.selectbox("3. 挨拶の大きさ", options=[1, 2, 3, 4, 5], index=existing_eval["q3"] - 1, key="q3")
        q4 = st.selectbox("4. 2分前に準備ができているか", options=[1, 2, 3, 4, 5], index=existing_eval["q4"] - 1, key="q4")
        
        if st.button("評価を保存・更新する"):
            new_data = {
                "user_id": current_user,
                "date": date_str,
                "授業態度": q1,
                "学習に必要ないものは見ていないか": q2,
                "挨拶の大きさ": q3,
                "2分前に準備ができているか": q4
            }
            
            if existing_index is not None:
                # 既存データを上書き
                st.session_state["evaluations"][existing_index] = new_data
                st.success(f"{date_str} の評価を更新しました！")
            else:
                # 新規追加
                st.session_state["evaluations"].append(new_data)
                st.success(f"{date_str} の評価を新しく保存しました！")
            st.rerun()

    # -------------------------------------------------------------------------
    # 【教師側画面】
    # -------------------------------------------------------------------------
    elif current_role == "教師":
        tab1, tab2, tab3 = st.tabs(["📊 生徒の評価確認・削除", "👤 アカウント作成", "⚙️ アカウントの変更・削除"])
        
        # --- タブ1: 評価の確認と削除 ---
        with tab1:
            st.subheader("生徒の評価履歴一覧")
            student_list = [uid for uid, info in st.session_state["users"].items() if info["role"] == "生徒"]
            
            if not student_list:
                st.warning("登録されている生徒アカウントがありません。")
            else:
                selected_student = st.selectbox("確認したい生徒を選択", options=student_list)
                
                # 該当生徒のデータを抽出
                student_evals = [ev for ev in st.session_state["evaluations"] if ev["user_id"] == selected_student]
                
                if student_evals:
                    # 日付の新しい順に並び替え
                    student_evals.sort(key=lambda x: x["date"], reverse=True)
                    
                    # 1件ずつ表示し、横に削除ボタンを配置
                    for ev in student_evals:
                        with st.container():
                            col_txt, col_del = st.columns()
                            with col_txt:
                                st.write(f"📅 **日付: {ev['date']}**")
                                st.text(f" └ 授業態度: {ev['授業態度']} | 外部確認: {ev['学習に必要ないものは見ていないか']} | 挨拶: {ev['挨拶の大きさ']} | 準備: {ev['2分前に準備ができているか']}")
                            with col_del:
                                if st.button("❌ 評価を削除", key=f"del_ev_{ev['user_id']}_{ev['date']}"):
                                    st.session_state["evaluations"].remove(ev)
                                    st.success(f"{ev['date']} の評価データを削除しました。")
                                    st.rerun()
                            st.divider()
                else:
                    st.info(f"{selected_student} さんの評価データはまだありません。")
                    
        # --- タブ2: アカウントの新規作成 ---
        with tab2:
            st.subheader("新しいアカウントの追加")
            new_id = st.text_input("新規ユーザーID")
            new_pw = st.text_input("新規パスワード", type="password")
            new_role = st.radio("権限（役割）", options=["生徒", "教師"], key="new_role")
            
            if st.button("アカウントを作成する"):
                if not new_id or not new_pw:
                    st.error("IDとパスワードを入力してください。")
                elif new_id in st.session_state["users"]:
                    st.error("このユーザーIDはすでに存在します。")
                else:
                    st.session_state["users"][new_id] = {"password": new_pw, "role": new_role}
                    st.success(f"アカウント「{new_id}」（{new_role}）を作成しました！")
                    st.rerun()
            
        # --- タブ3: アカウントの変更・削除 ---
        with tab3:
            st.subheader("登録済みアカウントの編集と削除")
            st.caption("先生や生徒のID・パスワードの変更、アカウント自体の削除が可能です。")
            
            all_users = list(st.session_state["users"].keys())
            selected_user = st.selectbox("編集・削除するアカウントを選択", options=all_users)
            
            if selected_user:
                user_info = st.session_state["users"][selected_user]
                st.write(f"現在の権限: **{user_info['role']}**")
                
                # 変更用フォーム
                edit_id = st.text_input("IDを変更する場合に入力", value=selected_user)
                edit_pw = st.text_input("パスワードを変更する場合に入力", value=user_info["password"])
                
                col_update, col_delete = st.columns(2)
                
                with col_update:
                    if st.button("💾 変更を保存する"):
                        if not edit_id or not edit_pw:
                            st.error("IDとパスワードは空にできません。")
                        else:
                            if edit_id != selected_user:
                                if edit_id in st.session_state["users"]:
                                    st.error("変更先のIDはすでに他のユーザーに使われています。")
                                else:
                                    st.session_state["users"][edit_id] = {"password": edit_pw, "role": user_info["role"]}
                                    del st.session_state["users"][selected_user]
                                    
                                    for ev in st.session_state["evaluations"]:
                                        if ev["user_id"] == selected_user:
                                            ev["user_id"] = edit_id
                                            
                                    if current_user == selected_user:
                                        st.session_state["logged_in_user"] = edit_id
                                    st.success("ユーザーIDとパスワードを変更しました！")
                                    st.rerun()
                            else:
                                st.session_state["users"][selected_user]["password"] = edit_pw
                                st.success("パスワードを変更しました！")
                                st.rerun()
                                
                with col_delete:
                    if selected_user == "admin" and current_user == "admin":
                        st.warning("⚠️ 初期管理者(admin)は削除できません。")
                    else:
                        if st.button("🗑️ アカウントを削除する"):
                            del st.session_state["users"][selected_user]
