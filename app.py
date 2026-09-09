import streamlit as st
from datetime import date

# -----------------------------------------------------------------------------
# 1. データの初期化（簡易データベースの作成）
# Streamlitのセッション状態を利用してアプリ内でデータを保持します
# -----------------------------------------------------------------------------
if "users" not in st.session_state:
    # 初期ユーザー（教師アカウントを最低1つ用意）
    st.session_state["users"] = {
        "admin": {"password": "admin", "role": "教師"}
    }

if "evaluations" not in st.session_state:
    # 評価データ保存用辞書: { (ユーザーID, 日付): {項目1: 点数, ...} }
    st.session_state["evaluations"] = {}

# -----------------------------------------------------------------------------
# 2. ログイン状態の管理
# -----------------------------------------------------------------------------
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

# -----------------------------------------------------------------------------
# 3. アプリ全体のタイトル
# -----------------------------------------------------------------------------
st.title("🏫 生徒評価管理アプリ")

# -----------------------------------------------------------------------------
# 4. ログイン画面（未ログインの場合に表示）
# -----------------------------------------------------------------------------
if st.session_state["logged_in_user"] is None:
    st.subheader("ログイン")
    
    login_id = st.text_input("ユーザーID", key="login_id")
    login_pw = st.text_input("パスワード", type="password", key="login_pw")
    
    if st.button("ログイン"):
        # ユーザーの存在とパスワードのチェック
        if login_id in st.session_state["users"] and st.session_state["users"][login_id]["password"] == login_pw:
            st.session_state["logged_in_user"] = login_id
            st.session_state["user_role"] = st.session_state["users"][login_id]["role"]
            st.success(f"{login_id} としてログインしました！")
            st.rerun()  # 画面を更新
        else:
            st.error("ユーザーIDまたはパスワードが正しくありません。")
            st.info("※初回起動時は、教師ID: admin / パスワード: admin でログインできます。")

# -----------------------------------------------------------------------------
# 5. ログイン後のメイン画面
# -----------------------------------------------------------------------------
else:
    current_user = st.session_state["logged_in_user"]
    current_role = st.session_state["user_role"]
    
    # ログアウトボタンとヘッダー情報
    col_header, col_logout = st.columns([4, 1])
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
        st.subheader("本日の自己評価入力")
        today = date.today()
        st.info(f"日付: {today.strftime('%Y年%m月%d日')} (本日中であれば何度でも変更可能です)")
        
        # すでに今日のデータがあればそれを初期値にする
        existing_eval = st.session_state["evaluations"].get((current_user, today), {
            "授業態度": 3,
            "学習に必要ないものは見ていないか": 3,
            "挨拶の大きさ": 3,
            "2分前に準備ができているか": 3
        })
        
        # 4つの評価基準（1〜5の選択肢）
        q1 = st.selectbox("1. 授業態度", options=[1, 2, 3, 4, 5], index=existing_eval["授業態度"] - 1)
        q2 = st.selectbox("2. 学習に必要ないものは見ていないか", options=[1, 2, 3, 4, 5], index=existing_eval["学習に必要ないものは見ていないか"] - 1)
        q3 = st.selectbox("3. 挨拶の大きさ", options=[1, 2, 3, 4, 5], index=existing_eval["挨拶の大きさ"] - 1)
        q4 = st.selectbox("4. 2分前に準備ができているか", options=[1, 2, 3, 4, 5], index=existing_eval["2分前に準備ができているか"] - 1)
        
        if st.button("評価を保存する"):
            # データを保存
            st.session_state["evaluations"][(current_user, today)] = {
                "授業態度": q1,
                "学習に必要ないものは見ていないか": q2,
                "挨拶の大きさ": q3,
                "2分前に準備ができているか": q4
            }
            st.success("本日の評価を保存しました！")

    # -------------------------------------------------------------------------
    # 【教師側画面】
    # -------------------------------------------------------------------------
    elif current_role == "教師":
        # タブで「評価の確認」と「アカウント管理」を分ける
        tab1, tab2 = st.tabs(["📊 生徒の評価を確認する", "👤 アカウント管理（追加・設定）"])
        
        # --- タブ1: 評価の確認 ---
        with tab1:
            st.subheader("生徒の評価履歴")
            
            # 生徒一覧を取得
            student_list = [uid for uid, info in st.session_state["users"].items() if info["role"] == "生徒"]
            
            if not student_list:
                st.warning("現在、登録されている生徒アカウントがありません。右側の「アカウント管理」から追加してください。")
            else:
                selected_student = st.selectbox("確認したい生徒を選択", options=student_list)
                
                # 選択された生徒の過去データを抽出
                history_data = []
                for (uid, eval_date), scores in st.session_state["evaluations"].items():
                    if uid == selected_student:
                        history_data.append({
                            "日付": eval_date.strftime("%Y-%m-%d"),
                            "授業態度": scores["授業態度"],
                            "学習に必要ないものは見ていないか": scores["学習に必要ないものは見ていないか"],
                            "挨拶の大きさ": scores["挨拶の大きさ"],
                            "2分前に準備ができているか": scores["2分前に準備ができているか"]
                        })
                
                if history_data:
                    # 日付順に並び替えてテーブル表示
                    history_data.sort(key=lambda x: x["日付"], reverse=True)
                    st.dataframe(history_data, use_container_width=True)
                else:
                    st.info(f"{selected_student} さんの評価データはまだ投稿されていません。")
                    
        # --- タブ2: アカウント管理 ---
        with tab2:
            st.subheader("新しいアカウントの追加")
            st.caption("生徒や他の教師のアカウントを何個でも新規作成できます。")
            
            new_id = st.text_input("新規ユーザーID（英数字推奨）")
            new_pw = st.text_input("新規パスワード", type="password")
            new_role = st.radio("権限（役割）", options=["生徒", "教師"])
            
            if st.button("アカウントを作成する"):
                if not new_id or not new_pw:
                    st.error("IDとパスワードは必須です。")
                elif new_id in st.session_state["users"]:
                    st.error("このユーザーIDはすでに使われています。")
                else:
                    # アカウントを追加登録
                    st.session_state["users"][new_id] = {
                        "password": new_pw,
                        "role": new_role
                    }
                    st.success(f"アカウント「{new_id}」（{new_role}）を新しく作成しました！")
                    st.rerun()
            
            st.divider()
            st.subheader("現在の登録アカウント一覧")
            # 確認用に登録されているアカウントをリスト表示
            for uid, info in st.session_state["users"].items():
                st.text(f"・ID: {uid} | パスワード: {info['password']} | 権限: {info['role']}")
