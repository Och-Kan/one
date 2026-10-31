#Agentic RAG 实践
#后端代码
#第九周往返校区实验实习活动用车安排

#1. 数据库
schedule_data = [
    {
    "weekday": "周一",
    "date": "4.27",
    "course_name": "普通化学实验B",
    "colleges": "土木",
    "depart_time": "12:40",
    "return_time": "17:50"
    },
    {
    "weekday": "周一",
    "date": "4.27",
    "course_name": "大学物理实验",
    "colleges": "生工、物信",
    "depart_time": "13:10",
    "return_time": "16:25"
    },
  {
    "weekday": "周一",
    "date": "4.27",
    "course_name": "大学物理实验",
    "colleges": "物信",
    "depart_time": "15:10",
    "return_time": "18:25"
  },
  {
    "weekday": "周二",
    "date": "4.28",
    "course_name": "大学物理实验",
    "colleges": "化工、土木",
    "depart_time": "07:20",
    "return_time": "10:45"
  },
  {
    "weekday": "周二",
    "date": "4.28",
    "course_name": "大学物理实验",
    "colleges": "化工、土木",
    "depart_time": "09:20",
    "return_time": "12:45"
  },
  {
    "weekday": "周二",
    "date": "4.28",
    "course_name": "普通化学实验B",
    "colleges": "土木",
    "depart_time": "07:20",
    "return_time": "12:40"
  },
  {
    "weekday": "周二",
    "date": "4.28",
    "course_name": "普通化学实验B",
    "colleges": "土木",
    "depart_time": "12:40",
    "return_time": "17:55"
  },
  {
    "weekday": "周二",
    "date": "4.28",
    "course_name": "分析化学实验B",
    "colleges": "化工",
    "depart_time": "12:40",
    "return_time": "18:10"
  },
  {
    "weekday": "周二",
    "date": "4.28",
    "course_name": "有机化学实验B",
    "colleges": "生工",
    "depart_time": "12:40",
    "return_time": "18:10"
  },
  {
    "weekday": "周二",
    "date": "4.29",
    "course_name": "大学物理实验",
    "colleges": "物信、化学",
    "depart_time": "13:10",
    "return_time": "16:25"
  },
  {
    "weekday": "周三",
    "date": "4.29",
    "course_name": "大学物理实验",
    "colleges": "材料",
    "depart_time": "13:10",
    "return_time": "16:25"
  },
  {
    "weekday": "周四",
    "date": "4.29",
    "course_name": "有机化学实验B",
    "colleges": "材料",
    "depart_time": "07:20",
    "return_time": "12:40"
  },
  {
    "weekday": "周四",
    "date": "4.29",
    "course_name": "有机化学实验A下",
    "colleges": "化学",
    "depart_time": "07:20",
    "return_time": "13:40"
  },
    {
    "weekday": "周四",
    "date": "4.29",
    "course_name": "无机化学实验J下",
    "colleges": "化学",
    "depart_time": "07:20",
    "return_time": "13:40"
  },
  {
    "weekday": "周四",
    "date": "4.29",
    "course_name": "有机化学实验C",
    "colleges": "地矿",
    "depart_time": "07:20",
    "return_time": "12:10"
  },
  {
    "weekday": "周四",
    "date": "4.30",
    "course_name": "普通化学实验B",
    "colleges": "地矿",
    "depart_time": "07:20",
    "return_time": "12:30"
  },
  {
    "weekday": "周四",
    "date": "4.30",
    "course_name": "大学物理实验",
    "colleges": "机械、土木",
    "depart_time": "07:20",
    "return_time": "10:45"
  },
  {
    "weekday": "周四",
    "date": "4.30",
    "course_name": "大学物理实验",
    "colleges": "机械、土木",
    "depart_time": "07:20",
    "return_time": "10:45"
  }
]

import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime,timedelta
from flask import Flask, request, jsonify, render_template   
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()  # 加载 .env 文件
api_key = os.getenv("BAIDU_API_KEY")
if not api_key:
    raise ValueError("错误：请在 .env 文件中设置 BAIDU_API_KEY")

client = OpenAI(
            api_key= os.getenv("BAIDU_API_KEY"),
            base_url="https://aistudio.baidu.com/llm/lmapi/v3"
        )



