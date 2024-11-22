from openai import OpenAI
import streamlit as st
import os


st.title("ChatGPT by Streamlit") # タイトルの設定

api_key = st.text_input("Enter your OpenAI API Key:", type="password")

client = OpenAI(
    # api_key=api_key
    api_key=api_key,
)

# セッション内で使用するモデルが指定されていない場合のデフォルト値
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

# セッション内のメッセージが指定されていない場合のデフォルト値
if "messages" not in st.session_state:
    st.session_state.messages = []

# セッション内でチャット履歴をクリアするかどうかの状態変数
if "Clear" not in st.session_state:
    st.session_state.Clear = False

# 以前のメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザーからの新しい入力を取得
if prompt := st.chat_input("質問を入力してください"):
    st.session_state.messages.append({"role": "user", "content":[{'type':'text','text':prompt},],},)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 一時的なプレースホルダーを作成
        full_response = ""
        # ChatGPTからのストリーミング応答を処理
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.content if response.choices[0].delta.content else ""
            message_placeholder.markdown(full_response + "▌") # レスポンスの途中結果を表示
        message_placeholder.markdown(full_response) # 最終レスポンスを表示
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.Clear = True # チャット履歴のクリアボタンを有効にする

# チャット履歴をクリアするボタンが押されたら、メッセージをリセット
if st.session_state.Clear:
    if st.button('clear chat history'):
        st.session_state.messages = [] # メッセージのリセット
        full_response = ""
        st.session_state.Clear = False # クリア状態をリセット
        st.rerun() # 画面を更新