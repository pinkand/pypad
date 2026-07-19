from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uvicorn

app = FastAPI(title="Python Learning OS API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class KnowledgeNode(BaseModel):
    id: str
    name: str
    description: str
    category: str
    importance: int
    prerequisites: List[str] = []

class KnowledgeEdge(BaseModel):
    source: str
    target: str
    relationType: str
    strength: str = "soft"

class UserKnowledge(BaseModel):
    userId: str
    knowledgeId: str
    masteryScore: float = 0.0
    lastStudyTime: Optional[str] = None

class StudyRecord(BaseModel):
    userId: str
    knowledgeId: str
    duration: int
    behavior: str
    result: dict = {}

class AgentRequest(BaseModel):
    message: str
    agentType: str = "tutor"
    knowledgeId: Optional[str] = None

# 模拟数据
knowledge_nodes = []
knowledge_edges = []
user_knowledge = {}
study_records = []

# 加载知识数据
@app.on_event("startup")
async def load_knowledge_data():
    try:
        with open("public/data/python-knowledge.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            global knowledge_nodes, knowledge_edges
            knowledge_nodes = data.get("nodes", [])
            knowledge_edges = data.get("edges", [])
    except Exception as e:
        print(f"Failed to load knowledge data: {e}")

# API路由
@app.get("/")
async def root():
    return {"message": "Python Learning OS API"}

@app.get("/api/knowledge/nodes", response_model=List[KnowledgeNode])
async def get_knowledge_nodes():
    return knowledge_nodes

@app.get("/api/knowledge/nodes/{node_id}", response_model=KnowledgeNode)
async def get_knowledge_node(node_id: str):
    for node in knowledge_nodes:
        if node["id"] == node_id:
            return node
    raise HTTPException(status_code=404, detail="Knowledge node not found")

@app.get("/api/knowledge/relations", response_model=List[KnowledgeEdge])
async def get_knowledge_relations():
    return knowledge_edges

@app.get("/api/knowledge/categories")
async def get_knowledge_categories():
    categories = list(set(node["category"] for node in knowledge_nodes))
    return {"categories": categories}

@app.get("/api/user/knowledge")
async def get_user_knowledge(user_id: str = "user-1"):
    user_nodes = user_knowledge.get(user_id, {})
    return {"userId": user_id, "knowledge": user_nodes}

@app.post("/api/user/knowledge")
async def update_user_knowledge(data: UserKnowledge):
    if data.userId not in user_knowledge:
        user_knowledge[data.userId] = {}
    user_knowledge[data.userId][data.knowledgeId] = {
        "masteryScore": data.masteryScore,
        "lastStudyTime": data.lastStudyTime
    }
    return {"success": True}

@app.post("/api/user/study")
async def record_study(data: StudyRecord):
    study_records.append({
        "userId": data.userId,
        "knowledgeId": data.knowledgeId,
        "duration": data.duration,
        "behavior": data.behavior,
        "result": data.result
    })
    return {"success": True, "recordId": len(study_records)}

@app.get("/api/user/study-records")
async def get_study_records(user_id: str = "user-1", limit: int = 10):
    user_records = [r for r in study_records if r["userId"] == user_id]
    return {"records": user_records[-limit:]}

@app.post("/api/agent/chat")
async def chat_with_agent(request: AgentRequest):
    # 模拟AI响应
    response = {
        "message": f"这是来自{request.agentType}的响应：{request.message}",
        "agentType": request.agentType,
        "knowledgeId": request.knowledgeId
    }
    return response

@app.post("/api/agent/plan")
async def generate_learning_plan(goal: str):
    # 模拟学习计划生成
    plan = {
        "goal": goal,
        "nodes": ["python-basics", "variables", "control-flow", "functions", "oop"],
        "estimatedTime": "20小时"
    }
    return plan

@app.post("/api/agent/practice")
async def generate_practice(knowledgeId: str, difficulty: str = "medium"):
    # 模拟练习题生成
    practice = {
        "knowledgeId": knowledgeId,
        "difficulty": difficulty,
        "questions": [
            {
                "id": 1,
                "question": f"关于{knowledgeId}的练习题",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "answer": "A"
            }
        ]
    }
    return practice

@app.get("/api/analytics/overview")
async def get_analytics_overview(user_id: str = "user-1"):
    user_nodes = user_knowledge.get(user_id, {})
    total_nodes = len(knowledge_nodes)
    mastered_nodes = sum(1 for n in user_nodes.values() if n.get("masteryScore", 0) >= 90)
    learning_nodes = sum(1 for n in user_nodes.values() if 60 <= n.get("masteryScore", 0) < 90)
    weak_nodes = sum(1 for n in user_nodes.values() if n.get("masteryScore", 0) < 60)
    
    return {
        "totalNodes": total_nodes,
        "masteredNodes": mastered_nodes,
        "learningNodes": learning_nodes,
        "weakNodes": weak_nodes,
        "averageMastery": sum(n.get("masteryScore", 0) for n in user_nodes.values()) / max(len(user_nodes), 1)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)