#匹配搜索的函数
def filter_schedule(
        weekday=None,      
        course_name=None,  
        college=None,      
        time_range=None    
    ):
        results = []
        for item in schedule_data:

            if weekday and item["weekday"] != weekday: #匹配星期
                continue
            if course_name and course_name not in item["course_name"]:  #匹配课程名称
                continue
            if college and college != item["colleges"]: #匹配学院
                continue
            

            if time_range: #时间：拆开再判断，分为上午和下午
                dep_hour = int(item["depart_time"].split(":")[0])
                if time_range == "上午" and not (6 <= dep_hour < 12):
                    continue
                if time_range == "下午" and not (12 <= dep_hour < 18):
                    continue
            
            results.append(item) #将符合条件的词加入到结果的列表中
        return results

#用正则来提取日期，统一映射成周x的形式
def extract_weekday(text):
    pattern = r'(?:周|星期|礼拜)[\s]*(?:日|天|0|七|7|一|1|二|2|三|3|四|4|五|5|六|6)'
    match = re.search(pattern, text)
    if not match:
        return None
    raw = match.group(0)
    num_part = re.search(r'(日|天|0|七|7|一|1|二|2|三|3|四|4|五|5|六|6)$', raw)
    if not num_part:
         return None
    code = num_part.group(1)
    mapping = {
        '一': '周一', '1': '周一',
        '二': '周二', '2': '周二',
        '三': '周三', '3': '周三',
        '四': '周四', '4': '周四',
        '五': '周五', '5': '周五',
        '六': '周六', '6': '周六',
        '日': '周日', '天': '周日', '0': '周日', '七': '周日', '7': '周日',
    }
    return mapping.get(code)

#处理一些相对时间比如今天明天和后天
def parse_relative_weekday(text):
    today = datetime.now()
    if '今天' in text:
        target = today
    elif '明天' in text:
        target = today + timedelta(days=1)
    elif '后天' in text:
        target = today + timedelta(days=2)
    else:
        return None
    weekday_map = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekday_map[target.weekday()]

#处理用户输入的内容
def parse_query(user_input):
    params = {
        "weekday": None,
        "course_name": None,
        "college": None,
        "time_range": None
    } #准备空的字典，用来收集用户的输入并拆分
    #处理日期    
    weekday = parse_relative_weekday(user_input)
    if weekday is None:
        weekday = extract_weekday(user_input)
    params["weekday"] = weekday
    #处理课程
    courses = ["大学物理实验", "普通化学实验B", "分析化学实验B", "有机化学实验B", 
                "有机化学实验A下","无机化学实验J下", "有机化学实验C"]

    courses_sorted = sorted(courses, key=len, reverse=True)
    course_pattern = "(" + "|".join(re.escape(c) for c in courses_sorted) + ")"
    '''
    此时课程显示变为"(有机化学实验A下|无机化学实验J下|有机化学实验C|大学物理实验|
    普通化学实验B|分析化学实验B|有机化学实验B)"
    '''
    match = re.search(course_pattern, user_input)
    if match:
        params["course_name"] = match.group(1)
    #处理学院
    colleges = ["物信", "化学", "材料", "生工", "土木", "化工", "地矿", "机械"]
    colleges_sorted = sorted(colleges, key=len, reverse=True)
    college_pattern = "(" + "|".join(re.escape(c) for c in colleges_sorted) + ")"
    match = re.search(college_pattern, user_input)
    if match:
        params["college"] = match.group(1)
    #处理时间段
    if re.search(r"上午|早上", user_input):
        params["time_range"] = "上午"
    elif re.search(r"下午|傍晚", user_input):
        params["time_range"] = "下午"

    return params

#组织答案的关键词
def format_results(results):
    if not results:
        return "未找到符合条件的内容。"
    lines = []
    for r in results:
        lines.append(f"{r['weekday']} {r['course_name']}（{r['colleges']}） 去程 {r['depart_time']} 返程 {r['return_time']}")
    return "\n".join(lines)


# 测试用
'''if __name__ == "__main__":
        test = "周一下午大学物理实验物信学院几点出发？"
        print(answer_question(test))
    '''

def get_answer(user_input: str) -> str:
    # 1. 获得并处理用户的输入
    params = parse_query(user_input)
    # 2. 检索
    results = filter_schedule(**params)
    # 3. 格式化检索结果文本
    search_result_text = format_results(results)
    # 4. 调用大模型生成最终回答
    system_prompt = "你是一个实验班车信息助手。请根据用户问题和检索到的班次信息，生成最简洁、准确、友好的中文回答，不要有太多思考的内容。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"用户问题: {user_input}\n\n检索结果: {search_result_text}"}
    ]
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1",
            messages=messages,
            max_tokens=150,
            temperature=0.3
        )
        answer = completion.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return f"调用大模型失败: {e}"

# 合体部分
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    if not user_input:
        return jsonify({'answer': '请输入问题。'})
    answer = get_answer(user_input)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)