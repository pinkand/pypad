"""
Seed the database from public/data/python-knowledge.json.
- Stores ai_summary, course_id, chapter_id, section_id on every KnowledgeNode
- Creates 11 Sections (one per chapter)
- Creates Practices for every knowledge node (3 per node)
- Infers tree parent_id / depth from prerequisite DAG
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, deque

from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import (
    KnowledgeNode, KnowledgeEdge,
    Course, Chapter, Section,
    Project, Practice,
    CodeReview, WorkspaceRun, SessionEventLog,
    LearningSession, UserMastery, StudyRecord,
)

# ── Category → chapter mapping ───────────────────────────────────────────────
CATEGORY_TO_CHAPTER = {
    "基础环境":   "chap-1",
    "基本语法":   "chap-2",
    "控制结构":   "chap-3",
    "数据结构":   "chap-4",   # strings / lists / tuples
    "函数设计":   "chap-6",
    "模块与架构": "chap-8",
    "面向对象":   "chap-9",
    "文件与数据": "chap-10",
    "健壮性":     "chap-11",
}

# Node → specific chapter overrides (dict/set belong to chap-7)
NODE_CHAPTER_OVERRIDE = {
    "dict-basic":    "chap-7",
    "dict-methods":  "chap-7",
    "set-basic":     "chap-7",
}

# ── Per-node practice definitions ─────────────────────────────────────────────
# Each entry: (id_suffix, title, difficulty, prompt, starter, solution, test_cases)
PRACTICES_BY_NODE: dict[str, list[dict]] = {
    "py-intro": [
        {
            "id": "prac-py-intro-1", "title": "查看Python版本", "difficulty": "easy",
            "prompt": "编写一段代码，使用 sys 模块打印当前 Python 版本号。",
            "starter": "import sys\n# TODO: 打印 Python 版本\n",
            "solution": "import sys\nprint(sys.version)\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
        {
            "id": "prac-py-intro-2", "title": "Hello Python", "difficulty": "easy",
            "prompt": "编写并运行你的第一个 Python 程序，打印 'Hello, Python!'。",
            "starter": "# TODO: 打印 Hello, Python!\n",
            "solution": "print('Hello, Python!')\n",
            "tests": [{"input": "", "expectedOutput": "Hello, Python!"}],
        },
    ],
    "py-syntax-spec": [
        {
            "id": "prac-syntax-1", "title": "PEP8 规范注释", "difficulty": "easy",
            "prompt": "为以下函数添加符合 PEP8 规范的单行注释和函数文档字符串。\n\ndef add(a, b):\n    return a + b",
            "starter": "def add(a, b):\n    # TODO: 添加文档字符串\n    return a + b\n",
            "solution": "def add(a, b):\n    \"\"\"返回两个数的和。\"\"\"\n    # 直接返回加法结果\n    return a + b\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
        {
            "id": "prac-syntax-2", "title": "命名规范练习", "difficulty": "easy",
            "prompt": "定义一个符合 snake_case 命名规范的函数 calculate_area，接受 width 和 height，返回面积。",
            "starter": "# TODO: 定义 calculate_area 函数\n",
            "solution": "def calculate_area(width, height):\n    return width * height\n",
            "tests": [{"input": "3\n4", "expectedOutput": "12"}],
        },
    ],
    "input-output": [
        {
            "id": "prac-input-1", "title": "基本输入输出体验", "difficulty": "easy",
            "prompt": "编写程序接收用户输入的姓名，并打印欢迎消息 'Hello, {name}!'",
            "starter": "def greet():\n    name = input()\n    # TODO: 打印欢迎语\n    pass\n",
            "solution": "def greet():\n    name = input()\n    print(f'Hello, {name}!')\n",
            "tests": [{"input": "Alice", "expectedOutput": "Hello, Alice!"}],
        },
        {
            "id": "prac-input-2", "title": "格式化输出", "difficulty": "easy",
            "prompt": "接收两个整数输入，计算它们的和，并以 '{a} + {b} = {result}' 格式输出。",
            "starter": "a = int(input())\nb = int(input())\n# TODO: 格式化输出\n",
            "solution": "a = int(input())\nb = int(input())\nprint(f'{a} + {b} = {a + b}')\n",
            "tests": [{"input": "3\n5", "expectedOutput": "3 + 5 = 8"}],
        },
        {
            "id": "prac-input-3", "title": "多行输出控制", "difficulty": "easy",
            "prompt": "使用 print 的 sep 和 end 参数，将 'A', 'B', 'C' 以逗号分隔输出在同一行（末尾无换行）。",
            "starter": "# TODO: 使用 sep 和 end 参数\n",
            "solution": "print('A', 'B', 'C', sep=',', end='')\n",
            "tests": [{"input": "", "expectedOutput": "A,B,C"}],
        },
    ],
    "vars-datatypes": [
        {
            "id": "prac-vars-1", "title": "类型转换", "difficulty": "easy",
            "prompt": "接收一个字符串类型的整数，将其转换为 int，乘以 2 后输出。",
            "starter": "s = input()\n# TODO: 转换并计算\n",
            "solution": "s = input()\nprint(int(s) * 2)\n",
            "tests": [{"input": "7", "expectedOutput": "14"}],
        },
        {
            "id": "prac-vars-2", "title": "变量交换", "difficulty": "easy",
            "prompt": "使用 Python 的多重赋值特性，交换变量 a 和 b 的值并输出。",
            "starter": "a = int(input())\nb = int(input())\n# TODO: 交换 a, b\nprint(a, b)\n",
            "solution": "a = int(input())\nb = int(input())\na, b = b, a\nprint(a, b)\n",
            "tests": [{"input": "3\n7", "expectedOutput": "7 3"}],
        },
    ],
    "operators-expressions": [
        {
            "id": "prac-ops-1", "title": "整除与取模", "difficulty": "easy",
            "prompt": "接收两个整数 a, b，输出 a // b 和 a % b。",
            "starter": "a = int(input())\nb = int(input())\n# TODO: 整除和取模\n",
            "solution": "a = int(input())\nb = int(input())\nprint(a // b)\nprint(a % b)\n",
            "tests": [{"input": "17\n5", "expectedOutput": "3\n2"}],
        },
        {
            "id": "prac-ops-2", "title": "幂运算", "difficulty": "easy",
            "prompt": "接收底数 base 和指数 exp，输出 base ** exp 的结果。",
            "starter": "base = int(input())\nexp = int(input())\n# TODO: 幂运算\n",
            "solution": "base = int(input())\nexp = int(input())\nprint(base ** exp)\n",
            "tests": [{"input": "2\n10", "expectedOutput": "1024"}],
        },
    ],
    "conditionals": [
        {
            "id": "prac-conditionals-1", "title": "成绩等级判断", "difficulty": "easy",
            "prompt": "编写函数 judge_score(score)，根据分数返回 'A'(>=90), 'B'(>=80), 'C'(>=60), 'D'(<60)。",
            "starter": "def judge_score(score):\n    # TODO: 判断成绩等级\n    pass\n",
            "solution": "def judge_score(score):\n    if score >= 90:\n        return 'A'\n    elif score >= 80:\n        return 'B'\n    elif score >= 60:\n        return 'C'\n    else:\n        return 'D'\n",
            "tests": [{"input": "85", "expectedOutput": "B"}],
        },
        {
            "id": "prac-conditionals-2", "title": "BMI 分类", "difficulty": "easy",
            "prompt": "编写 bmi_category(bmi) 函数：bmi<18.5 返回'偏瘦'，18.5<=bmi<24 返回'正常'，>=24 返回'偏胖'。",
            "starter": "def bmi_category(bmi):\n    # TODO: BMI 分类\n    pass\n",
            "solution": "def bmi_category(bmi):\n    if bmi < 18.5:\n        return '偏瘦'\n    elif bmi < 24:\n        return '正常'\n    else:\n        return '偏胖'\n",
            "tests": [{"input": "22.0", "expectedOutput": "正常"}],
        },
        {
            "id": "prac-conditionals-3", "title": "闰年判断", "difficulty": "medium",
            "prompt": "编写 is_leap(year) 函数，判断是否为闰年，返回 True 或 False。",
            "starter": "def is_leap(year):\n    # TODO: 闰年判断\n    pass\n",
            "solution": "def is_leap(year):\n    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)\n",
            "tests": [{"input": "2024", "expectedOutput": "True"}],
        },
    ],
    "loops": [
        {
            "id": "prac-loops-1", "title": "累加求和", "difficulty": "easy",
            "prompt": "接收整数 n，使用 for 循环计算 1+2+...+n 的值并输出。",
            "starter": "n = int(input())\n# TODO: 累加求和\n",
            "solution": "n = int(input())\nprint(sum(range(1, n + 1)))\n",
            "tests": [{"input": "10", "expectedOutput": "55"}],
        },
        {
            "id": "prac-loops-2", "title": "九九乘法表", "difficulty": "medium",
            "prompt": "使用嵌套 for 循环打印 9×9 乘法表，每行以制表符分隔。",
            "starter": "# TODO: 打印乘法表\n",
            "solution": "for i in range(1, 10):\n    row = [f'{j}x{i}={i*j}' for j in range(1, i + 1)]\n    print('\\t'.join(row))\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
        {
            "id": "prac-loops-3", "title": "猜数字游戏逻辑", "difficulty": "medium",
            "prompt": "接收目标数 target 和一次猜测 guess，输出 '偏大'、'偏小' 或 '正确'。",
            "starter": "target = int(input())\nguess = int(input())\n# TODO: 判断输出\n",
            "solution": "target = int(input())\nguess = int(input())\nif guess > target:\n    print('偏大')\nelif guess < target:\n    print('偏小')\nelse:\n    print('正确')\n",
            "tests": [{"input": "50\n30", "expectedOutput": "偏小"}],
        },
    ],
    "control-flow-extra": [
        {
            "id": "prac-flow-1", "title": "break 提前退出", "difficulty": "easy",
            "prompt": "接收整数列表（空行结束），找到第一个负数后立即输出并停止。",
            "starter": "nums = list(map(int, input().split()))\n# TODO: 找第一个负数\n",
            "solution": "nums = list(map(int, input().split()))\nfor n in nums:\n    if n < 0:\n        print(n)\n        break\n",
            "tests": [{"input": "3 5 -2 8 -1", "expectedOutput": "-2"}],
        },
        {
            "id": "prac-flow-2", "title": "continue 跳过", "difficulty": "easy",
            "prompt": "接收整数 n，使用 continue 打印 1~n 中所有奇数（每行一个）。",
            "starter": "n = int(input())\n# TODO: 打印奇数\n",
            "solution": "n = int(input())\nfor i in range(1, n + 1):\n    if i % 2 == 0:\n        continue\n    print(i)\n",
            "tests": [{"input": "7", "expectedOutput": "1\n3\n5\n7"}],
        },
    ],
    "strings-basic": [
        {
            "id": "prac-str-1", "title": "字符串拼接", "difficulty": "easy",
            "prompt": "接收姓和名，用空格拼接后输出全名。",
            "starter": "first = input()\nlast = input()\n# TODO: 拼接并输出\n",
            "solution": "first = input()\nlast = input()\nprint(first + ' ' + last)\n",
            "tests": [{"input": "Zhang\nWei", "expectedOutput": "Zhang Wei"}],
        },
        {
            "id": "prac-str-2", "title": "字符串长度与索引", "difficulty": "easy",
            "prompt": "接收字符串，输出其长度和最后一个字符。",
            "starter": "s = input()\n# TODO: 输出长度和最后一个字符\n",
            "solution": "s = input()\nprint(len(s))\nprint(s[-1])\n",
            "tests": [{"input": "hello", "expectedOutput": "5\no"}],
        },
    ],
    "strings-slicing": [
        {
            "id": "prac-slice-1", "title": "字符串逆序", "difficulty": "easy",
            "prompt": "接收字符串，使用切片将其逆序输出。",
            "starter": "s = input()\n# TODO: 逆序输出\n",
            "solution": "s = input()\nprint(s[::-1])\n",
            "tests": [{"input": "python", "expectedOutput": "nohtyp"}],
        },
        {
            "id": "prac-slice-2", "title": "提取子字符串", "difficulty": "easy",
            "prompt": "接收字符串和起止索引 start, end，输出 s[start:end] 的结果。",
            "starter": "s = input()\nstart, end = map(int, input().split())\n# TODO: 切片输出\n",
            "solution": "s = input()\nstart, end = map(int, input().split())\nprint(s[start:end])\n",
            "tests": [{"input": "helloworld\n0 5", "expectedOutput": "hello"}],
        },
    ],
    "strings-methods": [
        {
            "id": "prac-strm-1", "title": "大小写转换", "difficulty": "easy",
            "prompt": "接收字符串，分别输出其大写和小写形式。",
            "starter": "s = input()\n# TODO: 大写和小写\n",
            "solution": "s = input()\nprint(s.upper())\nprint(s.lower())\n",
            "tests": [{"input": "Hello", "expectedOutput": "HELLO\nhello"}],
        },
        {
            "id": "prac-strm-2", "title": "词语搜索", "difficulty": "medium",
            "prompt": "接收文本和关键词，输出关键词在文本中出现的次数。",
            "starter": "text = input()\nword = input()\n# TODO: 统计出现次数\n",
            "solution": "text = input()\nword = input()\nprint(text.count(word))\n",
            "tests": [{"input": "banana\nan", "expectedOutput": "2"}],
        },
    ],
    "lists-basic": [
        {
            "id": "prac-list-1", "title": "列表最大最小值", "difficulty": "easy",
            "prompt": "接收空格分隔的整数序列，输出最大值和最小值。",
            "starter": "nums = list(map(int, input().split()))\n# TODO: 输出最大值和最小值\n",
            "solution": "nums = list(map(int, input().split()))\nprint(max(nums))\nprint(min(nums))\n",
            "tests": [{"input": "3 1 4 1 5 9 2 6", "expectedOutput": "9\n1"}],
        },
        {
            "id": "prac-list-2", "title": "列表去重", "difficulty": "easy",
            "prompt": "接收整数列表，去除重复元素后按原顺序输出（空格分隔）。",
            "starter": "nums = list(map(int, input().split()))\n# TODO: 去重并保持顺序\n",
            "solution": "nums = list(map(int, input().split()))\nseen = []\nfor n in nums:\n    if n not in seen:\n        seen.append(n)\nprint(*seen)\n",
            "tests": [{"input": "1 2 3 2 1 4", "expectedOutput": "1 2 3 4"}],
        },
    ],
    "lists-operations": [
        {
            "id": "prac-listop-1", "title": "列表排序", "difficulty": "easy",
            "prompt": "接收整数列表，分别输出升序和降序排列结果（空格分隔）。",
            "starter": "nums = list(map(int, input().split()))\n# TODO: 升序和降序\n",
            "solution": "nums = list(map(int, input().split()))\nprint(*sorted(nums))\nprint(*sorted(nums, reverse=True))\n",
            "tests": [{"input": "5 2 8 1 9", "expectedOutput": "1 2 5 8 9\n9 8 5 2 1"}],
        },
        {
            "id": "prac-listop-2", "title": "列表推导式", "difficulty": "medium",
            "prompt": "接收整数 n，用列表推导式生成 [1², 2², ..., n²] 并输出（空格分隔）。",
            "starter": "n = int(input())\n# TODO: 列表推导式\n",
            "solution": "n = int(input())\nprint(*[i**2 for i in range(1, n + 1)])\n",
            "tests": [{"input": "5", "expectedOutput": "1 4 9 16 25"}],
        },
    ],
    "tuples-basic": [
        {
            "id": "prac-tuple-1", "title": "元组解包", "difficulty": "easy",
            "prompt": "创建元组 (1, 2, 3)，使用解包赋值给 a, b, c，分别输出三个变量。",
            "starter": "t = (1, 2, 3)\n# TODO: 解包并输出\n",
            "solution": "t = (1, 2, 3)\na, b, c = t\nprint(a)\nprint(b)\nprint(c)\n",
            "tests": [{"input": "", "expectedOutput": "1\n2\n3"}],
        },
        {
            "id": "prac-tuple-2", "title": "不可变性验证", "difficulty": "easy",
            "prompt": "尝试修改元组元素，捕获 TypeError，并打印 'tuple is immutable'。",
            "starter": "t = (1, 2, 3)\ntry:\n    # TODO: 尝试修改元素\n    pass\nexcept TypeError:\n    print('tuple is immutable')\n",
            "solution": "t = (1, 2, 3)\ntry:\n    t[0] = 99\nexcept TypeError:\n    print('tuple is immutable')\n",
            "tests": [{"input": "", "expectedOutput": "tuple is immutable"}],
        },
    ],
    "functions-def": [
        {
            "id": "prac-func-1", "title": "偶数和函数", "difficulty": "medium",
            "prompt": "编写函数 sum_even_numbers(n)，计算 1 到 n 之间所有偶数的和。",
            "starter": "def sum_even_numbers(n):\n    # TODO: 计算偶数和\n    pass\n",
            "solution": "def sum_even_numbers(n):\n    return sum(i for i in range(1, n + 1) if i % 2 == 0)\n",
            "tests": [{"input": "10", "expectedOutput": "30"}],
        },
        {
            "id": "prac-func-2", "title": "阶乘递归", "difficulty": "medium",
            "prompt": "编写递归函数 factorial(n)，返回 n 的阶乘（n >= 0）。",
            "starter": "def factorial(n):\n    # TODO: 递归计算阶乘\n    pass\n",
            "solution": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n",
            "tests": [{"input": "5", "expectedOutput": "120"}],
        },
        {
            "id": "prac-func-3", "title": "温度转换函数", "difficulty": "easy",
            "prompt": "编写 celsius_to_fahrenheit(c) 函数，公式：F = C * 9/5 + 32，保留1位小数。",
            "starter": "def celsius_to_fahrenheit(c):\n    # TODO: 摄氏转华氏\n    pass\n",
            "solution": "def celsius_to_fahrenheit(c):\n    return round(c * 9 / 5 + 32, 1)\n",
            "tests": [{"input": "100", "expectedOutput": "212.0"}],
        },
    ],
    "func-params-return": [
        {
            "id": "prac-param-1", "title": "默认参数", "difficulty": "easy",
            "prompt": "编写 greet(name, greeting='你好') 函数，接收姓名与问候语（有默认值），输出 '{greeting}, {name}!'。",
            "starter": "def greet(name, greeting='你好'):\n    # TODO: 格式化输出\n    pass\n",
            "solution": "def greet(name, greeting='你好'):\n    print(f'{greeting}, {name}!')\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
        {
            "id": "prac-param-2", "title": "可变参数求和", "difficulty": "medium",
            "prompt": "编写 total(*args) 函数，接受任意个数整数并返回它们的总和。",
            "starter": "def total(*args):\n    # TODO: 求和\n    pass\n",
            "solution": "def total(*args):\n    return sum(args)\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
    ],
    "func-scope": [
        {
            "id": "prac-scope-1", "title": "global 关键字", "difficulty": "medium",
            "prompt": "定义全局变量 count=0，编写函数 increment() 使用 global 将 count 加 1，调用三次后输出 count。",
            "starter": "count = 0\ndef increment():\n    # TODO: 使用 global\n    pass\n\nincrement()\nincrement()\nincrement()\nprint(count)\n",
            "solution": "count = 0\ndef increment():\n    global count\n    count += 1\n\nincrement()\nincrement()\nincrement()\nprint(count)\n",
            "tests": [{"input": "", "expectedOutput": "3"}],
        },
    ],
    "func-advanced": [
        {
            "id": "prac-adv-1", "title": "lambda 排序", "difficulty": "medium",
            "prompt": "给定列表 words=['banana','apple','cherry']，使用 lambda 按字符串长度排序并输出。",
            "starter": "words = ['banana', 'apple', 'cherry']\n# TODO: 按长度排序\n",
            "solution": "words = ['banana', 'apple', 'cherry']\nwords.sort(key=lambda x: len(x))\nprint(words)\n",
            "tests": [{"input": "", "expectedOutput": "['apple', 'banana', 'cherry']"}],
        },
        {
            "id": "prac-adv-2", "title": "map 与 filter", "difficulty": "medium",
            "prompt": "接收整数列表，先过滤出偶数，再将每个偶数乘以 2，输出结果列表。",
            "starter": "nums = list(map(int, input().split()))\n# TODO: filter 偶数再 map 乘2\n",
            "solution": "nums = list(map(int, input().split()))\nresult = list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, nums)))\nprint(result)\n",
            "tests": [{"input": "1 2 3 4 5 6", "expectedOutput": "[4, 8, 12]"}],
        },
    ],
    "dict-basic": [
        {
            "id": "prac-dict-1", "title": "字典词频统计", "difficulty": "medium",
            "prompt": "编写函数 count_words(word_list)，返回列表中每个单词出现次数的字典。",
            "starter": "def count_words(word_list):\n    # TODO: 统计词频\n    pass\n",
            "solution": "def count_words(word_list):\n    res = {}\n    for w in word_list:\n        res[w] = res.get(w, 0) + 1\n    return res\n",
            "tests": [{"input": "['apple', 'banana', 'apple']", "expectedOutput": "{'apple': 2, 'banana': 1}"}],
        },
        {
            "id": "prac-dict-2", "title": "字典查找与默认值", "difficulty": "easy",
            "prompt": "给定字典 scores={'Alice':90,'Bob':80}，安全获取键 'Charlie' 的值，不存在时返回 0 并输出。",
            "starter": "scores = {'Alice': 90, 'Bob': 80}\n# TODO: 安全获取 Charlie 的分数\n",
            "solution": "scores = {'Alice': 90, 'Bob': 80}\nprint(scores.get('Charlie', 0))\n",
            "tests": [{"input": "", "expectedOutput": "0"}],
        },
    ],
    "dict-methods": [
        {
            "id": "prac-dictm-1", "title": "字典推导式", "difficulty": "medium",
            "prompt": "将列表 ['a','b','c'] 转为字典 {'a':1,'b':2,'c':3}（值为索引+1），使用字典推导式。",
            "starter": "keys = ['a', 'b', 'c']\n# TODO: 字典推导式\n",
            "solution": "keys = ['a', 'b', 'c']\nresult = {k: i + 1 for i, k in enumerate(keys)}\nprint(result)\n",
            "tests": [{"input": "", "expectedOutput": "{'a': 1, 'b': 2, 'c': 3}"}],
        },
    ],
    "set-basic": [
        {
            "id": "prac-set-1", "title": "集合去重", "difficulty": "easy",
            "prompt": "接收整数列表，用集合去重后输出元素个数。",
            "starter": "nums = list(map(int, input().split()))\n# TODO: 集合去重并输出个数\n",
            "solution": "nums = list(map(int, input().split()))\nprint(len(set(nums)))\n",
            "tests": [{"input": "1 2 3 2 1 4 5", "expectedOutput": "5"}],
        },
        {
            "id": "prac-set-2", "title": "集合交并差", "difficulty": "medium",
            "prompt": "接收两行整数（集合 A 和集合 B），分别输出交集、并集、差集（A-B）。",
            "starter": "a = set(map(int, input().split()))\nb = set(map(int, input().split()))\n# TODO: 输出交集、并集、差集\n",
            "solution": "a = set(map(int, input().split()))\nb = set(map(int, input().split()))\nprint(sorted(a & b))\nprint(sorted(a | b))\nprint(sorted(a - b))\n",
            "tests": [{"input": "1 2 3 4\n3 4 5 6", "expectedOutput": "[3, 4]\n[1, 2, 3, 4, 5, 6]\n[1, 2]"}],
        },
    ],
    "modules-import": [
        {
            "id": "prac-mod-1", "title": "导入 math 模块", "difficulty": "easy",
            "prompt": "导入 math 模块，接收整数 n，输出 math.sqrt(n) 和 math.factorial(n)。",
            "starter": "import math\nn = int(input())\n# TODO: 输出平方根和阶乘\n",
            "solution": "import math\nn = int(input())\nprint(round(math.sqrt(n), 4))\nprint(math.factorial(n))\n",
            "tests": [{"input": "5", "expectedOutput": "2.2361\n120"}],
        },
    ],
    "stdlib-sys": [
        {
            "id": "prac-sys-1", "title": "sys.argv 读取", "difficulty": "easy",
            "prompt": "使用 sys 模块输出 Python 版本的主版本号（major）和次版本号（minor）。",
            "starter": "import sys\n# TODO: 输出主版本号和次版本号\n",
            "solution": "import sys\nprint(sys.version_info.major)\nprint(sys.version_info.minor)\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
    ],
    "packages-custom": [
        {
            "id": "prac-pkg-1", "title": "自定义模块", "difficulty": "medium",
            "prompt": "假设有模块 mathtools.py 包含 add(a,b) 函数，编写导入并调用它的代码框架（注释说明）。",
            "starter": "# TODO: 展示如何 import 自定义模块中的函数\n# from mathtools import add\n# print(add(3, 4))\nprint('模块导入示例')\n",
            "solution": "# from mathtools import add\n# print(add(3, 4))\nprint('模块导入示例')\n",
            "tests": [{"input": "", "expectedOutput": "模块导入示例"}],
        },
    ],
    "oop-concepts": [
        {
            "id": "prac-oop-1", "title": "Dog 类创建", "difficulty": "hard",
            "prompt": "创建 Dog 类，拥有 name 与 age 属性，以及 bark() 方法返回 '{name} says Woof!'",
            "starter": "class Dog:\n    # TODO: 实现 Dog 类\n    pass\n",
            "solution": "class Dog:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    def bark(self):\n        return f'{self.name} says Woof!'\n",
            "tests": [{"input": "Buddy, 3", "expectedOutput": "Buddy says Woof!"}],
        },
        {
            "id": "prac-oop-2", "title": "类的基本属性", "difficulty": "medium",
            "prompt": "创建 Circle 类，接受 radius，提供 area() 方法返回面积（π取3.14159，保留2位小数）。",
            "starter": "class Circle:\n    def __init__(self, radius):\n        self.radius = radius\n    def area(self):\n        # TODO: 计算面积\n        pass\n",
            "solution": "class Circle:\n    def __init__(self, radius):\n        self.radius = radius\n    def area(self):\n        return round(3.14159 * self.radius ** 2, 2)\n",
            "tests": [{"input": "5", "expectedOutput": "78.54"}],
        },
    ],
    "class-attributes-methods": [
        {
            "id": "prac-attr-1", "title": "类方法与实例方法", "difficulty": "medium",
            "prompt": "创建 Counter 类，有类变量 count=0，每次实例化时 count+1，提供类方法 get_count() 返回 count。",
            "starter": "class Counter:\n    count = 0\n    def __init__(self):\n        # TODO: 实例化时增加 count\n        pass\n    @classmethod\n    def get_count(cls):\n        # TODO: 返回 count\n        pass\n",
            "solution": "class Counter:\n    count = 0\n    def __init__(self):\n        Counter.count += 1\n    @classmethod\n    def get_count(cls):\n        return cls.count\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
    ],
    "encapsulation-access": [
        {
            "id": "prac-encap-1", "title": "私有属性与 getter", "difficulty": "medium",
            "prompt": "创建 BankAccount 类，私有属性 __balance，提供 deposit(amount)、withdraw(amount) 方法和 balance 属性（property）。",
            "starter": "class BankAccount:\n    def __init__(self):\n        self.__balance = 0\n    def deposit(self, amount):\n        # TODO: 存款\n        pass\n    def withdraw(self, amount):\n        # TODO: 取款，余额不足返回 False\n        pass\n    @property\n    def balance(self):\n        # TODO: 返回余额\n        pass\n",
            "solution": "class BankAccount:\n    def __init__(self):\n        self.__balance = 0\n    def deposit(self, amount):\n        self.__balance += amount\n    def withdraw(self, amount):\n        if amount > self.__balance:\n            return False\n        self.__balance -= amount\n        return True\n    @property\n    def balance(self):\n        return self.__balance\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
    ],
    "inheritance-polymorphism": [
        {
            "id": "prac-inherit-1", "title": "继承与重写", "difficulty": "hard",
            "prompt": "定义基类 Animal，有 speak() 方法返回 'Some sound'。子类 Cat 重写 speak() 返回 'Meow'。",
            "starter": "class Animal:\n    def speak(self):\n        return 'Some sound'\n\nclass Cat(Animal):\n    def speak(self):\n        # TODO: 重写 speak\n        pass\n",
            "solution": "class Animal:\n    def speak(self):\n        return 'Some sound'\n\nclass Cat(Animal):\n    def speak(self):\n        return 'Meow'\n",
            "tests": [{"input": "", "expectedOutput": "Meow"}],
        },
    ],
    "file-open-close": [
        {
            "id": "prac-file-1", "title": "文件读取", "difficulty": "medium",
            "prompt": "使用 with open 读取文件 'data.txt' 的内容并打印（假设文件已存在，演示代码结构即可）。",
            "starter": "# TODO: 使用 with open 读取文件\nprint('文件读取示例')\n",
            "solution": "# with open('data.txt', 'r', encoding='utf-8') as f:\n#     content = f.read()\n#     print(content)\nprint('文件读取示例')\n",
            "tests": [{"input": "", "expectedOutput": "文件读取示例"}],
        },
    ],
    "file-read-write": [
        {
            "id": "prac-rw-1", "title": "文件写入", "difficulty": "medium",
            "prompt": "接收多行输入直到空行，将内容写入 output.txt，每行一条，最后打印写入行数。",
            "starter": "lines = []\nwhile True:\n    line = input()\n    if not line:\n        break\n    lines.append(line)\n# TODO: 写入文件并输出行数\nprint(len(lines))\n",
            "solution": "lines = []\nwhile True:\n    line = input()\n    if not line:\n        break\n    lines.append(line)\nwith open('output.txt', 'w', encoding='utf-8') as f:\n    for l in lines:\n        f.write(l + '\\n')\nprint(len(lines))\n",
            "tests": [{"input": "hello\nworld\n", "expectedOutput": "2"}],
        },
    ],
    "file-os-ops": [
        {
            "id": "prac-os-1", "title": "路径操作", "difficulty": "medium",
            "prompt": "使用 os.path 模块，检测当前目录下是否存在 'test.txt'，输出 True 或 False。",
            "starter": "import os\n# TODO: 检测文件是否存在\n",
            "solution": "import os\nprint(os.path.exists('test.txt'))\n",
            "tests": [{"input": "", "expectedOutput": "False"}],
        },
    ],
    "exceptions-try": [
        {
            "id": "prac-exc-1", "title": "除零保护", "difficulty": "easy",
            "prompt": "接收两个整数 a, b，捕获除零异常，正常时输出商，异常时输出 '除数不能为零'。",
            "starter": "a = int(input())\nb = int(input())\ntry:\n    # TODO: 计算并输出\n    pass\nexcept ZeroDivisionError:\n    print('除数不能为零')\n",
            "solution": "a = int(input())\nb = int(input())\ntry:\n    print(a // b)\nexcept ZeroDivisionError:\n    print('除数不能为零')\n",
            "tests": [{"input": "10\n0", "expectedOutput": "除数不能为零"}],
        },
        {
            "id": "prac-exc-2", "title": "多异常捕获", "difficulty": "medium",
            "prompt": "接收字符串，尝试转为整数。捕获 ValueError 输出'类型错误'，IndexError 输出'索引错误'。",
            "starter": "s = input()\ntry:\n    # TODO: 转换并处理异常\n    pass\nexcept ValueError:\n    print('类型错误')\nexcept IndexError:\n    print('索引错误')\n",
            "solution": "s = input()\ntry:\n    print(int(s))\nexcept ValueError:\n    print('类型错误')\nexcept IndexError:\n    print('索引错误')\n",
            "tests": [{"input": "abc", "expectedOutput": "类型错误"}],
        },
    ],
    "exceptions-raise": [
        {
            "id": "prac-raise-1", "title": "自定义异常", "difficulty": "hard",
            "prompt": "定义 NegativeNumberError 异常类，编写 check_positive(n) 函数，n<0 时 raise 该异常，否则返回 n。",
            "starter": "class NegativeNumberError(Exception):\n    pass\n\ndef check_positive(n):\n    # TODO: 检查并 raise\n    pass\n",
            "solution": "class NegativeNumberError(Exception):\n    pass\n\ndef check_positive(n):\n    if n < 0:\n        raise NegativeNumberError(f'{n} is negative')\n    return n\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
    ],
    "exceptions-assert-trace": [
        {
            "id": "prac-assert-1", "title": "断言测试", "difficulty": "medium",
            "prompt": "编写函数 divide(a, b)，使用 assert 断言 b != 0，然后返回 a / b。",
            "starter": "def divide(a, b):\n    # TODO: assert b != 0 然后返回结果\n    pass\n",
            "solution": "def divide(a, b):\n    assert b != 0, '除数不能为零'\n    return a / b\n",
            "tests": [{"input": "", "expectedOutput": ""}],
        },
    ],
}


def load_json() -> dict:
    json_path = Path(__file__).parent.parent / "pypad-frontend" / "public" / "data" / "python-knowledge.json"
    if not json_path.exists():
        json_path = Path(__file__).parent.parent / "public" / "data" / "python-knowledge.json"
    if not json_path.exists():
        print(f"ERROR: {json_path} not found.")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def infer_tree(nodes_data: list, edges_data: list) -> dict:
    """
    Infer a tree structure from the prerequisite DAG.
    Returns: { node_id: { parent_id, depth, sort_order } }
    """
    prereqs = defaultdict(list)
    for edge in edges_data:
        prereqs[edge["target"]].append((edge["source"], edge.get("strength", "soft")))

    node_ids = {n["id"] for n in nodes_data}
    tree_info: dict = {}

    roots = [n["id"] for n in nodes_data if not n.get("prerequisites")]
    visited: set = set()
    queue: deque = deque()

    for root_id in roots:
        tree_info[root_id] = {"parent_id": None, "depth": 0, "sort_order": 0}
        visited.add(root_id)
        queue.append(root_id)

    children_map: dict = defaultdict(list)
    for edge in edges_data:
        children_map[edge["source"]].append(edge["target"])

    while queue:
        current = queue.popleft()
        current_depth = tree_info[current]["depth"]
        sort_idx = 0
        for child_id in children_map[current]:
            if child_id in visited or child_id not in node_ids:
                continue
            child_prereqs = prereqs.get(child_id, [])
            hard_prereqs = [p for p, s in child_prereqs if s == "hard"]
            primary_parent = hard_prereqs[0] if hard_prereqs else (
                child_prereqs[0][0] if child_prereqs else current
            )
            if primary_parent == current:
                tree_info[child_id] = {
                    "parent_id": current,
                    "depth": current_depth + 1,
                    "sort_order": sort_idx,
                }
                sort_idx += 1
                visited.add(child_id)
                queue.append(child_id)

    # Handle orphans
    for n in nodes_data:
        if n["id"] not in tree_info:
            prereq_list = n.get("prerequisites", [])
            parent = next((p for p in prereq_list if p in tree_info), None)
            depth = (tree_info[parent]["depth"] + 1) if parent else 0
            tree_info[n["id"]] = {"parent_id": parent, "depth": depth, "sort_order": 99}

    return tree_info


def seed():
    """Main seed function."""
    print("Creating tables...")
    create_db_and_tables()

    data = load_json()
    nodes_data = data.get("nodes", [])
    edges_data  = data.get("edges", [])

    print(f"Loaded {len(nodes_data)} nodes and {len(edges_data)} edges from JSON.")

    tree_info = infer_tree(nodes_data, edges_data)

    with Session(engine) as session:
        # ── Guard / Force-clear ───────────────────────────────────────────────
        existing = session.exec(select(KnowledgeNode)).first()
        if existing and "--force" not in sys.argv:
            print("Database already seeded. Use --force to re-seed.")
            return

        if "--force" in sys.argv:
            print("Clearing existing data (FK order)...")
            for cls in [CodeReview, WorkspaceRun, SessionEventLog, LearningSession,
                        Practice, Project, UserMastery, StudyRecord, KnowledgeEdge]:
                for item in session.exec(select(cls)).all():
                    session.delete(item)
            session.commit()
            for cls in [KnowledgeNode, Section, Chapter, Course]:
                for item in session.exec(select(cls)).all():
                    session.delete(item)
            session.commit()
            print("Cleared.")

        # ── 1. Course ─────────────────────────────────────────────────────────
        course = Course(
            id="py-course-1",
            title="Python 程序设计项目化教程",
            description="清华大学出版社出版 · 11大项目驱动全流程学习 (基础语法、数据结构、OOP、文件IO与AI编程)",
            level="beginner", category="Python项目化", sort_order=1,
        )
        session.add(course)
        session.commit()
        print("Inserted course.")

        # ── 2. Chapters ───────────────────────────────────────────────────────
        chapters_list = [
            Chapter(id="chap-1",  course_id="py-course-1", title="项目1：猜价赢大奖",          description="Python开发环境搭建与编程规范",          sort_order=1),
            Chapter(id="chap-2",  course_id="py-course-1", title="项目2：简单计算器",           description="基本输入输出、数据类型与运算符",           sort_order=2),
            Chapter(id="chap-3",  course_id="py-course-1", title="项目3：健康数据分析",         description="条件分支与循环控制流结构",                sort_order=3),
            Chapter(id="chap-4",  course_id="py-course-1", title="项目4：词语踪迹寻觅",         description="字符串处理、检索与切片操作",               sort_order=4),
            Chapter(id="chap-5",  course_id="py-course-1", title="项目5：核心价值观问答挑战",    description="列表与元组容器数据结构",                 sort_order=5),
            Chapter(id="chap-6",  course_id="py-course-1", title="项目6：公益图书角管理系统",    description="函数定义、参数传递与模块化设计",            sort_order=6),
            Chapter(id="chap-7",  course_id="py-course-1", title="项目7：校园热点话题统计",      description="字典与集合的高效查找与统计",               sort_order=7),
            Chapter(id="chap-8",  course_id="py-course-1", title="项目8：天气预报应用程序",      description="模块化开发、内置标准库与第三方包",           sort_order=8),
            Chapter(id="chap-9",  course_id="py-course-1", title="项目9：个人财务管理系统",      description="面向对象编程 (OOP) 核心理念",             sort_order=9),
            Chapter(id="chap-10", course_id="py-course-1", title="项目10：销售数据分析",        description="文件 I/O 操作与数据持久化存储",            sort_order=10),
            Chapter(id="chap-11", course_id="py-course-1", title="项目11：居民肺活量监测",       description="异常捕获处理与程序健壮性设计",             sort_order=11),
        ]
        for ch in chapters_list:
            session.add(ch)
        session.commit()
        print(f"Inserted {len(chapters_list)} chapters.")

        # ── 3. Sections (one per chapter) ─────────────────────────────────────
        sections_list = [
            Section(id="sec-1",  chapter_id="chap-1",  title="Python 简介与环境搭建",    content_type="text", estimated_minutes=30, sort_order=1),
            Section(id="sec-2",  chapter_id="chap-2",  title="基本输入输出与数据类型",     content_type="text", estimated_minutes=40, sort_order=1),
            Section(id="sec-3",  chapter_id="chap-3",  title="条件分支与循环结构",        content_type="text", estimated_minutes=45, sort_order=1),
            Section(id="sec-4",  chapter_id="chap-4",  title="字符串与序列操作",         content_type="text", estimated_minutes=50, sort_order=1),
            Section(id="sec-5",  chapter_id="chap-5",  title="列表与元组数据结构",        content_type="text", estimated_minutes=45, sort_order=1),
            Section(id="sec-6",  chapter_id="chap-6",  title="函数定义与参数传递",        content_type="text", estimated_minutes=50, sort_order=1),
            Section(id="sec-7",  chapter_id="chap-7",  title="字典与集合统计分析",        content_type="text", estimated_minutes=50, sort_order=1),
            Section(id="sec-8",  chapter_id="chap-8",  title="模块导入与标准库使用",      content_type="text", estimated_minutes=45, sort_order=1),
            Section(id="sec-9",  chapter_id="chap-9",  title="面向对象编程核心",         content_type="text", estimated_minutes=60, sort_order=1),
            Section(id="sec-10", chapter_id="chap-10", title="文件读写与数据持久化",      content_type="text", estimated_minutes=50, sort_order=1),
            Section(id="sec-11", chapter_id="chap-11", title="异常处理与程序健壮性",      content_type="text", estimated_minutes=45, sort_order=1),
        ]
        # section_id lookup: chap-id → sec-id
        chap_to_sec = {s.chapter_id: s.id for s in sections_list}
        for sec in sections_list:
            session.add(sec)
        session.commit()
        print(f"Inserted {len(sections_list)} sections.")

        # ── 4. KnowledgeNodes (with ai_summary, course_id, chapter_id, section_id) ──
        for n in nodes_data:
            info = tree_info.get(n["id"], {"parent_id": None, "depth": 0, "sort_order": 0})
            category = n.get("category", "")

            # Determine chapter_id
            chap_id = NODE_CHAPTER_OVERRIDE.get(n["id"]) or CATEGORY_TO_CHAPTER.get(category)
            sec_id  = chap_to_sec.get(chap_id) if chap_id else None

            node = KnowledgeNode(
                id=n["id"],
                name=n["name"],
                description=n.get("description", ""),
                category=category,
                importance=n.get("importance", 5),
                parent_id=info["parent_id"],
                depth=info["depth"],
                sort_order=info["sort_order"],
                # ✅ Now stored correctly
                ai_summary=n.get("aiSummary"),
                course_id="py-course-1",
                chapter_id=chap_id,
                section_id=sec_id,
            )
            session.add(node)

        session.commit()
        print(f"Inserted {len(nodes_data)} knowledge nodes (with ai_summary, course/chapter/section links).")

        # ── 5. KnowledgeEdges ─────────────────────────────────────────────────
        edge_count = 0
        for edge in edges_data:
            if not session.get(KnowledgeNode, edge["source"]) or \
               not session.get(KnowledgeNode, edge["target"]):
                print(f"  Skipping edge {edge['source']} -> {edge['target']} (missing node)")
                continue
            strength = edge.get("strength", "soft")
            session.add(KnowledgeEdge(
                source_id=edge["source"],
                target_id=edge["target"],
                relation_type=edge.get("relationType", "prerequisite"),
                strength=strength,
                weight=1.0 if strength == "hard" else 0.5,
            ))
            edge_count += 1
        session.commit()
        print(f"Inserted {edge_count} edges.")

        # ── 6. Projects ───────────────────────────────────────────────────────
        projects_list = [
            Project(
                id="proj-calc-2", title="简单计算器开发",
                description="实现包含加、减、乘、除运算及格式化结果输出的简单计算器",
                difficulty="easy", estimated_hours=2,
                init_code="def calculator(a, b, op):\n    # TODO: 实现计算器逻辑\n    pass\n",
                readme_markdown="# 简单计算器开发项目\n\n## 目标\n实现支持 +、-、*、/ 四种运算的命令行计算器。\n\n## 输入格式\n两个操作数和运算符\n\n## 示例\n```python\ncalculator(10, 5, '+')  # 返回 15\ncalculator(10, 0, '/')  # 应处理除零异常\n```\n",
                test_cases=[{"input": "3, 5, '+'", "expectedOutput": "8", "isHidden": False}],
            ),
            Project(
                id="proj-health-3", title="健康数据分析系统",
                description="基于 BMI 公式计算身体质量指数并输出健康分类评级",
                difficulty="easy", estimated_hours=2,
                init_code="def calculate_bmi(height, weight):\n    # TODO: 计算 BMI 指数并返回分类\n    pass\n",
                readme_markdown="# 健康数据分析系统\n\n## 目标\n根据身高(m)和体重(kg)自动计算 BMI 并给出健康评级。\n\n## BMI 分类标准\n- < 18.5: 偏瘦\n- 18.5 ~ 24: 正常\n- >= 24: 偏胖\n",
                test_cases=[{"input": "1.75, 65", "expectedOutput": "正常", "isHidden": False}],
            ),
            Project(
                id="proj-library-6", title="公益图书角管理系统",
                description="实现图书录入、借阅查询、库存更新与图书信息修改",
                difficulty="medium", estimated_hours=4,
                init_code="class LibrarySystem:\n    def __init__(self):\n        self.books = {}\n    def add_book(self, title, count=1):\n        # TODO: 增加图书\n        pass\n    def borrow(self, title):\n        # TODO: 借阅逻辑\n        pass\n    def query(self, title):\n        # TODO: 查询库存\n        pass\n",
                readme_markdown="# 公益图书角管理系统\n\n## 目标\n使用字典与函数模块化管理图书资源，实现借阅和归还功能。\n",
                test_cases=[{"input": "", "expectedOutput": "", "isHidden": False}],
            ),
            Project(
                id="proj-finance-9", title="个人财务管理系统",
                description="设计 Account 类与 Transaction 记录实现收入、支出与余额核算",
                difficulty="hard", estimated_hours=5,
                init_code="class Account:\n    def __init__(self, owner, balance=0.0):\n        self.owner = owner\n        self.balance = balance\n    def deposit(self, amount):\n        # TODO: 存款逻辑\n        pass\n    def withdraw(self, amount):\n        # TODO: 取款逻辑，余额不足时拒绝\n        pass\n    def __str__(self):\n        # TODO: 格式化输出账户信息\n        pass\n",
                readme_markdown="# 个人财务管理系统\n\n## 目标\n运用 OOP 面向对象封装与方法重写管理个人资金流。\n\n## 功能要求\n- 支持存款和取款\n- 取款余额不足时返回 False\n- __str__ 方法格式：'Account[owner]: ¥balance'\n",
                test_cases=[{"input": "", "expectedOutput": "", "isHidden": False}],
            ),
        ]
        for pr in projects_list:
            session.add(pr)
        session.commit()
        print(f"Inserted {len(projects_list)} projects.")

        # ── 7. Practices (from PRACTICES_BY_NODE) ────────────────────────────
        practice_count = 0
        for node_id, prac_list in PRACTICES_BY_NODE.items():
            # Verify node exists
            if not session.get(KnowledgeNode, node_id):
                print(f"  Warning: node '{node_id}' not found, skipping practices.")
                continue
            for p in prac_list:
                session.add(Practice(
                    id=p["id"],
                    title=p["title"],
                    type="fixed",
                    difficulty=p["difficulty"],
                    knowledge_node_id=node_id,
                    prompt=p["prompt"],
                    starter_code=p["starter"],
                    solution_code=p["solution"],
                    test_cases=p["tests"],
                ))
                practice_count += 1
        session.commit()
        print(f"Inserted {practice_count} practices across {len(PRACTICES_BY_NODE)} nodes.")

    # ── Print tree for verification ───────────────────────────────────────────
    print("\nKnowledge tree:")
    print_tree(tree_info, nodes_data)


def print_tree(tree_info: dict, nodes_data: list):
    """Pretty-print the tree."""
    name_map = {n["id"]: n["name"] for n in nodes_data}
    children: dict = defaultdict(list)
    roots = []
    for nid, info in tree_info.items():
        if info["parent_id"] is None:
            roots.append(nid)
        else:
            children[info["parent_id"]].append((nid, info["sort_order"]))

    def _print(nid, indent=0):
        name = name_map.get(nid, nid)
        depth = tree_info[nid]["depth"]
        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}{name} (depth={depth})")
        for kid_id, _ in sorted(children.get(nid, []), key=lambda x: x[1]):
            _print(kid_id, indent + 1)

    for root in roots:
        _print(root)


if __name__ == "__main__":
    seed()
