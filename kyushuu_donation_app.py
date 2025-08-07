import streamlit as st
from datetime import date
from docxtpl import DocxTemplate
from io import BytesIO

import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# .env 読み込み
load_dotenv()
EMAIL_ADDRESS = os.getenv("GMAIL_USER")
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# メール送信関数
def send_email_with_attachment(to_address, cc_address, subject, body, attachment_data, filename):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Cc"] = cc_address
    msg.set_content(body)

    msg.add_attachment(
        attachment_data,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# セッションステートの初期化
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "downloaded" not in st.session_state:
    st.session_state.downloaded = False
if "email_sent" not in st.session_state:
    st.session_state.email_sent = False
if "buffer" not in st.session_state:
    st.session_state.buffer = None

st.set_page_config(page_title="九州大学 寄附申込フォーム", layout="centered")
st.title("🐐 九州大学 寄附申込フォーム（佐々木玲仁 研究支援）")

st.markdown("以下のフォームに入力すると、大学提出用の寄附申込書（Wordファイル）が自動生成されます。")

st.markdown("""
### 📄 ご利用手順（約1〜2分で完了します）

1. 以下のフォームに必要事項を入力してください  
2. 入力内容を確認し、「この内容で生成する」にチェック  
3. Wordファイルをダウンロードした後、「送信」ボタンからメール提出
""")

# フォーム本体
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

    if amount_option != "金額は自分で入力する":
        amount = int(amount_option.replace(",", "").split()[0])
    else:
        amount = int(custom_amount)

    st.markdown("### 寄附目的")
    purpose_detail = st.radio(
        "寄附先の選択（佐々木玲仁 研究関連）",
        [
            "研究全般",
            "糸島市子どもの居場所プロジェクト"
        ],
        index=0
    )

    condition = st.radio("寄附の条件", ["なし", "あり"])
    condition_detail = ""
    if condition == "あり":
        condition_detail = st.text_input("条件の内容")

    other = st.text_area("その他コメント（任意）")

    submitted = st.form_submit_button("📋 入力内容を確認する")

if submitted:
    st.session_state.submitted = True
    st.session_state.confirmed = False
    st.session_state.downloaded = False
    st.session_state.email_sent = False

if st.session_state.submitted:
    formatted_date = today.strftime("%Y年%-m月%-d日") if st.runtime.exists() else today.strftime("%Y年%m月%d日")

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
        "other": other or "なし"
    }

    doc = DocxTemplate("donate_format.docx")
    doc.render(context)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.session_state.buffer = buffer

    st.success("✅ 寄附申込書が生成されました。内容を確認後、ダウンロード・送信してください。")

    st.download_button(
        label="📄 寄附申込書（Word形式）をダウンロード",
        data=buffer,
        file_name="寄附申込書.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    if st.button("📨 寄附申込書をメールで提出する", disabled=st.session_state.email_sent):
        try:
            body = f"""
九州大学 寄附申込フォームを通じて、以下のとおり寄附申込書を提出いたします。
添付ファイルをご確認いただき、所定の手続きへのご対応をよろしくお願いいたします。

提出者（代理）：佐々木 玲仁（人間環境学研究院）
寄附者：{name} 様
寄附目的：{purpose_detail}
寄附金額：{amount:,} 円

控えとして寄附者様にも本メールをCCにてお送りしております。

—
本メールはフォーム入力により自動生成されています。
ご不明点等ございましたら、佐々木（sasaki@hes.kyushu-u.ac.jp）までご連絡ください。
"""

            send_email_with_attachment(
                to_address="jbzkeiri1@jimu.kyushu-u.ac.jp",
                cc_address=email,
                subject="【自動送信】九州大学寄附申込書の提出",
                body=body,
                attachment_data=st.session_state.buffer.getvalue(),
                filename="寄附申込書.docx"
            )
            st.success("✅ メールを送信しました（控えをCC送信しました）")
            st.session_state.email_sent = True
        except Exception as e:
            st.error(f"❌ メール送信に失敗しました: {e}")