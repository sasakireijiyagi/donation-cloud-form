import streamlit as st
from datetime import date
from docxtpl import DocxTemplate
from io import BytesIO
import urllib.parse as up  # mailto のエンコード用

# ---- セッションステート初期化 ----
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "downloaded" not in st.session_state:
    st.session_state.downloaded = False

st.set_page_config(page_title="九州大学 寄附申込フォーム", layout="centered")
st.title("🐐 九州大学 寄附申込フォーム（佐々木玲仁 研究支援）")

st.markdown("以下のフォームに入力すると、大学提出用の寄附申込書（Wordファイル）が自動生成されます。")

st.markdown("""
### 📄 ご利用手順（約1〜2分で完了）

1. 以下のフォームに必要事項を入力  
2. 入力内容を確認し、「この内容で生成する」にチェック  
3. **Wordファイルをダウンロード**  
4. ダウンロード後に出る **「メールを作成する」ボタン** から送信（添付はご自身で）
""")

# ---- フォーム本体 ----
with st.form("donation_form"):
    today = st.date_input("申込日", date.today())
    name = st.text_input("寄附者氏名")
    zip_code = st.text_input("郵便番号（ハイフンなし 7桁）", max_chars=7, help="例：8190395")
    address1 = st.text_input("住所1（例：福岡県福岡市西区元岡744）")
    address2 = st.text_input("住所2（例：マンション名・部屋番号など）")
    email = st.text_input("メールアドレス（控えを送付します）")

    st.markdown("### 寄附金額")
    amount_option = st.radio(
        "金額を選んでください",
        ["1,000 円", "3,000 円", "5,000 円", "10,000 円", "金額は自分で入力する"],
        index=1
    )
    custom_amount = st.number_input("自由入力欄（円）", min_value=1, step=1000, value=3000)

    st.caption("💡 入金は銀行振込となります。振込手数料は寄附者のご負担となります。")

    amount = int(amount_option.replace(",", "").split()[0]) if amount_option != "金額は自分で入力する" else int(custom_amount)

    st.markdown("### 寄附目的")
    purpose_detail = st.radio(
        "寄附先の選択（佐々木玲仁 研究関連）",
        ["研究全般", "糸島市子どもの居場所プロジェクト"],
        index=0
    )

    condition = st.radio("寄附の条件", ["なし", "あり"])
    condition_detail = st.text_input("条件の内容") if condition == "あり" else ""

    other = st.text_area("その他コメント（任意）")

    # ▼ 個人情報の取扱い（明示表示）
    st.markdown("### 個人情報の取扱い")
    st.markdown(
        "入力いただいた個人情報は、**今回のご寄附に関する連絡・手続き**の目的にのみ使用します。"
        "大学の規程に基づき適切に管理し、**研究・教育・広報その他の目的で第三者に提供・使用することはありません**。"
    )

    submitted = st.form_submit_button("📋 入力内容を確認する")

if submitted:
    st.session_state.submitted = True
    st.session_state.confirmed = False
    st.session_state.downloaded = False

# ---- 確認画面 ----
if st.session_state.submitted:
    try:
        formatted_date = today.strftime("%Y年%-m月%-d日")
    except Exception:
        formatted_date = today.strftime("%Y年%m月%d日")

    st.markdown("### ✅ 入力内容の確認")
    st.write(f"**申込日：** {formatted_date}")
    st.write(f"**氏名：** {name}")
    st.write(f"**住所：** 〒{zip_code} {address1}")
    st.write(f"**住所2：** {address2}")
    st.write(f"**メールアドレス：** {email}")
    st.write(f"**寄附金額：** {amount:,} 円")
    st.write(f"**寄附目的：** 研究者へ［佐々木玲仁／{purpose_detail}］")
    st.write(f"**条件：** {'なし' if condition == 'なし' else condition_detail}")
    st.write(f"**その他コメント：** {other or 'なし'}")

    if st.checkbox("内容に間違いがないことを確認しました", key="confirmation"):
        st.session_state.confirmed = True

# ---- 生成＆ダウンロード ----
if st.session_state.confirmed:
    context = {
        "date": formatted_date,
        "name": name,
        "address1": f"〒{zip_code} {address1}",
        "address2": address2,
        "email": email,
        "amount": f"{amount:,}",
        "purpose": f"研究者へ［佐々木玲仁／{purpose_detail}］",
        "condition": condition_detail if condition == "あり" else "なし",
        "other": other or "なし",
    }

    doc = DocxTemplate("donate_format.docx")
    doc.render(context)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.success("✅ 寄附申込書が生成されました。内容を確認後、まずはダウンロードしてください。")

    downloaded = st.download_button(
        label="📄 寄附申込書（Word形式）をダウンロード",
        data=buffer,
        file_name="寄附申込書.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    if downloaded:
        st.session_state.downloaded = True

    # ---- ダウンロード後だけ「メールを作成する」ボタンを表示 ----
    if st.session_state.downloaded:
        to_addr = "jbzkeiri1@jimu.kyushu-u.ac.jp"
        subject = "九州大学寄附申込書の提出"

        body_text = f"""九州大学人間環境学研究院 経理第一係 御中

お世話になっております。
寄附申込フォームで作成した寄附申込書を提出いたします。
添付ファイルをご確認いただき、所定の手続きをお願いいたします。

【寄附者情報】
氏名：{name}
寄附金額：{amount:,}円
寄附目的：研究者へ［佐々木玲仁／{purpose_detail}］
申込日：{formatted_date}

—
本メールは寄附申込者のメール環境から送信されています。
ご不明点がございましたら、下記までご連絡ください。
佐々木 玲仁（人間環境学研究院）
sasaki@hes.kyushu-u.ac.jp
"""

        # 改行を CRLF (%0D%0A) に置換してクライアント互換性を高める
        encoded_subject = up.quote(subject)
        encoded_body = up.quote(body_text).replace("%0A", "%0D%0A")
        mailto = f"mailto:{to_addr}?subject={encoded_subject}&body={encoded_body}"

        st.markdown("---")
        # アンカーをボタン風に装飾（Streamlitの標準ボタンは外部リンクに使えないため）
        st.markdown(
            f'''
            <a href="{mailto}" target="_self"
               style="
                 display:inline-block;padding:0.65rem 1rem;border-radius:0.5rem;
                 background:#0f62fe;color:#fff;text-decoration:none;
                 font-weight:600;letter-spacing:.01em;
               ">
               📧 メールを作成する（添付はご自身でお願いします）
            </a>
            ''',
            unsafe_allow_html=True,
        )
        st.caption("※ クリックでお使いのメーラが開きます。先ほどダウンロードした Word ファイルを添付して送信してください。")