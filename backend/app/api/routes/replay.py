from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.replay_engine import get_replay_engine
from app.database.database import SessionLocal

router = APIRouter()

class SpeedRequest(BaseModel):
    speed: str  # 1x | 5x | 10x

@router.get("/replay/status")
def replay_status():
    engine = get_replay_engine()
    return engine.status()

@router.post("/replay/start")
def replay_start():
    engine = get_replay_engine()
    ok = engine.start()
    if not ok:
        return {"status": "already_running", **engine.status()}
    return {"status": "started", **engine.status()}

@router.post("/replay/stop")
def replay_stop():
    engine = get_replay_engine()
    ok = engine.stop()
    if not ok:
        return {"status": "not_running", **engine.status()}
    return {"status": "stopped", **engine.status()}

@router.post("/replay/reset")
def replay_reset():
    engine = get_replay_engine()
    engine.reset()
    return {"status": "reset", **engine.status()}

@router.post("/replay/speed")
def replay_speed(req: SpeedRequest):
    engine = get_replay_engine()
    ok = engine.set_speed(req.speed)
    if not ok:
        raise HTTPException(status_code=422, detail="speed must be 1x, 5x, or 10x")
    return {"status": "speed_updated", **engine.status()}

@router.post("/replay/step")
def replay_step():
    engine = get_replay_engine()
    db = SessionLocal()
    try:
        result = engine.step(db=db)
    finally:
        db.close()
    if not result:
        raise HTTPException(status_code=500, detail="replay step failed")
    return result

@router.post("/replay/reload")
def replay_reload():
    engine = get_replay_engine()
    engine.reload()
    return {"status": "reloaded", **engine.status()}
