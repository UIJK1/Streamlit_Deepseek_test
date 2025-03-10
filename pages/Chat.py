import time

import streamlit as st
import os
import pickle
from openai import OpenAI
from rag_utils import retrieve_documents

# 缓存目录
CACHE_DIR = ".cache"

# 设置页面标题
st.set_page_config(page_title="小卢AI", page_icon="🤖", layout="wide")


# 初始化会话状态
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""  # 记录 API Key 输入次数

if "message" not in st.session_state:
    st.session_state.message = []  # 存储聊天记录

st.title("欢迎使用小卢AI")

# 显示历史消息
for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 隐藏提示词
HIDDEN_PROMPT = ("请参考文字材料，尽量用文字材料中的内容进行回答："
                 "作为银行的大堂经理，以下是常见业务，注意我的视角是大堂经理：\
                  新办银行卡：首先需要查询有没有当地社保缴费记录，当地企业工作证明等（企业微信，钉钉等截图也可以），核实客户在当地工作或者居住的情况（在本地居住或者工作的证明提供一项即可）；然后需要查询手机号的实名情况，若手机号非本人所有，需要提供号主与本人的关系证明，如母女则提供出生证明或者母女名字在同一个户口本上，若无证明材料原则上不予办理银行卡，但是若客户是学生，则可以凭借学生证，办理二类卡（注意：2类卡限入限出，均限10000）；\
                  首先查询名下有没有一类卡，如果有的话，可能先降级成2类，再新办一类卡，记得开卡的时候要开电子钱包。\
                  开通银行卡时，在个人信息页面需要客户注意预留手机号是否正确，如果手机号不正确，需要退出页面，修改手机号码，修改完成后，回到开卡时的修改个人信息界面，即可看到手机号已更改。最好不要直接在个人信息界面修改手机号，否则在电子银行部分，是使用修改前的手机号进行短信验证码验证，若客户以前的手机号不再使用，只有先跳过电子银行开通，在客户银行卡办理出来后，关闭全部电子银行账户，重新开通电子银行。\
                  当客户在开通电子银行时，一定需要提醒客户短信业务是否开通，并告知客户短信费用收费规则。\
                  当新办卡的客户储值在10万元以上时，可以办理金卡，金卡可以免年费，免短信费。\
                  打征信：在个人业务，上面横着的滑条拉到最后，更多功能，信用报告，但是只能打简版征信。\
                  打流水明细：个人打流水明细，在常用功能中点击“查明细打流水”，插入身份证或者银行卡查询流水，最多可以打十五年的流水，该项业务不会收费。\
                  存折ATM机取款：在发社保日时，通常是每个月10号，老年人会来取现金，若老年人手持存折，且钱是活期，可以在智慧柜员机点击“ATM取款申请”进行凭证领取，然后去ATM机进行办理，无需上柜台。\
                  个人贷款：还房贷，卡还款可以在7、8、9号窗口，现金还款可以去柜台。\
                  结清证明：可以在STM机上打印。\
                  到期换卡：到期换卡可以分为保号换卡和不保号换卡，不保号换卡可以当日拿卡，需要去柜面办理；而保号换卡不能当日拿卡，成都本地的卡可以在智慧柜员机或者手机银行上办理申请，5个工作日以后，取号上柜台凭旧卡和身份证拿新卡，并且尽量不要在12点~14点来网点，因为保管卡的人可能中午休息；而非成都市的卡不能在手机银行和智慧柜员机办理，需要去柜台办理。\
                  挂失补卡：挂失换卡，若不保同号，可以在STM上办理；若保同号，需要注意卡种，4,5开头的卡不能保号换取，且外地的卡需要较长工作日，需要定制和邮寄，若能保号换卡，需要填单子上柜台办理，单子是十问和反电信诈骗。\
                  损毁补卡：也要注意是不是外地的卡，且需要注意卡种，4,5开头的卡不能保号换取。\
                  客户定期续存：在存定期里面，零存整取。\
                  关闭电子银行：若客户不记得以前账户的密码，并且没有带卡（无法重置卡的密码），关闭全部账号，插入当前拥有的银行卡，输入当前卡的密码来进行办理。\
                  提额：限额涉及卡本身的限额和手机银行的限额，手机银行的限额可以在手机银行上进行提额申请，但是若提额后，仍然不能转账，还是需要去柜台办理提额。\
")





# 如果用户输入了 API Key，则初始化 OpenAI 客户端
if st.session_state["OPENAI_API_KEY"]!="":
    client = OpenAI(
        api_key=st.session_state["OPENAI_API_KEY"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 获取用户输入
    prompt = st.chat_input("输入内容")
    if prompt:
        # 显示用户消息
        with st.chat_message("human"):
            st.write(prompt)

        # 将用户消息添加到对话历史（不包含隐藏提示词）
        st.session_state.message.append({"role": "user", "content": prompt})

        # 显示“正在思考”的标志
        with st.spinner("AI 正在思考，请稍等..."):
            # 检索相关文档
            # context = retrieve_documents(prompt, model, index, chunks, similarity_threshold=0.7)  # 降低相似度阈值
            # context_text = "\n".join(context)

            # 构建提示词
            #full_prompt = f"{HIDDEN_PROMPT}\n{context_text}\n\n问题：{prompt}\n回答："
            full_prompt = f"{HIDDEN_PROMPT}\n\n问题：{prompt}\n回答："

            # 调用阿里云百炼的 API 生成回复
            response = client.chat.completions.create(
                model="qwen-plus",  # 使用 qwen-plus 模型
                messages=[
                    {"role": "system", "content": "你是一个有帮助的助手。"},
                    {"role": "user", "content": full_prompt},
                ],
            )
            ai_response = response.choices[0].message.content

            # 后处理：移除 <think></think> 结构
            ai_response = ai_response.replace("<think>", "").replace("</think>", "")

        # 显示 AI 回复
        with st.chat_message("AI"):
            st.write(ai_response)

        # 将 AI 回复添加到对话历史
        st.session_state.message.append({"role": "assistant", "content": ai_response})
