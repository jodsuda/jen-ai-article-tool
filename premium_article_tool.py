import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# HTML形式変換
def convert_to_html(text):
    lines = text.split('\n')
    html_lines = []
    for line in lines:
        if line.startswith("## "):
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:].strip()}</h3>")
        else:
            html_lines.append(line + "<br>")
    return "\n".join(html_lines)

# note形式変換
def convert_to_note_format(text):
    lines = text.split('\n')
    converted = []
    for line in lines:
        if line.startswith("## "):
            converted.append("■ " + line[3:])
        elif line.startswith("### "):
            converted.append("▶ " + line[4:])
        else:
            converted.append(line)
    return "\n".join(converted)

# SEO要素生成
def generate_seo_elements(keyword):
    seo_prompt = f"""
以下のキーワードに基づいて、ブログ記事やnote投稿で使えるSEO情報を出力してください。

【キーワード】：{keyword}

■ 出力形式：
1. フォーカスキーフレーズ（自然な日本語で）
2. SEOタイトル（クリックされやすく32文字以内）
3. メタディスクリプション（検索結果に表示されやすい120〜160文字程度）
4. スラッグ（英単語、ハイフン区切りでURL用に適した形）

日本語・記号整形済みで、箇条書き形式で出力してください。
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": seo_prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

# UI構成
st.set_page_config(page_title="AI記事構成メーカー（有料版）", layout="centered")
st.title("🧠 AI記事構成メーカー（有料版）")
st.write("テンプレ・タイトル・CTA・タグ・SEOまで一括生成。もう“書くだけ”の状態へ。")

# 入力
keyword = st.text_input("📝 キーワードを入力してください")
template = st.selectbox("🧩 構成テンプレートを選択", ["PREP", "AIDA", "SEO記事型"])
generate_title = st.checkbox("✅ タイトル案を生成する")
generate_cta = st.checkbox("✅ CTA（締めの文章）を生成する")
generate_tags = st.checkbox("✅ ハッシュタグを提案する")
add_writing_guide = st.checkbox("✅ 各見出しに“執筆ガイド”をつける")
generate_seo = st.checkbox("✅ SEO情報（タイトル・キーフレーズなど）を生成する")
output_format = st.radio("📄 出力形式を選択", ["Markdown", "HTML", "note用プレーンテキスト"])

# 実行
if st.button("🚀 すべて生成する") and keyword:
    with st.spinner("AIが記事構成を考えています..."):
        guide_instruction = (
            "各見出しの直後に、“このパートで書くべき内容”を1〜2行のアドバイスとして加えてください。"
            if add_writing_guide else ""
        )

        base_prompt = (
            f"以下のキーワードに基づいて、{template}型の記事構成を作成してください。\n\n"
            f"【キーワード】：{keyword}\n"
            f"■出力形式：\n"
            f"1. H2とH3を使った記事構成（テンプレートに従って流れを組む）\n"
            f"2. 150〜200文字の導入文\n"
            f"{guide_instruction}\n"
            f"文章は自然な日本語で、Markdown形式で出力してください。"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": base_prompt}],
            temperature=0.7,
        )
        structure = response.choices[0].message.content
        extra_output = ""

        if generate_title:
            title_prompt = f"{keyword} をテーマに、クリックされやすい記事タイトルを32文字以内で3案出力してください。"
            title_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": title_prompt}],
                temperature=0.7,
            )
            extra_output += "\n\n## 📝 タイトル案\n" + title_response.choices[0].message.content

        if generate_cta:
            cta_prompt = f"{keyword} に関連するブログやnote記事の最後に使える締めの文章（CTA）を2〜3文提案してください。"
            cta_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": cta_prompt}],
                temperature=0.7,
            )
            extra_output += "\n\n## 📢 CTA文\n" + cta_response.choices[0].message.content

        if generate_tags:
            tag_prompt = f"{keyword} に関するブログ投稿向けのハッシュタグを5個、日本語で出力してください。"
            tag_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": tag_prompt}],
                temperature=0.7,
            )
            extra_output += "\n\n## 🔖 ハッシュタグ\n" + tag_response.choices[0].message.content

        if generate_seo:
            seo_info = generate_seo_elements(keyword)
            extra_output += "\n\n## 🧠 SEO情報\n" + seo_info

        final_output = structure + extra_output

        if output_format == "HTML":
            final_output = convert_to_html(final_output)
        elif output_format == "note用プレーンテキスト":
            final_output = convert_to_note_format(final_output)

        st.success("✅ 生成完了！")
        st.text_area("生成結果", value=final_output, height=600)
