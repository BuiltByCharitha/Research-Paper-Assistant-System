from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import uuid
import json
import jwt

from services.pdf_loader import extract_text, chunk_text
from services.embedder import create_index_for_paper, load_paper_index, STORAGE_DIR
from services.summarizer import summarize_full_paper, summarize_query, global_query, SUPPORTED_MODELS
from services.database import SessionLocal, Base, engine, Paper, User

# ---- Create tables ----
Base.metadata.create_all(bind=engine)

# ---- FastAPI app ----
app = FastAPI(title="Research Paper Assistant System")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- JWT & Auth setup ----
SECRET_KEY = "your-secret-key"  # replace with env variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---- DB dependency ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Password utils ----
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ---- Schemas ----
class UserCreate(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    paper_id: str
    query: str
    top_k: int = 3
    model: str = "phi3:mini"

class SummarizeRequest(BaseModel):
    paper_id: str
    model: str = "phi3:mini"

class GlobalQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    model: str = "phi3:mini"
    use_papers: bool = True

# ---- Auth endpoints ----
@app.post("/signup/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = get_password_hash(user.password)
    db_user = User(id=str(uuid.uuid4())[:8], username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ---- Paper Upload ----
@app.post("/upload-paper/")
async def upload_paper(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    paper_id = str(uuid.uuid4())[:8]
    paper_dir = os.path.join(STORAGE_DIR, paper_id)
    os.makedirs(paper_dir, exist_ok=True)

    file_path = os.path.join(paper_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)
    chunks = chunk_text(text)
    metadata = create_index_for_paper(paper_id, chunks)
    metadata["title"] = file.filename

    paper_entry = Paper(id=paper_id, title=file.filename, user_id=current_user.id)
    db.add(paper_entry)
    db.commit()

    return {"message": f"Paper '{file.filename}' uploaded successfully!", "paper_id": paper_id}

# ---- List Papers ----
@app.get("/list-papers/")
def list_papers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_papers = db.query(Paper).filter(Paper.user_id == current_user.id).all()
    papers = [{"id": p.id, "title": p.title} for p in db_papers]
    return {"papers": papers}

# ---- Keyword-based Recommendation ----
@app.get("/recommend-papers/")
def recommend_papers(keyword: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_papers = db.query(Paper).filter(Paper.user_id == current_user.id).all()
    papers = [{"id": p.id, "title": p.title} for p in db_papers if keyword.lower() in p.title.lower()]
    return {"recommended_papers": papers}

# ---- Summarization & Query Endpoints ----
@app.post("/summarize-full/")
def summarize_full(req: SummarizeRequest, current_user: User = Depends(get_current_user)):
    if req.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from {SUPPORTED_MODELS}")
    return {"paper_id": req.paper_id, "summary": summarize_full_paper(req.paper_id, model=req.model), "model": req.model}

@app.post("/summarize-query/")
def summarize_query_endpoint(req: QueryRequest, current_user: User = Depends(get_current_user)):
    if req.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from {SUPPORTED_MODELS}")
    return {"query": req.query, "answer": summarize_query(req.paper_id, req.query, req.top_k, req.model), "model": req.model}

@app.post("/global-query/")
def global_query_endpoint(req: GlobalQueryRequest, current_user: User = Depends(get_current_user)):
    return {
        "query": req.query,
        "answer": global_query(req.query, req.top_k, req.model, req.use_papers),
        "model": req.model,
        "used_papers": req.use_papers
    }

# ---- Supported Models ----
@app.get("/models/")
def get_models(current_user: User = Depends(get_current_user)):
    return {"supported_models": SUPPORTED_MODELS}

# ---- Root ----
@app.get("/")
def root():
    return {"message": "Research Paper Assistant System is running"}
