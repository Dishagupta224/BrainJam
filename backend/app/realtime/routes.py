from flask import Blueprint

bp = Blueprint("realtime", __name__, url_prefix="/ws")


@bp.get("/rooms/<room_id>")
def rooms_ws_placeholder(room_id: str):
    # Phase 4: implement real websocket endpoint (flask-sock or SocketIO)
    # For now this keeps blueprint registration stable.
    return "WebSocket not implemented yet", 501
