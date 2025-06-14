import streamlit as st
from datetime import date
from docxtpl import DocxTemplate
from io import BytesIO

st.set_page_config(page_title="九州大学 寄附申込フォーム", layout="centered")
st.title("🐐 九州大学 寄附申込フォーム（佐々木玲仁 研究支援）")

st.markdown("以下のフォームに入力すると、大学提出用の寄附申込書（Wordファイル）が自動生成されます。")

st.markdown("""
### 📄 ご利用手順（約1〜2分で完了します）

1. 以下のフォームに必要事項を入力してください  
2. 「Wordファイルを生成する」ボタンを押してください  
3. ダウンロードされたファイルを、下記の提出先にメール添付で送信してください

📬 **提出先メールアドレス：**  
jbzkeiri1@jimu.kyushu-u.ac.jp（九州大学 人間環境学研究院 経理第一係）
""")

with st.form("donation_form"):
    today = st.date_input("申込日", date.today())
    name = st.text_input("寄附者氏名")
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
            "糸島市子どもの居場所プロジェクト",
            "研究全般"
        ]
    )

    condition = st.radio("寄附の条件", ["なし", "あり"])
    condition_detail = ""
    if condition == "あり":
        condition_detail = st.text_input("条件の内容")

    other = st.text_area("その他コメント（任意）")

    submitted = st.form_submit_button("📄 Wordファイルを生成する")

if submitted:
    formatted_date = today.strftime("%Y年%-m月%-d日") if st.runtime.exists() else today.strftime("%Y年%m月%d日")
    context = {
        "date": formatted_date,
        "name": name,
        "address1": address1,
        "address2": address2,
        "email": email,
        "amount": f"{amount:,}",
        "purpose": f"研究者へ［佐々木玲仁／{purpose_detail}］",
        "condition": condition_detail if condition == "あり" else "なし",
        "other": other or "なし"
    }

    # Word差し込み → バッファ保存
    doc = DocxTemplate("donate_format.docx")
    doc.render(context)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📄 寄附申込書（Word形式）をダウンロード",
        data=buffer,
        file_name="寄附申込書.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
