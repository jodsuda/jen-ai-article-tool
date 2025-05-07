import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# .envからAPIキー読み込み
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI記事構成メーカー（無料体験）", layout="centered")
st.title("🧠 AI記事構成メーカー（無料版）")
st.write("キーワードを入れるだけで記事構成と導入文を自動生成します。")

keyword = st.text_input("📝 キーワードを入力してください", "")

if st.button("構成を生成する") and keyword:
    with st.spinner("AIが構成を考えています..."):
        prompt = f"""
以下のキーワードに基づいて、ブログ記事の構成を作成してください。

【キーワード】：{keyword}

■必要な出力形式（Markdown形式で）：
1. H2（##）とH3（###）を使った記事構成（H2×2〜3、H3を含めてください）
2. 150〜200文字程度の導入文（最初のパラグラフ）

Markdownとして正しく整形し、日本語で自然に書いてください。
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        raw = response.choices[0].message.content

        # ▼ Markdown整形
        formatted = raw.replace("###", "####").replace("##", "###")  # H2→H3、H3→H4 表示安定化用

        st.success("✅ 生成完了！")
        st.markdown("### 生成結果（Markdown表示）")
        st.markdown(formatted, unsafe_allow_html=True)

st.markdown("""
📌 有料版では以下のような拡張機能をご利用いただけます：

・テンプレ選択（PREP/AIDA/SEO型など構成を自由に変更）  
・導入文のトーン切替（親しみ／専門／キャッチー）＋複数案出力  
・32文字以内のクリック率を意識したタイトル案を自動生成  
・Xやnoteに最適なハッシュタグを5つ提案  
・シェアや購入を促すCTA文（締めの文章）も自動出力  
・HTML形式でのコピーも可能（ブログ貼り付け用）  
""")

